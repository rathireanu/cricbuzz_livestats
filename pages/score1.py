import pandas as pd
import requests
import streamlit as st
import mysql.connector

url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/8733/batting"

headers = {
	"x-rapidapi-key": "49bf8fa595mshc29bb7272aa862cp141394jsn8cc537810b17",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

data=response.json()
stats = []

headers = data.get("headers", [])[1:]  # Extracts format names: ["Test", "ODI", "T20", "IPL"]
rows = data.get("values", [])

if headers and rows:
    # Build a lookup mapping for metrics: {"Matches": [70, 99, 72, 159], ...}
    metrics = {}
    for row_obj in rows:
        val_list = row_obj.get("values", [])
        if val_list:
            metric_name = val_list[0]  # "Matches", "Innings", "Runs"
            # Safely cast each numeric value to INT
            metric_values = [int(v) if str(v).isdigit() else 0 for v in val_list[1:]]
            metrics[metric_name] = metric_values

    # Transpose matrix columns into format-based objects
    for idx, format_name in enumerate(headers):
        try:
            stat_info = {
                "player_id": player_id,
                "format_name": str(format_name),
                "matches": metrics.get("Matches", [])[idx] if idx < len(metrics.get("Matches", [])) else 0,
                "innings": metrics.get("Innings", [])[idx] if idx < len(metrics.get("Innings", [])) else 0,
                "runs": metrics.get("Runs", [])[idx] if idx < len(metrics.get("Runs", [])) else 0,
            }
            stats.append(stat_info)
        except (IndexError, ValueError):
            continue

st.write("Parsed API Stats:", stats)

# 3. Database Insertion Logic
if stats:
    conn = None
    cursor = None
    try:
        # Connect to MySQL Database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="2024",
            database="cricbuzz_db",
            autocommit=True,
        )
        cursor = conn.cursor()

        # Create Table if it doesn't exist (Composite PRIMARY KEY on player_id + format_name)
        create_table_query = """
        CREATE TABLE IF NOT EXISTS player_career_stats (
            player_id INT,
            format_name VARCHAR(20),
            matches INT DEFAULT 0,
            innings INT DEFAULT 0,
            runs INT DEFAULT 0,
            PRIMARY KEY (player_id, format_name)
        );
        """
        cursor.execute(create_table_query)

        # Prepare List of Tuples for Batch Insertion
        stat_tuples = [
            (
                s["player_id"],
                s["format_name"],
                s["matches"],
                s["innings"],
                s["runs"],
            )
            for s in stats
        ]

        # Bulk Upsert Query
        upsert_query = """
        INSERT INTO player_career_stats (player_id, format_name, matches, innings, runs)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            matches = VALUES(matches),
            innings = VALUES(innings),
            runs = VALUES(runs);
        """

        cursor.executemany(upsert_query, stat_tuples)

        st.success(
            f"Successfully created table `player_career_stats` and updated {len(stats)} format records for Player ID {player_id}!"
        )

    except mysql.connector.Error as err:
        st.error(f"MySQL Database Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
else:
    st.warning("No career stats parsed! Check the REST API JSON matrix structure.")