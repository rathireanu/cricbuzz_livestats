
import pandas as pd
import requests
import streamlit as st
import mysql.connector

url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/rankings/batsmen"

querystring = {"formatType":"test"}

headers = {
	"x-rapidapi-key": st.secrets["RAPIDAPI_KEY"],
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
data = response.json()

players = []

# Parse API response
for item in data.get("rank", []):
    if isinstance(item, dict) and "id" in item:
        player_info = {
            "id": item.get("id"),
            "rank": item.get("rank"),
            "name": item.get("name"),
            "country": item.get("country"),
            "rating": item.get("rating"),
            "points": item.get("points"),
        }
        players.append(player_info)

#st.write("Parsed Players:", players)
with st.container(border=True):
    st.page_link("app.py", label="Home", icon="🏠")
# =========================================================
# STEP 1: CONNECT & CREATE TABLE FIRST (ALWAYS EXECUTED)
# =========================================================
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=st.secrets["DB_PASSWORD"],
        database="cricbuzz_db",
        autocommit=True,  # Guarantees instant creation
    )
    cursor = conn.cursor()

    # Note: Backticks `` around `rank` prevent MySQL 1064 syntax error
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ranking (
        id INT PRIMARY KEY,
        `rank` VARCHAR(255),
        name VARCHAR(100),
        country VARCHAR(100),
        rating VARCHAR(100),
        points VARCHAR(100)
    );
    """
    cursor.execute(create_table_query)
   
except mysql.connector.Error as err:
    st.error(f"MySQL Initialization Error: {err}")
    st.stop()  # Stop execution if database connection fails

# ==========================================
# 2. FETCH & PARSE API RESPONSE
# ==========================================
response = requests.get(url, headers=headers, params=querystring)
data = response.json()

players = []

# RapidAPI Cricbuzz rankings structure parsing
rank_list = data.get("rank", [])
if not rank_list and isinstance(data, dict):
    # Fallback if rankings are wrapped under 'player' or 'rankings'
    rank_list = data.get("rankings", []) or data.get("player", [])

for item in rank_list:
    if isinstance(item, dict) and "id" in item:
        player_info = {
            "id": item.get("id"),
            "rank": item.get("rank"),
            "name": item.get("name"),
            "country": item.get("country"),
            "rating": item.get("rating"),
            "points": item.get("points"),
        }
        players.append(player_info)

if players:
    players_tuples = [
        (p["id"], p["rank"], p["name"], p["country"], p["rating"], p["points"])
        for p in players
    ]

    upsert_query = """
    INSERT INTO ranking (id, `rank`, name, country, rating, points)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        `rank` = VALUES(`rank`),
        name = VALUES(name),
        country = VALUES(country),
        rating = VALUES(rating),
        points = VALUES(points)
    """

    try:
        cursor.executemany(upsert_query, players_tuples)
        
        # to display a ranking
        st.header("Players Rank")
        query ="SELECT * FROM ranking ORDER BY `rank`ASC;"
        df=pd.read_sql(query,conn)
        st.dataframe(df)
    except mysql.connector.Error as err:
        st.error(f"MySQL Error during insert: {err}")
    finally:
        cursor.close()
        conn.close()
else:
    st.warning("`players` list is empty! Check API parameters or key limits.")
    cursor.close()
    conn.close()

