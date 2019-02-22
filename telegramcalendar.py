#!/usr/bin/env python3
#
# A library that allows to create an inline calendar keyboard.
# grcanosa https://github.com/grcanosa
# Modified by Deniskore
"""
Base methods for calendar keyboard creation and processing.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from datetime import *
from settings import *
from database import *

import calendar


def create_callback_data(action, year, month, day, time, cv_link):
    """ Create the callback data associated to each button"""
    return ';'.join([action, str(year), str(month), str(day), time, cv_link])


def separate_callback_data(data):
    """ Separate the callback data"""
    return data.split(';')


def create_calendar(year=None, month=None, cv_link=''):
    """
    Create an inline keyboard with the provided year and month
    :param int year: Year to use in the calendar, if None the current year is used.
    :param int month: Month to use in the calendar, if None the current month is used.
    :return: Returns the InlineKeyboardMarkup object with the calendar.
    """
    now = datetime.now()
    if year == None:
        year = now.year
    if month == None:
        month = now.month
    data_ignore = create_callback_data('IGNORE', year, month, 0, '', '')
    keyboard = []
    # First row - Month and Year
    row = []
    row.append(
        InlineKeyboardButton(
            calendar.month_name[month] + ' ' + str(year),
            callback_data=data_ignore))
    keyboard.append(row)
    # Second row - Week Days
    row = []
    for day in ss.week_days:
        row.append(InlineKeyboardButton(day, callback_data=data_ignore))
    keyboard.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for idx, day in enumerate(week):
            # Exclude weekend, and today in case of end of working day
            if (day == 0 or day < now.day) or (idx in [
                    5, 6
            ]) or (day == now.day and now.hour >= ss.end_of_day - 1):
                row.append(
                    InlineKeyboardButton(' ', callback_data=data_ignore))
            else:
                row.append(
                    InlineKeyboardButton(
                        str(day),
                        callback_data=create_callback_data(
                            'DAY', year, month, day, '', cv_link)))
        keyboard.append(row)

    row = []
    row.append(
        InlineKeyboardButton(
            '<',
            callback_data=create_callback_data('PREV-MONTH', year, month, day,
                                               '', cv_link)))
    row.append(InlineKeyboardButton(' ', callback_data=data_ignore))
    row.append(
        InlineKeyboardButton(
            '>',
            callback_data=create_callback_data('NEXT-MONTH', year, month, day,
                                               '', cv_link)))
    keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def create_time_pick(date, cv_link):
    new_time = (datetime.now() + timedelta(hours=1)).replace(
        minute=0, second=0, microsecond=0)
    row = []
    keyboard = []
    start = new_time
    end = new_time.replace(hour=ss.end_of_day)

    available_time = []
    # Get reserved list of time
    busy = db.get(date.strftime('%d/%m/%Y'))
    busy_time = []
    if busy:
        for i in busy:
            busy_time.append(int(i.split(':')[0]))

    # If user picked day in the future
    now = datetime.now()
    if date.day > now.day:
        for t in range(ss.start_of_day, ss.end_of_day, 1):
            if t not in busy_time:
                available_time.append(str(t) + ':00')
    else:
        for t in range(ss.start_of_day, ss.end_of_day, 1):
            if t > ss.start_of_day and t < ss.end_of_day and t >= new_time.hour and now.now(
            ).day == new_time.day:
                if t not in busy_time:
                    available_time.append(str(t) + ":00")

    # Split to rows * 3
    available_time = [
        available_time[x:x + 3] for x in range(0, len(available_time), 3)
    ]
    # Create keyboard
    for t in available_time:
        for i in t:
            row.append(
                InlineKeyboardButton(
                    i,
                    callback_data=create_callback_data(
                        'TIME', date.year, date.month, date.day, i, cv_link)))
        keyboard.append(row)
        row = []

    return InlineKeyboardMarkup(keyboard)


def process_calendar_selection(bot, update):
    """
    Process the callback_query. This method generates a new calendar if forward or
    backward is pressed. This method should be called inside a CallbackQueryHandler.
    :param telegram.Bot bot: The bot, as provided by the CallbackQueryHandler
    :param telegram.Update update: The update, as provided by the CallbackQueryHandler
    :return: Returns a tuple (Boolean,datetime.datetime), indicating if a date is selected
                and returning the date if so.
    """
    dt = None
    ret_data = (False, None, None)
    query = update.callback_query
    (action, year, month, day, t, cv_link) = separate_callback_data(query.data)
    curr = datetime(int(year), int(month), 1)

    if action == 'IGNORE' or day == '0':
        bot.answer_callback_query(callback_query_id=query.id)
    else:
        dt = datetime(int(year), int(month), int(day))

    if action == 'DAY':
        bot.answer_callback_query(query.id, text=ss.msg_callback_date_picked)
        bot.edit_message_text(
            text=ss.msg_choose_time,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=create_time_pick(dt, cv_link))
        ret_data = True, dt, t, cv_link

    elif action == 'TIME':
        bot.answer_callback_query(query.id, text=ss.msg_callback_time_picked)
        # Remove message
        bot.delete_message(query.message.chat_id, query.message.message_id)
        ret_data = True, dt, t, cv_link

    elif action == 'PREV-MONTH':
        pre = curr - timedelta(days=1)
        bot.edit_message_text(
            text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(pre.year), int(pre.month)))

    elif action == 'NEXT-MONTH':
        ne = curr + timedelta(days=31)
        bot.edit_message_text(
            text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(ne.year), int(ne.month)))

    else:
        bot.answer_callback_query(
            callback_query_id=query.id, text='Something went wrong!')
        # UNKNOWN
    return ret_data
