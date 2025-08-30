import streamlit as st
import mysql.connector
import pandas as pd
import requests
from flask import Flask, request, jsonify

# ----------------- DB CONNECTION -----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",       
        user="root",            
        password="12345",
        database="cricbuzzz_db"   
    )




# ------------------API setup----------------------
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"
API_KEY = "44efe6ce85msh4292891f1caeca8p109352jsn0b2d04852e04"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

live_url = f"{BASE_URL}/matches/v1/live"
upcoming_url = f"{BASE_URL}/matches/v1/upcoming"
recent_url = f"{BASE_URL}/matches/v1/recent"
# player_stats_url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"

# ---------------- Divider ----------------
st.markdown("---")

# # Info Box
# st.info("This section gives a quick glance of Cricket.")



# ----------------- STREAMLIT UI -----------------
st.set_page_config(page_title="🏏 Cricket Dashboard", layout="wide")
st.title("🏏 Cricket Analytics Dashboard")

st.sidebar.title("🏏 Cricket Dashboard")

matches = st.sidebar.selectbox(
    "Select a Page",
    ["🟢 Live Matches", "📅 Upcoming Matches", "📜 Recent Matches","📝 SQL Questions"]
)


def fetch_json(url):
    """Fetch API response safely with error handling"""
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            st.error(f"❌ API Error {response.status_code}")
            st.code(response.text[:500])
            return None
        try:
            return response.json()
        except Exception:
            st.error("❌ JSON Decode Failed")
            st.code(response.text[:500])  # show first 500 chars of raw response
            return None
    except Exception as e:
        st.error(f"⚠️ Request Failed: {e}")
        return None


import streamlit as st
from datetime import datetime, timezone, timedelta

#  Convert timestamp (ms) 
def format_date(timestamp):
    if not timestamp:
        return "N/A"
    ts = int(timestamp) // 1000  # milliseconds → seconds
    ist = timezone(timedelta(hours=5, minutes=30))  # IST timezone
    return datetime.fromtimestamp(ts, tz=ist).strftime("%d %b %Y, %I:%M %p")


# def scoreboard_details(match_id):
#     import requests

#     url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/hscard"



#     response = requests.get(url, headers=headers)

#     return response.json()


# ----------------------------------------Scorecard--------------------------------

def scoreboard(match_id: int):
    """
    Display full scoreboard (batting + bowling) for a given match_id.
    """
    h_url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/hscard" # replace with your API endpoint
    response = requests.get(h_url,headers=headers)

    if response.status_code != 200:
        st.error("⚠️ Failed to fetch scoreboard data.")
        return

    data = response.json()
    if not data or "scoreCard" not in data:
        st.warning("📭 Scoreboard not available yet.")
        return

    innings_data = data["scoreCard"]

    # Select innings
    innings_options = [f"Innings {inn['inningsId']}" for inn in innings_data]
    
    if not innings_options:
        st.info("⚠️ No innings available yet (match not started).")
        return
        
        
    selected_innings = st.selectbox("Select Innings", innings_options)

    selected_innings_id = int(selected_innings.split()[-1])
    inning_obj = next((inn for inn in innings_data if inn["inningsId"] == selected_innings_id), None)

    if not inning_obj:
        st.warning("⏳ Innings not started yet.")
        return
    
    

    # === TEAM SCORE SUMMARY ===
    bat_team = inning_obj["batTeamDetails"]["batTeamName"]
    score_info = inning_obj.get("scoreDetails", {})

    runs = score_info.get("runs", 0)
    wickets = score_info.get("wickets", 0)
    overs = score_info.get("overs", 0)

    st.markdown(f"### 📊 {bat_team} {runs}/{wickets} (Overs: {overs})")

    # === BATTING TABLE ===
    st.subheader(f"🏏 {bat_team} Batting")

    batsmen = []
    for b in inning_obj["batTeamDetails"]["batsmenData"].values():
        batsmen.append([
            b.get("batName"), b.get("runs"), b.get("balls"),
            b.get("fours"), b.get("sixes"),
            b.get("strikeRate"), b.get("outDesc")
        ])
    if batsmen:
        st.table(pd.DataFrame(
            batsmen, 
            columns=["👤 Batter", "🏃 R", "⚪ B", "💥 4s", "🎯 6s", "📊 SR", "❌ Dismissal"]
        ))
    else:
        st.info("⚠️ No batting data available.")

    # === BOWLING TABLE ===
    bowl_team = inning_obj["bowlTeamDetails"]["bowlTeamName"]
    st.subheader(f"🎯 {bowl_team} Bowling")

    bowlers = []
    for bo in inning_obj["bowlTeamDetails"]["bowlersData"].values():
        bowlers.append([
            bo.get("bowlName"), bo.get("overs"), bo.get("maidens"),
            bo.get("runs"), bo.get("wickets"), bo.get("economy")
        ])
    if bowlers:
        st.table(pd.DataFrame(
            bowlers, 
            columns=["👤 Bowler", "⏱️ Overs", "🧹 Maidens", "💡 Runs", "🎯 Wickets", "📊 Econ"]
        ))
    else:
        st.info("⚠️ No bowling data available.")




        
        
        
