import mysql.connector
import pandas as pd
import streamlit as st
import warnings

# ==========================================
# 1. MYSQL CONFIGURATION
# ==========================================
MYSQL_HOST = "localhost"
MYSQL_USER = "root"          # Change to your MySQL username
MYSQL_PASSWORD = st.secrets["DB_PASSWORD"]  # Change to your MySQL password
MYSQL_DB = "cricbuzz_db"

def get_db_connection():
    """Establishes connection to MySQL database."""
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

def run_query(query):
    """Executes SQL query and returns results as a Pandas DataFrame."""
    try:
        conn = get_db_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)
st.write("Welcome to Query Practice Portal")
options=["Select the question",
         """1.Find all players who represent India. Display their full name, playing role, 
batting style, and bowling style.""",
"2. Show all cricket matches that were played in the last Few days",
"3. Top 10 ODI Run scorers",
"4. Cricket venues that seating capacity over 25000",
"5. Calculate how amny matches each team won",
"6. Count players belong their role",
"7. Highest batting score players Test, ODI, T20I",
"8. Show all the cricket series in 2024",
"9. Find all rounders >100runs and >50 wickets",
"10. get last 20 completed matches"

]
selected_option=st.selectbox("choose a query", options)
query=None
if selected_option == options[1]:
    # SQL query to fetch all players (or specific columns filtering India)
    query = "SELECT * FROM players;"
elif selected_option==options[2]:
    query = "SELECT * FROM matches;" 
elif selected_option==options[3]:
    query = "SELECT * FROM ranking ORDER BY `rank` ASC LIMIT 10;"
elif selected_option==options[4]:
    query = "SELECT * FROM venues;"
elif selected_option==options[5]:
    query = "SELECT series_name , COUNT(*) FROM matches WHERE state='complete' GROUP BY series_name;"
elif selected_option==options[6]:
    query="SELECT role, COUNT(*) AS count FROM players1 GROUP BY role;"
elif selected_option==options[7]:
    query="SELECT name, strkrate FROM score ORDER BY strkrate DESC;"
elif selected_option==options[8]:
    query="SELECT * FROM matches WHERE MONTH (start_date)=10;"
elif selected_option==options[9]:
    query="SELECT name FROM players1 WHERE ROLE='Batting Allrounder';"
elif selected_option==options[10]:
    query="SELECT name,runs,balls,fours,sixes,strkrate FROM score WHERE name in ('Stirling','Balbirnie');"
if query:
    # Run the query
    df, error = run_query(query)
    
    # Display the result in a DataFrame or show an error
    if error:
        st.error(f"Error executing query: {error}")
    else:
        st.subheader("Query Output:")
        st.dataframe(df)

elif selected_option != "Select the question":
    st.info("Please select a valid question.")

warnings.filterwarnings('ignore', category=UserWarning, module='pandas')