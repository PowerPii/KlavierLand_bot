import json
import math
import random
import time

from utils import update_json


def max_exp(player: dict):
    return int(math.pow(10, player["game_level"] + 1))


def is_level_up(player: dict):
    if player["game_exp"] >= max_exp(player):
        return True
    else:
        return False


def dice(update, context):
    players = json.load(open("players_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username
    text = update.message.text.split(" ")

    bet_amount = "x"

    try:
        bet_amount = int(text[1]) if text[1].isnumeric() else "x"
    except IndexError:
        pass

    if chat_id in players.keys():
        player = players[chat_id]

        if len(text) == 2 and isinstance(bet_amount, int):
            if player["game_date"] < int(time.time()):
                if bet_amount not in range(1, 51):
                    over_bet_text = "<code>Bet must be between 1 and 50 quavers</code>"

                    context.bot.send_message(chat_id=groupchat_id, text=over_bet_text, parse_mode="HTML")

                elif player["quavers"] >= bet_amount:
                    player["game_date"] = int(time.time()) + 900
                    player_die_total, bot_die_total = 0, 0

                    for i in range(2):
                        player_die_total += random.randint(1, 6)
                    for i in range(2):
                        bot_die_total += random.randint(1, 6)

                    summary_text = f"<code>{username}\'s dice game summary\n</code>" \
                                   f"<code>-------------------------------\n</code>" \
                                   f"<code>Your total    : {player_die_total}\n</code>" \
                                   f"<code>Bot total     : {bot_die_total}\n</code>"

                    if player_die_total > bot_die_total:
                        winning = int(math.floor(bet_amount * player["game_increment"]))
                        player["game_exp"] += 1
                        player["quavers"] += winning

                        summary_text += f"<code>You win {winning} quavers!</code>\n"

                    elif player_die_total == bot_die_total:
                        summary_text += "<code>It\'s a tie\n</code>"

                    else:
                        player["quavers"] -= bet_amount

                        summary_text += f"<code>You lost {bet_amount} quavers\n</code>" \

                    quavers = player["quavers"]
                    game_exp = player["game_exp"]
                    game_level = player["game_level"]

                    summary_text += f"<code>-------------------------------\n</code>" \
                                    f"<code>Game level    : {game_level} ({game_exp}/{max_exp(player)})\n</code>" \
                                    f"<code>Total quavers : {quavers} quavers\n</code>"

                    context.bot.send_message(chat_id=groupchat_id, text=summary_text, parse_mode="HTML")
                else:
                    insufficient_amount_text = f"<code>\n{username} does not have enough quavers!\n</code>"

                    context.bot.send_message(chat_id=groupchat_id, text=insufficient_amount_text, parse_mode="HTML")
            else:
                game_duration_left = player["game_date"] - int(time.time())

                minutes = math.floor(game_duration_left / 60)
                seconds = game_duration_left % 60

                game_text = f"<code>{username}'s game cooldown duration : {minutes}:{str(seconds).zfill(2)}</code>"

                context.bot.send_message(chat_id=groupchat_id, text=game_text, parse_mode="HTML")
        else:
            format_error_text = f"<code>Error: wrong dice game format\n</code>" \
                                f"<code>Format : /dice amount</code>\n"

            context.bot.send_message(chat_id=groupchat_id, text=format_error_text, parse_mode="HTML")

        if is_level_up(player):
            player["game_exp"] -= max_exp(player)
            player["game_level"] += 1
            player["game_increment"] += 0.5

            game_level = player["game_level"]
            game_increment = player["game_increment"]

            level_up_text = f"<code>{username}'s game summary\n</code>" \
                            f"<code>--------------------------------\n</code>" \
                            f"<code>Game level increased to level {game_level}\n</code>" \
                            f"<code>Game multiplier is now {game_increment}</code>"

            context.bot.send_message(chat_id=groupchat_id, text=level_up_text, parse_mode="HTML")
        players[chat_id] = player
    else:
        unregistered_user_text = f"<code>{username} has no permission to play games\n</code>" \

        context.bot.send_message(chat_id=groupchat_id, text=unregistered_user_text, parse_mode="HTML")

    update_json("players_data.json", players)
