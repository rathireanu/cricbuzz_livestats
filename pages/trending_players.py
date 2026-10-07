
import pandas as pd
import requests
import streamlit as st
import mysql.connector

url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/trending"

headers = {
	"x-rapidapi-key": "49bf8fa595mshc29bb7272aa862cp141394jsn8cc537810b17",
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
            "teamName": item.get("teamName")
        }
        players.append(player_info)

st.write(players)

# 1. Connect to MySQL Database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2024",
    database="cricbuzz_db",
)
cursor = conn.cursor()

# 2. AUTOMATIC TABLE CREATION (Safe Step)
create_table_query = """
CREATE TABLE IF NOT EXISTS playerstrend (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    teamName VARCHAR(100)
);
"""
cursor.execute(create_table_query)

# 3. MySQL Upsert Query
if players:
    players_tuples = [
        (p["id"], p["name"], p["teamName"])
        for p in players
    ]

    query = """
    INSERT INTO playerstrend (id, name, teamName)
    VALUES (%s, %s,%s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        teamName = VALUES(teamName);
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