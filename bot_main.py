import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import random
import words

API_TOKEN = '7395990552:AAG8P5sgSO9nmsxUELkFsB3NDRIi6S6zYr0'

# Initialize bot
bot = telebot.TeleBot(API_TOKEN)

# Define a dictionary to maintain game state for each user
user_data = {}

def choose_word():
    """Choose a random word from the list."""
    word = random.choice(words.words)
    word1 = list(word)  # List of characters in the word
    len_word = len(word)
    print(word)
    return word, word1, len_word

def make_unable_to_see(len_word):
    """Return a list of underscores to hide the word."""
    return ['_'] * len_word

def check_letter(letter, word1, under1):
    """Update the underscores with correctly guessed letters and return the updated underscores."""
    found = False
    for i, l in enumerate(word1):
        if l == letter:
            under1[i] = letter
            word1[i] = ' '
            found = True
    return ''.join(under1), found

# Handle '/start' and '/help'
@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = KeyboardButton('Play▶️')
    markup.add(btn)
    bot.send_message(message.chat.id, "Hi! I'm your bot. I will generate a word then you should try to find it.", reply_markup=markup)

# Handle 'Play' button
@bot.message_handler(func=lambda message: message.text == 'Play▶️')
def start_game(message):
    word, word1, len_word = choose_word()
    under1 = make_unable_to_see(len_word)
    
    user_data[message.chat.id] = {
        'word': word,
        'word1': word1,
        'len_word': len_word,
        'under1': under1,
        'attempts': 0
    }

    bot.send_message(message.chat.id, f'I thought of a word that consists of {len_word} letters. Let\'s find it.')
    bot.send_message(message.chat.id, ''.join(under1))
    bot.send_message(message.chat.id, 'Enter a letter:')
    bot.register_next_step_handler(message, guess_letter)

def guess_letter(message):
    user = user_data.get(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, 'Game not found. Type /start to begin a new game.')
        return

    letter = message.text.lower()
    if len(letter) != 1 or not letter.isalpha():
        bot.send_message(message.chat.id, 'Please enter a single letter.')
        bot.register_next_step_handler(message, guess_letter)
        return

    under1, found = check_letter(letter, user['word1'], user['under1'])
    user_data[message.chat.id]['under1'] = list(under1)  # Convert string back to list for future updates
    user_data[message.chat.id]['attempts'] += 1

    bot.send_message(message.chat.id, ''.join(user['under1']))
    
    if '_' not in user['under1']:
        bot.send_message(message.chat.id, f'Congratulations! You found the word "{user["word"]}" with {user["attempts"]} attempts!')
        show_play_again_buttons(message.chat.id)
    else:
        if found:
            bot.send_message(message.chat.id, 'Good guess! Keep going.')
        else:
            bot.send_message(message.chat.id, 'Try again.')
        bot.register_next_step_handler(message, guess_letter)

def show_play_again_buttons(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    btn_yes = InlineKeyboardButton('Yes', callback_data='play_again')
    btn_no = InlineKeyboardButton('No', callback_data='stop')
    markup.add(btn_yes, btn_no)
    bot.send_message(chat_id, 'Do you want to play again?', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['play_again', 'stop'])
def handle_callback_query(call):
    if call.data == 'play_again':
        start_game(call.message)
    elif call.data == 'stop':
        bot.send_message(call.message.chat.id, 'Goodbye! Type /restart to play again.')

# Start polling
if __name__ == "__main__":
    bot.polling()



