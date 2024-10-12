import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Função para formatar valores monetários no estilo brasileiro
def format_currency(value):
    """Format the currency value to Brazilian style."""
    if value >= 1_000_000:
        return f"R$ {value / 1_000_000:.1f} Milhões"
    elif value >= 1_000:
        return f"R$ {value / 1_000:.0f} Mil"
    else:
        return f"R$ {value:.2f}"
    
def main():

    #st.set_page_config(page_title="Análise de Risco do Cliente", layout="wide", page_icon="📊")

# Carregar dados do Excel
    
    st.markdown("<h1 style='text-align: center;'>Análise de Risco do Cliente</h1>", unsafe_allow_html=True)
    file_path = r'CLIENTE E TIPO DE SERVIÇO.xlsx'
    data = pd.read_excel(file_path)

    # Converter a coluna 'TotalCharges' para numérico, forçando erros a se tornarem NaN
    data['TotalCharges'] = pd.to_numeric(data['TotalCharges'], errors='coerce')

    # Dividir o layout em duas colunas principais
    left_column, right_column = st.columns([1, 3])

    # Conteúdo da coluna esquerda
    with left_column:
        st.header("Filtros")
        
        # Filtro de Risco de Churn
        churn_risk_sim = st.checkbox("Risco de Churn: Sim")
        churn_risk_nao = st.checkbox("Risco de Churn: Não")
        
        # Filtro de Tipo de Internet
        st.subheader("Tipo de Internet:")
        internet_dsl = st.checkbox("DSL")
        internet_fiber = st.checkbox("Fibra Ótica")
        internet_no = st.checkbox("Sem Internet")
        
        # Filtro de Tipo de Contrato
        st.subheader("Tipo de Contrato:")
        contract_monthly = st.checkbox("Mês a Mês")
        contract_annual = st.checkbox("Um Ano")
        contract_two_years = st.checkbox("Dois Anos")
        
        # Slider de Tenure
        tenure_range = st.slider(
            "Selecionar Tenure (meses):",
            min_value=0,
            max_value=72,
            value=(0, 72)  # Valor padrão do slider
        )

    # Filtrar dados com base nos seletores
    filtered_data = data.copy()

    # Aplicar filtro de Risco de Churn
    if churn_risk_sim:
        filtered_data = filtered_data[filtered_data['Churn'] == 'Yes']
    if churn_risk_nao:
        filtered_data = filtered_data[filtered_data['Churn'] == 'No']

    # Aplicar filtro de Tipo de Internet
    if internet_dsl:
        filtered_data = filtered_data[filtered_data['InternetService'] == 'DSL']
    if internet_fiber:
        filtered_data = filtered_data[filtered_data['InternetService'] == 'Fiber optic']
    if internet_no:
        filtered_data = filtered_data[filtered_data['InternetService'] == 'No']

    # Aplicar filtro de Tipo de Contrato
    if contract_monthly:
        filtered_data = filtered_data[filtered_data['Contract'] == 'Month-to-month']
    if contract_annual:
        filtered_data = filtered_data[filtered_data['Contract'] == 'One year']
    if contract_two_years:
        filtered_data = filtered_data[filtered_data['Contract'] == 'Two year']

    # Aplicar filtro de Tenure
    filtered_data = filtered_data[
        (filtered_data['tenure'] >= tenure_range[0]) & 
        (filtered_data['tenure'] <= tenure_range[1])
    ]

    # Conteúdo da coluna direita
    with right_column:
        # Dividir a coluna direita em dois contêineres (top e bottom)
        with st.container():  # Top row
            # Calcular e exibir os dados
            total_customers = len(filtered_data)
            churn_percentage = (filtered_data['Churn'].value_counts(normalize=True) * 100).get('Yes', 0)
            
            # Calcular pagamentos anuais
            total_charges = filtered_data['TotalCharges'].sum()
            tech_tickets = filtered_data['numTechTickets'].sum() if 'numTechTickets' in filtered_data else 0
            admin_tickets = filtered_data['numAdminTickets'].sum() if 'numAdminTickets' in filtered_data else 0
            
            # Criar colunas para exibir os dados na horizontal
            metrics_columns = st.columns(5)

            # Definir estilo para a caixa de métricas
            metric_box_style = """
                <style>
                .metric-box {
                    background-color: #00407d;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                    text-align: center;
                    font-size: 18px;
                    color: white;
                    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
                }
                </style>
            """
            st.markdown(metric_box_style, unsafe_allow_html=True)

            with metrics_columns[0]:
                st.markdown("<div class='metric-box'>Número Total de Clientes:<br><strong>{}</strong></div>".format(total_customers), unsafe_allow_html=True)
            
            with metrics_columns[1]:
                st.markdown("<div class='metric-box'>Porcentagem de Churn:<br><strong>{:.2f}%</strong></div>".format(churn_percentage), unsafe_allow_html=True)
            
            with metrics_columns[2]:
                st.markdown("<div class='metric-box'>Pagamentos Anuais:<br><strong>{}</strong></div>".format(format_currency(total_charges)), unsafe_allow_html=True)
            
            with metrics_columns[3]:
                st.markdown("<div class='metric-box'>Tickets Técnicos:<br><strong>{}</strong></div>".format(tech_tickets), unsafe_allow_html=True)
            
            with metrics_columns[4]:
                st.markdown("<div class='metric-box'>Tickets Administrativos:<br><strong>{}</strong></div>".format(admin_tickets), unsafe_allow_html=True)

        # Conteúdo da seção inferior (bottom)
        with st.container():  # Bottom row
            st.header("Análises Gráficas")
            
            # Dividir o bottom row em três colunas
            bottom_left, bottom_mid, bottom_right = st.columns(3)

            with bottom_left:
                # Gráfico de Colunas Clusterizado: Churn por Tipo de Serviço de Internet
                churn_by_internet = filtered_data.groupby(['InternetService', 'Churn']).size().reset_index(name='Count')
                churn_fig = px.bar(churn_by_internet, x='InternetService', y='Count', color='Churn', barmode='group',
                                labels={'Count': 'Contagem', 'InternetService': 'Tipo de Serviço'},
                                title='Churn por Tipo de Serviço de Internet')
                st.plotly_chart(churn_fig, height=400)

                # Gráfico de Churn Rate x Tipo de Contrato
                churn_by_contract = filtered_data.groupby(['Contract', 'Churn']).size().unstack(fill_value=0)
                churn_by_contract['Total_Customers'] = churn_by_contract.sum(axis=1)
                churn_fig_contract = go.Figure()
                churn_fig_contract.add_trace(go.Bar(
                    x=churn_by_contract.index,
                    y=churn_by_contract['Yes'],
                    name='Churn Rate',
                    marker_color='blue'
                ))
                churn_fig_contract.add_trace(go.Scatter(
                    x=churn_by_contract.index,
                    y=churn_by_contract['Total_Customers'],
                    name='Total de Clientes',
                    mode='lines+markers',
                    line=dict(color='red')
                ))
                churn_fig_contract.update_layout(title='Churn Rate por Tipo de Contrato')
                st.plotly_chart(churn_fig_contract, height=400)

            with bottom_mid:
                # Gráfico de Pizza: Clientes por Tipo de Serviço de Internet
                internet_service_counts = filtered_data['InternetService'].value_counts()
                pie_fig1 = go.Figure(data=[go.Pie(labels=internet_service_counts.index, values=internet_service_counts.values, hole=.3)])
                pie_fig1.update_layout(title_text='Clientes por Tipo de Serviço de Internet')
                st.plotly_chart(pie_fig1, height=400)

                # Gráfico de Tendência de Churn ao Longo do Tempo
                filtered_data['tenure_years'] = (filtered_data['tenure'] / 12).astype(int)
                churn_over_time = filtered_data.groupby(['tenure_years', 'Churn']).size().unstack(fill_value=0)
                churn_over_time_fig = go.Figure()
                churn_over_time_fig.add_trace(go.Scatter(
                    x=churn_over_time.index,
                    y=churn_over_time['Yes'],
                    name='Churn',
                    mode='lines+markers',
                    marker=dict(color='blue')
                ))
                churn_over_time_fig.update_layout(title='Tendência de Churn ao Longo do Tempo', xaxis_title='Tenure (Anos)', yaxis_title='Contagem')
                st.plotly_chart(churn_over_time_fig, height=400)

            with bottom_right:
                # Gráfico de Pizza: Soma de Pagamentos Mensais (MonthlyCharges)
                monthly_revenue = filtered_data.groupby('InternetService')['MonthlyCharges'].sum().reset_index()
                pie_fig2 = go.Figure(data=[go.Pie(labels=monthly_revenue['InternetService'], values=monthly_revenue['MonthlyCharges'], hole=.3)])
                pie_fig2.update_layout(title_text='Soma de Pagamentos Mensais por Tipo de Serviço de Internet')
                st.plotly_chart(pie_fig2, height=400)

                # Agrupamento dos dados por Método de Pagamento e Churn
                churn_by_payment = filtered_data.groupby(['PaymentMethod', 'Churn']).size().unstack(fill_value=0)
                churn_by_payment['Total_Customers'] = churn_by_payment.sum(axis=1)
                churn_by_payment['Avg_MonthlyCharges'] = filtered_data.groupby('PaymentMethod')['MonthlyCharges'].mean()
    # Criação do gráfico de Churn por Método de Pagamento com linha para Monthly Charges
                churn_fig_payment = go.Figure()
    # Adicionando barras para a taxa de churn por método de pagamento
                churn_fig_payment.add_trace(go.Bar(
                x=churn_by_payment.index,
                y=churn_by_payment['Yes'],
                name='Churn Rate',
                marker_color='blue'
                ))
    # Adicionando uma linha para os valores médios de MonthlyCharges por método de pagamento
                churn_fig_payment.add_trace(go.Scatter(
                x=churn_by_payment.index,
                y=churn_by_payment['Avg_MonthlyCharges'],
                name='Média de Pagamentos Mensais',
                mode='lines+markers',
                line=dict(color='red')
                ))
    # Configuração do layout do gráfico
                churn_fig_payment.update_layout(
                title='Churn Rate por Método de Pagamento e Média de Pagamentos Mensais',
                xaxis_title='Método de Pagamento',
                yaxis_title='Valores',
                legend=dict(x=0.1, y=1.1, orientation='h'),
                template='simple_white',  # Aplicando um template simples sem fundo
                )
                # Adicionando o gráfico à posição bottom_right
                with bottom_right:
                    st.plotly_chart(churn_fig_payment, height=400)