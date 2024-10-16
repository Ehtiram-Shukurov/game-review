from db import get_game_by_id_database, save_game_data
from igdbAPI import get_game_by_id


def build_hierarchy(replies, parent_id=None):
    hierarchy = []
    for reply in replies:
        if reply['parent_id'] == int(parent_id):
            reply['replies'] = build_hierarchy(replies, reply['post_id'])
            hierarchy.append(reply)
    return hierarchy


def save_game(game_id):
    game = get_game_by_id_database(game_id)

    if game is None:
        game_data = get_game_by_id(game_id)
        print(game_data[0])
        save_game_data(game_data[0])

