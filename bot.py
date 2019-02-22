from uuid import uuid4

from telegram.utils.helpers import escape_markdown
from telegram.ext.dispatcher import run_async
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent, InputMediaPhoto, ChatAction,\
    InlineKeyboardButton, InlineKeyboardMarkup,\
    ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, \
    MessageHandler, CallbackQueryHandler, Filters, ConversationHandler,\
    RegexHandler
from settings import *
from database import *
from datetime import *
from mimetypes import MimeTypes
from urllib.parse import urlparse

import logging
import glob
import telegramcalendar
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# Get all images
images = glob.glob(ss.image_path + '/*.jpg')

# Statuses for conversation handler
INTERVIEW_CHOOSE, INTERVIEW_REPLY, INTERVIEW_CHOICE = range(3)
reply_keyboard = [[ss.reply_first], [ss.reply_cancel]]
choose_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def start(bot, update):
    update.message.reply_text(ss.msg_start)


def help(bot, update):
    start(bot, update)


def is_channel_message(message):
    if message.chat.type == 'group':
        return True
    return False


@run_async
def info(bot, update):
    if not is_channel_message(update.message):
        bot.send_message(
            chat_id=update.message.chat_id,
            text=ss.msg_innopolis_info,
            parse_mode=ParseMode.HTML)
        # Create Telegram album
        input_album = []
        for i in images:
            s = open(i, 'rb')
            input_album.append(InputMediaPhoto(s))
            s.close()
        # Split up to ten items in array
        splitted_album = [
            input_album[i:i + 10] for i in range(0, len(input_album), 10)
        ]

        for i in splitted_album:
            # Exclude albums with wrong length, info from TG docs:
            # "An array describing photos and videos to be sent, must include 2–10 items."
            if len(i) >= 2:
                bot.send_media_group(update.message.chat_id, i)
            else:
                logger.info(
                    'Wrong album size, please add more photos to the album')


def write_to_group(bot, data):
    bot.send_message(chat_id=ss.private_channel_id, text=data)


def get_usage_counter(update):
    user_info = db.get(update.message.chat_id)
    if user_info:
        if datetime.now().strftime('%d/%m/%Y') == user_info['lastUsage']:
            return user_info['counter']
        else:
            # Update user information if the date has changed
            user_info['counter'] = 0
            user_info['lastUsage'] = datetime.now().strftime('%d/%m/%Y')
            db.set(update.message.chat_id, user_info)
    return 0


def cancel_interview(bot, update):
    if not is_channel_message(update.message):
        data = db.get(update.message.chat_id)
        if data:
            user_info = data
            if user_info and user_info.get('time'):
                bot.send_message(
                    text=ss.msg_interview_canceled % (user_info['date'],
                                                      user_info['time']),
                    chat_id=update.message.chat_id)
                group_text = user_info[
                    'name'] + ss.msg_canceled_interview + user_info[
                        'date'] + ' ' + user_info['time']
                write_to_group(bot, group_text)
                # Delete reserved time
                t = user_info['time']
                interview_time = db.get(user_info['date'])
                try:
                    interview_time.remove(user_info['time'])
                except:
                    pass
                db.set(user_info['date'], interview_time)
                # Copy usage counter and last used date
                counter = user_info['counter'] + 1
                lastUsage = user_info['lastUsage']
                # Generate new dict
                user_info = dict([(key, []) for key in user_info])
                user_info['counter'] = counter
                user_info['lastUsage'] = lastUsage
                db.set(update.message.chat_id, user_info)
            else:
                bot.send_message(
                    text=ss.msg_noreserved_interview,
                    chat_id=update.message.chat_id)
    # Remove from scheduler
    key = 'scheduler'
    if db.is_exists(key):
        data = db.get(key)
        if data:
            data.pop(str(update.message.chat_id))
            db.set(key, data)


def inline_handler(bot, update):
    selected, date, t, cv_link = telegramcalendar.process_calendar_selection(
        bot, update)
    username = update.callback_query.from_user.name

    if selected and not t:
        bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text=ss.msg_chose_date % (username, date.strftime('%d/%m/%Y')),
            reply_markup=ReplyKeyboardRemove())

    elif selected:
        bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text=ss.msg_chose_time % (username, t),
            reply_markup=ReplyKeyboardRemove())
        user_info = {}
        if not db.is_exists(update.callback_query.from_user.id):
            user_info['counter'] = 0
        else:
            # Retrieve old user info from db
            user_info = db.get(update.callback_query.from_user.id)
            user_info = user_info
        # Fill new user info
        user_info['name'] = username
        user_info['date'] = date.strftime('%d/%m/%Y')
        user_info['time'] = t
        user_info['lastUsage'] = datetime.now().strftime('%d/%m/%Y')
        user_info['cvLink'] = cv_link
        # Insert new reservation to db
        db.set(update.callback_query.from_user.id, user_info)
        # Check if key is already present
        key = date.strftime('%d/%m/%Y')
        if db.is_exists(key):
            # Append new time element to an existing array
            data = db.get(key)
            data.append(t)
            db.set(key, data)
        else:
            db.set(key, [t])
        # Add to scheduler
        user_list = {}
        del user_info['lastUsage']
        del user_info['cvLink']
        del user_info['counter']
        user_list[update.callback_query.from_user.id] = user_info
        key = 'scheduler'
        if db.is_exists(key):
            # Add new element to an existing dict
            data = db.get(key)
            data[update.callback_query.from_user.id] = user_info
            db.set(key, data)
        else:
            db.set(key, user_list)
        # Write message to a private channel
        write_to_group(
            bot, username + ss.msg_someone_reserved + user_info['date'] + ' ' +
            user_info['time'] + ', ' + ss.msg_link_to_cv + ' - ' + cv_link)
    return ConversationHandler.END


