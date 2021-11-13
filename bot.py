import torch
from torch import nn

from transformers import AutoModel, AutoTokenizer

import telebot
import parser


with open(".tg_token") as inf:
    TOKEN = inf.readline()[:-1]
bot = telebot.TeleBot(TOKEN)

model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased-conversational")
print(type(model))

tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased-conversational")
classifier = nn.Linear(768, 4)
classifier.load_state_dict(torch.load("classifier_weights.pts"))


@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет, когда я вырасту, я буду парсить заголовки с Хабра')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id

    X = torch.tensor([tokenizer(text)["input_ids"]])
    model_output = model(X).pooler_output
    print(model_output)
    output = int(classifier(model_output)[0].argmax())

    if output == 0:
        bot.send_message(chat_id, 'Здравствуйте!')
    elif output == 1:
        bot.send_message(chat_id, 'Всего доброго!')
    elif output == 2:
        bot.send_message(chat_id, 'Погода в Санкт-Петербурге')
    else:
        bot.send_message(chat_id, 'Простите, я вам не понял :(')


bot.polling()
