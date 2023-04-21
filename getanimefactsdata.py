import requests
import json
import os
import sqlite3
# Created by Neal Patel. Copyright Team NSU 2023

def main():
    #check for the existence of MangaDex database- if not, create it
    if not os.path.isfile("AnimeFacts.db"):
        with open("AnimeFacts.db", 'x') as f:
            pass 
    
# Open connection to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+"AnimeFacts.db")
    cur = conn.cursor()

#  # If table does not exist, create it
    cur.execute('''CREATE TABLE IF NOT EXISTS AnimeFacts (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   anime_title TEXT NOT NULL,
                   fact TEXT NOT NULL)''')
    
# Get number of rows in the table
    cur.execute("SELECT COUNT(*) FROM AnimeFacts")
    numItems = cur.fetchone()[0]

# If we have 25+ items, we're good
    if numItems >= 25:
        exit(0)

# Anime Facts API base URL
    facts_url = "https://chandan-02.github.io/anime-facts-rest-api/data.json"

#Fetch all Anime Facts
    response = requests.get(facts_url)
    if response.status_code != 200:
        exit(1)

    jsonData = json.loads(response.text)

# Iterate through the list of anime facts
    for fact_data in jsonData:
        anime_title = fact_data["title"]
        fact_text = fact_data["fact"]

# Insert data into AnimeFacts table
    cur.execute("INSERT INTO AnimeFacts (anime_title, fact) VALUES (?, ?)", (anime_title, fact_text))
    conn.commit()

if __name__ == '__main__':
    main()