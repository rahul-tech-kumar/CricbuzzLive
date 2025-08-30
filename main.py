import requests
import mysql.connector

# ---------------- DB CONNECTION ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",  
    database="cricket"       # create this DB in Workbench before running
)
cursor = conn.cursor()

# ---------------- INSERT FUNCTIONS ----------------
def insert_player(player):
    cursor.execute("""
        INSERT INTO players (player_id, name, nick_name, role, batting_style, bowling_style, dob, birth_place, intl_team)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE name=VALUES(name);
    """, (
        player.get("id"),
        player.get("name"),
        player.get("nickName"),
        player.get("role"),
        player.get("bat"),
        player.get("bowl"),
        player.get("DoB"),
        player.get("birthPlace"),
        player.get("intlTeam")
    ))
    conn.commit()

def insert_match(match, match_type="recent"):
    cursor.execute("""
        INSERT INTO matches (match_id, series_id, match_type, status, team1, team2, venue, start_time)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE status=VALUES(status);
    """, (
        match.get("matchId"),
        match.get("seriesId"),
        match.get("matchType"),
        match.get("status"),
        match.get("team1"),
        match.get("team2"),
        match.get("venue"),
        match.get("startTime")
    ))
    conn.commit()
    
    
def insert_batting_stats(player_id, stats):
    cursor.execute("""
        INSERT INTO batting_stats (player_id, format, matches, innings, runs, hundreds, fifties, average, strike_rate)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        player_id,
        stats.get("format", "N/A"),
        stats.get("matches", 0),
        stats.get("innings", 0),
        stats.get("runs", 0),
        stats.get("hundreds", 0),
        stats.get("fifties", 0),
        stats.get("average", 0.0),
        stats.get("strike_rate", 0.0)
    ))
    conn.commit()
    
def insert_bowling_stats(player_id, stats):
    cursor.execute("""
        INSERT INTO bowling_stats (player_id, format, matches, innings, wickets, economy, average, strike_rate, best_figures)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        player_id,
        stats.get("format", "N/A"),
        stats.get("matches", 0),
        stats.get("innings", 0),
        stats.get("wickets", 0),
        stats.get("economy", 0.0),
        stats.get("average", 0.0),
        stats.get("strike_rate", 0.0),
        stats.get("best_figures", "0/0")
    ))
    conn.commit()

def insert_series(series):
    cursor.execute("""
        INSERT INTO series (series_id, name, start_date, end_date, type)
        VALUES (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE name=VALUES(name);
    """, (
        series.get("id"),
        series.get("name"),
        series.get("startDt"),
        series.get("endDt"),
        series.get("type")
    ))
    conn.commit()

def insert_icc_rank(rank):
    cursor.execute("""
        INSERT INTO icc_rankings (format, category, player_id, rank, rating)
        VALUES (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE rating=VALUES(rating);
    """, (
        rank.get("format"),
        rank.get("category"),
        rank.get("playerId"),
        rank.get("rank"),
        rank.get("rating")
    ))
    conn.commit()
    

    
    
