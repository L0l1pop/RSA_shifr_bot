import random
import telebot
from telebot import types
from dotenv import load_dotenv
import os


load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))
private_key = 0, 0
public_key = 0, 0

@bot.message_handler(commands=['start'])
def main(message):
    create_key = types.ReplyKeyboardMarkup()
    key = types.KeyboardButton('создать ключ')
    create_key.row(key)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}, это бот по RSA шифрованию. Давайте создадим ключ', reply_markup=create_key)
    bot.register_next_step_handler(message, info)


def shifr(message):
    bot.send_message(message.chat.id, encrypt(message.text, public_key))

def deshifr(message):
    bot.send_message(message.chat.id, decrypt(message.text, private_key))


@bot.message_handler(content_types=['text'])
def info(message):
    if message.text == 'создать ключ' or message.text == 'сгенерировать ключ':
        global private_key, public_key
        public_key, private_key = generate_keys(8)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        encrpyt = types.KeyboardButton('зашифровать')
        decrypt = types.KeyboardButton('расшифровать')
        key_generate = types.KeyboardButton('сгенерировать ключ')
        markup.row(encrpyt, decrypt)
        markup.row(key_generate)
        bot.send_message(message.chat.id, f'ключ шифрования:<b>{public_key}</b>\nключ для расшифровки:<b>{private_key}</b>', parse_mode='html', reply_markup=markup)
        return
    if message.text == 'зашифровать':
        bot.send_message(message.chat.id, 'Введите текст')
        bot.register_next_step_handler(message, shifr)
        return
    if message.text == 'расшифровать':
        bot.send_message(message.chat.id, 'Введите текст')
        bot.register_next_step_handler(message, deshifr)
        return

#быстрое возведение в степень
def exp_mod(a, b, n):
    bin = 0
    charge = 1
    charge_count = 0
    while (b != 0):
        bin += int(b % 2) * charge
        charge *= 10
        charge_count += 1
        b = b // 2
    mas_bin = (charge_count) * [0]
    for i in range(charge_count):
        mas_bin[i] = int(bin % 10)
        bin = bin // 10
    mas_a = (charge_count) * [0]
    mas_a[0] = a
    j = 1
    for i in range(charge_count - 2, -1, -1):
        if (mas_bin[i] == 0):
            mas_a[j] = (mas_a[j - 1] * mas_a[j - 1]) % n
        else:
            mas_a[j] = (a * mas_a[j - 1] * mas_a[j - 1]) % n
        j += 1
    return mas_a[charge_count - 1]


def MillerRabin(n, k=20):
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for i in range(k):
        a = random.randrange(2, n - 1)
        x = exp_mod(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for j in range(r - 1):
            x = exp_mod(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def gcd(a, b):
    if (b == 0):
        return a
    return gcd(b, a % b)

def gcd_extended(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        gcd, x, y = gcd_extended(b % a, a)
    return (gcd, y - (b // a) * x, x)

def generate_prime(n_bits=512):
    while True:
        prime = random.getrandbits(n_bits)
        if MillerRabin(prime):
            return prime


def generate_e(phi):
    while (True):
        e = random.randint(2, phi)
        if gcd(e, phi) == 1:
            return e


def generate_d(e, phi):
    g, x, y = gcd_extended(e, phi)
    if g != 1:
        raise ValueError('generate d is not exist')
    return x % phi


def generate_keys(n_bits=512):
    p = generate_prime(n_bits)
    q = generate_prime(n_bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = generate_e(phi)
    d = generate_d(e, phi)
    return (e, n), (d, n)


def encrypt(plaintext, public_key):
    e, n = public_key
    ciphertext = [chr(exp_mod(ord(el), e, n)) for el in plaintext]
    return ''.join(ciphertext)


def decrypt(ciphertext, private_key):
    d, n = private_key
    plaintext = [chr(exp_mod(ord(el), d, n)) for el in ciphertext]
    return ''.join(plaintext)


bot.polling(none_stop=True)



