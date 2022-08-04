from re import L
import sqlite3
import requests
from sqlite3 import Error
from bs4 import BeautifulSoup

#SQLite query to create skins table
create_skins_table = """
CREATE TABLE IF NOT EXISTS skins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  CollectionID INT NOT NULL,
  Collection TEXT NOT NULL,
  WeaponType TEXT NOT NULL,
  SkinName TEXT NOT NULL,
  Rarity TEXT,
  FloatMin INT,
  FloatMax INT,
  Wear TEXT NOT NULL,
  statTrak INT NOT NULL,
  Price INT NOT NULL
);
"""
#SQLite query to create collections table
create_collections_table = """
CREATE TABLE IF NOT EXISTS collections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  CollectionName TEXT UNIQUE NOT NULL,
  CollectionCode TEXT UNIQUE NOT NULL
);

"""

def create_connection(path):
    '''Connects to or creates SQLite database at path
    Returns connection object to operate on database'''
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")

    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    '''Executes SQL query on connection'''
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def scrape_setup():
    '''Setup code for webscraping
    returns soup object'''
    #setup code for webscraping
    website = "https://counterstrike.fandom.com/wiki/Skins/List"
    result = requests.get(website)
    #200 means all website access is good
    print(result.status_code)
    src = result.content
    soup = BeautifulSoup(src, 'lxml')

    return soup

def get_collection_code(collection):
    '''Returns unique code needed for collection in Steam URL
    For now, the last accpeted case is the Recoil Case
    Needs to be manually updated
    '''
    #list of keys for each case up to Recoil Case
    codes = {
                #map collections
                'Ancient Collection': 'op10_ancient',
                'Assault Collection': 'assault',
                'Aztec Collection': 'aztec',
                'Baggage Collection': 'baggage',
                'Bank Collection': 'bank',
                'Blacksite Collection': 'blacksite',
                'Cache Collection': 'cache',
                'Canals Collection': 'canals',
                'Cobblestone Collection': 'cobblestone',
                'Dust Collection': 'dust',
                'Dust II Collection': 'dust_2',
                'Inferno Collection': 'inferno',
                'Italy Collection': 'italy',
                'Lake Collection': 'lake',
                'Militia Collection': 'militia',
                'Mirage Collection': 'mirage',
                'Nuke Collection': 'nuke',
                'Office Collection': 'office',
                'Overpass Collection': 'overpass',
                'Safehouse Collection': 'safehouse',
                'St. Marc Collection': 'stmarc',
                'Train Collection': 'train',
                'Vertigo Collection': 'vertigo',
                '2018 Inferno Collection': 'inferno_2',
                '2018 Nuke Collection': 'nuke_2',
                '2021 Dust II Collection': 'dust_2_2021',
                '2021 Mirage Collection': 'mirage_2021',
                '2021 Train Collection': 'train_2021',
                '2021 Vertigo Collection': 'vertigo_2021',

                #themed collections
                'Chop Shop Collection': 'chopshop',
                'Gods and Monsters Collection': 'gods_and_monsters',
                'Rising Sun Collection': 'kimono',
                'Alpha Collection': 'bravo_ii',
                'Norse Collection': 'norse',
                'Control Collection': 'op10_ct',
                'Havoc Collection': 'op10_t',

                #weapon case collections
                #Weapon Case = Arms Deal
                'CS:GO Weapon Case': 'weapons_i',
                'eSports 2013 Case': 'esports',
                'Operation Bravo Case': 'bravo_i',
                'CS:GO Weapon Case 2': 'weapons_ii',
                'Winter Offensive Weapon Case': 'community_1',
                'eSports 2013 Winter Case': 'esports_ii',
                'CS:GO Weapon Case 3': 'weapons_iii',
                'Operation Phoenix Weapon Case': 'community_2',
                'Huntsman Weapon Case': 'community_3',
                'Operation Breakout Weapon Case': 'community_4',
                'eSports 2014 Summer Case': 'esports_iii',
                'Operation Vanguard Weapon Case': 'community_5',
                'Chroma Case': 'community_6',
                'Chroma 2 Case': 'community_7',
                'Falchion Case': 'community_8',
                'Shadow Case': 'community_9',
                'Revolver Case': 'community_10',
                'Operation Wildfire Case': 'community_11',
                'Chroma 3 Case': 'community_12',
                'Gamma Case': 'community_13',
                'Gamma 2 Case': 'gamma_2',
                'Glove Case': 'community_15',
                'Spectrum Case': 'community_16',
                'Operation Hydra Case': 'community_17',
                'Spectrum 2 Case': 'community_18',
                'Clutch Case': 'community_19',
                'Horizon Case': 'community_20',
                'Danger Zone Case': 'community_21',
                'Prisma Case': 'community_22',
                'CS20 Case': 'community_24',
                'Shattered Web Case': 'community_23',
                'Prisma 2 Case': 'community_25',
                'Fracture Case': 'community_26',
                'Broken Fang Case': 'community_27',
                'Snakebite Case': 'community_28',
                'Operation Riptide Case': 'community_29',
                'Dreams & Nightmares Case': 'community_30',
                'Recoil Case': 'community_31'

                #not on wiki as of August 2022

                }

    return codes[collection]
    

def collection_update(connection):
    '''Add all collections to collection table if not already there'''
    #headers to be removed from collection
    headers = ['Collections', 'Map Collections', 'Themed Collections', 'Weapon Case Collections']

    soup = scrape_setup()

    #insert collection info into collection table if not exists
    for col in soup.find_all('span', {'class': 'mw-headline'}):
        collection_name = str(col.text)

        #skip over section headers
        if collection_name not in headers:
            key = get_collection_code(collection_name)
            
            #collection insert SQLite query
            collection_insert_query = f"""
            INSERT INTO collections (CollectionName, CollectionCode)
            VALUES ('{collection_name}', '{key}')
            """
            execute_query(connection, collection_insert_query)
        
def create_tables():
    '''Creates tables and updates collections to be used for skins updating'''
    connection = create_connection('CSGO.sqlite')
    execute_query(connection, create_collections_table)
    execute_query(connection, create_skins_table)
    collection_update(connection)

create_tables()