
import pandas as pd
import requests
import streamlit as st
import mysql.connector

url = "https://cricbuzz-cricket.p.rapidapi.com/series/v1/3718/squads/15826"

headers = {
	"x-rapidapi-key": st.secrets["RAPIDAPI_KEY"],
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
data=response.json()
players = []

for item in data.get("player", []):
    if "id" in item:
        player_info = {
            "id": item.get("id"),
            "name": item.get("name"),
            "role": item.get("role"),
            "battingStyle": item.get("battingStyle"),
            "bowlingStyle": item.get("bowlingStyle"),
        }
        players.append(player_info)

st.write(players)

# 1. Connect to MySQL Database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=st.secrets["DB_PASSWORD"],
    database="cricbuzz_db",
)
cursor = conn.cursor()

# 2. AUTOMATIC TABLE CREATION (Safe Step)
create_table_query = """
CREATE TABLE IF NOT EXISTS players1 (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    role VARCHAR(100),
    batting_style VARCHAR(100),
    bowling_style VARCHAR(100)
);
"""
cursor.execute(create_table_query)

# 3. MySQL Upsert Query
if players:
    players_tuples = [
        (p["id"], p["name"], p["role"], p["battingStyle"], p["bowlingStyle"])
        for p in players
    ]

    query = """
    INSERT INTO players1 (id, name, role, batting_style, bowling_style)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        role = VALUES(role),
        batting_style = VALUES(batting_style),
        bowling_style = VALUES(bowling_style);
    """

    try:
        cursor.executemany(query, players_tuples)
        conn.commit()  # ESSENTIAL: Without commit, changes are rolled back!
        st.success(
            f"Successfully inserted/updated {len(players)} players in MySQL database!"
        )
    except mysql.connector.Error as err:
        st.error(f"MySQL Error: {err}")
else:
    st.warning("`players` list is empty! Check API JSON key structure.")