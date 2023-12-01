
import pandas as pd
import math
import os  # Importe a biblioteca os para manipulação de caminhos

# Obtenha o diretório atual do script
script_dir = os.path.dirname(__file__)

# Atualize os caminhos dos arquivos CSV
steam_games_users = pd.read_csv("dataset/users.csv")
steam_games = pd.read_csv("dataset/games.csv")
steam_games_recomendation = pd.read_csv("dataset/recommendations.csv")


# In[2]:


def DefineEuclideanDistance(reviews1, reviews2):
    distance = 0
    commomNumberOfReviews = 0
    commomReview = False
    reviews1_list = reviews1["app_id"].tolist()
    reviews2_list = reviews2["app_id"].tolist()
    
    for games in reviews1_list:
        if games in reviews2_list:
            distance += pow(abs(reviews1[reviews1["app_id"] == games]["is_recommended"].iloc[0] -  reviews2[reviews2["app_id"] == games]["is_recommended"].iloc[0]),2)
            commomNumberOfReviews += 1
            commomReview = True
    
    root_distance = math.sqrt(distance)
    
    if commomReview:
        return [root_distance, commomNumberOfReviews]
    else:
        return [-1, commomNumberOfReviews]


# In[3]:


def computeNearestNeighbor(reviews, username, users):
    distance_list = []
    users_list = users["user_id"].tolist()
    
    for user in users_list:
        if user != username["user_id"].iloc[0]:
            distance = DefineEuclideanDistance(reviews[reviews["user_id"] == user], username)
            if(distance[0] >= 0):
                distance_list.append((distance[0], distance[1], users[users["user_id"] == user].iloc[0].iloc[0]))

    distance_list.sort()
    return distance_list


# In[4]:


def recomendation(games_book, reviews, username, users):
    nearest = computeNearestNeighbor(reviews, username, users)
    if not nearest:
        return nearest
    
    
    for i in range(len(nearest)):
        recommendations = []
        nearest_user = nearest[i][2]
        
        positive_filtered_reviews = reviews[reviews["is_recommended"] != 0]
        neighborRatings = positive_filtered_reviews[positive_filtered_reviews["user_id"] == nearest_user]
        
        neighbor_recommend_ratings = neighborRatings["app_id"].tolist()
        username_recommend_list = username["app_id"].tolist()

        for game_id in neighbor_recommend_ratings:
            if game_id not in username_recommend_list:
                title_game = games_book[games_book["app_id"] == game_id].iloc[0].iloc[1]
                steam_rating = games_book[games_book["app_id"] == game_id].iloc[0].iloc[7]
                recommendations.append((steam_rating, title_game))
        
        # Verifica se a lista de recomendações não é nula
        if recommendations:
            break

    recommendations.sort(reverse=True)
    return recommendations


# In[5]:


steam_games_users.head(10)


# In[6]:


steam_games_users.info()


# In[7]:


steam_games.head(10)


# In[8]:


steam_games_recomendation.info(10)


# In[9]:


steam_games_recomendation.head(10)


# In[10]:


sgr_clean = steam_games_recomendation.drop(columns=["helpful", "funny", "date", "hours", "review_id"])
new_sgr_clear = sgr_clean.replace({True: 1, False: 0})
new_sgr_clear.head(10)


# In[11]:


positive_filtred_reviews = new_sgr_clear[new_sgr_clear["is_recommended"] != 0]
positive_filtred_reviews.head(10)


# In[12]:


dados1 = {'app_id': 578080, 'is_recommended': 1, 'user_id': 1}
dados2 = {'app_id': 289070, 'is_recommended': 0, 'user_id': 1}
df_usuario_test = pd.DataFrame([dados1, dados2])
df_usuario_test.head()


# In[13]:


steam_games_users_lite = steam_games_users.sample(n=100)
steam_games_users_lite.head()


# In[14]:


l = recomendation(steam_games ,new_sgr_clear, df_usuario_test, steam_games_users_lite)


# In[15]:


print(l)

# In[16] Games Query for Title:


# LOOP
lista_dics = []

nome_do_jogo_inputado = "Rust"
linha_do_jogo = steam_games.loc[steam_games["title"] == nome_do_jogo_inputado].values[0]


for input_nome_jogo_servidor in range(5):
    nome_do_jogo_inputado = "Rust"
    linha_do_jogo = steam_games.loc[steam_games["title"] == nome_do_jogo_inputado].values[0]
    app_id_game = linha_do_jogo[0]

    dados = {'app_id': app_id_game, 'is_recommended': 1, 'user_id': 1}
    lista_dics.append(dados)

# quando loop terminar, cria o dataframe

df_usuario_input = pd.DataFrame([lista_dics[0], lista_dics[1], lista_dics[2], lista_dics[3], lista_dics[4]])

Lista_recomendações = recomendation(steam_games, new_sgr_clear, df_usuario_input, steam_games_users_lite)

#print(Lista_recomendações[0][0])
#print(Lista_recomendações[0][1])
