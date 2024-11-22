import streamlit as st
import pandas as pd
import plotly.express as px

def main():
# Configurando a página

#st.set_page_config(page_title="Churn Dashboard", layout="wide", page_icon="📊")

# Título do Dashboard centralizado
    st.markdown("<h1 style='text-align: center;'>Análise de Churn</h1>", unsafe_allow_html=True)

    # Carregando o dataset
    # Substitua 'seu_arquivo.xlsx' pelo caminho do seu arquivo de dados
    df = pd.read_excel(r'CLIENTE E TIPO DE SERVIÇO.xlsx')

    # Calculando as métricas para a top row
    clientes_churn = df[df['Churn'] == 'Yes'].shape[0]
    total_tickets_tech = df['numTechTickets'].sum()
    total_tickets_admin = df['numAdminTickets'].sum()
    receita_anual = df[df['Contract'] == 'One year']['MonthlyCharges'].sum() * 12
    receita_mensal = df[df['Contract'] == 'Month-to-month']['MonthlyCharges'].sum()

    # Estilo CSS para as métricas
    st.markdown("""
        <style>
            .metric-box {
                background-color: #00407d;
                border: 1px solid #d3d3d3;
                border-radius: 5px;
                padding: 20px;
                margin: 10px;
                text-align: center;
            }
            .title {
                font-size: 20px;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    # Criando a linha superior (top row) com cinco blocos de métricas
    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f'<div class="metric-box"><span class="title">Clientes com risco de Churn</span><br>{clientes_churn}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><span class="title">Tickets Técnicos</span><br>{total_tickets_tech}</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><span class="title">Tickets Admin</span><br>{total_tickets_admin}</div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-box"><span class="title">Receita por Cobrança Anual</span><br>R$ {receita_anual:,.2f}</div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="metric-box"><span class="title">Receita por Cobrança Mensal</span><br>R$ {receita_mensal:,.2f}</div>', unsafe_allow_html=True)

    # Criando a linha inferior (bottom row) diretamente como três colunas
    with st.container():
        left_col, mid_col, right_col = st.columns([1, 1, 1])

        # Configurando a coluna left com título e dados demográficos
        with left_col:
            st.markdown("### Dados Demográficos")
            # Gráfico de rosca para mostrar os gêneros
            genero_data = df['gender'].value_counts()
            fig_donut = px.pie(
                names=genero_data.index,
                values=genero_data.values,
                hole=0.5,
                title="Distribuição de Gênero",
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_donut)

            # Gráfico de barras horizontais mostrando a duração do contrato
            df['Contract_Duration'] = pd.cut(
                df['tenure'],
                bins=[0, 12, 24, 36, 48, 60],
                labels=['< 1 ano', '< 2 anos', '< 3 anos', '< 4 anos', '< 5 anos'],
                right=False
            )
            contract_data = df['Contract_Duration'].value_counts().sort_index(ascending=False)  # Inverte a ordem aqui
            fig_bar = px.bar(
                contract_data,
                x=contract_data.values,
                y=contract_data.index,
                orientation='h',
                title='Tipo de Assinatura por Duração',
                labels={'x': 'Número de Clientes', 'y': 'Duração do Contrato'}
            )
            st.plotly_chart(fig_bar)

            # Três métricas adicionais para % de Idosos, Parceiros e Dependentes
            percent_seniors = (df['SeniorCitizen'].sum() / len(df)) * 100
            percent_partners = (df['Partner'].value_counts().get('Yes', 0) / len(df)) * 100
            percent_dependents = (df['Dependents'].value_counts().get('Yes', 0) / len(df)) * 100

            col1, col2, col3 = st.columns(3)
            col1.metric("% de Idosos", f"{percent_seniors:.2f}%")
            col2.metric("% de Parceiros", f"{percent_partners:.2f}%")
            col3.metric("% de Dependentes", f"{percent_dependents:.2f}%")

        # Configurando a coluna mid com título e informações da conta do cliente
        with mid_col:
            st.markdown("### Informações da Conta do Cliente")
            # Gráfico de barras clusterizado para os tipos de pagamento
            payment_data = df['PaymentMethod'].value_counts(normalize=True) * 100
            payment_df = pd.DataFrame({
                'Payment Method': payment_data.index,
                'Percentage': payment_data.values
            })
            fig_payment = px.bar(
                payment_df,
                x='Payment Method',
                y='Percentage',
                title='Tipos de Pagamento',
                text='Percentage',
                labels={'Payment Method': 'Método de Pagamento', 'Percentage': 'Porcentagem'}
            )
            fig_payment.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
            st.plotly_chart(fig_payment)

            # Gráfico de rosca para Pagamentos sem papel
            paperless_counts = df['PaperlessBilling'].value_counts()
            fig_paperless = px.pie(
                names=paperless_counts.index,
                values=paperless_counts.values,
                hole=0.5,
                title="Uso de pagamentos sem papel",
            )
            fig_paperless.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_paperless)

            # Dados de receita para Paperless Billing
            selected_option = st.radio("Selecionar tipo de Pagamento:", ("Sem papel", "Com papel"))

            if selected_option == "Sem papel":
                filtered_data = df[df['PaperlessBilling'] == 'Yes']
            else:
                filtered_data = df[df['PaperlessBilling'] == 'No']

            revenue_monthly = filtered_data['MonthlyCharges'].sum()
            revenue_total = revenue_monthly * 12

            col1, col2 = st.columns(2)
            col1.metric("Receita Mensal", f"R$ {revenue_monthly:,.2f}")
            col2.metric("Receita Total", f"R$ {revenue_total:,.2f}")

            # Gráfico de barras clusterizado de tipo de contratos e suas porcentagens
            contract_type_counts = df['Contract'].value_counts(normalize=True) * 100
            contract_df = pd.DataFrame({
                'Contract Type': contract_type_counts.index,
                'Percentage': contract_type_counts.values
            })
            fig_contract = px.bar(
                contract_df,
                x='Contract Type',
                y='Percentage',
                title='Tipos de Contrato e Porcentagens',
                text='Percentage',
                labels={'Contract Type': 'Tipo de Contrato', 'Percentage': 'Porcentagem'}
            )
            fig_contract.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
            st.plotly_chart(fig_contract)

        # Configurando a coluna right com título e serviços que os clientes assinaram
        with right_col:
            st.markdown("### Serviços que os Clientes Assinaram")
            # Cálculo das porcentagens de serviços assinados
            services = ['PhoneService', 'StreamingTV', 'StreamingMovies', 'DeviceProtection', 'OnlineBackup', 'TechSupport', 'OnlineSecurity']
            services_percent = {service: (df[service].value_counts(normalize=True) * 100).get('Yes', 0) for service in services}

            # Criando um DataFrame para as porcentagens
            services_df = pd.DataFrame(list(services_percent.items()), columns=['Serviço', 'Porcentagem'])
            fig_services = px.bar(
                services_df,
                x='Porcentagem',
                y='Serviço',
                title='Porcentagem de Serviços Assinados',
                labels={'Serviço': 'Serviço', 'Porcentagem': 'Porcentagem'},
                text='Porcentagem',
                orientation='h'
            )
            fig_services.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
            st.plotly_chart(fig_services)

            # Exibindo se os clientes contrataram múltiplos serviços
            internet_data = df['InternetService'].value_counts()
            fig_internet = px.pie(
                names=internet_data.index,
                values=internet_data.values,
                hole=0.5,
                title="Serviços de Internet Contratados",
            )
            fig_internet.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_internet)

