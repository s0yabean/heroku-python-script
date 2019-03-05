# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

from emoji import emojize
import logging
import requests
import json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
# Emoji: https://www.webfx.com/tools/emoji-cheat-sheet/

## GLOBAL VARIABLE TO BACKEND #####################################################################################################################################

link = 'https://thirdwheel-backend.herokuapp.com'

## LOGGING #####################################################################################################################################

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

## NON-CONVERSATION FUNCTIONS #####################################################################################################################################
## For telegram, no auth token need be sent, but rather just the auth is 3 things:
# 1) Email
# 2) Friend
# 3) Time Frequency
## and the linkage of the telegram chatid with the person_id will be permanent.

def start(bot, update):
    print("chat_id = " + str(update.message.chat_id));
    print("" + str(update.message.text));
    bot.send_message(chat_id=update.message.chat_id, text="Hi, I'm ThirdWheel_Bot, and I'll help nurture your long-term relationships like a snugly warm fire." +  emojize(":fire:", use_aliases=True) + emojize(":fire:", use_aliases=True) + "\n\nRelationships are like plants, they need warmth, care and support to flourish." + emojize(":seedling:", use_aliases=True) + emojize(":sun:") + emojize(":heart:", use_aliases=True) + emojize(":droplet:", use_aliases=True))
    bot.send_message(chat_id=update.message.chat_id, text="If it's your first time, I need to you to do 1 thing: \n\n1) Click /connect to link me to your web account! \n\nI need it to keep your relationships snugly warm!" +  emojize(":fire:", use_aliases=True))
    bot.send_message(chat_id=update.message.chat_id, text="If not, click /help for your list of commands.")
    return;

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="You can control me by sending these commands:  \n\n/next - See your list of upcoming connections \n/log - Reseting cycle for a user after contacting them \n/connect - To connect me with your email")

def next(bot, update, user_data):
    user_data['chat_id'] = update.message.chat_id
    try:
        bot.send_message(chat_id=update.message.chat_id, text="Pulling your data...")
        resp = requests.post(url= link + '/api/telegram_person_id', data=json.dumps({'chat_id': user_data['chat_id']}))
        
        if (json.loads(resp.text) == "person_id not found"):
            bot.send_message(chat_id=update.message.chat_id, text='Your telegram is not yet linked to the app. Set it up at /connect.')
            return;

        if (json.loads(resp.text) == "person_id not found"):
            bot.send_message(chat_id=update.message.chat_id, text='Your telegram is not yet linked to the app. Set it up at /connect.')
            return;

        value = json.loads(resp.text)
        logger.info("/NEXT Person_id found, able to run populate_table in telegram")
        resp_2 = requests.post(url= link + '/api/populate_table_telegram', data=json.dumps({'person_id': value[0]['person_id']}))
        logger.info(resp_2)
        value_2 = json.loads(resp_2.text)
        logger.info(value_2)

        if (value_2 == []):
            bot.send_message(chat_id=update.message.chat_id, text="You have no upcoming connections. Seriously? \n\n Add someone now!" + emojize(":stuck_out_tongue:", use_aliases=True))

        else: 
            bot.send_message(chat_id=update.message.chat_id, text="Your list of upcoming connections:" + emojize(":fire:", use_aliases=True))
            for row in value_2:
                #bot.send_message(chat_id=update.message.chat_id, text=row) # All data available in json
                bot.send_message(chat_id=update.message.chat_id, text=str(row['connection_name']) +
                                                                  '\nMonths Left: ' + str(int(row['months'])) +
                                                                  '\nDays Left: ' + str(int(row['days'])) +
                                                                  '\nLink: ' + str(row['contact_link']) +
                                                                  '\nRemarks: ' + str(row['remarks']))
            bot.send_message(chat_id=update.message.chat_id, text='There might still be time, but why wait when you have the time to chat with me? \n\n Send a message now and /log it!' + emojize(":point_right:", use_aliases=True) + emojize(":point_left:", use_aliases=True))
    except:
        bot.send_message(chat_id=update.message.chat_id, text='Sorry, there was an error. Have you finished setting up your bot in /connect ?')
        logger.info('Error in next() function in telegram bot.')

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command. My list of available commands: \n /connect - To connect your telegram account with ThirdWheel email \n /next - See list of upcoming connections \n /log - Reseting cycle for a user after contacting them \n /check - To check if your setup is complete")

## LOG CONVERSATION FUNCTIONS #####################################################################################################################################

CONFIRM_RESET, OBTAIN_CONNECTION_ID = range(2)

