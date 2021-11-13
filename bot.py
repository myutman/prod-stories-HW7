import time

import requests

import torch
from torch import nn

from transformers import AutoModel, AutoTokenizer

import telebot
import parser

import json


with open(".tg_token") as inf:
    TOKEN = inf.readline()[:-1]
with open(".api_token") as inf:
    API_TOKEN = inf.readline()[:-1]

bot = telebot.TeleBot(TOKEN)

model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased-conversational")
print(type(model))

tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased-conversational")
classifier = nn.Linear(768, 4)
classifier.load_state_dict(torch.load("classifier_weights.pts"))


@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет, когда я вырасту, я буду парсить заголовки с Хабра')


def get_actual_weather_info():
    r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Saint%20Petersburg&APPID={API_TOKEN}")
    return json.loads(r.text)


def get_weather():
    with open("current_weather.json") as inf:
        weather_info = json.load(inf)
    ts = weather_info["timestamp"]
    if time.time() - ts > 3600:
        weather_info["info"] = get_actual_weather_info()
        weather_info["timestamp"] = time.time()
        with open("current_weather.json", "w") as ouf:
            json.dump(weather_info, ouf)

    condition = weather_info["info"]["weather"][0]["main"]
    condition_ru = "переменная облачность"

    if condition == "Clouds":
        condition_ru = "облачно"
    elif condition == "Sun":
        condition_ru = "солнечно"
    elif condition == "Rain":
        condition_ru = "дождь"
    elif condition == "Snow":
        condition_ru = "снег"
    elif condition == "Clear":
        condition_ru = "ясно"

    temp = round(weather_info["info"]["main"]["temp"] - 273)
    feels_like = round(weather_info["info"]["main"]["feels_like"] - 273)
    wind = max(1, round(weather_info["info"]["wind"]["speed"]))
    pressure = round(weather_info["info"]["main"]["pressure"] * 760 / 1013.247)

    return f"{condition_ru}, температура {temp} градусов по цельсию, ощущается, как {feels_like}, ветер до {wind} мс, давление {pressure} мм рт ст"


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id

    X = torch.tensor([tokenizer(text)["input_ids"]])
    model_output = model(X).pooler_output
    output = int(classifier(model_output)[0].argmax())

    if output == 0:
        bot.send_message(chat_id, 'Здравствуйте!')
    elif output == 1:
        bot.send_message(chat_id, 'Всего доброго!')
    elif output == 2:
        weather = get_weather()
        bot.send_message(chat_id, 'Погода в Санкт-Петербурге ' + weather)
    else:
        bot.send_message(chat_id, 'Простите, я вам не понял :(')


bot.polling()
