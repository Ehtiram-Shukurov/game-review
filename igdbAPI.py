from igdb.wrapper import IGDBWrapper
from dotenv import load_dotenv
import requests
import json
import os
from igdb.igdbapi_pb2 import GameResult
from google.protobuf.json_format import MessageToDict

load_dotenv()

CLIENT_ID = os.environ.get("IGDB_CLIENT_ID")
ACCESS_TOKEN = os.environ.get("IGDB_ACCESS_TOKEN")

wrapper = IGDBWrapper(CLIENT_ID, ACCESS_TOKEN)


def get_game_id(name):
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


def data_extractor(data, search):
    res = []
    for modes in data:
        res.append(modes.get(search))
    return res


def get_game_data(name):
    #TODO handle failure gracefully, redirect to error page
    id = get_game_id(name)
    query = f"""
  fields name, storyline, genres.name, game_modes.name, player_perspectives.name, similar_games.name, summary, themes.name, cover.url, involved_companies.company.name, artworks.url;
  where id = {id};
  limit 1;
  """
    byte_array = wrapper.api_request("games.pb", query)
    games_message = GameResult()
    games_message.ParseFromString(byte_array)  # Fills the protobuf message object with the response
    games = games_message.games

    res = []
    # Loop through each game in the `RepeatedCompositeContainer`
    for game in games:
        # Convert each protobuf message to a dictionary
        game_dict = MessageToDict(game)
        res.append(game_dict)
    # artworksData = res[0].get("artworks")
    # name = data[0].get("name")
    name = res[0].get("name")
    cover_image = "http:" + res[0].get("cover").get("url")
    # all list below here
    cover_image_url = cover_image.replace("t_thumb", "t_720p")
    game_modes = data_extractor(res[0].get("gameModes"), "name")
    #genres = data_extractor(res[0].get("genres"), "name")
    # trust. this is ugly, but it was uglier
    companies = data_extractor(data_extractor(res[0].get("involvedCompanies"), "company"), "name")
    player_perspectives = data_extractor(res[0].get("playerPerspectives"), "name")
    similar_games = data_extractor(res[0].get("similarGames"), "name")
    storyline = res[0].get("storyline")
    summary = res[0].get("summary")
    themes = data_extractor(res[0].get("themes"), "name")
    data = {}
    data["game_id"] = id
    data["coverImageUrl"] = cover_image_url
    data["game_modes"] = game_modes
    #data["genres"] = genres
    data["companies"] = companies
    data["playerPerspectives"] = player_perspectives
    data["similarGames"] = similar_games
    data["storyline"] = storyline
    data["summary"] = summary
    data["themes"] = themes
    data["name"] = name
    return data


def broad_search(name, limit=99):
    query = f"""
    fields name;
    search "{name}";
    limit {limit};
  """
    response = wrapper.api_request('games', query)
    games = json.loads(response.decode('utf-8'))
    # list of dict
    return games

def game_search(name, limit=99):
    query = f"""
      fields name, summary, cover.url;
      search "{name}";
      limit {limit};
    """
    response = wrapper.api_request('games', query)
    games = json.loads(response.decode('utf-8'))
    # list of dict
    return games


def get_game_by_id(id):
    query = f"""
    fields name, summary, cover.url;
    where id = ({id});
    """
    response = wrapper.api_request('games', query)
    game = json.loads(response.decode('utf-8'))
    return game


def get_games_by_genre(genre):
    query = f"""
    fields name, summary, cover.url, genres;
    where genres = ({genre}) & rating > 90;
    limit 10;"""
    #popularity_primitives
    response = wrapper.api_request('games', query)
    games = json.loads(response.decode('utf-8'))
    return games


from datetime import datetime

def get_recent_games(limit=10):
    current_timestamp = int(datetime.now().timestamp())
    
    query = f"""
    fields name, cover.url, first_release_date;
    sort first_release_date desc;
    where first_release_date <= {current_timestamp};
    limit {limit};
    """
    
    response = wrapper.api_request('games', query)
    games = json.loads(response.decode('utf-8'))
    
    game_data = []
    for game in games:
        release_date = game.get("first_release_date")
        
        if release_date:
            release_date = int(release_date)
        game_info = {
            "name": game.get("name"),
            "id": game.get("id"),
            "cover": "http:" + game.get("cover", {}).get("url", "").replace("t_thumb", "t_cover_big"),
            "release_date": release_date
        }
        game_data.append(game_info)
    
    return game_data