def log(bot, update, user_data):
    user_data['chat_id'] = update.message.chat_id
    try:
        bot.send_message(chat_id=update.message.chat_id, text="Pulling your data... \n\nSend /cancel to stop talking to me.")
        resp = requests.post(url= link + '/api/telegram_person_id', data=json.dumps({'chat_id': user_data['chat_id']}))
        value = json.loads(resp.text)
        user_data['person_id'] = value[0]['person_id']


        logger.info("/LOG Person_id found, able to run reset_cycle in telegram")
        resp_2 = requests.post(url= link + '/api/populate_table_telegram', data=json.dumps({'person_id': value[0]['person_id']}))

        value_2 = json.loads(resp_2.text)
        user_data['response'] = value_2
        print(value_2)

        if (value_2 == []):
            bot.send_message(chat_id=update.message.chat_id, text="You have no upcoming connections. Seriously? \n\n Add someone now!" + emojize(":stuck_out_tongue:", use_aliases=True))
            return ConversationHandler.END

        bot.send_message(chat_id=update.message.chat_id, text="Congrats on reigniting a connection!" + emojize(":fire:", use_aliases=True) + emojize(":clap:", use_aliases=True) + emojize(":fire:", use_aliases=True) +
            "\n\nSince I've no way of finding out, I'm going to trust that you actually sent that message *fingers crossed* " + emojize(":see_no_evil:", use_aliases=True) + emojize(":hear_no_evil:", use_aliases=True) + emojize(":speak_no_evil:", use_aliases=True) + "\n\nIf not, it's not too late to /cancel " + emojize(":smile:", use_aliases=True))

        # Creation of button with each selection for each person
        friend_list = []
        for row in value_2:
            friend_list.append(str(row['connection_name']))
            print(friend_list)
        update.message.reply_text('Which friend did you connect with?' + str(friend_list), reply_markup=ReplyKeyboardMarkup([friend_list], one_time_keyboard=True))

    except:
        bot.send_message(chat_id=update.message.chat_id, text='Sorry, there was an error. Have you finished setting up your bot in /connect ?')
        logger.info('Error in log function.')

    return OBTAIN_CONNECTION_ID

