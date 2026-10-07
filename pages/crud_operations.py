import streamlit as st
from utils.db_connection import get_connection, run_query

st.header("⚙️ Player Analytics CRUD Management")

# Reduced to 3 tabs since Update & Delete are combined in tab3
tab1, tab2, tab3 = st.tabs(["Read", "Create", "Update / Delete"])

# ---------------------------------------------------------
# 1. READ TAB
# ---------------------------------------------------------
with tab1:
    st.subheader("View Players")
    df = run_query("SELECT * FROM players1 LIMIT 50;")
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# 2. CREATE TAB
# ---------------------------------------------------------
with tab2:
    st.subheader("Add New Player")

    # Form is now correctly indented inside tab2
    with st.form("add_player_form", clear_on_submit=True):
        name = st.text_input("Player Name")
        role = st.selectbox(
            "Role", 
            ["Batsman", "Bowler", "All-rounder", "Wicket-keeper", "Batting Allrounder", "Bowling Allrounder"]
        )
        battingstyle = st.selectbox(
            "Batting Style", 
            ["Right-hand bat", "Left-hand bat"]
        )
        bowlingstyle = st.selectbox(
            "Bowling Style", 
            [
                "Right-arm fast", 
                "Right-arm medium", 
                "Right-arm offbreak",
                "Right-arm legbreak", 
                "Left-arm fast", 
                "Left-arm medium", 
                "Left-arm orthodox", 
                "None"
            ]
        )
        
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not name.strip():
                st.error("Please enter a player name.")
            else:
                conn = None
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO players1 (id, name, role, batting_style, bowling_style) 
                        VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM players1 p), %s, %s, %s, %s)
                        """,
                        (name.strip(), role, battingstyle, bowlingstyle)
                    )
                    conn.commit()
                    st.success(f"Player '{name}' added successfully!")
                except Exception as e:
                    st.error(f"Error adding player: {e}")
                finally:
                    if conn:
                        conn.close()

# ---------------------------------------------------------
# 3. UPDATE & DELETE TAB (Auto-Complete / Search Enabled)
# ---------------------------------------------------------
with tab3:
    st.subheader("Manage Players (Update / Delete)")

    # 1. Fetch player records
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role, batting_style, bowling_style FROM players1 ORDER BY name ASC")
    
    # Safely fetch column names and rows regardless of cursor type
    if cursor.description:
        columns = [desc[0] for desc in cursor.description]
        raw_rows = cursor.fetchall()
        
        # Convert any tuple/dict row format safely into standard dictionaries
        players = []
        for row in raw_rows:
            if isinstance(row, dict):
                players.append(row)
            else:
                players.append(dict(zip(columns, row)))
    else:
        players = []
        
    conn.close()

    if players:
        # 2. Map formatted string label -> player dict object
        player_map = {
            f"{p.get('name', 'Unknown')} (ID: {p.get('id', 'N/A')})": p 
            for p in players
        }

        # 3. Selectbox displaying actual player names
        selected_label = st.selectbox(
            "👤 Select Player Name:",
            options=list(player_map.keys()),
            key="all_players_selectbox"
        )

        # Retrieve selected player object
        selected_player = player_map[selected_label]

        st.markdown("---")

        col_update, col_delete = st.columns([2, 1])

        # ------------------- UPDATE SECTION -------------------
        with col_update:
            st.markdown(f"#### ✏️ Update Details for **{selected_player.get('name', '')}**")
            
            with st.form("update_player_form", clear_on_submit=False):
                up_name = st.text_input("Player Name", value=selected_player.get("name", ""))

                roles = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper", "Batting Allrounder", "Bowling Allrounder"]
                cur_role = selected_player.get("role", "")
                role_idx = roles.index(cur_role) if cur_role in roles else 0
                up_role = st.selectbox("Role", roles, index=role_idx)

                bat_styles = ["Right-hand bat", "Left-hand bat"]
                cur_bat = selected_player.get("batting_style", "")
                bat_idx = bat_styles.index(cur_bat) if cur_bat in bat_styles else 0
                up_batting = st.selectbox("Batting Style", bat_styles, index=bat_idx)

                bowl_styles = [
                    "Right-arm fast", "Right-arm medium", "Right-arm offbreak", "Right-arm legbreak",
                    "Left-arm fast", "Left-arm medium", "Left-arm orthodox", "None"
                ]
                cur_bowl = selected_player.get("bowling_style", "")
                bowl_idx = bowl_styles.index(cur_bowl) if cur_bowl in bowl_styles else 0
                up_bowling = st.selectbox("Bowling Style", bowl_styles, index=bowl_idx)

                submit_update = st.form_submit_button("Save Changes")

                if submit_update:
                    if not up_name.strip():
                        st.error("Player name cannot be empty.")
                    else:
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                """
                                UPDATE players1 
                                SET name = %s, role = %s, batting_style = %s, bowling_style = %s 
                                WHERE id = %s
                                """,
                                (up_name.strip(), up_role, up_batting, up_bowling, selected_player["id"])
                            )
                            conn.commit()
                            conn.close()

                            st.success(f"Player '{up_name.strip()}' updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating player: {e}")

        # ------------------- DELETE SECTION -------------------
        with col_delete:
            st.markdown("#### 🗑️ Delete Player")
            st.warning(f"Delete **{selected_player.get('name', '')}** (ID: {selected_player.get('id', '')})?")

            if st.button("Confirm Delete", type="primary", key="del_btn_fixed"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM players1 WHERE id = %s", (selected_player["id"],))
                    conn.commit()
                    conn.close()

                    st.success(f"Player '{selected_player.get('name', '')}' deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting player: {e}")

    else:
        st.info("No players found in database.")