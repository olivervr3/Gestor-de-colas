from sqlite3.dbapi2 import Timestamp
from kafka import KafkaConsumer, KafkaProducer
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import random
import threading
import time as time 
import socket
import json
from datetime import datetime
import sqlite3
import requests
from cryptography.fernet import Fernet
import os
from colorama import Fore, Back, Style



# DEFAULT
topic = "sensorinfo"
HEADER = 64
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 2  
ADDR = ""
VISITORS = 0
MAX_VISITORS = 0

KAFKA_SERVER = "localhost:9092" #default

RUTE_DB = "./bd/basededatos.db"

estimatedTimes = list()
attractions = list()
tokens = list()
users = list()

WTS_isAlive = 0

config = list()

w_config = ["", ["", "", "", ""]]

cryptoKey = "-1" 

cities = [-1, -1, -1, -1]




def sendToSocketServer(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def decryptMessage(msg):
    global cryptoKey
    f = Fernet(cryptoKey)
    msg = f.decrypt(msg).decode()
    return msg

def encryptMessage(msg):
    global cryptoKey
    try:
        f = Fernet(cryptoKey)
        msg = f.encrypt(str(msg).encode())
        msg = msg.decode()
    except:
        print("Error encriptando el mensaje revisa tu clave...")
        msg = "-1"
    return msg

# Funcion que revisa si hay conexion
def checkIfWaitingServerIsOnline():
    while(1):
        if(WTS_isAlive != 1):
            print("[WAITING TIME SERVER] Starting task")
            connectWTS()
        time.sleep(2)

# Funcion que establece conexion con el servidor de sockets
def connectWTS():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global ADDR 
    global WTS_isAlive
    global attractions
    try:
        print("[WAITING TIME SERVER] Connecting on " + str(ADDR))
        client.connect(ADDR)
        WTS_isAlive = 1
        while 1: 
            print("[WAITING TIME SERVER] Requesting info...")
            sendToSocketServer("info", client)
            answer = client.recv(2048).decode(FORMAT)
            print("[WAITING TIME SERVER] Got a response: " + answer)
            res = answer.split(":")
            if ":" in answer:
                for i in range(len(attractions)):
                    attractions[i][2] = int(res[i])
            else:
                attractions[0][2] = res
            time.sleep(3)

    except socket.error as exc:
        # Excepcion
        print("[WAITING TIME SERVER] Connection lost! New exception: " + str(exc))
        WTS_isAlive = 0
        for i in range(len(attractions)):
            attractions[i][2] = -1
    finally:
        client.close()


# Funcion que permite el login
def handleLoginRequest(): 
    #Consumidor de login
    global KAFKA_SERVER
    global MAX_VISITORS
    topic = "logindetails"
    consumer = KafkaConsumer(topic, bootstrap_servers = KAFKA_SERVER)

    print("[LOGIN] Awaiting for info on Kafka Server topic = " + topic)
    for message in consumer: 
        try:
            valor = message.value
            valor = decryptMessage(valor)
            valor = valor.split(":")
            time.sleep(1)
            if VISITORS < MAX_VISITORS:
                generateLoginResponse(valor[0], valor[1])
            else:
                print("PARQUE FULL")
                topic = "logintoken"
                producer = KafkaProducer(bootstrap_servers = KAFKA_SERVER)
                send = str(valor[0]) + ":0:" + "MAX_VISITORS_REACHED"
                send = encryptMessage(send)
                if(send != "-1"):
                    producer.send(topic, send.encode(FORMAT))
                producer.close()
        except:
            print(Fore.RED + "[ERROR] Can't decrypt the message, check the key on the file config.json" + Fore.RESET)
        

# Generate token
def generateLoginResponse(username, password):
    global RUTE_DB
    global MAX_VISITORS, VISITORS
    global tokens
    topic = "logintoken"
    conDb = sqlite3.connect(RUTE_DB)
    cur = conDb.cursor()
    print("[LOGIN] User " + username + " is trying to login")
    cur.execute('SELECT COUNT(), password FROM users WHERE username = "' + username + '"')
    numberOfRows = cur.fetchone()
    res = False
    if numberOfRows[0] == 1 and check_password_hash(numberOfRows[1], password): 
        # Generate token
        VISITORS = VISITORS + 1
        token = username + str(int(time.time()))
        # Session will expire on 3600 sec's
        token_expires = 3600 + int(time.time())
        print("Generated token: '" + token + "' expires: " + str(token_expires))
        cur.execute("DELETE FROM tokens where user = '" + username + "'")
        cur.execute("INSERT INTO tokens (user, token, expires) VALUES ('" + username + "', '" + token + "', '" + str(token_expires) + "');")
        conDb.commit()
        users.append([username, token, token_expires, [-1, -1, -1], int(time.time())])
        print("[DATABASE] Inserted the token on the database")
        #print(tokens)
        producer = KafkaProducer(bootstrap_servers = KAFKA_SERVER)
        send = str(username) + ":1:" + str(token) + ":" + str(token_expires)
        send = encryptMessage(send)
        if send != "-1":
            producer.send(topic, send.encode(FORMAT))
        producer.close()
    else:
        # Response
        print("[LOGIN] Failed login")
        producer = KafkaProducer(bootstrap_servers = KAFKA_SERVER)
        send = str(username) + ":0:" + "NO_USERNAME/PASSWORD_FOUND_ON_SERVER"
        if send != "-1":
            send = encryptMessage(send)
        producer.send(topic, send.encode(FORMAT))
        producer.close()

    conDb.close()

# Keep Alive 
def userKeepAlive(): 
    global VISITORS
    global users
    while 1:
        el = 0
        for u in users:
            if (int(time.time())-u[4]) > 5:
                print("[KEEP ALIVE] User: " + u[0] + " disconnected")
                el = u
        if el != 0:
            users.remove(el) 
            VISITORS = VISITORS - 1
        time.sleep(1)
                


# Update information
def userinfo(): 
    global users, VISITORS
    consumer = KafkaConsumer('userinfo',bootstrap_servers=KAFKA_SERVER)
    for message in consumer: 
        # usuario:token:3,1:1
        try:
            valor = message.value
            valor = decryptMessage(valor)
            # print("He recibido: " + valor)
            valor = valor.split(":")
            user = valor[0]
            token = valor[1]
            coordenada = [valor[2].split(",")[0], valor[2].split(",")[1]]
            atDirige = valor[3]
            conDb = sqlite3.connect(RUTE_DB)
            print("[USER-INFO] Got a request... Updating user info")
            cur = conDb.cursor()
            cur.execute('SELECT * FROM tokens WHERE user = "' + user + '" AND token = "' + token + '"')
            row = cur.fetchone()
            if row is not None:
                if int(row[2]) > int(time.time()):
                    # Se encuentra el usuario con la sesion iniciada
                    find = False
                    i = 0
                    for visitor in users:
                        if(visitor[0] == user):
                            find = True
                        if find == False:
                            i = i + 1
                    if find == True:
                        users[i][3][0] = int(coordenada[0])
                        users[i][3][1] = int(coordenada[1])
                        users[i][3][2] = int(atDirige)
                        users[i][4] = int(time.time())
                    if find == False:
                        users.append([row[0], row[1], row[2], [int(coordenada[0]), int(coordenada[1]), int(atDirige)], int(time.time())])
                        VISITORS = VISITORS + 1
        except: 
            print(Fore.RED + "[ERROR] Can't decrypt the message, check the key on the file config.json" + Fore.RESET)

def readConfig():
    global w_config, cryptoKey
    last_mod = -1
    while 1: 
        try:
            if last_mod == -1 or  last_mod != os.stat('./config.json').st_mtime:
                print("[INFO] Getting info from config.json...")
                with open('./config.json') as json_file:
                    data = json.load(json_file)
                    w_config[0] = data['weather']['apikey']
                    w_config[1][0] = data['weather']['city1']
                    w_config[1][1] = data['weather']['city2']
                    w_config[1][2] = data['weather']['city3']
                    w_config[1][3] = data['weather']['city4']
                    cryptoKey = data['cryptoKey']
                    
                print("[INFO] Loaded config file")
                last_mod = os.stat('./config.json').st_mtime
        except:
            print("[ERROR] Error opening the file config.json")
            quit()
        time.sleep(3)

def weatherMonitoring(): 
    global w_config, cities
    print("[WEATHER] Starting weather monitoring...")
    while(1):
        if w_config != -1:
            try:
                api_url = "http://api.openweathermap.org/data/2.5/weather?q=" + w_config[1][0] +"&appid=" + w_config[0]
                response = requests.get(api_url)
                if response.status_code == 200:
                    json = response.json()
                    temp = float(json["main"]["temp"]) - 273.15
                    if int(temp) == -1:
                        temp = -2
                    cities[0] = int(temp)
                else:
                    cities[0] = -1

                api_url = "http://api.openweathermap.org/data/2.5/weather?q=" + w_config[1][1] +"&appid=" + w_config[0]
                response = requests.get(api_url)
                if response.status_code == 200:
                    json = response.json()
                    temp = float(json["main"]["temp"]) - 273.15
                    if int(temp) == -1:
                        temp = -2
                    cities[1] = int(temp)
                else:
                    cities[1] = -1

                api_url = "http://api.openweathermap.org/data/2.5/weather?q=" + w_config[1][2] +"&appid=" + w_config[0]
                response = requests.get(api_url)
                if response.status_code == 200:
                    json = response.json()
                    temp = float(json["main"]["temp"]) - 273.15
                    if int(temp) == -1:
                        temp = -2
                    cities[2] = int(temp)
                else:
                    cities[2] = -1
                
                api_url = "http://api.openweathermap.org/data/2.5/weather?q=" + w_config[1][3] +"&appid=" + w_config[0]
                response = requests.get(api_url)
                if response.status_code == 200:
                    json = response.json()
                    temp = float(json["main"]["temp"]) - 273.15
                    if int(temp) == -1:
                        temp = -2
                    cities[3] = int(temp)
                else:
                    cities[3] = -1
            except:
                cities[0] = -1
                cities[1] = -1
                cities[2] = -1
                cities[3] = -1
            
            print("[WEATHER] The weather of the 4 cities is: " + str(cities))
        time.sleep(5)




def sendMap(): 
    global KAFKA_SERVER
    global attractions
    global users
    global cities
    producer = KafkaProducer(bootstrap_servers = KAFKA_SERVER) 
    topic = "mapinfo"
    while(1): 
        # Format at Id:tiempo:posX:posY,...#nombre:atDirige:PosX:posY~#Ciudad1:2...
        send = ""
        if len(attractions) == 0:
            send = "NONE"
        for i in range(len(attractions)):
            send = send + str(i+1) + ":" + str(attractions[i][2]) + ":" + str(attractions[i][0]) + ":" + str(attractions[i][1]) + ":" + str(attractions[i][3])
            if i != len(attractions)-1:
                send = send + ","
        send = send + "#"
        if len(users) == 0:
            send = send + "NONE"
        for i in range(len(users)):
            if(users[i][3] != -1):
                send = send + str(users[i][0]) + ":" + str(users[i][3][2]) + ":" + str(users[i][3][0]) + ":" + str(users[i][3][1])
            else:
                send = send + str(users[i][0]) + ":-1" + ":" + str(users[i][3][0]) + ":" + str(users[i][3][1])
            if i != len(users)-1:
                send = send + ","
        send = send + "#"
        for i in range(len(cities)):
            send = send + str(cities[i])
            if i != len(cities)-1:
                send = send + ":"
        if send != "-1":
            print("[MAP SENDER] Sending map to the topic: " + topic)
            send = encryptMessage(send)
        producer.send(topic, send.encode('utf-8'))
        time1 = 1 #random.randint(1, 3)
        time.sleep(time1)

def getCuadrante(x, y):
    if x >= 0 and x <= 9:
        if y >=0 and y <= 9:
            return 1
        else:
            return 3
    else: 
        if y >=0 and y <= 9:
            return 2
        else:
            return 4

def mapToDb():
    global attractions, cities
    while 1: 
        conDb = sqlite3.connect(RUTE_DB)
        cur = conDb.cursor()
        cur.execute("DELETE FROM map_attractions;")
        for i in range(len(attractions)):
            cur.execute('INSERT INTO map_attractions (X, Y, waiting, cuadrante) VALUES (' + str(attractions[i][0]) + ", " + str(attractions[i][1]) + ", " + str(attractions[i][2]) + ", " + str(attractions[i][3]) + ');')
        cur.execute("DELETE FROM map_info;")
        cur.execute("INSERT INTO map_info VALUES (" + str(int(time.time())) + ")")
        cur.execute("DELETE FROM map_cities;")
        for i in range(len(cities)):
            cur.execute('INSERT INTO map_cities (temp) VALUES (' + str(int(cities[i])) + ");")
        cur.execute("DELETE FROM map_users;")
        for i in range(len(users)):
            cur.execute('INSERT INTO map_users (at, X, Y, nombre) VALUES (' + str(int(users[i][3][2])+1) + ", " + str(users[i][3][0]) + ", " + str(users[i][3][1]) + ", '" + str(users[i][0]) + "');")
        conDb.commit()
        time.sleep(1)


def main(): 
    global ADDR
    global RUTE_DB
    global KAFKA_SERVER
    global MAX_VISITORS
    global tokens
    if len(sys.argv) == 4:
        if ":" in sys.argv[1] and ":" in sys.argv[3]:

            SERVER = sys.argv[3].split(":")[0]
            PORT = int(sys.argv[3].split(":")[1])
            ADDR = (SERVER, PORT)
            KAFKA_SERVER = sys.argv[1]
            MAX_VISITORS = int(sys.argv[2])
            
            print("[DATABASE] Connecting to data base")
            conDb = sqlite3.connect(RUTE_DB)
            cur = conDb.cursor()
            print("[DATABASE] Getting information of attractions")
            for row in cur.execute('SELECT * FROM attractions ORDER BY id'):
                estimatedTimes.append(-1)
                x = row[2]
                y = row[3]
                attractions.append([row[2], row[3], -1, getCuadrante(x, y)])
            for row in cur.execute('SELECT * FROM tokens'):
                tokens.append([row[0], row[1], row[2]])
            print("[DATABASE] There is/are " + str(len(estimatedTimes)) + " attractions")
            print("[MODULE] Starting Waiting Time Server module...")
            thread_1 = threading.Thread(target = checkIfWaitingServerIsOnline )
            thread_1.start()

            print("[MODULE] Starting Login System")
            thread_2 = threading.Thread(target = handleLoginRequest)
            thread_2.start()          

            print("[MODULE] Starting Kafka Consumer for User Info")
            thread_3 = threading.Thread(target = userinfo)
            thread_3.start()

            print("[MODULE] Starting Map Sender")
            thread_4 = threading.Thread(target = sendMap)
            thread_4.start()

            print("[MODULE] Starting Keep Alive User")
            thread_5 = threading.Thread(target = userKeepAlive)
            thread_5.start()

            print("[MODULE] Starting Configure Manager")
            thread_7 = threading.Thread(target = readConfig)
            thread_7.start()

            time.sleep(1)
            print("[MODULE] Starting Weather Monitoring")
            thread_6 = threading.Thread(target = weatherMonitoring)
            thread_6.start()

            thread_db = threading.Thread(target = mapToDb)
            thread_db.start()

        else:
            print("Incorrect usage -> FWQ_Engine ip:port(Kafka) MaxVisitors ip:port(FWQ_WaitingTimeServer) ")
    else:
        print("Incorrect usage -> FWQ_Engine ip:port(Kafka) MaxVisitors ip:port(FWQ_WaitingTimeServer) ")


if __name__ == "__main__":
    main()