def obtain_connection_id(bot, update, user_data):
    connection = update.message.text
    user_data['connection'] = connection
    print(user_data)

    for row in user_data['response']:
        if row['connection_name'] == user_data['connection']:
            user_data['frequency'] = row['frequency']

    update.message.reply_text('Would you like to reset the cycle for ' + user_data['connection'] + ' ? \n\nYou will contact ' + user_data['connection'] + ' again in ' + user_data['frequency'] + ' from now.', reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
    return CONFIRM_RESET

def confirm_reset(bot, update, user_data):
    try:
        resp = requests.post(url= link + '/api/telegram_connection_id',
                         data=json.dumps({'person_id': user_data['person_id'], 'connection_name': user_data['connection']}))
        update.message.reply_text('Doing work behind the scenes...', reply_markup=ReplyKeyboardRemove())
        value = json.loads(resp.text)
        print(value)
        user_data['connection_id'] = value[0]['connection_id']
        resp_2 = requests.post(url= link + '/api/reset_cycle_telegram',
                         data=json.dumps({'connection_id': user_data['connection_id']}))
        value_2 = json.loads(resp_2.text)
        if (value_2 == 'Successfully RESET Deadline Cycle'):
          update.message.reply_text('Successfully updated cycle! \n\nSee your updated list at /next !')

    except:
        bot.send_message(chat_id=update.message.chat_id, text='/CONFIRM_RESET Sorry, there was an error. Have you finished setting up your bot in /connect ?')
        logger.info('/CONFIRM_RESET Error in confirm_reset function.')

    return ConversationHandler.END

## CONNECTION CONVERSATION FUNCTIONS #####################################################################################################################################

EMAIL, NAME, CONFIRM, FREQUENCY, SECURE_CONNECT = range(5)

def connect(bot, update, user_data):
    update.message.reply_text(
        'Hi! I will now help you connect telegram to your ThirdWheel account.\n\n'
        'Send /cancel to stop talking to me.\n\n'
        'What is your login email?', reply_markup=ReplyKeyboardRemove())
    return EMAIL

# user_data is like a global variable (dictionary) that can store data across states for use.
# To use, it needs to be put in the functions where it is accessed, and in the ConversationalHandler states below.
def email(bot, update, user_data):
    user = update.message.from_user
    email = update.message.text
    user_data['email'] = email
    logger.info("Email of %s: %s", user.first_name, email)
    update.message.reply_text('Confirm ' + email + ' is correct? \n\n Kindly reply "Yes" or "No".', reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
    return NAME

# Ask for name of 1 person user added
def name(bot, update, user_data):
    user = update.message.from_user
    logger.info("User %s is getting tested to see if email %s belongs to him/her.", user.first_name, user_data['email'])
    update.message.reply_text('Great, now I need to check if your email ' + user_data['email'] + ' belongs to you.' 
                               ' \n\nTell me the name of 1 person you added to ThirdWheel.\n\n' + 'Send /cancel to stop talking to me.', reply_markup=ReplyKeyboardRemove())
    return FREQUENCY

# Ask for frequency
def frequency(bot, update, user_data):
    user = update.message.from_user
    friend = update.message.text
    user_data['friend'] = friend
    update.message.reply_text('Now tell me, what freqency did you set ' + friend + ' to? \n\n' + 'W...= Week \nM...= Month',
           reply_markup=ReplyKeyboardMarkup([['1 Week', '2 Weeks', '3 Weeks', '1 Month', '6 Weeks', '3 Months', '6 Months']], one_time_keyboard=True))
    return CONFIRM

# Confirm 2 data points above
def confirm(bot, update, user_data):
    user = update.message.from_user
    frequency = update.message.text
    user_data['frequency'] = frequency
    update.message.reply_text('To confirm, you set ' + user_data['friend'] + ' on ' + user_data['frequency'] + ' ?',
                              reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
    return SECURE_CONNECT

def secure_connect(bot, update, user_data):
    update.message.reply_text('Checking records...')
    user_data['chat_id'] = update.message.chat_id
    logger.info("Telegram script sending SQL query to verify data...")
    resp = requests.post(url= link + '/api/telegram_check',
                  data=json.dumps({'chat_id': user_data['chat_id'] ,'email': user_data['email'], 'connection_name': user_data['friend'], 'frequency': user_data['frequency']}))
    value = json.loads(resp.text)
    logger.info(value)
    if (value == 'true'):
        update.message.reply_text('Record Found! Account successfully connected!')
        update.message.reply_text('You will now received personalised updates for connections like ' + user_data['friend'] + emojize(":heart:", use_aliases=True))
        update.message.reply_text('That is all you need to do for now, get back to life and crush it! \n\n Bye!' + emojize(":waving_hand:", use_aliases=True),
                              reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    elif (value == 'suspicious user'):
        update.message.reply_text('Our data shows you have already connected to telegram before.')
        update.message.reply_text('For security purposes, we cannot connect this account to prevent other people from stealing your data. Sorry!' + emojize(":hand:", use_aliases=True))
        update.message.reply_text('Kindly contact @tonytonggg if you still want to connect, or /help to see other options.',
                              reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    elif (value == 'duplicate user'):
        update.message.reply_text('Our data shows you have already connected to telegram before, using a different email.')
        update.message.reply_text('Kindly /connect using your right email.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    else :
        update.message.reply_text('Sorry, I could not find your record, could you kindly double check the data and try again /connect? \n\n' +
                                  'email: ' + user_data['email'] +
                                  '\n name: ' + user_data['friend'] +
                                  '\n frequency: ' + user_data['frequency'],
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! Let\'s reconnect again someday! \n\nClick /help for more commands.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

## ERROR FUNCTIONS #####################################################################################################################################

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        logger.warning('remove update.message.chat_id from conversation list', update, error)
    except BadRequest:
        logger.warning('handle malformed requests', update, error)
    except TimedOut:
        logger.warning('handle slow connection problems', update, error)
    except NetworkError:
        logger.warning('handle other connection problems', update, error)
    except ChatMigrated as e:
        logger.warning('the chat_id of a group has changed, use e.new_chat_id instead', update, error)
    except TelegramError:
        logger.warning('handle all other telegram related errors', update, error)

## MAIN FUNCTION #####################################################################################################################################

def main():
    print("Bot Initialised!")

    # Create the EventHandler and pass it your bot's token.
    updater = Updater("780399904:AAEKW7dbep4SY4TRTivFU-MMavmlQUrqLdI")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

######################################################

    # Add conversation handler for connecting chatid with person_id in DB.
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('connect', connect, pass_user_data=True)],

        states={
            EMAIL: [RegexHandler('[^@]+@[^@]+\.[^@]+', email, pass_user_data=True)],

            NAME: [RegexHandler('Yes', name, pass_user_data=True),
                   RegexHandler('No', connect, pass_user_data=True)],

            FREQUENCY: [MessageHandler(Filters.text, frequency, pass_user_data=True)],

            CONFIRM: [RegexHandler('1 Week|2 Weeks|3 Weeks|1 Month|6 Weeks|3 Months|6 Months', confirm, pass_user_data=True),
                      RegexHandler('No', connect, pass_user_data=True)],

            SECURE_CONNECT: [RegexHandler('Yes', secure_connect, pass_user_data=True),
                   RegexHandler('No', name, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

######################

    #Add conversation handler for /log to trigger the reset_cycle route
    log_handler = ConversationHandler(
        entry_points=[CommandHandler('log', log, pass_user_data=True)],

        states={

            OBTAIN_CONNECTION_ID: [MessageHandler(Filters.text, obtain_connection_id, pass_user_data=True)],

            CONFIRM_RESET: [RegexHandler('Yes', confirm_reset, pass_user_data=True),
                   RegexHandler('No', cancel)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

######################################################
# Every new 'route' has to be logged/ instantiated here!
################################################################################################
    start_handler = CommandHandler('start', start)
    next_handler = CommandHandler('next', next, pass_user_data=True)
    help_handler = CommandHandler('help', help)
################################################################################################
    dp.add_handler(start_handler)
    dp.add_handler(next_handler)
    dp.add_handler(help_handler)
######################################
    dp.add_handler(conv_handler)
    dp.add_handler(log_handler)
######################################
    unknown_handler = MessageHandler(Filters.command, unknown)
    dp.add_handler(unknown_handler) #this has to be at the last of the last of the add_handlers, like the final else after a long elif conditions!
################################################################################################

    # log all errors
    dp.add_error_handler(error)
    dp.add_error_handler(error_callback)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
  main();
#     app.run(host='0.0.0.0', port=5000);

#app.run(environ.get('PORT'))