def insert_match_detailed(match_data, match_type="recent"):
    match_info = match_data.get("matchInfo", {})
    match_score = match_data.get("matchScore", {})

    # 1️⃣ Insert into matches
    sql_match = """
    INSERT INTO matches (match_id, series_name, match_desc, match_format,
                         start_date, end_date, state, status, team1, team2, venue, match_type)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE status=%s
    """
    vals_match = (
        match_info.get("matchId"),
        match_info.get("seriesName"),
        match_info.get("matchDesc"),
        match_info.get("matchFormat"),
        match_info.get("startDate"),
        match_info.get("endDate"),
        match_info.get("state"),
        match_info.get("status"),
        match_info.get("team1", {}).get("teamName"),
        match_info.get("team2", {}).get("teamName"),
        match_info.get("venueInfo", {}).get("ground"),
        match_type,
        match_info.get("status"),
    )
    cursor.execute(sql_match, vals_match)

    # 2️⃣ Insert team1 innings
    if "team1Score" in match_score:
        t1 = match_info.get("team1", {})
        t1_score = match_score.get("team1Score", {}).get("inngs1", {})
        sql_innings = """
        INSERT INTO match_innings (match_id, team_id, team_name, runs, wickets, overs)
        VALUES (%s,%s,%s,%s,%s,%s)
        """
        vals_innings = (
            match_info.get("matchId"),
            t1.get("teamId"),
            t1.get("teamName"),
            t1_score.get("runs"),
            t1_score.get("wickets"),
            t1_score.get("overs"),
        )
        cursor.execute(sql_innings, vals_innings)

    # 3️⃣ Insert team2 innings
    if "team2Score" in match_score:
        t2 = match_info.get("team2", {})
        t2_score = match_score.get("team2Score", {}).get("inngs1", {})
        sql_innings = """
        INSERT INTO match_innings (match_id, team_id, team_name, runs, wickets, overs)
        VALUES (%s,%s,%s,%s,%s,%s)
        """
        vals_innings = (
            match_info.get("matchId"),
            t2.get("teamId"),
            t2.get("teamName"),
            t2_score.get("runs"),
            t2_score.get("wickets"),
            t2_score.get("overs"),
        )
        cursor.execute(sql_innings, vals_innings)

    conn.commit()
    print(f"✅ Match {match_info.get('matchId')} inserted with innings")
    
    

