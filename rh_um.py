import streamlit as st
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go

def main():
    st.markdown("<h1 style='text-align: center;'>Diversidade e Inclusão 1</h1>", unsafe_allow_html=True)

    # Carregando os dados
    file_path = r"C:\Users\makim\OneDrive\Área de Trabalho\PASTA\DIVERSIDADE NA EMPRESA.xlsx"
    data = pd.read_excel(file_path)
    data['New hire FY20?'] = data['New hire FY20?'].replace({'Y': 1, 'N': 0})

    # Criando o container superior (top row) com filtros interativos
    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        # Filtro de Departamento
        department_filter = col1.selectbox(
            'Selecione o Departamento:',
            options=['Todos'] + sorted(data['Department @01.07.2020'].unique())
        )

        # Filtro de Nível de Trabalho
        job_level_filter = col2.selectbox(
            'Selecione o Nível de Trabalho:',
            options=['Todos'] + sorted(data['Job Level after FY20 promotions'].unique())
        )

        # Filtro de Grupo de Idade
        age_group_filter = col3.selectbox(
            'Selecione o Grupo de Idade:',
            options=['Todos'] + sorted(data['Age group'].unique())
        )

        # Filtro de Grupo de Região
        region_group_filter = col4.selectbox(
            'Selecione o Grupo de Região:',
            options=['Todos'] + sorted(data['Region group: nationality 1'].unique())
        )

    # Aplicando filtros ao DataFrame
    filtered_data = data.copy()
    if department_filter != 'Todos':
        filtered_data = filtered_data[filtered_data['Department @01.07.2020'] == department_filter]
    if job_level_filter != 'Todos':
        filtered_data = filtered_data[filtered_data['Job Level after FY20 promotions'] == job_level_filter]
    if age_group_filter != 'Todos':
        filtered_data = filtered_data[filtered_data['Age group'] == age_group_filter]
    if region_group_filter != 'Todos':
        filtered_data = filtered_data[filtered_data['Region group: nationality 1'] == region_group_filter]

    # Criando o container inferior (bottom row)
    with st.container():
        # Dividindo o container inferior em três colunas
        bottom_left_col, bottom_mid_col, bottom_right_col = st.columns(3)

        # Conteúdo para a coluna da esquerda
        with bottom_left_col:
            st.markdown("### KPI 1 - Contratação")

            # Gráfico de Barras 100% Empilhadas mostrando Cargo por Gênero
            stacked_bar_fig = go.Figure()

            gender_counts = filtered_data.groupby(['Job Level after FY20 promotions', 'Gender']).size().unstack(fill_value=0)
            gender_percent = gender_counts.div(gender_counts.sum(axis=1), axis=0) * 100

            for gender in gender_percent.columns:
                stacked_bar_fig.add_trace(go.Bar(
                    y=gender_percent.index,
                    x=gender_percent[gender],
                    name=gender,
                    orientation='h'
                ))

            stacked_bar_fig.update_layout(
                barmode='stack',
                title='Distribuição de Gênero por Cargo (100% Empilhadas)',
                xaxis_title='Percentual',
                yaxis_title='Cargo',
                height=400
            )

            st.plotly_chart(stacked_bar_fig, use_container_width=True)
                        # Adicionando caixas estilizadas para mostrar as porcentagens de homens e mulheres
            total_male = filtered_data[filtered_data['Gender'] == 'Male'].shape[0]
            total_female = filtered_data[filtered_data['Gender'] == 'Female'].shape[0]
            total = total_male + total_female

            male_percentage = (total_male / total * 100) if total > 0 else 0
            female_percentage = (total_female / total * 100) if total > 0 else 0

            # Estilizando as caixas
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                    <div style="background-color: #00407d; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 48%;">
                        <h3 style="text-align: center;color: #FFFFFF; ">Porcentagem de Homens:</h3>
                        <h2 style="text-align: center; color: #FFFFFF;">{male_percentage:.2f}%</h2>
                    </div>
                    <div style="background-color: #FFB6C1; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 48%;">
                        <h3 style="text-align: center; color: #5e2129;">Porcentagem de Mulheres:</h3>
                        <h2 style="text-align: center; color: #5e2129;">{female_percentage:.2f}%</h2>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

            # Gráfico de Linha e Colunas com % de gênero por cargo
            line_column_fig = go.Figure()

            # Calculando a porcentagem de contratação feminina para cada cargo
            female_hire_percentage = filtered_data[filtered_data['Gender'] == 'Female'].groupby(
                'Job Level after FY20 promotions')['New hire FY20?'].mean() * 100

            gender_percent_by_job = filtered_data.groupby(['Job Level after FY20 promotions', 'Gender']).size().unstack(fill_value=0).div(
                filtered_data.groupby('Job Level after FY20 promotions').size(), axis=0
            ) * 100

            # Adicionando a linha ao gráfico para a % de contratação feminina
            line_column_fig.add_trace(go.Scatter(
                x=female_hire_percentage.index,
                y=female_hire_percentage.values,
                mode='lines+markers',
                name='Contratação Feminina (%)',
                line=dict(color='purple', width=2)
            ))

            # Adicionando as colunas para % de cada gênero por cargo
            for gender in gender_percent_by_job.columns:
                line_column_fig.add_trace(go.Bar(
                    x=gender_percent_by_job.index,
                    y=gender_percent_by_job[gender],
                    name=f'{gender} (%)',
                    marker=dict(opacity=0.6)
                ))

            line_column_fig.update_layout(
                title='Distribuição de Gênero por Cargo e Linha de Contratação Feminina',
                xaxis_title='Cargo',
                yaxis_title='Percentual (%)',
                barmode='group',
                height=400
            )

            st.plotly_chart(line_column_fig, use_container_width=True)

        # Conteúdo para a coluna do meio (KPI 2)
        with bottom_mid_col:
            st.markdown("### KPI 2 - Promoções (deste ano)")

            # Gráfico 1: Colunas Agrupadas - Quantidade de Promoções por Gênero no Ano por Cargo
            promotion_data = filtered_data[filtered_data['Promotion in FY21?'] == 'Yes']  # Filtrando apenas promovidos
            gender_promotion_counts = promotion_data.groupby(['Job Level after FY21 promotions', 'Gender']).size().unstack(fill_value=0)

            grouped_bar_fig = go.Figure()

            for gender in gender_promotion_counts.columns:
                grouped_bar_fig.add_trace(go.Bar(
                    x=gender_promotion_counts.index,
                    y=gender_promotion_counts[gender],
                    name=gender
                ))

            grouped_bar_fig.update_layout(
                title='Quantidade de Promoções por Gênero no Ano por Cargo',
                xaxis_title='Cargo',
                yaxis_title='Quantidade de Promoções',
                barmode='group',
                height=400
            )

            st.plotly_chart(grouped_bar_fig, use_container_width=True)

            # Gráfico 2: Barras Agrupadas - Tempo Médio dos Funcionários Promovidos (com mais de 21 anos)
            age_21_plus_data = promotion_data[promotion_data['Age @01.07.2020'] > 21]  # Filtrando funcionários com mais de 21 anos
            avg_time_in_job = age_21_plus_data.groupby(['Job Level after FY21 promotions', 'Gender'])['Years since last hire'].mean().unstack(fill_value=0)

            time_bar_fig = go.Figure()

            for gender in avg_time_in_job.columns:
                time_bar_fig.add_trace(go.Bar(
                    x=avg_time_in_job.index,
                    y=avg_time_in_job[gender],
                    name=gender
                ))

            time_bar_fig.update_layout(
                title='Tempo Médio dos Funcionários Promovidos (Acima de 21 Anos)',
                xaxis_title='Cargo',
                yaxis_title='Tempo Médio (Anos)',
                barmode='group',
                height=400
            )

            st.plotly_chart(time_bar_fig, use_container_width=True)
        # Conteúdo para a coluna da direita
        with bottom_right_col:
            st.markdown("### KPI 3 - Taxa de Rotatividade (Acima dos 20)")

            # Filtrando os dados gerais aplicando os filtros interativos que já foram definidos
            filtered_data = data.copy()

            if department_filter != 'Todos':
                filtered_data = filtered_data[filtered_data['Department @01.07.2020'] == department_filter]
            if job_level_filter != 'Todos':
                filtered_data = filtered_data[filtered_data['Job Level after FY20 promotions'] == job_level_filter]
            if age_group_filter != 'Todos':
                filtered_data = filtered_data[filtered_data['Age group'] == age_group_filter]
            if region_group_filter != 'Todos':
                filtered_data = filtered_data[filtered_data['Region group: nationality 1'] == region_group_filter]

            # Gráfico 1: Homens
            st.markdown("#### Homens")
            
            # Filtrando os dados para homens com mais de 20 anos, com filtros aplicados
            male_data = filtered_data[(filtered_data['Gender'] == 'Male') & (filtered_data['Age @01.07.2020'] > 20)]

            # Separando os funcionários que saíram e que não saíram
            leavers_data_male = male_data[male_data['FY20 leaver?'] == 'Yes']
            stayers_data_male = male_data[male_data['FY20 leaver?'] == 'No']

            # Calculando a média de "Performance Rating" por cargo para os que saíram
            leavers_performance_male = leavers_data_male.groupby('Job Level after FY20 promotions')['FY20 Performance Rating'].mean()

            # Calculando a média de "Performance Rating" por cargo para os que não saíram
            stayers_performance_male = stayers_data_male.groupby('Job Level after FY20 promotions')['FY20 Performance Rating'].mean()

            # Criando o gráfico de linhas para homens
            line_fig_male = go.Figure()

            # Linha para funcionários que saíram
            line_fig_male.add_trace(go.Scatter(
                x=leavers_performance_male.index,
                y=leavers_performance_male.values,
                mode='lines+markers',
                name='Saíram',
                line=dict(color='red', width=2)
            ))

            # Linha para funcionários que não saíram
            line_fig_male.add_trace(go.Scatter(
                x=stayers_performance_male.index,
                y=stayers_performance_male.values,
                mode='lines+markers',
                name='Não Saíram',
                line=dict(color='green', width=2)
            ))

            # Configurando o layout do gráfico
            line_fig_male.update_layout(
                title='Média de Performance Rating por Cargo (Saíram vs. Não Saíram) - Homens',
                xaxis_title='Cargo',
                yaxis_title='Média de Performance Rating',
                height=400
            )

            # Exibindo o gráfico de linhas no Streamlit para homens
            st.plotly_chart(line_fig_male, use_container_width=True)

            # Gráfico 2: Mulheres
            st.markdown("#### Mulheres")
            
            # Filtrando os dados para mulheres com mais de 20 anos, com filtros aplicados
            female_data = filtered_data[(filtered_data['Gender'] == 'Female') & (filtered_data['Age @01.07.2020'] > 20)]

            # Separando as funcionárias que saíram e que não saíram
            leavers_data_female = female_data[female_data['FY20 leaver?'] == 'Yes']
            stayers_data_female = female_data[female_data['FY20 leaver?'] == 'No']

            # Calculando a média de "Performance Rating" por cargo para as que saíram
            leavers_performance_female = leavers_data_female.groupby('Job Level after FY20 promotions')['FY20 Performance Rating'].mean()

            # Calculando a média de "Performance Rating" por cargo para as que não saíram
            stayers_performance_female = stayers_data_female.groupby('Job Level after FY20 promotions')['FY20 Performance Rating'].mean()

            # Criando o gráfico de linhas para mulheres
            line_fig_female = go.Figure()

            # Linha para funcionárias que saíram
            line_fig_female.add_trace(go.Scatter(
                x=leavers_performance_female.index,
                y=leavers_performance_female.values,
                mode='lines+markers',
                name='Saíram',
                line=dict(color='red', width=2)
            ))

            # Linha para funcionárias que não saíram
            line_fig_female.add_trace(go.Scatter(
                x=stayers_performance_female.index,
                y=stayers_performance_female.values,
                mode='lines+markers',
                name='Não Saíram',
                line=dict(color='green', width=2)
            ))

            # Configurando o layout do gráfico
            line_fig_female.update_layout(
                title='Média de Performance Rating por Cargo (Saíram vs. Não Saíram) - Mulheres',
                xaxis_title='Cargo',
                yaxis_title='Média de Performance Rating',
                height=400
            )

            # Exibindo o gráfico de linhas no Streamlit para mulheres
            st.plotly_chart(line_fig_female, use_container_width=True)

