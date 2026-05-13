import os
import json
import pdfplumber
from google import genai
from dotenv import load_dotenv

# CONFIGURAÇÕES
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERRO: API Key não encontrada!")
    exit()

client = genai.Client(api_key=api_key)

# EXTRAÇÃO (PDF -> TEXTO)
def extrair_texto_pdf(caminho_pdf):
    texto_completo = ""
    try:
        if not os.path.exists(caminho_pdf):
            return f"Erro: Arquivo {caminho_pdf} não encontrado."
            
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() + "\n"
        return texto_completo.strip()
    except Exception as e:
        return f"Erro na leitura: {str(e)}"

# ANÁLISE COM A IA
def analisar_cv_com_ia(texto_cv, descricao_vaga, nome_empresa, cargo):
    prompt = f"""
    Aja como um Recrutador Técnico e Especialista em Algoritmos ATS. 
    Analise o currículo para o cargo de {cargo} na empresa {nome_empresa}.
    
    CURRÍCULO: {texto_cv}
    VAGA: {descricao_vaga}

    --- DIRETRIZES DE CALIBRAGEM (PESOS) ---
    1. PESO TÉCNICO (70%): Identifique as 5 Hard Skills mais críticas e 3 ferramentas na 'Descrição da Vaga' e utilize-as como base principal de comparação com o currículo.
    2. COMPENSAÇÃO DE EXPERIÊNCIA: Se o candidato possuir tempo de mercado em funções correlatas à vaga, Aplique um multiplicador de compensação de 1.05x, reduzindo o impacto de graduações ainda não concluídas.
    3. PENALIDADE DE ATS: Simule o rigor das plataformas, mas não zere o score por falta de 'Superior Completo' se o candidato demonstrar maturidade técnica e profissional equivalente.
    4. REGRA INEGOCIÁVEL: Use o formato 'R$ X.XXX - X.XXX' e use pontos para milhares.

    --- SIMULAÇÃO DE PLATAFORMAS ---
    - Gupy: Foco em densidade de Keywords e NLP.
    - Sólides: Foco em Hard Skills e fit de competências.
    - Workday: Foco em estrutura organizacional e progressão de carreira.

    SAÍDA OBRIGATÓRIA EM JSON (RETORNE APENAS O JSON):
    {{
        "score": int,
        "sugestoes": [],
        "competencias": {{ "Skill": 0-100 }},
        "ats_estimativa": {{
            "Gupy": int,
            "Sólides": int,
            "Workday": int,
            "Linkedin": int
        }},
        "empresa_pesquisa": {{
            "o_que_faz": "resumo curto",
            "salarios": {{ "Jr": "R$ X", "Pl": "R$ Y", "Sr": "R$ Z" }},
            "satisfacao": "nota e resumo estilo glassdoor",
            "cultura": "principais valores",
            "veracidade_da_vaga": "verificar se a vaga realmente existe e/ou foi criada por inteligência artificial"
        }}
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config={
                'temperature': 0.0,
                'response_mime_type': 'application/json'
                }
        )
        
        raw_text = response.text.strip()
        
        # Segurança contra resposta vazia
        if not raw_text:
            return {"error": "A API retornou um texto vazio.", "score": 0}
        
        # Limpeza de Markdown
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
        return json.loads(raw_text)
    
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON Malformado: {str(e)}", 
            "score": 0,
            "raw_output": raw_text[:300] # Para debug no terminal
        }
    except Exception as e:
        return {
            "error": f"Erro de processamento: {str(e)}", 
            "score": 0,
            "sugestoes": ["Não foi possível gerar sugestões."],
            "competencias": {},
            "empresa_pesquisa": {}
        }

# EXECUÇÃO
if __name__ == "__main__":
    cv_arquivo = "xxx.pdf"
    vaga_desc = "xxx xxx"
    empresa_alvo = "xxx"
    cargo_alvo = "xxx"

    print("--- 1. Extraindo texto do PDF ---")
    texto = extrair_texto_pdf(cv_arquivo)

    if "Erro" in texto:
        print(texto)
    else:
        print("--- 2. Enviando para análise (IA) ---")
        resultado = analisar_cv_com_ia(texto, vaga_desc, empresa_alvo, cargo_alvo)
        
        if "error" in resultado:
            print(f"⚠️ Falha: {resultado['error']}")
        else:
            print("\n✅ ANÁLISE CONCLUÍDA:")
            print(json.dumps(resultado, indent=4, ensure_ascii=False))
