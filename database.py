import sqlite3
import hashlib
import streamlit as st
import pandas as pd

def conectar():
    return sqlite3.connect('usuarios.db', check_same_thread=False)

import streamlit as st
import hashlib

def criar_tabela():
    conn = conectar()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (email TEXT PRIMARY KEY, senha TEXT, tipo TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS logs (data TEXT, usuario TEXT, empresa TEXT, cargo TEXT, score INTEGER)')
    
    #Busca E-mail
    meu_email = st.secrets.get("ADMIN_EMAIL") 
    
    if meu_email:
        c.execute('SELECT * FROM usuarios WHERE email = ?', (meu_email,))
        user = c.fetchone()
        if user and user[2] != 'admin':
            c.execute("UPDATE usuarios SET tipo = 'admin' WHERE email = ?", (meu_email,))
            conn.commit()
    
    c.execute('SELECT * FROM usuarios WHERE tipo = "admin"')
    if not c.fetchone() and not meu_email:
        # Só cria o admin@admin se você esquecer de configurar o seu e-mail nos Secrets
        senha_adm = hashlib.sha256("senha_muito_forte_aqui".encode()).hexdigest()
        c.execute('INSERT INTO usuarios VALUES (?, ?, ?)', ("admin@admin.com", senha_adm, "admin"))
        conn.commit()

    conn.close()

def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def criar_usuario(email, senha):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO usuarios VALUES (?, ?, ?)', (email, hash_senha(senha), 'user'))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def autenticar_usuario(email, senha):
    conn = conectar()
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, hash_senha(senha)))
    res = c.fetchone()
    conn.close()
    return res

def registrar_log(usuario, empresa, cargo, score):
    from datetime import datetime
    conn = conectar()
    c = conn.cursor()
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO logs VALUES (?, ?, ?, ?, ?)", (data, usuario, empresa, cargo, score))
    conn.commit()
    conn.close()

def obter_metricas_admin():
    conn = conectar()
    u_count = pd.read_sql("SELECT COUNT(*) as t FROM usuarios", conn).iloc[0]['t']
    a_count = pd.read_sql("SELECT COUNT(*) as t FROM logs", conn).iloc[0]['t']
    df_logs = pd.read_sql("SELECT * FROM logs ORDER BY data DESC LIMIT 10", conn)
    conn.close()
    return u_count, a_count, df_logs