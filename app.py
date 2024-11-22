import streamlit as st
import analise_de_risco
import atendentes
import churn
import rh_um
import rh_dois

# Configuração do layout e estado do menu lateral
st.set_page_config(
    page_title="Dashboard Navigation",
    layout="wide",
    initial_sidebar_state="collapsed",  # Define o menu recolhido inicialmente
)

# Título da aplicação
st.title("Estudo de Caso: BBG Telecom")

# Menu lateral para selecionar o dashboard
menu = st.sidebar.selectbox(
    "Selecione o Dashboard",
    ["Performance do SAC", "Análise de Risco do Cliente", "Análise de Churn", "Diversidade e Inclusão 1", "Diversidade e Inclusão 2"]
)

# Carregar o dashboard selecionado
if menu == "Performance do SAC":
    atendentes.main()  # Chama a função principal do arquivo atendentes.py
elif menu == "Análise de Churn":
    churn.main()  # Chama a função principal do arquivo churn.py
elif menu == "Análise de Risco do Cliente":
    analise_de_risco.main()  # Chama a função principal do arquivo analise_de_risco.py
elif menu == "Diversidade e Inclusão 1":
    rh_um.main()  # Chama a função principal do arquivo churn.py
elif menu == "Diversidade e Inclusão 2":
    rh_dois.main()  # Chama a função principal do arquivo churn.py