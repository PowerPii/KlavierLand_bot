import json
import requests


def update_json(file_name: str, new_data: dict):
    with open(file_name, "r+") as old_data:
        old_data.seek(0)
        json.dump(new_data, old_data, indent=4)
        old_data.truncate()


def get_key_from_attribute(file: str, key: str, value):
    data = json.load(open(file))
    for data_key, data_value in data.items():
        for att_key, att_val in data_value.items():
            if att_key == key and att_val == value:
                return data_key

    return "x"


def get_crypto_price():
    key = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"
    data = requests.get(key)
    data = data.json()

    return int(float(data['price']) * 1.38)


def get_stock_value(stock_amount: int):
    return get_crypto_price() * stock_amount
