import json

from utils import get_crypto_price, get_key_from_attribute, get_stock_value, update_json


def open_account(update, context):
    recipients = json.load(open("bank_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username

    if chat_id not in recipients.keys():
        recipient = {"username": username,
                     "quavers": 0,
                     "stocks": 0,
                     "total_buy": 0,
                     "total_sell": 0,
                     "buy_quantity": 0,
                     "sell_quantity": 0}

        new_recipient_text = f"<code>{username}'s account summary\n</code>" \
                             "<code>--------------------------------\n</code>" \
                             f"<code>Account summary : opened \n</code>"

        context.bot.send_message(chat_id=groupchat_id, text=new_recipient_text, parse_mode="HTML")

        recipients[chat_id] = recipient
    else:
        registered_text = f"<code>{username} is already in the bank database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=registered_text, parse_mode="HTML")
    update_json("bank_data.json", recipients)


def account_summary(update, context):
    recipients = json.load(open("bank_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username

    if chat_id in recipients.keys():
        recipient = recipients[chat_id]

        quavers_at_bank = recipient["quavers"]
        stocks = recipient["stocks"]

        stock_value = get_stock_value(stocks)

        account_summary_text = f"<code>{username}'s account summary\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Quavers at bank : {quavers_at_bank} quavers\n</code>" \
                               f"<code>Stock value     : {stock_value} quavers\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Total assets    : {quavers_at_bank + stock_value} quavers\n</code>"

        context.bot.send_message(chat_id=groupchat_id, text=account_summary_text, parse_mode="HTML")
    else:
        registered_text = f"<code>{username} is not found in the bank database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=registered_text, parse_mode="HTML")


def stock_summary(update, context):
    recipients = json.load(open("bank_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username

    if chat_id in recipients.keys():
        recipient = recipients[chat_id]

        stocks = recipient["stocks"]
        total_buy = recipient["total_buy"]
        buy_quantity = recipient["buy_quantity"]
        total_sell = recipient["total_sell"]
        sell_quantity = recipient["sell_quantity"]
        stock_value = get_stock_value(stocks)
        stock_price = get_crypto_price()

        average_buy = 0
        average_sale = 0

        try:
            average_buy = total_buy/buy_quantity
            average_sale = total_sell/sell_quantity
        except ZeroDivisionError:
            pass

        r_pnl = (average_sale-average_buy)*sell_quantity
        ur_pnl = (stock_price-average_buy)*stocks

        account_summary_text = f"<code>{username}'s stock summary\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Stock amount   : {stocks} unit(s)\n</code>" \
                               f"<code>Stock value    : {stock_value} quavers\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Realised PNL   : {int(r_pnl)} quavers\n</code>" \
                               f"<code>Unrealised PNL : {int(ur_pnl)} quavers</code>"

        context.bot.send_message(chat_id=groupchat_id, text=account_summary_text, parse_mode="HTML")
    else:
        registered_text = f"<code>{username} is not found in the bank database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=registered_text, parse_mode="HTML")


def deposit(update, context):
    recipients = json.load(open("bank_data.json"))
    players = json.load(open("players_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username
    text = update.message.text.split(" ")

    deposit_amount = "x"

    try:
        deposit_amount = int(text[1]) if text[1].isnumeric() else "x"
    except IndexError:
        pass

    if chat_id in recipients.keys():
        recipient = recipients[chat_id]
        player = players[chat_id]

        if len(text) == 2 and deposit_amount != "x":
            if player["quavers"] >= deposit_amount:
                recipient["quavers"] += deposit_amount
                player["quavers"] -= deposit_amount

                quavers_at_bank = recipient["quavers"]
                quavers_in_hand = player["quavers"]

                summary_text = f"<code>{username}'s account summary\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Deposit amount    : {deposit_amount} quavers\n</code>" \
                               f"<code>Available Balance : {quavers_at_bank} quavers\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Quavers in hand   : {quavers_in_hand} quavers</code>"

                context.bot.send_message(chat_id=groupchat_id, text=summary_text, parse_mode="HTML")
            else:
                insufficient_amount_text = f"<code>\n{username} has insufficient quavers to deposit\n</code>"

                context.bot.send_message(chat_id=groupchat_id, text=insufficient_amount_text, parse_mode="HTML")
        else:
            format_error_text = f"<code>Error: wrong deposit format\n</code>" \
                                f"<code>Format : /deposit amount</code>\n"

            context.bot.send_message(chat_id=groupchat_id, text=format_error_text, parse_mode="HTML")
        recipients[chat_id] = recipient
    else:
        unregistered_user_text = f"<code>{username} is not found in the bank database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=unregistered_user_text, parse_mode="HTML")

    update_json("players_data.json", players)
    update_json("bank_data.json", recipients)


def withdraw(update, context):
    recipients = json.load(open("bank_data.json"))
    players = json.load(open("players_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username
    text = update.message.text.split(" ")

    withdrawal_amount = "x"

    try:
        withdrawal_amount = int(text[1]) if text[1].isnumeric() else "x"
    except IndexError:
        pass

    if chat_id in recipients.keys():
        recipient = recipients[chat_id]
        player = players[chat_id]

        if len(text) == 2 and isinstance(withdrawal_amount, int):
            if recipient["quavers"] >= withdrawal_amount:
                recipient["quavers"] -= withdrawal_amount
                player["quavers"] += withdrawal_amount

                quavers_at_bank = recipient["quavers"]
                quavers_in_hand = player["quavers"]

                summary_text = f"<code>{username}'s account summary\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Withdrawal amount : {withdrawal_amount} quavers\n</code>" \
                               f"<code>Available Balance : {quavers_at_bank} quavers\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Quavers in hand   : {quavers_in_hand} quavers</code>"

                context.bot.send_message(chat_id=groupchat_id, text=summary_text, parse_mode="HTML")
            else:
                insufficient_amount_text = f"<code>\n{username} has insufficient quavers to withdraw\n</code>"

                context.bot.send_message(chat_id=groupchat_id, text=insufficient_amount_text, parse_mode="HTML")
        else:
            format_error_text = f"<code>Error: wrong withdrawal format\n</code>" \
                                f"<code>Format : /withdraw amount</code>\n"

            context.bot.send_message(chat_id=groupchat_id, text=format_error_text, parse_mode="HTML")
        recipients[chat_id] = recipient
    else:
        unregistered_user_text = f"<code>{username} is not found in the database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=unregistered_user_text, parse_mode="HTML")

    update_json("players_data.json", players)
    update_json("bank_data.json", recipients)


def transfer(update, context):
    recipients = json.load(open("bank_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username
    text = update.message.text.split(" ")

    other_recipient_username, other_recipient_chat_id, transfer_amount = "x", "x", "x"

    try:
        other_recipient_username = text[1][1:]
        transfer_amount = int(text[2]) if text[2].isnumeric() else "x"
        other_recipient_chat_id = get_key_from_attribute("bank_data.json", "username", other_recipient_username)
    except IndexError:
        pass

    if chat_id in recipients.keys():
        recipient = recipients[chat_id]

        if len(text) == 3 and other_recipient_username != "x" and transfer_amount != "x":
            if other_recipient_chat_id in recipients.keys():
                other_recipient = recipients[other_recipient_chat_id]

                if transfer_amount <= recipient["quavers"]:
                    recipient["quavers"] -= transfer_amount
                    other_recipient["quavers"] += transfer_amount

                    quavers = recipient["quavers"]

                    summary_text = f"<code>{username}'s transfer summary\n</code>" \
                                   "<code>--------------------------------\n</code>" \
                                   f"<code>Recipient name    : {other_recipient_username} quavers\n</code>" \
                                   f"<code>Transfer amount   : {transfer_amount} quavers\n</code>" \
                                   "<code>--------------------------------\n</code>" \
                                   f"<code>Available balance : {quavers} quavers\n</code>"

                    context.bot.send_message(chat_id=groupchat_id, text=summary_text, parse_mode="HTML")

                else:
                    insufficient_text = f"<code>Insufficient balance in bank to transfer</code>"

                    context.bot.send_message(chat_id=groupchat_id, text=insufficient_text, parse_mode="HTML")
                recipients[other_recipient_chat_id] = other_recipient
            else:
                no_recipient_in_list_text = f"<code>{other_recipient_username} is not in the bank database</code>"

                context.bot.send_message(chat_id=groupchat_id, text=no_recipient_in_list_text, parse_mode="HTML")

        else:
            format_error_text = f"<code>Error: wrong transfer format\n</code>" \
                                f"<code>Format : /transfer @recipient amount</code>\n"

            context.bot.send_message(chat_id=groupchat_id, text=format_error_text, parse_mode="HTML")
        recipients[chat_id] = recipient
    else:
        unregistered_user_text = f"<code>{username} is not found in the bank database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=unregistered_user_text, parse_mode="HTML")
    update_json("bank_data.json", recipients)


def market(update, context):
    recipients = json.load(open("bank_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username

    if chat_id in recipients.keys():
        stock_price = get_crypto_price()

        market_text = f"<code>Klavier stocks price\n</code>" \
                      "<code>--------------------------------\n</code>" \
                      f"<code>Klavier Corp. : {stock_price} quavers</code>"

        context.bot.send_message(chat_id=groupchat_id, text=market_text, parse_mode="HTML")

    else:
        unregistered_user_text = f"<code>{username} has no permission to check stock prices</code>"

        context.bot.send_message(chat_id=groupchat_id, text=unregistered_user_text, parse_mode="HTML")


def invest(update, context):
    recipients = json.load(open("bank_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username
    text = update.message.text.split(" ")

    stock_amount = "x"

    try:
        stock_amount = int(text[1]) if text[1].isnumeric() else "x"
    except IndexError:
        pass

    if chat_id in recipients.keys():
        recipient = recipients[chat_id]

        if len(text) == 2 and isinstance(stock_amount, int):
            stock_price = get_crypto_price()
            total_amount = stock_price * stock_amount

            if total_amount <= recipient["quavers"]:
                recipient["quavers"] -= total_amount
                recipient["stocks"] += stock_amount

                recipient["total_buy"] += total_amount
                recipient["buy_quantity"] += stock_amount

                summary_text = f"<code>{username}'s investment summary\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               "<code>Investment type    : buy\n</code>" \
                               f"<code>Stock price        : {stock_price} quavers\n</code>" \
                               f"<code>Stock amount       : {stock_amount} unit(s)\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Total amount       : {total_amount} quavers\n</code>"

                context.bot.send_message(chat_id=groupchat_id, text=summary_text, parse_mode="HTML")

            else:
                insufficient_text = f"<code>Insufficient balance in bank to invest</code>"

                context.bot.send_message(chat_id=groupchat_id, text=insufficient_text, parse_mode="HTML")
        else:
            format_error_text = f"<code>Error: wrong invest format\n</code>" \
                                f"<code>Format : /invest amount</code>\n"

            context.bot.send_message(chat_id=groupchat_id, text=format_error_text, parse_mode="HTML")
        recipients[chat_id] = recipient
    else:
        unregistered_user_text = f"<code>{username} is not found in bank database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=unregistered_user_text, parse_mode="HTML")
    update_json("bank_data.json", recipients)


def sell(update, context):
    recipients = json.load(open("bank_data.json"))

    chat_id = str(update.message.from_user.id)
    groupchat_id = update.message.chat.id
    username = update.message.from_user.username
    text = update.message.text.split(" ")

    stock_amount = "x"

    try:
        stock_amount = int(text[1]) if text[1].isnumeric() else "x"
    except IndexError:
        pass

    if chat_id in recipients.keys():
        recipient = recipients[chat_id]

        if len(text) == 2 and isinstance(stock_amount, int):
            if stock_amount <= recipient["stocks"]:
                stock_price = get_crypto_price()
                total_amount = stock_price * stock_amount

                recipient["quavers"] += total_amount
                recipient["stocks"] -= stock_amount

                recipient["total_sell"] += total_amount
                recipient["sell_quantity"] += stock_amount

                summary_text = f"<code>{username}'s investment summary\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               "<code>Investment type : sell\n</code>" \
                               f"<code>Stock price     : {stock_price} quavers\n</code>" \
                               f"<code>Stock amount    : {stock_amount} unit(s)\n</code>" \
                               "<code>--------------------------------\n</code>" \
                               f"<code>Total amount    : {total_amount} quavers\n</code>"

                context.bot.send_message(chat_id=groupchat_id, text=summary_text, parse_mode="HTML")

                if recipient["stocks"] == 0:
                    recipient["total_buy"] = 0
                    recipient["total_sell"] = 0
                    recipient["buy_quantity"] = 0
                    recipient["sell_quantity"] = 0

            else:
                insufficient_text = f"<code>{username} has insufficient stocks in bank to sell</code>"

                context.bot.send_message(chat_id=groupchat_id, text=insufficient_text, parse_mode="HTML")
        else:
            format_error_text = f"<code>Error: wrong invest format\n</code>" \
                                f"<code>Format : /invest stock amount</code>\n"

            context.bot.send_message(chat_id=groupchat_id, text=format_error_text, parse_mode="HTML")
        recipients[chat_id] = recipient
    else:
        unregistered_user_text = f"<code>{username} is not found in bank database</code>"

        context.bot.send_message(chat_id=groupchat_id, text=unregistered_user_text, parse_mode="HTML")
    update_json("bank_data.json", recipients)


def give_interest(context):
    recipients = json.load(open("bank_data.json"))

    if bool(recipients):

        print(recipients.keys())

        for chat_id in recipients.keys():
            recipient = recipients[chat_id]

            interest = int(recipient["quavers"]*0.01)

            recipient["quavers"] += interest
            recipients[chat_id] = recipient

        update_json("bank_data.json", recipients)

        bank_announcement = "<code>Klavier Bank announcement\n</code>" \
                            "<code>--------------------------------\n</code>" \
                            "<code>Interests have been credited into your account</code>"

        context.bot.send_message(chat_id=-1001570480369, text=bank_announcement, parse_mode="HTML")
