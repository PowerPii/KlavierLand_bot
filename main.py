import bank
import credentials as keys
import datetime
import games
import json
import practice
import performance
import time

from telegram.ext import *
from utils import update_json


def register(update, context):
    players = json.load(open("players_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username

    if chat_id not in players.keys():
        player = {"username": username, "practice_exp": 0, "practice_level": 0, "performance_exp": 0,
                  "performance_level": 0, "game_exp": 0, "game_level": 0, "quavers": 0, "performance_increment": 0,
                  "game_increment": 1.0, "performance_date": int(time.time()), "practice_date": int(time.time()),
                  "game_date": int(time.time()), "is_performing": False}

        players[chat_id] = player

        new_member_text = f"<code>Welcome {username} to Klavier Land!\n</code>" \
                          "<code>Please enjoy your stay here!</code>"

        context.bot.send_message(chat_id=groupchat_id, text=new_member_text, parse_mode="HTML")
    else:
        registered_text = f"<code>Error: {username} is already in the database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=registered_text, parse_mode="HTML")
    update_json("players_data.json", players)


def help(update, context):
    groupchat_id = update.message.chat.id

    help_text = "<code>Basic Command\n</code>" \
                "<code>/register : Compulsory command to register yourself into the community\n</code>" \
                "<code>/help     : Check for all available commands\n</code>" \
                "<code>/stats    : Display your current statistics\n</code>" \
                "<code>--------------------------------\n</code>" \
                "<code>Performance Command\n</code>" \
                "<code>/perform  : Perform to earn quavers, the currency in Klavier Land\n</code>" \
                "<code>/collect  : Collect your quavers from performance\n</code>" \
                "<code>/donate   : Donate your quavers to other member in the community\n</code>" \
                "<code>            /donate @member amount\n</code>" \
                "<code>--------------------------------\n</code>" \
                "<code>Game Command\n</code>" \
                "<code>/dice     : Roll dice against the bot\n</code>" \
                "<code>            /dice amount\n</code>" \
                "<code>--------------------------------\n</code>" \
                "<code>Bank Command\n</code>" \
                "<code>/open     : Open bank account\n</code>" \
                "<code>/account  : Check account status\n</code>" \
                "<code>/stock    : Check stock account status\n</code>" \
                "<code>/deposit  : Deposit quavers into your account\n</code>" \
                "<code>            /deposit amount\n</code>" \
                "<code>/withdraw : Withdraw quavers out your account\n</code>" \
                "<code>            /withdraw amount\n</code>" \
                "<code>/transfer : Transfer quavers to other recipients\n</code>" \
                "<code>            /donate @recipients amount\n</code>" \
                "<code>/market   : Check current stocks price\n</code>" \
                "<code>/invest   : Invest your quavers to buy stocks\n</code>" \
                "<code>            /invest amount\n</code>" \
                "<code>/sell     : Sell your stocks\n</code>" \
                "<code>            /sell amount\n</code>"

    context.bot.send_message(chat_id=groupchat_id, text=help_text, parse_mode="HTML")


def stats(update, context):
    players = json.load(open("players_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username

    if chat_id in players.keys():
        player = players[chat_id]

        practice_exp = player["practice_exp"]
        practice_level = player["practice_level"]
        performance_exp = player["performance_exp"]
        performance_level = player["performance_level"]
        game_exp = player["game_exp"]
        game_level = player["game_level"]
        quavers = player["quavers"]

        stats_text = f"<code>{username}'s statistics\n</code>" \
                     f"<code>--------------------------------\n</code>" \
                     f"<code>Practice level    : {practice_level} " \
                     f"({int(practice_exp)}/{practice.max_exp(player)})\n</code>" \
                     f"<code>Performance level : {performance_level} " \
                     f"({performance_exp}/{performance.max_exp(player)})\n</code>" \
                     f"<code>Game level        : {game_level} ({game_exp}/{games.max_exp(player)})\n</code>" \
                     f"<code>Total quavers     : {quavers} quavers</code>"

        context.bot.send_message(chat_id=groupchat_id, text=stats_text, parse_mode="HTML")


def error(update, context):
    print(f"Update {update} caused error\n{context.error}.")


def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    jq = updater.job_queue
    jq.run_daily(bank.give_interest, time=datetime.time(hour=16, minute=00, second=00), days=(0, 1, 2, 3, 4, 5, 6))

    dp.add_handler(CommandHandler("register", register))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_error_handler(error)

    dp.add_handler(CommandHandler("perform", performance.perform))
    dp.add_handler(CommandHandler("collect", performance.collect))
    dp.add_handler(CommandHandler("donate", performance.donate))

    dp.add_handler(CommandHandler("open", bank.open_account))
    dp.add_handler(CommandHandler("account", bank.account_summary))
    dp.add_handler(CommandHandler("stock", bank.stock_summary))
    dp.add_handler(CommandHandler("deposit", bank.deposit))
    dp.add_handler(CommandHandler("withdraw", bank.withdraw))
    dp.add_handler(CommandHandler("transfer", bank.transfer))
    dp.add_handler(CommandHandler("market", bank.market))
    dp.add_handler(CommandHandler("invest", bank.invest))
    dp.add_handler(CommandHandler("sell", bank.sell))

    dp.add_handler(CommandHandler("dice", games.dice))

    dp.add_handler(MessageHandler(Filters.text, practice.practice))

    updater.start_polling()
    jq.start()
    updater.idle()


if __name__ == "__main__":
    print("Bot started...")

    main()
