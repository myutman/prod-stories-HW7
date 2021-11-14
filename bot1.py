import telebot


with open(".tg_token") as inf:
    TOKEN = inf.readline()[:-1]

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет, когда я вырасту, я буду парсить заголовки с Хабра')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id

    bot.send_message(chat_id, 'Здравствуйте!')


bot.polling(none_stop=True)