def contact_author(bot, update):
    bot.send_message(text='@dinisoid', chat_id=update.message.chat_id)


def list_interviews(bot, update):
    key = 'scheduler'
    # This command only for admins
    if db.is_exists(key) and update.message.from_user.name in ss.admins:
        final_message = ss.msg_list_interviews
        data = db.get(key)
        if data:
            for chat_id, value in data.items():
                final_message = final_message + value['name'] + ' ' + value[
                    'date'] + ' ' + value['time'] + "\n"
            bot.send_message(
                chat_id=update.message.chat_id,
                text=final_message,
                parse_mode=ParseMode.HTML)
            return
    bot.send_message(
        chat_id=update.message.chat_id,
        text=ss.msg_no_coming_interviews,
        parse_mode=ParseMode.HTML)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def is_reserved(update):
    if not is_channel_message(update.message):
        if get_usage_counter(update) < ss.max_requests:
            data = db.get(update.message.chat_id)
            if data and db.is_exists(
                    update.message.chat_id) and data.get('time'):
                date = data.get('date')
                date = datetime.strptime(date, '%d/%m/%Y')
                # Skip old date
                if datetime.now() < date:
                    return True
    return False


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


@run_async
def interview(bot, update):
    if not is_channel_message(update.message):
        if is_reserved(update):
            bot.send_message(
                text=ss.msg_already_reserved, chat_id=update.message.chat_id)
            return ConversationHandler.END
        elif get_usage_counter(update) >= ss.max_requests:
            bot.send_message(
                text=ss.msg_interview_limit_exceeded,
                chat_id=update.message.chat_id)
            return ConversationHandler.END

        update.message.reply_text(
            ss.msg_choose_menu_item, reply_markup=choose_markup)

    return INTERVIEW_CHOOSE


def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(ss.msg_send_cv_link)
    return INTERVIEW_REPLY


def received_information(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    if is_url(text):
        update.message.reply_text(ss.msg_cv_received)
        if get_usage_counter(update) < ss.max_requests:
            bot.send_message(
                text=ss.msg_choose_date,
                chat_id=update.message.chat_id,
                reply_markup=telegramcalendar.create_calendar(
                    None, None, text))
    else:
        update.message.reply_text(ss.msg_incorrect_url)
        return INTERVIEW_REPLY

    return ConversationHandler.END


def done(bot, update, user_data):
    user_data.clear()
    return ConversationHandler.END


@run_async
def scheduler(updater):
    inform_first = {}
    inform_second = {}
    while True:
        bot = updater.bot
        now = datetime.now()
        today = datetime.now().strftime('%d/%m/%Y')
        key = 'scheduler'
        if db.is_exists(key):
            data = db.get(key)
            tmp_copy = data.copy()
            for chat_id, value in tmp_copy.items():
                reserved_time = value['date'] + ' ' + value['time']
                reserved_time = datetime.strptime(reserved_time,
                                                  '%d/%m/%Y %H:%M')
                rem = reserved_time - now
                remainder = divmod(rem.seconds, 3600)[1]
                minutes = divmod(remainder, 60)[0]
                # Remove old item
                if reserved_time < datetime.now():
                    if chat_id in inform_first:
                        del inform_first[chat_id]
                    elif chat_id in inform_second:
                        del inform_second[chat_id]
                    del data[chat_id]
                    db.set(key, data)
                    continue
                # Send message if the date is correct
                if value['date'] == today:
                    if rem <= timedelta(
                            hours=1) and not inform_first.get(chat_id):
                        inform_first[chat_id] = datetime.now().timestamp()
                        bot.send_message(
                            text=ss.msg_minutes_rem % minutes,
                            chat_id=int(chat_id))
                    elif rem <= timedelta(
                            minutes=10) and not inform_second.get(chat_id):
                        inform_second[chat_id] = datetime.now().timestamp()
                        bot.send_message(
                            text=ss.msg_minutes_rem % minutes,
                            chat_id=int(chat_id))
        time.sleep(5)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(ss.bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('info', info))
    dp.add_handler(CommandHandler('ci', cancel_interview))
    dp.add_handler(CommandHandler('author', contact_author))
    dp.add_handler(CommandHandler('li', list_interviews))
    dp.add_handler(CallbackQueryHandler(inline_handler))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('i', interview)],
        states={
            INTERVIEW_CHOOSE: [
                RegexHandler(
                    ss.reply_first_regex, regular_choice, pass_user_data=True),
                RegexHandler(ss.reply_cancel_regex, done, pass_user_data=True),
            ],
            INTERVIEW_CHOICE: [
                MessageHandler(
                    Filters.text, regular_choice, pass_user_data=True),
            ],
            INTERVIEW_REPLY: [
                MessageHandler(
                    Filters.text, received_information, pass_user_data=True),
            ],
        },
        fallbacks=[
            RegexHandler(ss.reply_cancel_regex, done, pass_user_data=True)
        ])

    # Run scheduler
    scheduler(updater)

    dp.add_handler(conv_handler)

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
