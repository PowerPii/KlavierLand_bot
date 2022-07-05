import json
import math
import time

from utils import update_json


def max_exp(player: dict):
    return int(math.pow(2, player["practice_level"]))


def is_level_up(player: dict):
    if player["practice_exp"] >= max_exp(player):
        return True
    else:
        return False


def practice(update, context):
    players = json.load(open("players_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username

    if chat_id in players.keys():
        player = players[chat_id]

        if player["practice_date"] < int(time.time()):
            player["practice_exp"] += 1
            player["practice_date"] = int(time.time()) + 60

        if is_level_up(player):
            player["practice_exp"] -= max_exp(player)
            player["practice_level"] += 1

            practice_level = player["practice_level"]

            level_up_text = f"<code>{username}'s practice summary\n</code>" \
                            f"<code>--------------------------------\n</code>" \
                            f"<code>Practice level increased to level {practice_level}\n</code>"

            context.bot.send_message(chat_id=groupchat_id, text=level_up_text, parse_mode="HTML")
        players[chat_id] = player

    update_json("players_data.json", players)