#--------------------------------------------------------------------------------------------------------------------------------------------
        
        

    # available_innings = df_batsmen['innings_id'].unique().tolist()

    # # Streamlit selectbox
    # innings_id = st.selectbox(
    #     "Select Innings",
    #     available_innings,
    #     format_func=lambda x: f"Innings {x}"   # shows like "Innings 1", "Innings 2"
    # )

    # st.markdown("---")

    # # Check if selected innings has data
    # if innings_id in available_innings:
    #     # Batting table
    #     st.subheader(f"🏏 {df_batsmen[df_batsmen['innings_id'] == innings_id]['team'].iloc[0]} Batting")
    #     df_bat = df_batsmen[df_batsmen['innings_id'] == innings_id][
    #         ["Batter", "R", "B", "4s", "6s", "SR", "Dismissal"]
    #     ]
    #     if df_bat.empty:
    #         st.info("⚠️ Innings not started yet.")
    #     else:
    #         st.table(df_bat)

    #     # Bowling table
    #     st.subheader(f"🎯 {df_bowlers[df_bowlers['innings_id'] == innings_id]['team'].iloc[0]} Bowling")
    #     df_bowl = df_bowlers[df_bowlers['innings_id'] == innings_id][
    #         ["Bowler", "O", "M", "Runs", "W", "Economy"]
    #     ]
    #     if df_bowl.empty:
    #         st.info("⚠️ Innings not started yet.")
    #     else:
    #         st.table(df_bowl)
    # else:
    #     st.warning("⚠️ Innings not started yet.")





# def scoreboard(match_id):
#     import pandas as pd

#     matches_batsman_list = []
#     matches_bowler_list = []

#     # Fetch live scoreboard details
#     match_scard = scoreboard_details(match_id)
#     score_cards = match_scard.get("scoreCard", [])

#     if not score_cards:
#         st.info("⚠️ No scorecard data available yet for this match.")
#         return

#     for card in score_cards:
#         match_id = card.get("matchId", "N/A")
#         innings_id = card.get("inningsId", "N/A")

#         # ---------- Batting Team ----------
#         bat_team = card.get("batTeamDetails", {})
#         bat_team_id = bat_team.get("batTeamId", "N/A")
#         bat_team_name = bat_team.get("batTeamName", "N/A")
#         bat_team_short = bat_team.get("batTeamShortName", "N/A")

#         # ---------- Batsmen Data ----------
#         batsmen_data = bat_team.get("batsmenData", {})
#         if not batsmen_data:
#             st.info(f"ℹ️ No batsmen data yet for {bat_team_name}")
#         for _,bat_info in batsmen_data.items():
#             matches_batsman_list.append({
#                 "match_id": match_id,
#                 "innings_id": innings_id,
#                 "bat_team_id": bat_team_id,
#                 "bat_team_name": bat_team_name,
#                 "bat_team_short": bat_team_short,
#                 "bat_id": bat_info.get("batId", "N/A"),
#                 "bat_name": bat_info.get("batName", "N/A"),
#                 "is_captain": bat_info.get("isCaptain", False),
#                 "is_keeper": bat_info.get("isKeeper", False),
#                 "runs": bat_info.get("runs", 0),
#                 "balls": bat_info.get("balls", 0),
#                 "fours": bat_info.get("fours", 0),
#                 "sixes": bat_info.get("sixes", 0),
#                 "strike_rate": bat_info.get("strikeRate", 0.0),
#                 "out_desc": bat_info.get("outDesc", ""),
#                 "bowler_id": bat_info.get("bowlerId", None),
#                 "fielder1_id": bat_info.get("fielderId1", None),
#                 "fielder2_id": bat_info.get("fielderId2", None),
#                 "fielder3_id": bat_info.get("fielderId3", None),
#                 "wicket_code": bat_info.get("wicketCode", None)
#             })

