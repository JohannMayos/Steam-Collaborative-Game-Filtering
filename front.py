import streamlit as st
import requests
import pandas as pd
from dataset import recomendation, steam_games, new_sgr_clear, steam_games_users_lite
import random
import numpy as np

# Configuração da sessão para armazenar variáveis
if 'avaliacoes_anteriores' not in st.session_state:
    st.session_state.avaliacoes_anteriores = []
    st.session_state.numero_avaliacoes = 0
    st.session_state.inputs_nome_jogo = {}
    st.session_state.rec_list = []

# Título da aplicação
st.title("Avaliação de Títulos de Jogos da Steam")

# Introdução e instruções
st.write("Bem-vindo à nossa aplicação para recomendação de títulos de jogos da Steam! Insira 5 jogos que chamaram sua atenção e nos diga se os recomenda ou não")

# Verificando se o número de avaliações já atingiu o limite
if st.session_state.numero_avaliacoes < 5:
    # Entrada do usuário para o nome do jogo
    nome_do_jogo = st.text_input("Nome do Jogo:" , key="name")

    # Entrada do usuário para a avaliação do jogo
    avaliacao = st.radio("Você Recomendaria Esse Jogo Para Outras Pessoas?", ["Sim", "Não"], key="av")

    game_name = st.session_state.inputs_nome_jogo
    rec =  st.session_state.rec_list 

   
    # Botão para submeter a avaliação
    if st.button("Adicionar à Lista de Avaliações", key="add"):
        # Fazendo a requisição à API usando o nome do jogo inserido
        url_jogo = f"https://www.cheapshark.com/api/1.0/games?title={nome_do_jogo}&limit=1"
        url_cotacao = f"https://api.exchangerate-api.com/v4/latest/USD"  # Nova API de cotação

        response_jogo = requests.get(url_jogo)
        response_cotacao = requests.get(url_cotacao)

        if response_jogo.status_code == 200 and response_cotacao.status_code == 200:
            # Verificando se a resposta é uma lista
            jogo_data = response_jogo.json()
            cotacao_data = response_cotacao.json()

            if isinstance(jogo_data, list) and len(jogo_data) > 0:
                # Exibindo os dados do primeiro jogo da lista
                st.write("Informações do Jogo:")
                st.write(f"Nome: {jogo_data[0]['external']}")

                # Obtendo o preço e a cotação
                preco_jogo = float(jogo_data[0].get('cheapest', 0))  # Use .get() para evitar KeyError

                # A cotação agora está em cotacao_data['rates']['BRL']
                cotacao_dolar = cotacao_data['rates'].get('BRL', 0)  # Use .get() para evitar KeyError

                # Exibindo o preço em dólar
                st.write(f"Preço em Dólar: {preco_jogo}")

                if cotacao_dolar == 0:
                    st.warning("A cotação do dólar para real é zero. Verifique a resposta da API de cotação.")
                else:
                    # Realizando a multiplicação
                    preco_real = preco_jogo * cotacao_dolar

                    # Exibindo o preço em Real
                    st.write(f"Preço em Real: {preco_real:.2f}")  # Formate o número para duas casas decimais

                    # Armazenando as informações em um dicionário
                    avaliacao_info = {
                        'nome_do_jogo': jogo_data[0]['external'],
                        'avaliacao': 1 if avaliacao == 'Sim' else 0,
                        'preco_jogo': preco_jogo,
                        'preco_real': preco_real,
                    }

                    
                    # Adicionando o dicionário à lista de avaliações anteriores
                    st.session_state.avaliacoes_anteriores.append(avaliacao_info)
                    st.session_state.numero_avaliacoes += 1

                    # Armazenando o nome do jogo no dicionário de inputs
                    st.session_state.inputs_nome_jogo[nome_do_jogo] = avaliacao

                    game_line = steam_games.loc[steam_games["title"] == avaliacao_info['nome_do_jogo']].values

                    if np.any(game_line):

                        app_id = game_line[0][0]

                        game_name = {
                            'app_id': app_id,
                            'is_recommended': 1 if avaliacao == 'Sim' else 0,
                            'user_id': random.randint(0,500)
                        }

                        rec.append(game_name)

                # Exibindo a imagem da chave "thumb" se existir
                if 'thumb' in jogo_data[0]:
                    st.image(jogo_data[0]['thumb'], caption="Thumbnail do Jogo", width=150)
                else:
                    st.write("A resposta da API não contém uma URL de imagem.")
            else:
                st.write("A resposta da API não contém dados do jogo.")
        else:
            st.write(f"Erro ao obter informações. Status Code - Jogo: {response_jogo.status_code}, Cotação: {response_cotacao.status_code}")

# Desabilitando os campos após 5 avaliações
if st.session_state.numero_avaliacoes >= 5:
    st.write("Você atingiu o limite de 5 avaliações.")
    st.text_input("Nome do Jogo:", value="", disabled=True)
    st.radio("Você Recomendaria Esse Jogo Para Outras Pessoas?", ["Sim", "Não"], index=0, disabled=True)
    st.button("Adicionar à Lista de Avaliações", disabled=True)

# Exibindo a lista de avaliações anteriores
st.header("Detalhes dos Jogos")
for avaliacao in st.session_state.avaliacoes_anteriores:
    st.write(f"Nome do Jogo: {avaliacao['nome_do_jogo']}")
    st.write(f"Avaliação: {avaliacao['avaliacao']}")
    st.write(f"Preço em Dólar: {avaliacao['preco_jogo']}")
    st.write(f"Preço em Real: {avaliacao['preco_real']:.2f}")
    st.write("---")

# Exibindo a lista de inputs de nome do jogo
st.header("Overview das Avaliações")
for nome_jogo, avaliacao in st.session_state.inputs_nome_jogo.items():
    st.write(f"Nome do Jogo: {nome_jogo}")
    st.write(f"Avaliação: {avaliacao}")
    st.write("---")

if st.button("Obter Recomendações"):

    lista_dics = rec
    
    result = pd.DataFrame(lista_dics)

    lista_rec = recomendation(steam_games, new_sgr_clear, result, steam_games_users_lite)

    if lista_rec:
        st.header("Recomendações:")
        for jogo in lista_rec:
            st.write(f"Nome do Jogo: {jogo[1]}")
            st.write(f"Steam Rating: {jogo[0]}")
            st.write("---")
    else:
        st.write("Nenhum Jogo Recomendado.")



