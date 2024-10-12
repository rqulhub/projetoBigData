import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

def main():


# Configuração de layout da página
#st.set_page_config(layout="wide", page_title="Dashboard de Call Center", page_icon="📞")

# Carregar o conjunto de dados
    st.markdown("<h1 style='text-align: center;'>Análise de Performance de SAC</h1>", unsafe_allow_html=True)
    data = pd.read_excel(r'ATENDENTES E PERFORMANCE.xlsx')

    # Função para converter datetime.time para segundos
    def time_to_seconds(time_value):
        if isinstance(time_value, pd.Timestamp):
            return time_value.hour * 3600 + time_value.minute * 60 + time_value.second
        elif isinstance(time_value, datetime.time):
            return time_value.hour * 3600 + time_value.minute * 60 + time_value.second
        elif isinstance(time_value, (int, float)):
            return time_value
        return 0

    # Aplicar a função de conversão na coluna AvgTalkDuration para garantir que está em segundos
    data['AvgTalkDuration'] = data['AvgTalkDuration'].apply(time_to_seconds)

    # Converta a coluna 'Date' para o formato datetime (se necessário)
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

    # Cálculo da Velocidade Média de Resposta
    average_speed_of_answer = data['Speed of answer in seconds'].mean()

    # Cabeçalho centralizado


    # Definindo as colunas para organização (1, 2, 2, 1)
    col_left, col_leftmid, col_rightmid, col_right = st.columns([1, 2, 2, 1])

    # Coluna à esquerda (Filtros, Data, Satisfação)
    with col_left:
        st.markdown("<h3 class='small-font'>Filtros</h3>", unsafe_allow_html=True)

        # Filtro de agente
        selected_agent = st.selectbox("Selecione o Agente", options=['Todos'] + list(data['Agent'].unique()), index=0)
        
        # Filtro de tópico
        selected_topic = st.selectbox("Selecione o Tópico", options=['Todos'] + list(data['Topic'].unique()), index=0)

        # Filtro de data com select_slider
        st.markdown("<h3 class='small-font'>Selecione o intervalo de datas</h3>", unsafe_allow_html=True)
        start_date, end_date = st.select_slider(
            "Intervalo de datas:",
            options=pd.to_datetime(data['Date']).dt.date.unique(),
            value=(pd.to_datetime(data['Date']).dt.date.min(), pd.to_datetime(data['Date']).dt.date.max()),
        )

    # Filtrando os dados com base nos seletores
    filtered_data = data.copy()

    # Aplicar o filtro de data
    filtered_data = filtered_data[(filtered_data['Date'].dt.date >= start_date) & (filtered_data['Date'].dt.date <= end_date)]

    # Aplicar o filtro de agente
    if selected_agent != 'Todos':
        filtered_data = filtered_data[filtered_data['Agent'] == selected_agent]

    # Aplicar o filtro de tópico
    if selected_topic != 'Todos':
        filtered_data = filtered_data[filtered_data['Topic'] == selected_topic]

    # Cálculo da Satisfação Geral com base nos filtros aplicados
    average_satisfaction = filtered_data['Satisfaction rating'].mean()

    # Gráfico de Satisfação Média (tons mais escuros e centralizado)
    with col_left:
        st.markdown("<h3 class='small-font'>Satisfação Média</h3>", unsafe_allow_html=True)
        fig_satisfaction = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_satisfaction,
            gauge={'axis': {'range': [0, 5], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': '#4B0082'},  # Tons escuros
                'steps': [{'range': [0, 5], 'color': '#2c2c2c'}],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': average_satisfaction}},
            title={'text': "Satisfação Média", 'font': {'size': 16, 'color': 'white'}}
        ))
        fig_satisfaction.update_traces(number={'font': {'size': 50}, 'valueformat': '.2f'})
        fig_satisfaction.update_layout(height=300, width=400)
        st.plotly_chart(fig_satisfaction)

    # Coluna à esquerda central (Chamadas Atendidas e Número de Chamadas por Mês)
    with col_leftmid:
        # Gráficos de Chamadas Atendidas (aumentar tamanho)
        st.markdown("<h3 class='small-font'>Chamadas Atendidas</h3>", unsafe_allow_html=True)
        call_status = filtered_data['Answered (Y/N)'].value_counts()
        call_status.index = call_status.index.map({'Y': 'Atendido', 'N': 'Não Atendido'})
        fig_calls = px.pie(call_status, values=call_status.values, names=call_status.index, hole=0.4,
                        color_discrete_sequence=['#003366', '#6699CC'])
        fig_calls.update_layout(height=350, width=600)
        st.plotly_chart(fig_calls)

        # Gráfico de "Número de Chamadas por Mês" (aumentar tamanho)
        st.markdown("<h3 class='small-font'>Número de Chamadas por Mês</h3>", unsafe_allow_html=True)
        filtered_data['Month'] = pd.to_datetime(filtered_data['Date'], errors='coerce').dt.month
        calls_by_month = filtered_data.groupby(['Month', 'Answered (Y/N)']).size().reset_index(name='Número de Chamadas')
        calls_by_month['Answered (Y/N)'] = calls_by_month['Answered (Y/N)'].replace({'Y': 'Atendido', 'N': 'Não Atendido'})
        month_names = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril'}
        calls_by_month['Month'] = calls_by_month['Month'].map(month_names)
        fig_month = px.bar(calls_by_month, x='Month', y='Número de Chamadas', color='Answered (Y/N)',
                        labels={'Month': 'Mês', 'Número de Chamadas': 'Número de Chamadas'},
                        color_discrete_sequence=['#003366', '#6699CC'], barmode='stack')
        fig_month.update_layout(height=350, width=600)
        st.plotly_chart(fig_month)

    # Coluna à direita central (Chamadas Resolvidas e Estatísticas dos Agentes)
    with col_rightmid:
        # Gráficos de Chamadas Resolvidas (aumentar tamanho)
        st.markdown("<h3 class='small-font'>Chamadas Resolvidas</h3>", unsafe_allow_html=True)
        resolved_status = filtered_data[filtered_data['Answered (Y/N)'] == 'Y']['Resolved'].value_counts()
        resolved_status.index = resolved_status.index.map({'Y': 'Resolvido', 'N': 'Não Resolvido'})
        fig_resolved = px.pie(resolved_status, values=resolved_status.values, names=resolved_status.index, hole=0.4,
                            color_discrete_sequence=['#003366', '#6699CC'])
        fig_resolved.update_layout(height=350, width=600)
        st.plotly_chart(fig_resolved)

        # Exibir tabela de desempenho dos agentes
        st.markdown("<h3 class='small-font'>Estatísticas dos Agentes</h3>", unsafe_allow_html=True)
        agent_performance = filtered_data[filtered_data['Answered (Y/N)'] == 'Y'].groupby('Agent').agg(
            AvgTalkDurationInSeconds=('AvgTalkDuration', 'mean'),
            CallsAnswered=('Agent', 'size')
        ).reset_index()

        agent_performance = agent_performance[agent_performance['CallsAnswered'] > 0]
        agent_performance['AvgTalkDurationInSeconds'] = agent_performance['AvgTalkDurationInSeconds'].apply(lambda x: f"{x:.0f} segundos" if x > 0 else "0 segundos")
        agent_performance = agent_performance.rename(columns={
            'Agent': 'Agente',
            'AvgTalkDurationInSeconds': 'Duração Média da Conversa (segundos)',
            'CallsAnswered': 'Chamadas Atendidas'
        })

        # Exibir tabela de desempenho dos agentes
        st.dataframe(agent_performance, height=400)

    # Coluna à direita (Velocidade Média de Resposta)
    with col_right:
        # Cabeçalho centralizado
        st.markdown(
            "<h3 class='small-font' style='text-align: center;'>Velocidade Média de Resposta (s)</h3>",
            unsafe_allow_html=True
        )
        
        # Adicionando o CSS para a caixa quadrada e estilosa
        st.markdown(
            f"""
            <style>
            .metric-card {{
                padding: 20px;
                border-radius: 15px;
                background-color: #00407d;  /* Mantendo o fundo escuro */
                color: white;
                text-align: center;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);  /* Sombra para efeito de profundidade */
                height: 150px;
                width: 150px;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: auto;
            }}
            .big-metric {{
                font-size: 32px;
                font-weight: bold;
            }}
            </style>
            <div class="metric-card">
                <p class="big-metric">{average_speed_of_answer:.2f}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


