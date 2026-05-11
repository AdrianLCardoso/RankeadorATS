
# 📈 Rankeador On-line de Currículos (ATS)

Este projeto é uma ferramenta avançada de análise e ranqueamento de currículos, desenhada para simular o comportamento de sistemas **ATS (Applicant Tracking Systems)**. Através de Inteligência Artificial Generativa (**Google Gemini**), a aplicação cruza dados de currículos em PDF com descrições de vagas para fornecer métricas de compatibilidade e insights estratégicos.

## 🚀 Funcionalidades

* **Extração Inteligente**: Conversão precisa de currículos PDF em texto processável via `pdfplumber`.
* **Análise de Compatibilidade (Score)**: Algoritmo de IA que calcula a aderência (0-100) baseada em requisitos técnicos e soft skills.
* **Visualização de Competências**: Gráficos de radar/barra polar que evidenciam graficamente o nível das competências detetadas.
* **Pesquisa de Mercado Automatizada**: Insights sobre a cultura da empresa alvo, benefícios e médias salariais (Jr, Pl, Sr).
* **Painel Administrativo**: Área restrita para monitorização de logs de consultas e métricas de uso do sistema.
* **Segurança Robusta**: Autenticação de utilizadores com criptografia de passwords (SHA-256) e gestão de acessos via variáveis de ambiente.

## 🛠️ Stack Tecnológica

* **Linguagem**: Python 3.10+
* **Framework Web**: [Streamlit](https://streamlit.io/)
* **IA & NLP**: [Google Gemini](https://ai.google.dev/) 
* **Base de Dados**: SQLite (Persistência de utilizadores e auditoria)
* **Processamento de PDF**: `pdfplumber`
* **Visualização de Dados**: Plotly Express & Pandas

## 📦 Estrutura do Projeto

```text
├── assets/              # Logótipos das plataformas e recursos visuais
├── app.py               # Interface principal e navegação
├── main.py              # Lógica de extração PDF e integração Gemini
├── database.py          # Gestão de base de dados e segurança
├── requirements.txt     # Dependências do sistema
├── .gitignore           # Proteção de dados sensíveis e cache
└── LICENSE              # Licença MIT
```

## ⚖️ Licença

Este projeto está licenciado sob a  **Licença MIT** . Consulte o ficheiro [LICENSE](https://www.google.com/search?q=LICENSE) para mais detalhes.


##### 👔Desenvolvido por  Adrian Cardoso - Graduando em Ciência de Dados.

##### Marcas e logotipos exibidos pertencem aos seus respectivos proprietários e são utilizados aqui apenas para fins ilustrativos e de portfólio acadêmico.
