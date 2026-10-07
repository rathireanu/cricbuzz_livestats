
import pandas as pd
import requests
import streamlit as st
import mysql.connector

url = "https://cricbuzz-cricket.p.rapidapi.com/series/v1/3718/venues"

headers = {
	"x-rapidapi-key": "49bf8fa595mshc29bb7272aa862cp141394jsn8cc537810b17",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
data=response.json()
venues = []

# Parse venues from API response
for item in data.get("seriesVenue", []):
    if "id" in item:
        venue_info = {
            "id": item.get("id"),
            "ground": item.get("ground"),
            "city": item.get("city"),
            "country": item.get("country"),
        }
        venues.append(venue_info)

#st.write(venues)
st.page_link("app.py", label="Home")
if venues:
    try:
        # 1. Connect to MySQL Database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="2024",
            database="cricbuzz_db",
            autocommit=True
        )
        cursor = conn.cursor()

        # 2. CREATE TABLE IF NOT EXISTS
        create_table_query = """
        CREATE TABLE IF NOT EXISTS venues (
            id INT PRIMARY KEY,
            ground VARCHAR(255),
            city VARCHAR(100),
            country VARCHAR(100)
        );
        """
        cursor.execute(create_table_query)

        # 3. Prepare Tuples
        venue_tuples = [
            (v["id"], v["ground"], v["city"], v["country"]) for v in venues
        ]

        # 4. Corrected Upsert Query (using 'ground' consistently)
        upsert_query = """
        INSERT INTO venues (id, ground, city, country)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            ground = VALUES(ground),
            city = VALUES(city),
            country = VALUES(country)
        """

        cursor.executemany(upsert_query, venue_tuples)
        conn.commit()

        st.success(
            f"Successfully created table and inserted/updated {len(venues)} venues!"
        )

    except mysql.connector.Error as err:
        st.error(f"MySQL Error: {err}")
    finally:
        # Close connection cleanly
        if "cursor" in locals() and cursor:
            cursor.close()
        if "conn" in locals() and conn.is_connected():
            conn.close()
else:
    st.warning("`venues` list is empty! Check API JSON key structure.")

#display a search bar
# display a search bar
st.header("welcome to the venuew details")
st.page_link("app.py", label="Home")

st.divider()
venue_options = {
    f"{v.get('ground', 'Unknown')}": idx
    for idx, v in enumerate(venues)
}

selected_venue_label = st.selectbox(
    "Select a venue:",
    options=list(venue_options.keys()),
    index=None,
    placeholder="Select venue...",
)

if selected_venue_label:
    selected_venue = venues[venue_options[selected_venue_label]]
    #st.write("Selected Player Data:", selected_player)
    st.write(f"player id:{selected_venue.get('id')}")
    st.write(f"ground name:{selected_venue.get('ground')}")
    st.write(f"ground city:{selected_venue.get('city')}")
    st.write(f"ground city:{selected_venue.get('country')}")