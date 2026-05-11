import hashlib
import psycopg2
import streamlit as st
import pandas as pd
from datetime import datetime

def conectar():
    # Busca a URL
    return psycopg2.connect(st.secrets["DB_URL"])

def criar_tabela():
    conn = conectar()
    c = conn.cursor()
    
    # Cria tabelas se não existirem
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (email TEXT PRIMARY KEY, senha TEXT, tipo TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS logs (data TEXT, usuario TEXT, empresa TEXT, cargo TEXT, score INTEGER)')
    
    meu_email = st.secrets.get("ADMIN_EMAIL") 
    if meu_email:
        c.execute('SELECT * FROM usuarios WHERE email = %s', (meu_email,))
        user = c.fetchone()
        
        if user:
            if user[2] != 'admin':
                c.execute("UPDATE usuarios SET tipo = 'admin' WHERE email = %s", (meu_email,))
                conn.commit()
        else:
            senha_padrao = hash_senha("mudar_em_breve")
            c.execute('INSERT INTO usuarios VALUES (%s, %s, %s)', (meu_email, senha_padrao, "admin"))
            conn.commit()

    c.close()
    conn.close()

def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def criar_usuario(email, senha):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO usuarios VALUES (%s, %s, %s)', (email, hash_senha(senha), 'user'))
        conn.commit()
        return True
    except:
        return False
    finally:
        c.close()
        conn.close()

def autenticar_usuario(email, senha):
    conn = conectar()
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE email = %s AND senha = %s', (email, hash_senha(senha)))
    res = c.fetchone()
    c.close()
    conn.close()
    return res

def registrar_log(usuario, empresa, cargo, score):
    conn = conectar()
    c = conn.cursor()
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO logs VALUES (%s, %s, %s, %s, %s)", (data, usuario, empresa, cargo, score))
    conn.commit()
    c.close()
    conn.close()

def buscar_logs():
    conn = conectar()
    df = pd.read_sql('SELECT * FROM logs ORDER BY data DESC', conn)
    conn.close()
    return df
def obter_metricas_admin():
    conn = conectar()
    u_count = pd.read_sql("SELECT COUNT(*) as t FROM usuarios", conn).iloc[0]['t']
    a_count = pd.read_sql("SELECT COUNT(*) as t FROM logs", conn).iloc[0]['t']
    df_logs = pd.read_sql("SELECT * FROM logs ORDER BY data DESC LIMIT 10", conn)
    conn.close()
    return u_count, a_count, df_logs