#         # ---------- Bowling Team ----------
#         bowl_team = card.get("bowlTeamDetails", {})
#         bowl_team_id = bowl_team.get("bowlTeamId", "N/A")
#         bowl_team_name = bowl_team.get("bowlTeamName", "N/A")
#         bowl_team_short = bowl_team.get("bowlTeamShortName", "N/A")

#         # ---------- Bowlers Data ----------
#         bowlers_data = bowl_team.get("bowlersData", {})
#         if not bowlers_data:
#             st.info(f"ℹ️ No bowlers data yet for {bowl_team_name}")
#         for _,bowl_info in bowlers_data.items():
#             matches_bowler_list.append({
#                 "match_id": match_id,
#                 "innings_id": innings_id,
#                 "bowl_team_id": bowl_team_id,
#                 "bowl_team_name": bowl_team_name,
#                 "bowl_team_short": bowl_team_short,
#                 "bowler_id": bowl_info.get("bowlerId", "N/A"),
#                 "bowler_name": bowl_info.get("bowlerName", "N/A"),
#                 "overs": bowl_info.get("overs", 0.0),
#                 "maidens": bowl_info.get("maidens", 0),
#                 "runs_conceded": bowl_info.get("runs", 0),
#                 "wickets": bowl_info.get("wickets", 0),
#                 "economy": bowl_info.get("economy", 0.0),
#                 "dots": bowl_info.get("dots", 0),
#                 "fours_conceded": bowl_info.get("fours", 0),
#                 "sixes_conceded": bowl_info.get("sixes", 0)
#             })

#     # Convert lists to DataFrames
#     df_batsmen = pd.DataFrame(matches_batsman_list)
#     df_bowlers = pd.DataFrame(matches_bowler_list)

#     # Show tables, even if empty
#     st.subheader("🏏 Match Teams")
#     st.markdown("---")

#     st.text(f"🏏 Batting Team: {bat_team_name}")
#     st.text(f"🎯 Bowling Team: {bowl_team_name}")

#     cards = st.selectbox(
#         f"⚡ {bat_team_name} vs {bowl_team_name} ⚡",
#         [f"🏏 {bat_team_name}", f"🎯 {bowl_team_name}"]
#     )

#     if cards == f"🏏 {bat_team_name}":
#         df_bat = df_batsmen[df_batsmen['bat_team_name'] == bat_team_name][[
#             "bat_name", "out_desc", "runs", "balls", "fours", "sixes", "strike_rate"
#         ]].rename(columns={
#             "bat_name": "🧑‍💻 Batter",
#             "out_desc": "💀 Out_desc",
#             "runs": "🏃 Runs",
#             "balls": "⚪ Balls",
#             "fours": "4️⃣",
#             "sixes": "6️⃣",
#             "strike_rate": "⚡ SR"
#         })
#         st.dataframe(df_bat)
#     else:
#         df_bowl = df_bowlers[df_bowlers['bowl_team_name'] == bowl_team_name][[
#             "bowler_name", "overs", "maidens", "runs_conceded", "wickets", "economy"
#         ]].rename(columns={
#             "bowler_name": "🎯 Bowler",
#             "overs": "⏱️ Overs",
#             "maidens": "🔒 Maidens",
#             "runs_conceded": "🏃 Runs",
#             "wickets": "⚡ Wkts",
#             "economy": "📊 Econ"
#         })
#         st.subheader("🎯 Bowlers Scorecard")
#         st.dataframe(df_bowl)


       
        
#     if df_batsmen.empty:
#         st.info("ℹ️ No batsmen data available yet.")
    
#     if df_bowlers.empty:
#         st.info("ℹ️ No bowlers data available yet.")
    

        

# --------------------------------Matches functions------------------------------------

