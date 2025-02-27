import telebot
import os
from telebot import types
from pymongo import MongoClient
import matplotlib.pyplot as plt

API_TOKEN = os.environ.get('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

client = MongoClient('mongodb://localhost:27017/')
db=client['btn']


list_bottun = ['django' , 'python' , 'ccna' , 'net+']

collection = db['servery']
collection_user = db['user']
# GROUP_CHAT_ID = 
# ADMIN_ID = 


@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.reply_to(message , 'wellcome to chat')


@bot.message_handler(commands=['new_option'])
def new_bot(message):
    collection.delete_many({})
    collection_user.delete_many({})
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True , row_width=4)
    for btn1 in list_bottun:
        markup.add(btn1)
        item = collection.find_one({'item':list_bottun})
        if item is None:
            collection.insert_one({'items':item,'count of votes':0})
    bot.reply_to(message , 'select one our option' , reply_markup=markup)


@bot.message_handler(commands=['end_option'])
def end_bot(message):
    data = []
    for case in list_bottun:
        item = collection.find_one({'item' , list_bottun})
        data.append(item['count of vote'])


bot.infinity_polling()



# collection.delete_many({})
# collection_user.delete_many({})
