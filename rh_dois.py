import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Função principal do dashboard
def main():
    st.markdown("<h1 style='text-align: center;'>Diversidade e Inclusão 2</h1>", unsafe_allow_html=True)

    # Carregar dados
    file_path = r'DIVERSIDADE NA EMPRESA.xlsx'
    df = pd.read_excel(file_path)

    # Dividir em dois containers: top e bottom row
    top_container = st.container()
    bottom_container = st.container()

    # Top row: Filtros interativos
    with top_container:
        st.markdown("### Filtros Interativos")

        col1, col2, col3, col4 = st.columns(4)

        # Filtro interativo de departamento
        department_filter = col1.selectbox(
            'Selecione o Departamento',
            options=['Todos'] + sorted(list(df['Department @01.07.2020'].unique()))
        )

        # Filtro interativo de job level
        job_level_filter = col2.selectbox(
            'Selecione o Nível de Trabalho',
            options=['Todos'] + sorted(list(df['Job Level after FY20 promotions'].unique()))
        )

        # Filtro interativo de grupo etário
        age_group_filter = col3.selectbox(
            'Selecione o Grupo Etário',
            options=['Todos'] + sorted(list(df['Age group'].unique()))
        )

        # Filtro interativo de região
        region_filter = col4.selectbox(
            'Selecione a Região',
            options=['Todos'] + sorted(list(df['Region group: nationality 1'].unique()))
        )

        # Aplicando os filtros ao dataframe
        filtered_data = df.copy()
        if department_filter != 'Todos':
            filtered_data = filtered_data[filtered_data['Department @01.07.2020'] == department_filter]
        if job_level_filter != 'Todos':
            filtered_data = filtered_data[filtered_data['Job Level after FY20 promotions'] == job_level_filter]
        if age_group_filter != 'Todos':
            filtered_data = filtered_data[filtered_data['Age group'] == age_group_filter]
        if region_filter != 'Todos':
            filtered_data = filtered_data[filtered_data['Region group: nationality 1'] == region_filter]

    # Bottom row: Três colunas
    with bottom_container:
        left_col, mid_col, right_col = st.columns(3)

        # Coluna Esquerda: KPI 4 - Avaliação de Performance
        with left_col:
            st.markdown("### KPI 4 - Avaliação de Performance")

            # Gráfico de barras 100% empilhadas por gênero e rating de performance
            performance_counts = filtered_data.groupby(['FY20 Performance Rating', 'Gender']).size().unstack(fill_value=0)
            performance_percent = performance_counts.div(performance_counts.sum(axis=1), axis=0) * 100

            bar_fig = go.Figure()
            for gender in performance_percent.columns:
                bar_fig.add_trace(go.Bar(
                    x=performance_percent.index,
                    y=performance_percent[gender],
                    name=gender
                ))

            bar_fig.update_layout(
                barmode='stack',
                title='Distribuição de Performance por Gênero (100% Empilhadas)',
                xaxis_title='Rating de Performance',
                yaxis_title='Percentual de Trabalhadores',
                legend_title='Performance Rating',
                xaxis=dict(
                    tickvals=[1, 2, 3, 4],
                    ticktext=['1 - Excelente', '2 - Bom', '3 - Suficiente', '4 - Ruim']
                )
            )
            st.plotly_chart(bar_fig)

            # Exibir as médias de avaliação masculina e feminina
            male_avg = filtered_data[filtered_data['Gender'] == 'Male']['FY20 Performance Rating'].mean()
            female_avg = filtered_data[filtered_data['Gender'] == 'Female']['FY20 Performance Rating'].mean()

            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                    <div style="background-color: #00407d; padding: 20px; border-radius: 5px; width: 48%; color: white;">
                        <h3>Nota Média Masculina</h3>
                        <h2>{male_avg:.2f}</h2>
                    </div>
                    <div style="background-color: #FFB6C1; padding: 20px; border-radius: 5px; width: 48%; color: black;">
                        <h3>Nota Média Feminina</h3>
                        <h2>{female_avg:.2f}</h2>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

        # Coluna do Meio: KPI 5 - Balanço de Gênero em Cargos Executivos
        with mid_col:
            st.markdown("### KPI 5 - Balanço de Gênero em Cargos Executivos")

            # Filtrando dados para cargos executivos FY20 e FY21
            exec_data_fy20 = filtered_data[filtered_data['Job Level before FY20 promotions'] == '1 - Executive']

            # Filtrar dados corretos para promoções FY21
            exec_data_fy21 = filtered_data[filtered_data['Job Level after FY20 promotions'] == '1 - Executive']
            hires_fy21 = exec_data_fy21[exec_data_fy21['Promotion in FY20?'] == 'Y']
            #variavel está com nome ruim, entretanto, foi feita abaixo para conseguir pegar o dado da exec_data_fy21
            hires_fy20 = exec_data_fy21[exec_data_fy21['New hire FY20?'] == 'Y']

            # Disposição 2x2 dos gráficos de rosca
            col1, col2 = st.columns(2)

            with col1:
                fig_fy20_exec = px.pie(exec_data_fy20, names='Gender', title='Cargos Executivos FY20')
                st.plotly_chart(fig_fy20_exec)

                fig_fy20_hire = px.pie(hires_fy20, names='Gender', title='Contratações para Executivos FY20')
                st.plotly_chart(fig_fy20_hire)

            with col2:
                fig_fy21_exec = px.pie(exec_data_fy21, names='Gender', title='Cargos Executivos FY21')
                st.plotly_chart(fig_fy21_exec)

                fig_fy21_hire = px.pie(hires_fy21, names='Gender', title='Promoções para Executivos FY20')
                st.plotly_chart(fig_fy21_hire)

        # Coluna Direita: KPI 6 - Grupo Etário
        with right_col:
            st.markdown("### KPI 6 - Grupo Etário")

            # Gráfico de barras clusterizado para idade por quantidade de trabalhadores
            age_fig = px.bar(filtered_data, x='Age group', y='Employee ID', color='Gender', barmode='group',
                             title='Distribuição de Trabalhadores por Grupo Etário')
            st.plotly_chart(age_fig)

            # Gráfico de colunas 100% empilhadas por grupo etário e cargo
            age_job_counts = filtered_data.groupby(['Age group', 'Job Level after FY20 promotions']).size().unstack(fill_value=0)
            age_job_percent = age_job_counts.div(age_job_counts.sum(axis=1), axis=0) * 100

            age_job_fig = go.Figure()
            for job_level in age_job_percent.columns:
                age_job_fig.add_trace(go.Bar(
                    x=age_job_percent.index,
                    y=age_job_percent[job_level],
                    name=job_level
                ))

            age_job_fig.update_layout(
                barmode='stack',
                title='Distribuição de Grupo Etário por Cargo (100% Empilhadas)',
                xaxis_title='Grupo Etário',
                yaxis_title='Percentual'
            )
            st.plotly_chart(age_job_fig)