def show_matches(url, title):
    st.header(title)
    data = fetch_json(url)
    if not data:
        st.warning("⚠️ No live matches right now (204).")
        return
    
    Matches = []
    for type_match in data.get("typeMatches", []):
        for series_match in type_match.get("seriesMatches", []):
            series_data = series_match.get('seriesAdWrapper', {})
            series_name = series_data.get('seriesName')
            
            for match in series_data.get('matches', []):
                info = match.get('matchInfo', {})
                venue_info = info.get("venueInfo", {})
                
                match_id = info.get('matchId')
                match_desc = info.get("matchDesc")
                match_format = info.get("matchFormat")
                start_date = info.get("startDate")
                readable_date = format_date(start_date)  #  formatted date
                status = info.get("status")
                team1 = info.get("team1", {}).get("teamSName")
                team2 = info.get("team2", {}).get("teamSName")
                ground = venue_info.get("ground")
                city = venue_info.get("city")
                country = venue_info.get("country")

                #  Get live score if available
                score_data = match.get("matchScore", {})
                
                
                if score_data:  
                    team1_score = score_data.get("team1Score", {}).get("inngs1", {})
                    team2_score = score_data.get("team2Score", {}).get("inngs1", {})

                    team1_runs = team1_score.get("runs", "-")
                    team1_wkts = team1_score.get("wickets", "-")
                    team1_overs = team1_score.get("overs", "-")

                    team2_runs = team2_score.get("runs", "-")
                    team2_wkts = team2_score.get("wickets", "-")
                    team2_overs = team2_score.get("overs", "-")
                else:
                    #  If match not started or no score yet
                    team1_runs = team1_wkts = team1_overs = "N/A"
                    team2_runs = team2_wkts = team2_overs = "N/A"
                    if "upcoming" in url:
                        status = "⏳ Match not started yet"
                    # elif "recent" in url:
                    #     status = "📜 No score available yet"

                Matches.append({
                    "title": f"{team1} vs {team2} ({match_desc}), ({readable_date})",
                    "series_name": series_name,
                    "match_id": match_id,
                    "match_desc": match_desc,
                    "match_format": match_format,
                    "team1": team1,
                    "team2": team2,
                    "team1_runs": team1_runs,
                    "team1_wkts": team1_wkts,
                    "team1_overs": team1_overs,
                    "team2_runs": team2_runs,
                    "team2_wkts": team2_wkts,
                    "team2_overs": team2_overs,
                    "ground": ground,
                    "city": city,
                    "country": country,
                    "status": status,
                    "start_date": readable_date  # ✅ show formatted date
                })


    if Matches:
        # ✅ use Matches list, not matches (sidebar var)
        match_titles = [m["title"] for m in Matches]
        selected_title = st.selectbox("🎯 Select a Match", match_titles)
        selected_match = next(m for m in Matches if m["title"] == selected_title)
        
        st.subheader(f"🏏 {selected_match['team1']} vs {selected_match['team2']}")
        st.caption(f"📌 Series: {selected_match['series_name']} | Format: {selected_match['match_format']}")
        st.caption(f"📍 Venue: {selected_match['ground']}, {selected_match['city']} ({selected_match['country']})")
        st.caption(f"⏳ Status: {selected_match['status']}")
        
        #showing scorecard symbols
        st.markdown("### 📊 Scorecard")
        # ✅ Show scores (if available, otherwise N/A)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{selected_match['team1']}", 
                      f"{selected_match['team1_runs']}/{selected_match['team1_wkts']}", 
                      f"Overs: {selected_match['team1_overs']}")
        with col2:
            st.metric(f"{selected_match['team2']}", 
                      f"{selected_match['team2_runs']}/{selected_match['team2_wkts']}", 
                      f"Overs: {selected_match['team2_overs']}")
            
        st.markdown("### 📊 ScoreBoard")
        scoreboard(selected_match["match_id"])
    else:
        st.warning("⚠️ No matches found in this category.")
        
        
        
# ------------------------------Run query----------------------
def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df



# --------------------------------------SQL Questions------------------------------

