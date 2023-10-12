import telebot
from dotenv import load_dotenv
import os

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

admin_id = int(os.getenv('ADMIN_ID'))
# загадываем слово
word = ''

users = {}

winners = []


# обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    if len(winners) == 0:
        if message.chat.id not in users:
            user_info = bot.get_chat_member(message.chat.id, message.from_user.id)
            users[message.chat.id] = {'attempts': 0, 'profile':
                f'{user_info.user.first_name}'
                f' {user_info.user.last_name}'
                f' (@{user_info.user.username})'
            }
        bot.send_message(message.chat.id, 'Привет, я квест-бот! Я загадал слово. Попробуй его отгадать.')
    else:
        bot.send_message(message.chat.id, 'Победитель уже найден')


@bot.message_handler(commands=['restart'])
def restart_message(message):
    global winners
    if message.from_user.id == admin_id:
        if message.chat.id in users:
            del users[message.chat.id]
        winners.clear()
        bot.send_message(message.chat.id, 'Обновляем игру! Введите команду /start.')
    else:
        bot.send_message(message.chat.id, 'Вы не являетесь администратором.')


@bot.message_handler(commands=['change_word'])
def change_word_message(message):
    if message.from_user.id == admin_id:
        command_parts = message.text.split('/change_word ')
        if len(command_parts) > 1:
            new_word = command_parts[1]
            if new_word:
                global word
                word = new_word

                bot.send_message(message.chat.id, f'Слово для отгадывания изменено на "{word}".')
            else:
                bot.send_message(message.chat.id, 'Вы не ввели новое слово.')
        else:
            bot.send_message(message.chat.id, 'Вы не указали новое слово.')
    else:
        bot.send_message(message.chat.id, 'Вы не являетесь администратором.')


@bot.message_handler(content_types=['text'])
def guess_word(message):
    if message.chat.id in users:
        users[message.chat.id]['attempts'] += 1
        if message.text.lower() == word:
            bot.send_message(message.chat.id,
                             f'Поздравляю, {message.from_user.first_name}!'
                             f' Ты отгадал слово за {users[message.chat.id]["attempts"]}'
                             f' попыток.')
            bot.send_message(message.chat.id, f'Победитель: {users[message.chat.id]["profile"]}')
            broadcast_message('Победитель найден! Это {}! Слово: {}'.format(message.from_user.first_name, word))
            winners.append(message.from_user.first_name)
            del users[message.chat.id]

        else:
            bot.send_message(message.chat.id, 'Не угадал, попробуй еще раз.')
    else:
        bot.send_message(message.chat.id, 'Чтобы начать игру, введите команду /start.')


def broadcast_message(message):
    for user in users:
        bot.send_message(user, message)


bot.polling()