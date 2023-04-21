import requests
import json
import os
import sqlite3
# Created by Neal Patel. Copyright Team NSU 2023

def main():
    #check for the existence of MangaDex database- if not, create it
    if not os.path.isfile("MangaDex.db"):
        with open("MangaDex.db", 'x') as f:
            pass 
    # Open connection to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+"MangaDex.db")
    cur = conn.cursor()

    #if table does not exist create it
    cur.execute('''CREATE TABLE IF NOT EXISTS MangaDex (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   manga_id TEXT NOT NULL,
                   title TEXT NOT NULL,
                   rating REAL,
                   users_rated INTEGER)''')

   # Get number of rows in the table
    cur.execute("SELECT COUNT(*) FROM MangaDex")
    numItems = cur.fetchone()[0]

    # If we have 25+ items, we're good
    if numItems >= 25:
        print("MangaDex DB has at least 25 items, exiting")
        exit(0)

    # MangaDex API base URL
    dex_url = "https://api.mangadex.org"

    # Fetch the next 25 manga list items
    response = requests.get(f"{dex_url}/manga?limit=25&offset={numItems}")
    if response.status_code != 200:
        print(f"Error: got status code {response.status_code} when sending GET request to {dex_url}/manga?limit=25&offset={numItems}")
        exit(1)
    
    jsonData = json.loads(response.text)

    # Iterate through the "data" list in the JSON response
    for item in jsonData["data"]:
        manga_id = item["id"]
        title = item["attributes"]["title"]["en"]

    # Fetch manga details for rating and statistics
        detail_response = requests.get(f"{dex_url}/manga/{manga_id}")
        if detail_response.status_code != 200:
            continue

    detail_data = json.loads(detail_response.text)
    rating = detail_data["data"]["attributes"]["rating"]["bayesian"]
    users_rated = detail_data["data"]["attributes"]["users"]["total"]

    # Insert data into MangaDex table
    cur.execute("INSERT INTO MangaDex (manga_id, title, rating, users_rated) VALUES (?, ?, ?, ?)", (manga_id, title, rating, users_rated))

    conn.commit()
    print("Added 100 entries to MangaDex.db. Please check the file and verify the results.")

if __name__ == '__main__':
    main()