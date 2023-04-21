import requests
import json
import os
import sqlite3
# Created by Justin Williams. Copyright Team NSU 2023

# Checks for necessary files MALClientID.txt, MyAnimeListIDs.txt, and Anime.db, gets the MAL Client ID.
# If Anime.db does not exist, this function will create it. If MALClientID or MyAnimeListIDs does not exist,
#   this function will exit with error.
# Inputs: None
# Outputs: MAL Client ID from MalClientID.txt
def getNecessaryFiles():
    # Check for existence of database - if not, create it
    if not os.path.isfile("Anime.db"):
        with open("Anime.db", 'x') as f:
            pass
    # Check for existence of Anime/Manga IDs file
    if not os.path.isfile("MyAnimeListIDs.txt"):
        exit("Cannot find MyAnimeListIDs.txt in current directory.")
    # Check for existence of MAL Client ID
    if not os.path.isfile("MALClientID.txt"):
        exit("Cannot find MALClientID.txt in current directory - if needed for testing, contact Justin Williams.")
    with open("MALClientID.txt", "r") as f:
        return f.read()

# Given a sqlite3 connection and cursor, sets up the necessary tables for Anime.db. If the tables already exist, nothing happens.
# Inputs: Connection object, Cursor object in reference to Anime.db.
# Outputs: Nothing.
def setUpTables(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Anime (id INTEGER PRIMARY KEY, title TEXT NOT NULL, rank INTEGER, popularity INTEGER, mean_score REAL, list_users INTEGER, scoring_users INTEGER, genre_id INTEGER, users_watching INTEGER, users_completed INTEGER, users_dropped INTEGER, users_plan_to_watch INTEGER)")
    # NOTE: Statistics like number of users with the media as completed/in progress/whatever is not returned by Manga search, so those fields are not in the Manga table
    cur.execute("CREATE TABLE IF NOT EXISTS Manga (id INTEGER PRIMARY KEY, title TEXT NOT NULL, rank INTEGER, popularity INTEGER, mean_score REAL, list_users INTEGER, scoring_users INTEGER, genre_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS Adaptations (anime_id INTEGER, manga_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS Genres (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
    conn.commit()

# Given a row number (0 to 111), returns the anime ID and manga IDs in a list.
# Inputs: Integer representing the desired row number (0 to 111).
# Outputs: a list of IDs for that row. The first element is an anime ID, and the rest of the elements are the corresponding Manga IDs.
def getIDsFromRow(rowNum):
    # First 2 rows of file's 114 are header, so add 2
    rowNum += 2
    try:
        with open("MyAnimeListIDs.txt", "r") as f:
            content = f.readlines()
            left, right = content[rowNum].strip().split(' - ')
            animeID = int(left)
            mangaIDs = [int(val) for val in right.split(',')]
            mangaIDs.insert(0, animeID)
            return mangaIDs
    except:
        exit(f"An error occured while trying to retrieve information from MyAnimeListIDs.txt at row {rowNum}")

# gets the Anime or Manga from MyAnimeList based on the ID and returns a dictionary from the JSON data the API gives.
# Inputs: ID (integer), isAnime (boolean), MAL Client ID (string)
# Outputs: Dictionary from the JSON data.
def getMediaFromMAL(ID, isAnime, clientID):
    url = f"https://api.myanimelist.net/v2/manga/{ID}?fields=title,rank,popularity,mean,num_list_users,num_scoring_users,genres"
    if isAnime:
        url = f"https://api.myanimelist.net/v2/anime/{ID}?fields=title,rank,popularity,mean,num_list_users,num_scoring_users,genres,statistics"
    response = requests.get(url, headers={"X-MAL-CLIENT-ID": clientID})
    if response.status_code == 401:
        exit("ERROR: invalid token provided, or access token expired. Exiting")
    elif response.status_code != 200:
        exit(f"Error: got error response code {response.status_code} from request {url}")
    # Valid response:
    jsonData = json.loads(response.text)
    return jsonData

# Attempts to add the genre (id, name) to the Genres table if it is unique.
# Inputs: ID (int), name (str), cursor object, connection object
# Outputs: Nothing.
def addToGenres(id, name, cur, conn):
    cur.execute("INSERT OR IGNORE INTO Genres VALUES (?,?)", (id, name))
    conn.commit()

# Fills the Adaptations table with the anime-manga adaptation relationships based on MyAnimeListIDs.txt.
# Inputs: Cursor object, Connection object
# Outputs: Nothing.
def fillAdaptationTable(cur, conn):
    for i in range(0, 112):
        ids = getIDsFromRow(i)
        for j in range(1,len(ids)):
            cur.execute("INSERT INTO Adaptations VALUES (?,?)", (ids[0], ids[j]))
    conn.commit()

def main():
    # Hard coded ID lists are OK according to professor
    animeIDs = [3588, 39940, 6, 22535, 31240, 28171, 530, 20, 21, 31765, 48661, 30, 33, 550, 1575, 43, 6702, 5680, 39486, 30276, 33352, 37450, 40028, 37981, 20583, 37991, 37999, 11887, 7791, 16498, 38000, 2167, 120, 121, 36474, 32379, 38524, 36475, 34944, 31374, 37520, 37521, 36511, 25777, 28851, 22199, 31933, 9919, 34497, 39617, 1735, 15051, 23755, 2251, 33486, 31964, 223, 35557, 23273, 235, 245, 35062, 31478, 24833, 34561, 34566, 49926, 269, 32526, 34577, 1818, 39195, 13601, 4898, 38691, 34599, 40748, 22319, 28977, 11061, 31043, 849, 4437, 2904, 31580, 1887, 356, 19815, 24439, 21881, 889, 14719, 16782, 37779, 918, 6045, 20899, 2472, 38826, 35760, 2994, 32182, 42938, 30654, 36296, 35790, 28623, 38883, 33255, 11757, 5114, 1535]
    mangaIDs = [2, 11, 12, 13, 90125, 3083, 113163, 21, 5655, 96792, 25, 26, 67617, 51747, 1061, 2598, 42, 25132, 44, 33327, 54, 36413, 123968, 583, 83019, 587, 598, 92, 1630, 105573, 102, 86129, 98930, 1658, 48251, 97916, 107645, 642, 98462, 13492, 36535, 698, 45757, 703, 12994, 13001, 49865, 715, 99529, 56529, 75989, 81117, 735, 70399, 61189, 48399, 103701, 3866, 60703, 100128, 91941, 103727, 3378, 87866, 44347, 24380, 1342, 37707, 103244, 336, 6997, 23390, 872, 82795, 60783, 37755, 44933, 908, 401, 39325, 90531, 35243, 3006, 3008, 3009, 44485, 96200, 74697, 44489, 39883, 103897, 56805, 21479, 95210, 1517, 113138, 1528, 96765, 96766, 1023]
    clientID = getNecessaryFiles()
    # Open connection to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+"Anime.db")
    cur = conn.cursor()
    setUpTables(cur, conn)
    # Get number of rows in Anime table
    cur.execute("SELECT COUNT(*) FROM Anime")
    numAnime = cur.fetchone()[0]
    # If we haven't gathered any data yet, fill adaptations table (no API calls needed)
    if numAnime == 0:
        fillAdaptationTable(cur, conn)
    # File contains 112 animes
    animeNeeded = 112 - numAnime
    itemsObtained = 0
    # Get anime
    while animeNeeded > 0:
        if itemsObtained == 25:
            conn.commit()
            print("Gathered maximum of 25 items, exiting")
            exit(0)
        # Get next anime ID
        animeID = animeIDs[numAnime]
        # Get anime data from API
        jsonData = getMediaFromMAL(animeID, True, clientID)
        # Insert data into database
        cur.execute("INSERT INTO Anime VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (animeID,jsonData["title"],jsonData["rank"],jsonData["popularity"],jsonData["mean"],jsonData["num_list_users"],jsonData["num_scoring_users"],jsonData["genres"][0]["id"],jsonData["statistics"]["status"]["watching"],jsonData["statistics"]["status"]["completed"],jsonData["statistics"]["status"]["dropped"],jsonData["statistics"]["status"]["plan_to_watch"]))
        addToGenres(jsonData["genres"][0]["id"],jsonData["genres"][0]["name"],cur,conn)
        # Increment numAnime, itemsObtained and decrement animeNeeded
        numAnime += 1
        itemsObtained += 1
        animeNeeded -= 1
    if itemsObtained == 25:
        conn.commit()
        print("Gathered maximum of 25 items, exiting")
        exit(0)
    # Get number of rows in Manga table
    cur.execute("SELECT COUNT(*) FROM Manga")
    numManga = cur.fetchone()[0]
    # File contains 100 Manga
    mangaNeeded = 100 - numManga
    # Get manga
    while mangaNeeded > 0:
        if itemsObtained == 25:
            conn.commit()
            print("Gathered maximum of 25 items, exiting")
            exit(0)
        # Get next manga ID
        mangaID = mangaIDs[numManga]
        # Get manga data from API
        jsonData = getMediaFromMAL(mangaID, False, clientID)
        # Insert data into database
        # NOTE: Two mangas do not have user scores recorded for them. These manga will instead have mean score "0".
        cur.execute("INSERT INTO Manga VALUES (?,?,?,?,?,?,?,?)", (mangaID,jsonData["title"],jsonData["rank"],jsonData["popularity"],jsonData.get("mean", 0),jsonData["num_list_users"],jsonData["num_scoring_users"],jsonData["genres"][0]["id"]))
        addToGenres(jsonData["genres"][0]["id"],jsonData["genres"][0]["name"],cur,conn)
        # Increment numManga, itemsObtained and decrement mangaNeeded
        numManga += 1
        itemsObtained += 1
        mangaNeeded -= 1
    print("Finished gathering all items, MAL database is complete! Exiting")
    exit(0)
if __name__ == '__main__':
    main()