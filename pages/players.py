import sqlite3
import os
import pandas as pd
import requests
import streamlit as st
import mysql.connector

import requests

url = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/2/players"

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
            "battingStyle": item.get("battingStyle"),
            "bowlingStyle": item.get("bowlingStyle")
        }
        players.append(player_info)

st.divider()
# --- YOUR CODE CONTINUATION BELOW ---


# 1. Connect to MySQL Database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=st.secrets["DB_PASSWORD"],
    database="cricbuzz_db",
)
cursor = conn.cursor()

# 2. MySQL Upsert Query


if players:
    players_tuples = [
        (p["id"], p["name"], p["battingStyle"], p["bowlingStyle"])
        for p in players
    ]

    query = """
    INSERT INTO players (id, name, batting_style, bowling_style)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        batting_style = VALUES(batting_style),
        bowling_style = VALUES(bowling_style);
    """

    cursor.executemany(query, players_tuples)
    conn.commit()
    st.success(
        f"Successfully inserted/updated {len(players)} players in MySQL database!"
    )
else:
    st.warning("No players found in API response. Database was not updated.")


# display a search bar
st.header("welcome to the players details")
st.page_link("app.py", label="Home")

st.divider()
player_options = {
    f"{p.get('name', 'Unknown')} (ID: {p.get('id', '')})": idx
    for idx, p in enumerate(players)
}

selected_player_label = st.selectbox(
    "Select a Player:",
    options=list(player_options.keys()),
    index=None,
    placeholder="Select player...",
)

if selected_player_label:
    selected_player = players[player_options[selected_player_label]]
    #st.write("Selected Player Data:", selected_player)
    st.write(f"player id:{selected_player.get('id')}")
    st.write(f"player name:{selected_player.get('name')}")
    st.write(f"player batting style:{selected_player.get('battingStyle')}")
    st.write(f"player bowling style:{selected_player.get('bowlingStyle')}")