import os
from steam_web_api import Steam
from dotenv import load_dotenv  
import requests
import json
load_dotenv()  

KEY = os.environ.get("STEAM_KEY")

steam = Steam(KEY)


def steamSearch(name):
    """
    Sample output of code
    
    The code wil return all items in the steam store that matches the given input
    
    so if the input was terra
    
    the code will return items such Terraria, Starship Troopers: Terran Command, Terra Invicta
    
    very similar when using the search bar in the steam store page
    
    could recreate the search bar feature with this output
    
    
    {
  "apps": [
    {
      "id": 105600,
      "link": "https://store.steampowered.com/app/105600/Terraria/?snr=1_7_15__13",
      "name": "Terraria",
      "img": "https://cdn.akamai.steamstatic.com/steam/apps/105600/capsule_sm_120.jpg?t=1590092560",
      "price": "$9.99"
    },
    {
      "id": 1202130,
      "link": "https://store.steampowered.com/app/1202130/Starship_Troopers_Terran_Command/?snr=1_7_15__13",
      "name": "Starship Troopers: Terran Command",
      "img": "https://cdn.akamai.steamstatic.com/steam/apps/1202130/capsule_sm_120.jpg?t=1657104501",
      "price": "$29.99"
    },
    {
      "id": 1176470,
      "link": "https://store.steampowered.com/app/1176470/Terra_Invicta/?snr=1_7_15__13",
      "name": "Terra Invicta",
      "img": "https://cdn.akamai.steamstatic.com/steam/apps/1176470/capsule_sm_120.jpg?t=1659933796",
      "price": ""
    },
    {
      "id": 1945600,
      "link": "https://store.steampowered.com/app/1945600/The_Riftbreaker_Metal_Terror/?snr=1_7_15__13",
      "name": "The Riftbreaker: Metal Terror",
      "img": "https://cdn.akamai.steamstatic.com/steam/apps/1945600/capsule_sm_120.jpg?t=1659109312",
      "price": "$9.99"
    },
    {
      "id": 285920,
      "link": "https://store.steampowered.com/app/285920/TerraTech/?snr=1_7_15__13",
      "name": "TerraTech",
      "img": "https://cdn.akamai.steamstatic.com/steam/apps/285920/capsule_sm_120.jpg?t=1644900341",
      "price": "$24.99"
    }
  ]
}
    """
    return steam.apps.search_games(name)

def getGameID(name):
    """
    assuming the user has selected a game name with the full game title
    """
    searchResults = steamSearch(name)
    for data in searchResults.get("apps"):
        if data['name'].lower() == name.lower():
            return data['id'][0]
    



def getGameData(gameID):

    data= steam.apps.get_app_details(gameID)
    #cleanData = data.get(str(gameID)).get("data")
    #print(cleanData.get("name"))
    #print(cleanData.get("about_the_game"))
    #print(cleanData.get("short_description"))
    #print(cleanData.get("header_image"))
    #print(cleanData.get("dlc"))
    #a = steamSearch(str(gameID))
    #print(a)


#"genres","screenshots","recommendations","developers","price_overview"

getGameData(1172470)