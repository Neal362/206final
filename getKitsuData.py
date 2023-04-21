import requests
import json
import os
import sqlite3
# Created by Justin Williams. Copyright Team NSU 2023

# Checks for necessary files MALtoKitsu.txt and Anime.db.
# If either file does not exist or Anime.db has not yet been filled by getMALData.py,
# this function will exit with error.
# Inputs: None
# Outputs: None
def getNecessaryFiles():
    # Check for existence of Anime database
    if not os.path.isfile("Anime.db"):
        exit("Cannot find anime database Anime.db in current directory.")
    # Check for existence of MAL Anime ID to Kitsu Anime ID mapping file
    if not os.path.isfile("MALtoKitsu.txt"):
        exit("Cannot find MALtoKitsu.txt in current directory.")
    # Check for Anime database not populated
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+"Anime.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Manga")
    numItems = cur.fetchone()[0]
    if numItems < 100:
        exit("Anime database is not filled- please run getMALData.py first and ensure all items are added!")
# Given a row number (0 to 111), returns the MAL and Kitsu IDs as a tuple.
# Inputs: Integer representing the desired row number (0 to 111).
# Outputs: Tuple (MALID, KitsuID)
def getIDsFromRow(rowNum):
    # First 2 rows of file's 114 are header, so add 2
    rowNum += 2
    try:
        with open("MALtoKitsu.txt", "r") as f:
            content = f.readlines()
            left, right = content[rowNum].strip().split(' - ')
            malID = int(left)
            kitsuID = int(right)
            return (malID, kitsuID)
    except:
        exit(f"An error occured while trying to retrieve information from MALtoKitsu.txt at row {rowNum}")

def main():
    getNecessaryFiles()
    # Open connection to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+"Anime.db")
    cur = conn.cursor()
    # If table does not exist, create it
    cur.execute("CREATE TABLE IF NOT EXISTS Kitsu (id INTEGER PRIMARY KEY, average_rating REAL, num_users INTEGER, num_favorites INTEGER, popularity_rank INTEGER, rating_rank INTEGER)")
    # Get number of rows in table
    cur.execute("SELECT COUNT(*) FROM Kitsu")
    numItems = cur.fetchone()[0]
    # at 112, db full
    if numItems >= 112:
        print("Kitsu DB already contains all 112 items, exiting!")
        exit(0)
    # Otherwise, we need to collect more items, capped at 25 more
    itemsToGet = min(25, 112 - numItems)
    # Attempt to get more items from Kitsu - NOTE: Kitsu maximum page size is 20
    obtained = 0
    while itemsToGet > 0:
        idTuple = getIDsFromRow(numItems)
        animeID = idTuple[1]
        malID = idTuple[0]
        response = requests.get(f"https://kitsu.io/api/edge/anime/{animeID}")
        if response.status_code != 200:
            print(f"Error: got status code {response.status_code} when sending GET request to https://kitsu.io/api/edge/anime/{animeID}")
            exit(1)
        jsonData = json.loads(response.text)["data"]["attributes"]
        cur.execute("INSERT INTO Kitsu VALUES (?,?,?,?,?,?)", (malID,jsonData["averageRating"],jsonData["userCount"],jsonData["favoritesCount"],jsonData["popularityRank"],jsonData["ratingRank"]))
        numItems += 1
        itemsToGet -= 1
        obtained += 1
    conn.commit()
    print(f"Added {obtained} entries to Anime.db. Please check the file and verify the results.")
if __name__ == '__main__':
    main()