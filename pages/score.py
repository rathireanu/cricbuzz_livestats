
import pandas as pd
import requests
import streamlit as st
import mysql.connector

url = "https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/40381/scard"

headers = {
	"x-rapidapi-key": st.secrets["RAPIDAPI_KEY"],
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
data=response.json()
scores = []
with st.container(border=True):
    st.page_link("app.py", label="Home", icon="🏠")
for innings in data.get("scorecard", []):
    # Cricbuzz nested structure: scorecard -> batsman / bowler list
    batsmen_list = innings.get("batsman", [])
    for item in batsmen_list:
        if isinstance(item, dict) and "id" in item:
            score_info = {
                "id": item.get("id"),
                "balls": str(item.get("balls", 0)),
                "runs": str(item.get("runs", 0)),
                "fours": str(item.get("fours", 0)),
                "sixes": str(item.get("sixes", 0)),
                "strkrate": str(item.get("strkrate", "0.0")),
                "name": item.get("name", "Unknown"),
            }
            scores.append(score_info)



if scores:
    try:
        # 1. Connect to MySQL Database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=st.secrets["DB_PASSWORD"],
            database="cricbuzz_db",
            autocommit=True,
        )
        cursor = conn.cursor()

        # 2. CREATE TABLE IF NOT EXISTS
        create_table_query = """
        CREATE TABLE IF NOT EXISTS score (
            id INT PRIMARY KEY,
            balls VARCHAR(255),
            runs VARCHAR(100),
            fours VARCHAR(100),
            sixes VARCHAR(255),
            strkrate VARCHAR(100),
            name VARCHAR(100)
        );
        """
        cursor.execute(create_table_query)

        # 3. Prepare Tuples
        score_tuples = [
            (
                s["id"],
                s["balls"],
                s["runs"],
                s["fours"],
                s["sixes"],
                s["strkrate"],
                s["name"],
            )
            for s in scores
        ]

        # 4. Fixed Upsert Query
        upsert_query = """
        INSERT INTO score (id, balls, runs, fours, sixes, strkrate, name)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            balls = VALUES(balls),
            runs = VALUES(runs),
            fours = VALUES(fours),
            sixes = VALUES(sixes),
            strkrate = VALUES(strkrate),
            name = VALUES(name)
        """

        cursor.executemany(upsert_query, score_tuples)

        st.header("Players Strkrate")
        query ="SELECT * FROM score ORDER BY strkrate DESC;"
        df=pd.read_sql(query,conn)
        df.columns = df.columns.str.strip().str.lower()
        event = st.dataframe(
            df,
            column_order=["name", "strkrate"],
            on_select="rerun",
            selection_mode="single-row",
            use_container_width=False
        )
        selected_rows=event.selection.rows
        if selected_rows:
            selected_index = selected_rows[0]
            person_details = df.iloc[selected_index]
        
            st.divider()
            st.subheader(f"Details for {person_details.get('name', 'N/A')}")
            st.write(f"balls: {person_details.get('balls', 'N/A')}")
            st.write(f"runs: {person_details.get('runs', 'N/A')}")
            st.write(f"fours: {person_details.get('fours', 'N/A')}")
            st.write(f"sixes: {person_details.get('sixes', 'N/A')}")
            st.write(f"strkrate: {person_details.get('strkrate', 'N/A')}")
        else:
            st.info("💡 Click on a row in the table to view full details.")


    except mysql.connector.Error as err:
        st.error(f"MySQL Error: {err}")
    finally:
        if "cursor" in locals() and cursor:
            cursor.close()
        if "conn" in locals() and conn.is_connected():
            conn.close()
else:
    st.warning("`scores` list is empty! Check API JSON key structure.")