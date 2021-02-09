#!/usr/bin/python3

import unittest, os, sys, unittest

import socketio, time, sqlite3

import shutil,shlex, subprocess

sys.path[:0] = ['../']
import QuickChat_client
import QuickChat_server as server
import QuickChat_bdd as bdd
from datetime import datetime

class testServer(unittest.TestCase):

    db_path = 'quick_chat.db'
    list_subprocess = []

    # Classmethod appelé à la fin de tous les tests
    # @classmethod
    # def setUpClass(cls):
    #     # Initialisation de la db et du path
    #     cls.db_path = 'quick_chat.db'
    #     print("Initialise cls.db_path to quick_chat.db")
    #     cls.connect = sqlite3.connect(cls.db_path)
    #     cls.cursor = cls.connect.cursor()

    def test_reception_historique(self):
        date = datetime.now()
        bdd.resetDb(self.db_path)
        connect = sqlite3.connect(self.db_path)

        cursor = connect.cursor()
        cursor.execute('INSERT INTO User (username, password) VALUES ("user1","pass")')
        cursor.execute('INSERT INTO Room (name, password, private, size) VALUES ("room1","pass","False",10)')
        cursor.execute('INSERT INTO Message (userId, roomId, mess, sendDate) VALUES (1,1,"Mon premier message","{}")'.format(date))
        connect.commit()

        res = server.getHistorique("room1")
        self.assertTrue( res == ['{} - user1 : Mon premier message'.format(str(date).split('.')[0])])

    def kill_subprocess(self):
        while len(self.list_subprocess) != 0 :
            p = self.list_subprocess.pop()
            p.terminate()

    def launch_server(self):

        cmd = "python3 ../QuickChat_server.py &"
        args = shlex.split(cmd)
        p  = subprocess.Popen(args) # launch command as a subprocess
        self.list_subprocess.append(p)
        time.sleep(5) #Temps que le serveur se mette en place

    def setUp(self):

        self.launch_server()

        self.db_path = 'quick_chat.db'
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.sio_test = socketio.Client()

        #Affiche un message lorsque le serveur nous informe que le
        #client est connecté
        @self.sio_test.on('connect')
        def connect():
            print("Connecté au serveur.")
            print(self.sio_test.get_sid())
            # self.sio_test.emit('message', {"data" : "Message test"})

        #Affiche les messages envoyés par le serveur
        @self.sio_test.on('message')
        def message(data):
            print(data)

        self.sio_test.connect('http://localhost:5000')

        #Création de la BDD
        bdd.resetDb(self.db_path)
        req = "INSERT INTO ROOM(name, password, private, size) VALUES(\"room_test\", \"\", 1, 10);"
        self.cursor.execute(req)
        self.conn.commit()

        time.sleep(2)

    def tearDown(self):
        bdd.deleteDb(self.db_path)
        self.sio_test.disconnect()
        self.kill_subprocess()

    def test_reception_donnees_connexion(self):

        #On emet des données type connexion au serveur
        self.sio_test.emit('connexion', {"username":"Jean", "room":"room_test"})
        self.sio_test.emit('connexion', {"username":"Jeremy", "room":"room_test"})
        self.sio_test.emit('connexion', {"username":"Jonathan", "room":"room_test"})

        #On fait attendre le test 2 secondes afin que l'ajout des données ait le
        #temps de se faire
        time.sleep(2)

        #Verification de l'ajout du user dans la BDD
        req = "SELECT username FROM USER;"
        res = self.cursor.execute(req).fetchall()
        self.conn.commit()
        # print(res)
        self.assertEqual(res, [('Jean',), ('Jeremy',), ('Jonathan',)])


    def test_reception_donnees_message(self):

        #On emet des données type connexion au serveur
        self.sio_test.emit('connexion', {"username":"Jean", "room":"room_test"})
        self.sio_test.emit('connexion', {"username":"Jeremy", "room":"room_test"})
        self.sio_test.emit('connexion', {"username":"Jonathan", "room":"room_test"})

        #On emet des données type message au serveur
        self.sio_test.emit('message_user',\
         {"username":"Jean",\
         "room":"room_test",\
         "message":"Bonjour, je suis Jean"})
        self.sio_test.emit('message_user',\
         {"username":"Jeremy",\
         "room":"room_test",\
          "message":"Bonjour, je suis Jeremy"})
        self.sio_test.emit('message_user',\
         {"username":"Jonathan",\
         "room":"room_test",\
          "message":"Bonjour, je suis Jonathan"})
        self.sio_test.emit('message_user',\
         {"username":"Jeremy",\
         "room":"room_test",\
          "message":"Bonjour tout le monde !"})

        #On fait attendre le test 2 secondes afin que l'ajout des données ait le
        #temps de se faire
        time.sleep(2)

        req = "SELECT id, userId, roomId, mess FROM MESSAGE WHERE id=1;"
        res = self.cursor.execute(req).fetchall()
        self.conn.commit()
        # print(res)
        self.assertEqual(res, [(1, 1, 1, 'Bonjour, je suis Jean')])

        req = "SELECT id, userId, roomId, mess FROM MESSAGE WHERE id=2;"
        res = self.cursor.execute(req).fetchall()
        self.conn.commit()
        # print(res)
        self.assertEqual(res, [(2, 2, 1, 'Bonjour, je suis Jeremy')])


        req = "SELECT id, userId, roomId, mess FROM MESSAGE WHERE id=3;"
        res = self.cursor.execute(req).fetchall()
        self.conn.commit()
        # print(res)
        self.assertEqual(res, [(3, 3, 1, 'Bonjour, je suis Jonathan')])


        req = "SELECT id, userId, roomId, mess FROM MESSAGE WHERE id=4;"
        res = self.cursor.execute(req).fetchall()
        self.conn.commit()
        # print(res)
        self.assertEqual(res, [(4, 2, 1, 'Bonjour tout le monde !')])

    def test_Add_Room(self):
        # Test d'ajout d'une salle
        bdd.resetDb(self.db_path)
        server.addRoom("room1", "0000", False, 10)
        print("Test de creation d'une room dans la table")
        requete = "SELECT * FROM Room;"
        resp = self.cursor.execute(requete).fetchall()
        self.assertEqual(resp, [(1, 'room1', '0000', 0, 10)])

        requete = "DROP TABLE Room;"
        self.cursor.execute(requete)

    # Classmethod appelé à la fin de tous les tests
    # @classmethod
    # def tearDownClass(cls):
    #     cls.connect.close()
    #     if(os.path.exists(cls.db_path)):
    #         print("Destruction de la db")
    #         os.remove(cls.db_path)

if __name__ == '__main__':
    unittest.main()