def show_sql():
    st.header("📊 SQL Questions")

    
    sql_questions = {
        "Find all players who represent India.": """
            SELECT name, role, batting_style, bowling_style 
            FROM players
            WHERE country = 'India';
        """,
        "Show all cricket matches that were played in the last 30 days.":"""
            SELECT  team1 ,team2,venue,start_date
            FROM matches 
            WHERE start_date >= CURDATE() - INTERVAL 30 DAY
            ORDER BY start_date DESC;

        """,
        "List the top 10 highest run scorers in ODI cricket. Show player name, total runs scored,batting average, and number of centuries.":"""
            -- Top 10 highest run scorers in ODI cricket
            SELECT 
                name AS player_name,
                total_runs,
                batting_avg,
                centuries
                FROM players
                ORDER BY total_runs DESC
                LIMIT 10;

        """,
        "Display all cricket venues that have a seating capacity of more than 50,000 spectators.":"""
            SELECT venue_name, city, country, capacity
            FROM venues
            WHERE capacity >= 50000
            ORDER BY capacity DESC;
            """,
        " Calculate how many matches each team has won.":"""
            SELECT 
                winner AS team_name,
                COUNT(*) AS total_wins
            FROM (
                SELECT
                    CASE
                        WHEN status LIKE 'India won%' THEN 'India'
                        WHEN status LIKE 'Australia won%' THEN 'Australia'
                        WHEN status LIKE 'Pakistan won%' THEN 'Pakistan'
                        WHEN status LIKE 'England won%' THEN 'England'
                        WHEN status LIKE 'Bangladesh won%' THEN 'Bangladesh'
                        WHEN status LIKE 'Sri Lanka won%' THEN 'Sri Lanka'
                        WHEN status LIKE 'Afghanistan won%' THEN 'Afghanistan'
                        WHEN status LIKE 'West Indies won%' THEN 'West Indies'
                        WHEN status LIKE 'South Africa won%' THEN 'South Africa'
                        WHEN status LIKE 'New Zealand won%' THEN 'New Zealand'
                        ELSE NULL
                    END AS winner
                FROM matches
            ) AS derived
            WHERE winner IS NOT NULL
            GROUP BY winner
            ORDER BY total_wins DESC;
            """,
        " Count how many players belong to each playing role (like Batsman, Bowler, All-rounder, Wicket-keeper).":"""
           SELECT role AS Playing_Role,count(role) AS count_No
                FROM Players
                group by Playing_Role
                ORDER BY count_No DESC;
             """,
        "Find the highest individual batting score achieved in each cricket format (Test, ODI, T20I).":"""
            SELECT format, MAX(runs_scored) AS highest_score
                FROM batting_records
                GROUP BY format;

            """,
        "Show all cricket series that started in the year 2024. ":"""
            SELECT 
                    s.name,
                    v.country AS host_country ,v.venue_name AS venue,
                    FROM_UNIXTIME(start_date / 1000) AS start_date
                FROM series as s
                left join venues as v ON s.series_id=v.venue_id
                WHERE YEAR(FROM_UNIXTIME(start_date / 1000)) = 2024
                ORDER BY start_date;
            """,
            #--------Intermediate Level----------
        "Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career.":"""
             select
                p.name as player_Name,
                p.total_runs as Total_Runs,
                p.wickets AS wickets,
                b.format as Format
                from players as p
                left join batting_records as b on b.player_id=p.player_id
                where p.total_runs>=1000 and wickets>=50
                limit 10;
            """,
        "Get details of the last 20 completed matches.":"""
            select
                series_name AS Match_Description,
                team1,
                team2,
                SUBSTRING_INDEX(status, ' ', 1) AS Winning_team,
                status as Victory_Margin,
                SUBSTRING_INDEX(status, ' ',-1) as Victory_Type,
                venue as Venue_Name
            FROM matches
            where state="Completed" or state="Complete"
            limit 20;
            """,
        "Compare each player's performance across different cricket formats.":"""
            SELECT 
                    p.player_id,
                    p.name AS name,

                    -- Total runs by format
                    SUM(CASE WHEN b.format = 'Test' THEN b.runs_scored ELSE 0 END) AS test_runs,
                    SUM(CASE WHEN b.format = 'ODI' THEN b.runs_scored ELSE 0 END)  AS odi_runs,
                    SUM(CASE WHEN b.format = 'T20I' THEN b.runs_scored ELSE 0 END) AS t20i_runs

                    -- Overall batting average across all formats
                    -- ROUND(SUM(b.runs_scored) * 1.0 / COUNT(b.match_date), 2) AS overall_batting_avg

                FROM players AS p
                JOIN batting_records AS b 
                    ON b.player_id = p.player_id
                GROUP BY p.player_id, p.name
                -- HAVING COUNT(DISTINCT b.format) >= 2   -- at least 2 formats
                LIMIT 0, 1000;
            """,
        "Analyze each international team's performance when playing at home versus playing away.":"""
            SELECT 
                t.team_name,
                CASE
                    WHEN t.country = 'India' THEN 'Home'
                    ELSE 'Away'
                END AS location,
                COUNT(*) AS matches_played
            FROM matches m
            JOIN team t 
                ON t.team_name = m.team1 OR t.team_name = m.team2
            GROUP BY t.team_name, location
            ORDER BY t.team_name, location;

            """,
            " Identify batting partnerships where two consecutive batsmen (batting positions next to each other) scored a combined total of 100 or more runs in the same innings":"""
            SELECT 
                    m.match_id,
                    m.series_name,
                    m.match_desc,
                    i.bat_team_name AS batting_team,
                    b1.player_name AS batsman1,
                    b2.player_name AS batsman2,
                    (b1.runs + b2.runs) AS partnership_runs,
                    b1.innings_no
                FROM batting_scorecard b1
                JOIN batting_scorecard b2
                    ON b1.match_id = b2.match_id
                    AND b1.innings_no = b2.innings_no
                    AND b1.id < b2.id   -- Assumes ID reflects batting order
                JOIN innings i
                    ON b1.match_id = i.match_id
                    AND b1.innings_no = i.innings_id
                JOIN matches m
                    ON b1.match_id = m.match_id
                WHERE (b1.runs + b2.runs) >= 100
                ORDER BY m.match_id, b1.innings_no, partnership_runs DESC;
                """,
                
                
            "Examine bowling performance at different venues. ":"""
                SELECT
                    p.name AS Player_name,
                    p.country,
                    AVG(p.bowling_avg) AS Avg_Economy_Rate,
                    SUM(p.wickets) AS Total_wickets,
                    AVG(p.economy) AS Avg_economy
                FROM players p
                GROUP BY p.name, p.country
                ORDER BY Total_wickets DESC;
                
                """,
                
            " Identify players who perform exceptionally well in close matches. A close match is defined as one decided by less than 50 runs OR less than 5 wickets.":
            """ 
                SELECT series_name,
                    match_format,
                    ABS(team1_runs - team2_runs) AS run_margin,
                    ABS(team1_wkts - team2_wkts) AS wicket_margin
                FROM matches
                WHERE state = 'Complete' AND ABS(team1_runs - team2_runs) > 50
                ORDER BY start_date ASC
                LIMIT 10; 
                """
        
        
        
            
    }

    # Selectbox to choose a question
    selected_question = st.selectbox("Select a Query:", list(sql_questions.keys()))

    # Show the SQL query for the selected question
    st.subheader("📝 SQL Query:")
    st.code(sql_questions[selected_question], language="sql")
    
    #results of query
    st.subheader("📋 Query Result:")
    df = run_query(sql_questions[selected_question])
    st.dataframe(df)
    # st.table(df)



