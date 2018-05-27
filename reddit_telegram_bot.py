#--------------------------------------------------------------------------------------------------------
# Name:        reddit_telegram_bot.py
# Purpose:     implement a bot for telegram - IDWall challenge
#
# Author:      Jerome Vergueiro Vonk
#
# Created:     29/04/2018
# Based on:    github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
#--------------------------------------------------------------------------------------------------------


TOKEN = '436795214:AAFsHI7qGy_eCuqsC8V43LEVKfnf28K5L6w'

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from reddit_crawler import find_hot_threads
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def start(bot, update):
    """Send a message when the command /start is issued."""
    msg = "Hello, {}. Try the command */nothingtodo [list;of;subreddits]*".format(update.message.from_user.first_name)
    update.message.reply_text(msg, parse_mode='Markdown')

def help(bot, update):
    """Send a message when the command /help is issued."""
    msg = "Try command */nothingtodo [list;of;subreddits]*"
    update.message.reply_text(msg, parse_mode='Markdown')

def noncommand(bot, update):
    """Warn the user that we only respond to one command"""
    msg = "I only answer to the command */nothingtodo [list;of;subreddits]*"
    update.message.reply_text(msg, parse_mode='Markdown')

def unknown_cmd(bot, update):
    msg = "Help me help you! I only answer to the command */nothingtodo [list;of;subreddits]*"
    update.message.reply_text(msg, parse_mode='Markdown')

def nothingtodo(bot, update):
    """Run crawler on reddit."""
    cmd_parsed = update.message.text.split()

    if len(cmd_parsed) == 1:
        msg = "Which subreddit(s) you wanna look for? Format is */nothingtodo [list;of;subreddits]*"
        update.message.reply_text(msg, parse_mode='Markdown')
        return

    # Get the subreddits
    subreddits = cmd_parsed[1]

    # Warn the user
    update.message.reply_text("Command received. Just a moment, please.")

    # Reddit
    threads = find_hot_threads(subreddits)

    if not threads:
        update.message.reply_text("Did not found anything hot!")
        return

    threads = sorted(threads, key=lambda k: k['likes'], reverse=True)

    msg = ''
    for item in threads:
        msg += "*Subreddit*: {}\n".format(item['subreddit'])
        msg += "*Title*: {}\n".format(item['title'])
        msg += "*Points*: {}\n".format(item['likes'])
        msg += "[Thread]({})\n".format(item['thread_link'])

        if item['thread_link'] != item['comments_link']:
            # Add the comments link if it's not the same as the thread link
            msg += "[Comments]({})\n\n".format(item['comments_link'])
        else:
            msg += "\n"

    # Send to user
    update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("nothingtodo", nothingtodo))

    # respond to invalid commands
    dp.add_handler(MessageHandler(Filters.command, unknown_cmd))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, noncommand))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT.
    updater.idle()

if __name__ == '__main__':
    main()