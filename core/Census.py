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
GROUP_CHAT_ID = -1002389019806
ADMIN_ID = 7673525927



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


    text = 'Be careful in choosing your vote.\nAfter casting your vote\nIt can no longer be returned.'
    for i in range(1 , len(list_bottun)+1):
        text += f'<b>{i}..{list_bottun[i-1]}</b>\n'

    bot.send_message(GROUP_CHAT_ID ,text , reply_markup = markup , parse_mode='HTML')


from matplotlib import pyplot as plt

@bot.message_handler(commands=['end_option'])
def end_bot(message):

    # خواندن داده‌ها از پایگاه داده
    data = []
    for option in list_bottun:
        item = collection.find_one({'item': option})
        if item:
            data.append(item['count_of_votes'])
        else:
            data.append(0)

    # رسم نمودار
    plt.bar(list_bottun, data)
    plt.savefig('results.png')
    plt.close()

    # ارسال نمودار به گروه
    with open('results.png', 'rb') as photo:
        bot.send_photo(GROUP_CHAT_ID, photo)


    # پاک کردن داده‌ها
    collection.delete_many({})
    collection_user.delete_many({})

    bot.send_message(GROUP_CHAT_ID, 'Voting has ended.')
    for i, option in enumerate(list_bottun):
        bot.send_message(GROUP_CHAT_ID, f"{option}: {data[i]}")
    bot.leave_chat(GROUP_CHAT_ID)

@bot.message_handler(func=lambda message: True)
def user_vote(message):
    user_select = message.text

    if user_select in list_bottun:
        user = collection_user.find_one({'user_id': message.from_user.id})
        if user is None:
            # ثبت رأی کاربر
            collection_user.insert_one({'user_id': message.from_user.id})
            collection.update_one({'item': user_select}, {'$inc': {'count_of_votes': 1}})
            bot.send_message(message.chat.id, f'Your vote for "{user_select}" has been counted.')
        else:
            bot.send_message(message.chat.id, 'You have already voted.')
    else:
        bot.send_message(message.chat.id, 'Invalid option. Please select one of the available options.')
bot.infinity_polling()