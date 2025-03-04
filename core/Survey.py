import telebot
import os
from telebot import types
from pymongo import MongoClient
import matplotlib.pyplot as plt

# تنظیمات Matplotlib برای محیط‌های بدون GUI
import matplotlib
matplotlib.use('Agg')


# MongoDBاتصال به پایگاه داده 
client = MongoClient('mongodb://localhost:27017/')
db = client['btn']
collection = db['servery']
collection_user = db['user']


# (توکن بات، ID گروه، و ID ادمین)خواندن متغیرهای محیطی 
API_TOKEN = os.environ.get('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

GROUP_CHAT_ID = os.environ.get('GROUP_CHAT_ID')
ADMIN_ID = os.environ.get('ADMIN_ID')


# لیست گزینه‌های رأی‌گیری
list_bottun = ['django', 'python', 'ccna', 'net+']


# دستور/start:برای ارسال پیام خوش‌آمدگویی به کاربر
@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.reply_to(message, 'Welcome to the chat!')


# دستور /new_option: شروع رأی‌گیری
@bot.message_handler(commands=['new_option'])
def new_bot(message):
#حذف داده های قبلی پایگاه داده
    collection.delete_many({})
    collection_user.delete_many({})

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    for btn in list_bottun:
        markup.add(btn)
        item = collection.find_one({'item': btn})
        if item is None:
            collection.insert_one({'item': btn, 'count_of_votes': 0})

    bot.reply_to(message, 'Select one of our options:', reply_markup=markup)

    text = 'Be careful in choosing your vote.\nAfter casting your vote\nIt can no longer be returned.'
    for i, option in enumerate(list_bottun, start=1):
        text += f'\n<b>{i}. {option}</b>'

    bot.send_message(GROUP_CHAT_ID, text, reply_markup=markup, parse_mode='HTML')


# دستور /end_option: پایان رأی‌گیری و نمایش نتایج
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

# رسم نمودار نتایج
    plt.bar(list_bottun, data)
    plt.savefig('results.png')
    plt.close()

#ارسال نمودار به گروه
    with open('results.png', 'rb') as photo:
        bot.send_photo(GROUP_CHAT_ID, photo)

#حذف داده های قبلی پایگاه داده
    collection.delete_many({})
    collection_user.delete_many({})

#اعلام پایان رأی‌گیری به گروه
    bot.send_message(GROUP_CHAT_ID, 'Voting has ended.')
    for i, option in enumerate(list_bottun):
        bot.send_message(GROUP_CHAT_ID, f"{option}: {data[i]}")
#ترک گروه توسط بات
    bot.leave_chat(GROUP_CHAT_ID)


#مدیریت رأی‌ دهی توسط کاربران
@bot.message_handler(func=lambda message: True)
def user_vote(message):
    user_select = message.text

# چک کردن اینکه گزینه انتخابی در لیست گزینه‌ها وجود دارد
    if user_select in list_bottun:
        user = collection_user.find_one({'user_id': message.from_user.id})
        if user is None:
#ثبت اطلاعات کاربر در پایگاه داده
            collection_user.insert_one({
                'user_id': message.from_user.id,
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            })
#افزایش تعداد رأی برای گزینه انتخابی
            collection.update_one({'item': user_select}, {'$inc': {'count_of_votes': 1}})
# اعلام ثبت رأی به کاربر
            bot.send_message(message.chat.id, f'Your vote for "{user_select}" has been counted.')
        else:
#اعلام اینکه کاربر قبلاً رأی داده است
            bot.send_message(message.chat.id, 'You have already voted.')
    else:
#اعلام اینکه گزینه انتخابی معتبر نیست
        bot.send_message(message.chat.id, 'Invalid option. Please select one of the available options.')


bot.infinity_polling()