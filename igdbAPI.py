from igdb.wrapper import IGDBWrapper
from dotenv import load_dotenv  
import requests
import json
import os
from igdb.igdbapi_pb2 import GameResult

load_dotenv()  

CLIENT_ID = os.environ.get("CLIENT_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

wrapper = IGDBWrapper(CLIENT_ID,ACCESS_TOKEN)

def getGameID(name):
  query = f"""
  fields name;
  search "{name}";
  limit 1;
  """
  response = wrapper.api_request('games', query)
  games = json.loads(response.decode('utf-8'))

  if games:
    game_id = games[0]['id']

    return game_id
  else:
      print(f"No game found for '{name}'")
      return None
  
def getGameData(name):
  id = getGameID(name)
  query = f"""
  fields name, storyline, genres.name, game_modes.name, player_perspectives.name, similar_games.name, summary, themes.name, cover.url, involved_companies.company.name, artworks.url;
  where id = {id};
  limit 1;
  """
  byte_array = wrapper.api_request("games.pb",query)
  games_message = GameResult()
  games_message.ParseFromString(byte_array) # Fills the protobuf message object with the response
  games = games_message.games
  print(games)
  

game_name = "Cyberpunk 2077"
getGameData(game_name)




