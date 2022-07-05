import json
import math
import time

from utils import update_json, get_key_from_attribute


def max_exp(player: dict):
    return int(2 * (player["performance_level"] + 1))


def is_level_up(player: dict):
    if player["performance_exp"] >= max_exp(player):
        return True
    else:
        return False


def perform(update, context):
    players = json.load(open("players_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username

    if chat_id in players.keys():
        player = players[chat_id]

        performance_text = f"<code>{username}'s performance summary</code>\n" \
                           f"<code>--------------------------------</code>\n"

        if player["performance_date"] <= int(time.time()):
            if player["is_performing"] is False:
                player["performance_date"] = int(time.time()) + 3600
                player["is_performing"] = True

                performance_text += f"<code>Performance status : started</code>\n" \
                                    f"<code>Duration left      : 60:00 mins</code>\n"
            else:
                player["performance_date"] = int(time.time()) + 3600
                player["is_performing"] = True

                player["performance_exp"] += 1
                total_quavers = 10 + player["performance_increment"]
                player["quavers"] += total_quavers

                performance_text += f"<code>Performance status : repeat</code>\n" \
                                    f"<code>Quavers gained     : {total_quavers} quavers</code>\n"
        else:
            performance_duration_left = player["performance_date"] - int(time.time())

            minutes = math.floor(performance_duration_left / 60)
            seconds = performance_duration_left % 60

            performance_text += f"<code>Performance status : ongoing</code>\n" \
                                f"<code>Duration left      : {minutes}:{seconds:02} mins</code>\n"

        performance_exp = player["performance_exp"]
        performance_level = player["performance_level"]
        quavers = player["quavers"]

        performance_text += f"<code>--------------------------------</code>\n" \
                            f"<code>Performance level  : {performance_level} " \
                            f"({performance_exp}/{max_exp(player)})\n</code>" \
                            f"<code>Total Quavers      : {quavers} quavers</code>"

        context.bot.send_message(chat_id=groupchat_id, text=performance_text, parse_mode="HTML")

        if is_level_up(player):
            player["performance_exp"] -= max_exp(player)
            player["performance_level"] += 1
            player["performance_increment"] += 2

            performance_level = player["performance_level"]
            performance_increment = player["performance_increment"]

            level_up_text = f"<code>{username}'s performance summary\n</code>" \
                            f"<code>--------------------------------\n</code>" \
                            f"<code>Performance level increased to level {performance_level}\n</code>" \
                            f"<code>Performance now grants {10 + performance_increment} quavers</code>"

            context.bot.send_message(chat_id=groupchat_id, text=level_up_text, parse_mode="HTML")

        players[chat_id] = player
    else:
        unregistered_user_text = f"<code>{username} is not found in community database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=unregistered_user_text, parse_mode="HTML")

    update_json("players_data.json", players)


def collect(update, context):
    players = json.load(open("players_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username

    if chat_id in players.keys():
        player = players[chat_id]

        performance_text = f"<code>{username}'s performance summary</code>\n" \
                           f"<code>--------------------------------</code>\n"
        if player["performance_date"] <= int(time.time()):
            if player["is_performing"] is False:
                performance_text = f"Performance status : stalled\n"

                context.bot.send_message(chat_id=groupchat_id, text=performance_text)
            else:
                players["performance_date"] = int(time.time()) + 3600
                player["is_performing"] = False

                player["performance_exp"] += 1
                total_quavers = 10 + player["performance_increment"]
                player["quavers"] += total_quavers

                performance_text += f"<code>Performance status : successful</code>\n" \
                                    f"<code>Quavers gained     : {total_quavers} quavers</code>\n"

        else:
            performance_duration_left = player["performance_date"] - int(time.time())

            minutes = math.floor(performance_duration_left / 60)
            seconds = performance_duration_left % 60

            performance_text += f"<code>Performance status : ongoing</code>\n" \
                                f"<code>Duration left      : {minutes}:{seconds:02} mins</code>\n"

        performance_exp = player["performance_exp"]
        performance_level = player["performance_level"]
        quavers = player["quavers"]

        performance_text += f"<code>--------------------------------</code>\n" \
                            f"<code>Performance level  : {performance_level} " \
                            f"({performance_exp}/{max_exp(player)})\n</code>" \
                            f"<code>Total Quavers      : {quavers} quavers</code>"

        context.bot.send_message(chat_id=groupchat_id, text=performance_text, parse_mode="HTML")

        if is_level_up(player):
            player["performance_exp"] -= max_exp(player)
            player["performance_level"] += 1
            player["performance_increment"] += 2

            performance_level = player["performance_level"]
            performance_increment = player["performance_increment"]

            level_up_text = f"<code>{username}'s performance summary\n</code>" \
                            f"<code>--------------------------------\n</code>" \
                            f"<code>Performance level increased to level {performance_level}</code>" \
                            f"<code>Performance now grants {10 + performance_increment} quavers</code>"

            context.bot.send_message(chat_id=groupchat_id, text=level_up_text, parse_mode="HTML")
        players[chat_id] = player
    else:
        unregistered_user_text = f"<code>{username} not found in community database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=unregistered_user_text, parse_mode="HTML")

    update_json("players_data.json", players)


def donate(update, context):
    players = json.load(open("players_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username
    text = update.message.text.split(" ")

    other_player_username, donation_amount, other_player_chat_id = "x", "x", "x"

    try:
        other_player_username = text[1][1:]
        donation_amount = int(text[2]) if text[2].isnumeric() else "x"
        other_player_chat_id = get_key_from_attribute("players_data.json", "username", other_player_username)
    except IndexError:
        pass

    if chat_id in players.keys() and other_player_chat_id in players.keys():
        if len(text) == 3 and "@" in text[1] and isinstance(donation_amount, int):
            player = players[chat_id]
            other_player = players[other_player_chat_id]

            if donation_amount <= player["quavers"]:
                player["quavers"] -= donation_amount
                other_player["quavers"] += donation_amount

                quavers = player["quavers"]

                donation_text = f"<code>{username}'s donation summary\n</code>" \
                                f"<code>-------------------------------\n</code>" \
                                f"<code>Receiver          : {other_player_username}\n</code>" \
                                f"<code>Donation amount   : {donation_amount}\n</code>" \
                                f"<code>-------------------------------\n</code>" \
                                f"<code>Available quavers : {quavers} quavers</code>" \

                context.bot.send_message(chat_id=groupchat_id, text=donation_text, parse_mode="HTML")

            else:
                insufficient_text = f"<code>{username} has insufficient amount to donate</code>"

                context.bot.send_message(chat_id=groupchat_id, text=insufficient_text, parse_mode="HTML")

            players[chat_id] = player
            players[other_player_chat_id] = other_player

        else:
            format_error_text = f"<code>Error : Wrong donation format\n</code>" \
                                f"<code>Format: /donate @member amount</code>"

            context.bot.send_message(chat_id=groupchat_id, text=format_error_text, parse_mode="HTML")
    else:
        if chat_id not in players.keys():
            unregistered_text = f"<code>{username} not found in community database</code>"

            context.bot.send_message(chat_id=groupchat_id, text=unregistered_text, parse_mode="HTML")
        if other_player_chat_id not in players.keys():
            unregistered_text = f"<code>{other_player_username} is not found in community database</code>"

            context.bot.send_message(chat_id=groupchat_id, text=unregistered_text, parse_mode="HTML")

    update_json("players_data.json", players)