#--------------------------Main Page---------------------------
if matches == "🟢 Live Matches":
    show_matches(live_url, "🟢 Live Matches Scorecard")

elif matches == "📅 Upcoming Matches":
    show_matches(upcoming_url, "📅 Upcoming Matches")

elif matches == "📜 Recent Matches":
    show_matches(recent_url, "📜 Recent Matches")
elif matches=="📝 SQL Questions":
    show_sql()





# -----------------------------------------CRUD Operations-------------------------------------------




# st.sidebar.subheader("⚙️ Manage Players")
# operation = st.sidebar.selectbox("Select Operation", ["🆕 Add", "🔄 Update", "🗑️ Delete", "📊 View"])

st.sidebar.markdown("## ⚙️ Manage Players")

operation = st.sidebar.selectbox(
    "Choose an Action",
    [
        "Select", 
        "🆕 Add Player",
        "📝 Update Player",
        "🗑️ Delete Player",
        "📊 View Players"
    ]
)


# # --- Inputs ---
# player_id = st.text_input("🆔 Player ID (for Update/Delete)")
# player_name = st.text_input("👤 Name")
# player_role = st.selectbox("🎭 Role", ["🏏 Batsman", "🎯 Bowler", "⚖️ All-rounder", "🧤 Wicket-keeper"])
# batting_style = st.text_input("🏏 Batting Style")
# bowling_style = st.text_input("🎯 Bowling Style")
# country = st.text_input("🌍 Country")
# total_runs = st.number_input("🏃 Total Runs", min_value=0)
# wickets = st.number_input("🎳 Wickets", min_value=0)

