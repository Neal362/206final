import requests
import json
import os
import sqlite3

def main():
    if not os.path.isfile("Anime.db"):
        with open("Anime.db", 'x') as f:
            pass
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+"Anime.db")
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS MangaDex (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   manga_id TEXT NOT NULL,
                   title TEXT NOT NULL,
                   rating REAL,
                   users_rated INTEGER,
                   user_score REAL)''')

    cur.execute("SELECT COUNT(*) FROM MangaDex")
    numItems = cur.fetchone()[0]

    if numItems >= 25:
        print("MangaDex DB has at least 25 items, exiting")
        exit(0)

    dex_url = "https://api.mangadex.org"

    response = requests.get(f"{dex_url}/manga?limit=25&offset={numItems}")
    if response.status_code != 200:
        print(f"Error: got status code {response.status_code} when sending GET request to {dex_url}/manga?limit=25&offset={numItems}")
        exit(1)
    
    jsonData = json.loads(response.text)

    for item in jsonData["data"]:
        manga_id = item["id"]
        title = item["attributes"]["title"]["en"]

        detail_response = requests.get(f"{dex_url}/manga/{manga_id}")
        if detail_response.status_code != 200:
            continue

        detail_data = json.loads(detail_response.text)
        print(detail_data["data"]["attributes"]["title"])
        rating = detail_data["data"]["attributes"].get("rating", {}).get("bayesian", None)
        users_rated = detail_data["data"]["attributes"].get("users", {}).get("total", None)
        user_score = detail_data["data"]["attributes"].get("user_score", None)

        cur.execute("INSERT INTO MangaDex (manga_id, title, rating, users_rated, user_score) VALUES (?, ?, ?, ?, ?)", (manga_id, title, rating, users_rated, user_score))

    conn.commit()
    print("Added 25 entries to Anime.db. Please check the file and verify the results.")

if __name__ == '__main__':
    main()
