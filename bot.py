import telebot
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from datetime import datetime

# Bot tokeningizni qo'shing
BOT_TOKEN = "7609777256:AAFuE0v3W3Bij_PVWzRjfbHdX0buv3Lld8U"  # Bot tokeningiz
bot = telebot.TeleBot(BOT_TOKEN)

# Global o'zgaruvchi uchun oldingi narx
previous_price = None

# Palma yog'i narxini olish funksiyasi
def get_palm_oil_price():
    url = "https://markets.businessinsider.com/commodities/palm-oil-price"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        price = soup.find("span", {"class": "price-section__current-value"})
        if price:
            price_text = price.text.strip()
            return float(price_text.replace(",", ""))  # Narxni float formatga o'zgartirish
        else:
            return None
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None

# Narxni kuzatish va o'zgarish haqida xabar berish funksiyasi
def check_price():
    global previous_price
    current_price = get_palm_oil_price()  # Yangi narxni olish

    if current_price is None:
        return  # Agar narxni olishda muammo bo'lsa, hech narsa qilmaslik

    if previous_price is not None:
        if current_price > previous_price:
            bot.send_message(chat_id="5059978236", text=f"Palma yog'i narxi oshdi: {current_price} USD")
        elif current_price < previous_price:
            bot.send_message(chat_id="5059978236", text=f"Palma yog'i narxi pasaydi: {current_price} USD")

    previous_price = current_price  # Yangi narxni saqlash

# /start komandasi uchun tugmali handler
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Price", callback_data="get_palm_oil_price")
    markup.add(button)
    bot.send_message(message.chat.id, "Assalamu alaykum! Palm oil Price:", reply_markup=markup)

# Tugmani bosganda narxni yuborish
@bot.callback_query_handler(func=lambda call: call.data == "get_palm_oil_price")
def send_palm_oil_price(call):
    price = get_palm_oil_price()
    if price:
        bot.send_message(call.message.chat.id, f"Palm oil : {price} USD")
    else:
        bot.send_message(call.message.chat.id, "Narxni olishda xatolik yuz berdi.")

# Narxni muntazam tekshirib borish uchun fon jarayonini ishga tushirish
def price_monitoring():
    while True:
        check_price()
        time.sleep(3600)  # 30 daqiqada bir marta narxni tekshirish

# Fon jarayonida narxni tekshirish funksiyasini ishga tushirish
import threading
monitor_thread = threading.Thread(target=price_monitoring)
monitor_thread.start()

# Botni ishga tushirish
bot.polling()