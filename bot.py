import telegram
import networkx as nx
import random
import string
import os

from telegram.ext import Updater, CommandHandler
from data import dibuixaMapa, creaGraf, connectedComponents, nodesGraph, edgesGraph, shortestPath, flows


# Generates a random name (multi-user support)
def randomName():
    stringLength = 10
    letters = string.ascii_lowercase
    r = ''.join(random.choice(letters) for i in range(stringLength))
    return (r + '.png')


def start(bot, update, user_data):
    directed = False
    startText = "Hola " + update.message.chat.first_name + "!😄 Sóc un bot del Bicing de Barcelona.\
    \nEt puc ajudar a buscar rutes i moltes coses més! 😏😏 \nPer més informació escriu /help."
    bot.send_message(chat_id=update.message.chat_id, text=startText)
    user_data['graf'] = creaGraf(1000, directed)


def help(bot, update):
    helpText = "Coses que puc fer: \n👨‍💻 /authors \n🖍️ /graph <distància> \n⭕ /nodes \
    \n↗️ /edges \n🔄 /components \n🗺️ /plotgraph \n🚴‍♀️ /route \n🚛 /distribute <rad, reqBikes, reqDocks>."
    bot.send_message(chat_id=update.message.chat_id, text=helpText)


def authors(bot, update):
    authorsText = "Els meus autors són: \nMarc Gallego🤓: marc.gallego.asin@est.fib.upc.edu \
    \nMarc Vernet😎: marc.vernet@est.fib.upc.edu"
    bot.send_message(chat_id=update.message.chat_id, text=authorsText)


def graph(bot, update, args, user_data):
    bot.send_message(chat_id=update.message.chat_id, text="⏲️Creant graf...")
    try:
        user_data['graf'] = creaGraf(int(args[0]), False)
        bot.send_message(chat_id=update.message.chat_id, text="✔️Graf creat!")
    except:
        bot.send_message(chat_id=update.message.chat_id, text="💀Alguna cosa ha fallat...")


def nodes(bot, update, user_data):
    n = nodesGraph(user_data['graf'])
    bot.send_message(chat_id=update.message.chat_id, text=n)


def edges(bot, update, user_data):
    n = edgesGraph(user_data['graf'])
    bot.send_message(chat_id=update.message.chat_id, text=n)


def components(bot, update, user_data):
    n = connectedComponents(user_data['graf'])
    bot.send_message(chat_id=update.message.chat_id, text=n)


def plotgraph(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id, text="🏗️Construint mapa...")
    try:
        photoName = randomName()
        dibuixaMapa(user_data['graf'], photoName)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(photoName, 'rb'))
        os.remove(photoName)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="💀Alguna cosa ha fallat...")


def route(bot, update, args, user_data):
    bot.send_message(chat_id=update.message.chat_id, text="⏲️Calculant ruta...")
    try:
        photoName = randomName()
        str = (" ".join(args))
        shortestPath(user_data['graf'], str, photoName)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(photoName, 'rb'))
        os.remove(photoName)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="💀Alguna cosa ha fallat...")


def distribute(bot, update, args, user_data):
    bot.send_message(chat_id=update.message.chat_id, text="⏲️Calculant...")
    try:
        cost, max_edge = flows(int(args[0]), int(args[1]), int(args[2]))
        bot.send_message(chat_id=update.message.chat_id, text=cost)
        bot.send_message(chat_id=update.message.chat_id, text=max_edge)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="💀Alguna cosa ha fallat...")


# Authentication issues
TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN)

dispatcher = updater.dispatcher


# Relates commands with the functions that have to be executed
dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('authors', authors))
dispatcher.add_handler(CommandHandler('graph', graph, pass_args=True, pass_user_data=True))
dispatcher.add_handler(CommandHandler('nodes', nodes, pass_user_data=True))
dispatcher.add_handler(CommandHandler('edges', edges, pass_user_data=True))
dispatcher.add_handler(CommandHandler('components', components, pass_user_data=True))
dispatcher.add_handler(CommandHandler('plotgraph', plotgraph, pass_user_data=True))
dispatcher.add_handler(CommandHandler('route', route, pass_args=True, pass_user_data=True))
dispatcher.add_handler(CommandHandler('distribute', distribute, pass_args=True, pass_user_data=True))


# Starts the bot
updater.start_polling()
