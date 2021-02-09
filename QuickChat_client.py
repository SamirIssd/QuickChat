"""
    QuickChat_client : Gestion des messages clients et des arguments lors de l'execution du script
"""

import socketio
from docopt import docopt
import sys

sio = socketio.Client()
host = 'localhost'
port = 5000

help = """
Usage:
    QuickChat_client.py <username> <room> [--host <name> -p <port>]

Options:
    -h --help       : Obtenir de l'aide
    --host <name>   : Choix de l'host (defaut: localhost)
    -p <port>       : Choix du port (defaut: 5000)
"""


# Affichage d'un message lorsque le client reçoit un évènement de connexion du serveur
@sio.on('connect')
def connect():
    """ Affichage d'un message lorsque le client reçois un évènement de connexion du serveur """
    if sio.connected:
        print('\033[32msuccessfully connected\033[39m')
        arg = sys.argv[1:]
        data = listArg(arg)
        sio.emit('connexion', data)
        sio.sleep(1)
        while(1):
            mess = writeMessage(data)
            sio.emit('message_user', mess)

@sio.on('disconnect')
def disconnect():
    """ Affichage d'un message en cas de perte de connexion avec le serveur """
    print('\033[31mdisconnected\033[39m')

def connexion():
    """ Fonction permettant une tentative de connexion au serveur """
    sio.connect('http://{}:{}'.format(host, str(port)))

#Fonction permettant de se deconnecter
def deconnexion():
    """ Description : TODO """
    sio.disconnect()


# Fonction pour écrire un message
def writeMessage(data):
    data['message'] = input()
    screen_code = "\033[1A[\033[2K"
    sys.stdout.write( screen_code )
    return data

# Vérification du nombre d'arguments
def verifArg(nbArg):
    if (nbArg == 2 or nbArg == 4):
        return True
    return False

# Stocke dans data: username et room
def listArg(arg):
    data = {}
    data['username'] = arg[0]
    data['room'] = arg[1]
    return data

def main():
    """ Gestion des arguments passés lors de l'éxécution du script """
    arguments = docopt(help)
    if arguments['-p']:
        port = arguments['-p']
    if arguments['--host']:
        host = arguments['--host']
    connexion()

if __name__ == '__main__':
    main()