# nickname = st.text_input("🏷️ Nickname")
# birthplace = st.text_input("📍 Birthplace")
# dob = st.date_input("🎂 Date of Birth")
# matches_played = st.number_input("🎮 Matches Played", min_value=0)
# innings = st.number_input("📝 Innings", min_value=0)


# fifties = st.number_input("5️⃣ Fifties", min_value=0)
# centuries = st.number_input("💯 Centuries", min_value=0)
# batting_avg = st.number_input("📊 Batting Avg", min_value=0.0, format="%.2f")
# strike_rate = st.number_input("⚡ Strike Rate", min_value=0.0, format="%.2f")




#-------------------------------------------------------CRUD OPERATION------------------------------------

def get_db_connection():
    return get_connection()

#--------------------------------------------------Adding the Player-----------------------------------

def add_player():
    # --- Inputs ---
    player_id = st.text_input("🆔 Player ID (for Update/Delete)")
    player_name = st.text_input("👤 Name")
    player_role = st.selectbox("🎭 Role", ["🏏 Batsman", "🎯 Bowler", "⚖️ All-rounder", "🧤 Wicket-keeper"])
    batting_style = st.text_input("🏏 Batting Style")
    bowling_style = st.text_input("🎯 Bowling Style")
    country = st.text_input("🌍 Country")
    total_runs = st.number_input("🏃 Total Runs", min_value=0)
    wickets = st.number_input("🎳 Wickets", min_value=0)
    
    
    if not player_name or not country:
        st.warning("⚠️ Please fill at least Name and Country!")
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO players
        (Player_id,name, role, batting_style, bowling_style, country, total_runs, wickets)
        VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
    """
    cursor.execute(query, (
        player_id,player_name, player_role, batting_style, bowling_style, country, total_runs, wickets
    ))
    conn.commit()
    cursor.close()
    conn.close()
    st.success(f"Player {player_name} added successfully!")
    st.balloons()


def update_player():
    # --- Inputs ---
    player_id = st.text_input("🆔 Player ID (for Update/Delete)")
    player_name = st.text_input("👤 Name")
    player_role = st.selectbox("🎭 Role", ["🏏 Batsman", "🎯 Bowler", "⚖️ All-rounder", "🧤 Wicket-keeper"])
    batting_style = st.text_input("🏏 Batting Style")
    bowling_style = st.text_input("🎯 Bowling Style")
    country = st.text_input("🌍 Country")
    total_runs = st.number_input("🏃 Total Runs", min_value=0)
    wickets = st.number_input("🎳 Wickets", min_value=0)
    if not player_id:
        st.warning("🚨 Provide Player ID to update!")
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE players SET
            name=%s, role=%s, batting_style=%s, bowling_style=%s, country=%s,
            total_runs=%s, wickets=%s
        WHERE player_id=%s
    """
    cursor.execute(query, (
        player_name, player_role, batting_style, bowling_style, country, total_runs, wickets, player_id
    ))
    conn.commit()
    cursor.close()
    conn.close()
    st.success(f"🎉 Player {player_name} updated successfully!")
    st.balloons()
    # 🎈🎈 Balloons animation

def delete_player():
    player_id = st.text_input("🆔 Player ID (for Update/Delete)")

    if not player_id:
        st.warning("⚠️ Provide Player ID to delete!")
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE player_id=%s", (player_id,))
    conn.commit()
    cursor.close()
    conn.close()
    st.success(f" 🎉 Player ID {player_id} deleted successfully!")
    st.balloons()  

def view_players():
    df = run_query("SELECT player_id, name, role, country, total_runs, wickets FROM players")
    st.dataframe(df)

