from datetime import datetime
import requests
import streamlit as st
import mysql.connector

# ==========================================
# 1. CONFIGURATION
# ==========================================
API_KEY = "49bf8fa595mshc29bb7272aa862cp141394jsn8cc537810b17"
API_HOST = "cricbuzz-cricket.p.rapidapi.com"
API_URL = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"

# MySQL Database Credentials
MYSQL_HOST = "localhost"
MYSQL_USER = "root"          # Change to your MySQL username
MYSQL_PASSWORD = "2024"  # Change to your MySQL password
MYSQL_DB = "cricbuzz_db"     # Database created in Workbench

# ==========================================
# 2. MYSQL DATABASE SETUP & FUNCTIONS
# ==========================================
def get_db_connection():
    """Returns a connection to the MySQL database."""
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

def init_db():
    """Creates the matches table in MySQL if it doesn't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_id INT PRIMARY KEY,
                series_id INT,
                series_name VARCHAR(255),
                match_desc VARCHAR(255),
                match_format VARCHAR(50),
                start_date VARCHAR(100),
                end_date VARCHAR(100),
                state VARCHAR(100),
                status TEXT,
                team1_name VARCHAR(100),
                team2_name VARCHAR(100),
                venue_name VARCHAR(255),
                city VARCHAR(100)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        st.error(f"MySQL Error: {err}")

def save_matches_to_db(matches):
    """Inserts or updates fetched matches into MySQL."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = '''
            INSERT INTO matches (
                match_id, series_id, series_name, match_desc, match_format,
                start_date, end_date, state, status, team1_name, team2_name,
                venue_name, city
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                series_id=VALUES(series_id),
                series_name=VALUES(series_name),
                match_desc=VALUES(match_desc),
                match_format=VALUES(match_format),
                start_date=VALUES(start_date),
                end_date=VALUES(end_date),
                state=VALUES(state),
                status=VALUES(status),
                team1_name=VALUES(team1_name),
                team2_name=VALUES(team2_name),
                venue_name=VALUES(venue_name),
                city=VALUES(city);
        '''

        for match in matches:
            match_id = match.get("matchId")
            if not match_id:
                continue

            start_date = format_timestamp(match.get("startDate"))
            end_date = format_timestamp(match.get("endDate"))

            values = (
                match_id,
                match.get("seriesId"),
                match.get("seriesName"),
                match.get("matchDesc"),
                match.get("matchFormat"),
                start_date,
                end_date,
                match.get("state"),
                match.get("status"),
                match.get("team1", {}).get("teamName"),
                match.get("team2", {}).get("teamName"),
                match.get("venueInfo", {}).get("ground"),
                match.get("venueInfo", {}).get("city")
            )
            cursor.execute(insert_query, values)

        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        st.error(f"Database insertion failed: {err}")

# ==========================================
# 3. API DATA FETCHING
# ==========================================
@st.cache_data(ttl=60)
def fetch_live_matches():
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        matches = []
        for match_type in data.get("typeMatches", []):
            for series in match_type.get("seriesMatches", []):
                if "seriesAdWrapper" in series:
                    series_data = series["seriesAdWrapper"]
                    for match in series_data.get("matches", []):
                        if "matchInfo" in match:
                            matches.append(match["matchInfo"])
        return matches

    except requests.exceptions.RequestException as e:
        st.error(f"API Request failed: {e}")
        return []

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
def format_timestamp(timestamp):
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return str(timestamp)

# ==========================================
# 5. STREAMLIT UI
# ==========================================
def main():
    st.set_page_config(page_title="Cricbuzz Live Match Center", layout="wide")
    st.title("🏏 Live Cricket Match Center (MySQL)")

    # Initialize Table in MySQL
    init_db()

    # Fetch Data from API
    with st.spinner("Fetching live matches..."):
        matches = fetch_live_matches()

    if matches:
        save_matches_to_db(matches)
        st.sidebar.success(f"Saved/Updated {len(matches)} matches in MySQL Database!")
    else:
        st.warning("No matches found or failed to load data.")
        st.stop()

    # Dropdown for selecting matches
    match_options = {
        f"{m.get('team1', {}).get('teamName', 'Team 1')} vs {m.get('team2', {}).get('teamName', 'Team 2')} - {m.get('matchDesc', '')}": idx
        for idx, m in enumerate(matches)
    }

    selected_label = st.selectbox("Select a Match:", list(match_options.keys()))
    selected_match = matches[match_options[selected_label]]
    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.page_link("pages/players.py", label="Players")
    with col2:
        st.page_link("pages/venue.py", label="Venue")
    with col3:
        st.page_link("pages/ranking.py", label="Top ranks")
    with col4:
        st.page_link("pages/score.py", label="Top Score")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 Match Overview")
        if "matchId" in selected_match:
            st.write("**Match ID:**", selected_match["matchId"])
        if "seriesId" in selected_match:
            st.write("**Series ID:**", selected_match["seriesId"])
        if "seriesName" in selected_match:
            st.write("**Series Name:**", selected_match["seriesName"])
        if "matchDesc" in selected_match:
            st.write("**Match Description:**", selected_match["matchDesc"])
        if "matchFormat" in selected_match:
            st.write("**Match Format:**", selected_match["matchFormat"])
            
        start_date = format_timestamp(selected_match.get("startDate"))
        if start_date:
            st.write("**Start Date:**", start_date)
            
        end_date = format_timestamp(selected_match.get("endDate"))
        if end_date:
            st.write("**End Date:**", end_date)

    with col2:
        venue = selected_match.get("venueInfo")
        if venue:
            st.subheader("🏟️ Venue Details")
            if "ground" in venue:
                st.write("**Venue Name:**", venue["ground"])
            if "city" in venue:
                st.write("**City:**", venue["city"])

if __name__ == "__main__":
    main()