def insert_match_players(match_id, players_section):
    all_players = []

    for group_name, players in players_section.items():
        for player in players:
            all_players.append((
                match_id,
                player.get("id"),
                player.get("name"),
                player.get("fullName"),
                player.get("nickName"),
                player.get("role"),
                player.get("captain"),
                player.get("keeper"),
                player.get("substitute"),
                player.get("teamId"),
                player.get("teamName"),
                player.get("battingStyle"),
                player.get("bowlingStyle"),
                player.get("faceImageId"),
                group_name
            ))

    sql = """
    INSERT INTO match_players (
        match_id, player_id, name, full_name, nick_name, role,
        captain, keeper, substitute, team_id, team_name,
        batting_style, bowling_style, image_id, player_group
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.executemany(sql, all_players)
    conn.commit()
    print(f"✅ {len(all_players)} players inserted for match {match_id}")
    
    
def insert_batting_scorecard(match_id, innings_no, batting_list):
    records = []
    for b in batting_list:
        records.append((
            match_id,
            innings_no,
            b.get("batsmanId"),
            b.get("batsmanName"),
            b.get("runs"),
            b.get("balls"),
            b.get("fours"),
            b.get("sixes"),
            b.get("strikeRate"),
            b.get("outDesc")
        ))

    sql = """
    INSERT INTO batting_scorecard (
        match_id, innings_no, player_id, player_name,
        runs, balls, fours, sixes, strike_rate, dismissal
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.executemany(sql, records)
    conn.commit()
    print(f"✅ Inserted {len(records)} batting records for match {match_id}, innings {innings_no}")


def insert_bowling_scorecard(match_id, innings_no, bowling_list):
    records = []
    for bw in bowling_list:
        records.append((
            match_id,
            innings_no,
            bw.get("bowlerId"),
            bw.get("bowlerName"),
            bw.get("overs"),
            bw.get("maidens"),
            bw.get("runs"),
            bw.get("wickets"),
            bw.get("economy")
        ))

    sql = """
    INSERT INTO bowling_scorecard (
        match_id, innings_no, player_id, player_name,
        overs, maidens, runs_conceded, wickets, economy
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.executemany(sql, records)
    conn.commit()
    print(f"✅ Inserted {len(records)} bowling records for match {match_id}, innings {innings_no}")
    
    
    



# ---------------- FETCH FUNCTIONS ----------------



headers = {
    "x-rapidapi-key": "YOUR_KEY",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}


def fetch_live_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        matches = res.json().get("matches", [])
        for m in matches:
            insert_match(m, "live")  # store with match_type = 'live'
    else:
        print(f"❌ Error fetching live matches: {res.status_code}")


def fetch_upcoming_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        matches = res.json().get("matches", [])
        for m in matches:
            insert_match(m, "upcoming")  # store with match_type = 'upcoming'
    else:
        print(f"❌ Error fetching upcoming matches: {res.status_code}")


def fetch_recent_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        matches = res.json().get("matches", [])
        for m in matches:
            insert_match(m, "recent")  # store with match_type = 'recent'
    else:
        print(f"❌ Error fetching recent matches: {res.status_code}")


def fetch_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        matches = res.json().get("matches", [])
        for m in matches:
            insert_match(m)

def fetch_player(player_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        player_data = res.json()
        insert_player(player_data)
    else:
        print(f"❌ Error fetching player {player_id}: {res.status_code}")

def fetch_series():
    url = "https://cricbuzz-cricket.p.rapidapi.com/series/v1/international"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        series_list = res.json().get("seriesMapProto", [])
        for s in series_list:
            for series in s.get("series", []):
                insert_series(series)

def fetch_icc_rankings():
    categories = ["batsmen", "bowlers", "allrounders", "teams"]
    for cat in categories:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/rankings/{cat}"
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            ranks = res.json().get("rank", [])
            for r in ranks:
                r["category"] = cat  # add category
                insert_icc_rank(r)

            
def fetch_batting_stats(player_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/career"
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        career_data = res.json()
        batting_list = career_data.get("batting", [])
        for bat in batting_list:
            insert_batting_stats(player_id, bat)   # insert into MySQL
    
        
        
def fetch_bowling_stats(player_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/career"
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        career_data = res.json()
        bowling_list = career_data.get("bowling", [])
        for bowl in bowling_list:
            insert_bowling_stats(player_id, bowl)   # insert into MySQL
            

def fetch_match_players(match_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        players_section = data.get("matchTeam", {}).get("players", {})
        if players_section:
            insert_match_players(match_id, players_section)
    else:
        print(f"❌ Error fetching players for match {match_id}: {res.status_code}")


def fetch_match_scorecard(match_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/scard"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        innings_list = data.get("scorecard", [])
        for inn in innings_list:
            innings_no = inn.get("inningsId")

            # batting
            batting = list(inn.get("batTeamDetails", {}).get("batsmenData", {}).values())
            if batting:
                insert_batting_scorecard(match_id, innings_no, batting)

            # bowling
            bowling = list(inn.get("bowlTeamDetails", {}).get("bowlersData", {}).values())
            if bowling:
                insert_bowling_scorecard(match_id, innings_no, bowling)
    else:
        print(f"❌ Error fetching scorecard for match {match_id}: {res.status_code}")

    



# ---------------- MAIN RUNNER ----------------
if __name__ == "__main__":
    print("⚡ Fetching Matches...")
    fetch_live_matches()
    fetch_upcoming_matches()
    fetch_recent_matches()

    print("⚡ Fetching Players (profile + career stats)...")
    player_ids = [8733, 253802, 34102]  # example
    for pid in player_ids:
        fetch_player(pid)
        fetch_batting_stats(pid)
        fetch_bowling_stats(pid)

    print("⚡ Fetching Series...")
    fetch_series()

    print("⚡ Fetching ICC Rankings...")
    fetch_icc_rankings()

    print("⚡ Fetching Match Players + Scorecards...")
    # Example: run for a few recent match_ids
    match_ids = [12345, 67890]  # replace with real matchIds from DB
    for mid in match_ids:
        fetch_match_players(mid)
        fetch_match_scorecard(mid)

    print("✅ All data stored in MySQL Workbench!")