# --- Execute operation ---
if operation == "🆕 Add Player":
    if st.button("Execute"):
        add_player()
elif operation == "📝 Update Player":
    if st.button("Execute"):
        update_player()
elif operation == "🗑️ Delete Player":
    if st.button("Execute"):
        delete_player()
elif operation == "📊 View Players":
    view_players()
# #----------------------------Player stats----------------------------



def search_player(name):
    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
    querystring = {"plrN": name}

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        st.error(f"❌ API Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    return data.get("player", [])


def get_player_career_stats(player_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None
    return response.json()     #.get("player", {})


# ------------------------------ Streamlit UI ------------------------------
option = st.sidebar.selectbox(
    "Check Statistics",
    ["Select", "🔍 Search Players"]
)

if option == "🔍 Search Players":
    st.subheader("🔍 Players Details")

    # Input box
    player_name = st.text_input("Enter player name", placeholder="e.g., Rohit Sharma")
    

    if st.button("Search"):
        if player_name:
            st.session_state.results = search_player(player_name)
            

    # Show dropdown only if results exist
    if "results" in st.session_state and st.session_state.results:
        player_choice = st.selectbox(
            "Select a player",
            [f"{p['name']} ({p.get('teamName','N/A')}) - ID: {p['id']}" for p in st.session_state.results]
        )

        selected_id = int(player_choice.split("ID:")[-1])
        
        st.session_state.selected_id = selected_id

    # Fetch career stats
    if st.button("Get Career Stats") and "selected_id" in st.session_state:
        p_info = get_player_career_stats(st.session_state.selected_id)

        if p_info:
            st.subheader(f"📌 {p_info.get('name', 'N/A')} ({p_info.get('nickName','')})")
            
            

            st.write(f"👤 **Role:** {p_info.get('role','N/A')}")
            st.write(f"🏏 **Batting Style:** {p_info.get('bat','N/A')}")
            st.write(f"🎯 **Bowling Style:** {p_info.get('bowl','N/A')}")
            st.write(f"🌍 **Team:** {p_info.get('intlTeam','N/A')}")
            st.write(f"🎂 **DOB:** {p_info.get('DoB','N/A')}")
            st.write(f"📍 **Birthplace:** {p_info.get('birthPlace','N/A')}")
            st.write(f"🛡️ **Teams Played:** {p_info.get('teams','N/A')}")

            
        else:
            st.warning("⚠️ Could not fetch player details")




# ---------------- Footer ----------------
st.sidebar.markdown("---")
# # # Info Box
# st.info("This section gives a quick glance of Cricket.")


# st.markdown("### 📱 MOBILE SITE & APPS")
# st.markdown("[🌐 m.cricbuzz.com](https://m.cricbuzz.com) | [📱 Android](https://play.google.com/store/apps/details?id=com.cricbuzz.android) | [🍏 iOS](https://apps.apple.com/in/app/cricbuzz-cricket-scores-news/id360466413)")

# st.markdown("### 🔗 FOLLOW US ON")
# st.markdown("[📘 Facebook](https://www.facebook.com/cricbuzz) | [🐦 Twitter](https://twitter.com/cricbuzz) | [▶️ YouTube](https://www.youtube.com/channel/UCSRQXk5yErn4e14vN76upOw) | [📌 Pinterest](https://in.pinterest.com/cricbuzz/)")

# st.markdown("### 🏢 COMPANY")
# st.markdown("[💼 Careers](https://www.cricbuzz.com/careers) | [📢 Advertise](https://www.cricbuzz.com/info/advertise) | [📺 Cricbuzz TV Ads](https://www.cricbuzz.com/cricbuzz-tv-ads) | [ℹ️ About Us](https://www.cricbuzz.com/info/about-us)")

# st.markdown("### 📜 LEGAL")
# st.markdown("[🔒 Privacy Notice](https://www.cricbuzz.com/info/privacy) | [📑 Terms of Use](https://www.cricbuzz.com/info/terms-of-use)")

st.sidebar.markdown("---")
st.sidebar.caption("⚡Data Source: Cricbuzz API | Built with ❤️ using Streamlit")

# ---------------- Footer ----------------
st.markdown("---")
st.caption("⚡ Data Source: Cricbuzz API | Built with ❤️ using Streamlit")
