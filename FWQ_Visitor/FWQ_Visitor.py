from kafka import KafkaConsumer, KafkaProducer, consumer
import sys
import random
import threading
import time as time 
import socket
import json
from datetime import datetime
import numpy as np
import os
from colorama import Fore, Back, Style
from cryptography.fernet import Fernet
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)

TOKEN = ""
TOKEN_END = 0

cryptoKey = "-1"
mapNotLegible = False

# DEFAULT
topic = "sensorinfo"
HEADER = 64
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 2

STOP = False

MAP_BASE = [["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ], 
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ], 
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ],
["-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t", "-\t" ]]


ATTRACTIONS = list()
USERS = list()
USERNAME = list()
TARGET_ATRACCION = -1
ATRACTION_ACTUAL = -1
MY_USERNAME = ""
MY_TOKEN = ""
LAST_TIMESTAMP = -1
res1 = 0
WEATHER = [-1, -1, -1, -1]



COORDENADAS_ACTUALES = [random.randint(0,19), random.randint(0,19)]

PARQUE_ONLINE = 0 # 0 no ha llegado informacion, -1 se ha perdido conexion, 1 online


KAFKA_SERVER = ""


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

def keepAlivePark():
    global PARQUE_ONLINE, LAST_TIMESTAMP
    while 1: 
        ahora = int(time.time())
        resta = ahora - LAST_TIMESTAMP
        if(LAST_TIMESTAMP == -1):
            resta = 0
        if(resta > 10) or mapNotLegible:
            PARQUE_ONLINE = -1
        time.sleep(3)
    


def getTarget():
    while 1:
        global TARGET_ATRACCION, WEATHER
        if TARGET_ATRACCION == -1: 
            # no existe ninguna atraccion
            posibles = list()
            if len(ATTRACTIONS) > 0: 
                #hay atracciones
                #print(ATTRACTIONS)
                for a in range(len(ATTRACTIONS)):
                    if ATTRACTIONS[a][1] <= 60 and ATTRACTIONS[a][1] != -1:
                        #print("añado la " + str(a))
                        cuadrante = int(ATTRACTIONS[a][4])-1
                        temp = int(WEATHER[cuadrante])
                        if(temp >= 20 and temp <= 30):
                            posibles.append(a)
            if len(posibles) <= 0:
                print("No hay atracciones disponibles")
            else:
                don = random.randint(0, (len(posibles)-1))
                TARGET_ATRACCION = posibles[don]
        else:
            if(ATTRACTIONS[TARGET_ATRACCION-1][1] > 60):
                # ha aumentado el tiempo
                TARGET_ATRACCION = -1 
            cuadrante = int(ATTRACTIONS[TARGET_ATRACCION-1][4])-1
            temp = int(WEATHER[cuadrante])
            if(temp >= 20 and temp <= 30) or temp == -1:
                TARGET_ATRACCION = -1
        time.sleep(5)

def move():
    global ATRACTION_ACTUAL
    global COORDENADAS_ACTUALES
    global ATTRACTIONS
    global TARGET_ATRACCION
    global mapNotLegible
    while 1:
        if TARGET_ATRACCION != -1 and PARQUE_ONLINE != -1 and mapNotLegible == False:
            # suponemos que hay una atraccion.
            aX = ATTRACTIONS[TARGET_ATRACCION][2]
            aY = ATTRACTIONS[TARGET_ATRACCION][3]
            cX = COORDENADAS_ACTUALES[0]
            cY = COORDENADAS_ACTUALES[1]
            newX = 0
            newY = 0
            if aY < cY:
                newY = -1
            if aY > cY:
                newY = +1
            if aX < cX:
                newX = -1
            if aX > cX:
                newX = +1
            if(newX == 0) and newY == 0:
                #Estamos en la posicion de la atraccion
                ATRACTION_ACTUAL = TARGET_ATRACCION
                TARGET_ATRACCION = -1 
                time.sleep(10)
            
            COORDENADAS_ACTUALES[0] = cX + newX
            COORDENADAS_ACTUALES[1] = cY + newY
        
        time.sleep(2)

def sendInfoToEngine():
    global mapNotLegible
    producer = KafkaProducer(bootstrap_servers = KAFKA_SERVER) 
    while 1: 
        # usuario:token:3,1:1
        if mapNotLegible == False:
            send = MY_USERNAME + ":" + MY_TOKEN + ":" + str(COORDENADAS_ACTUALES[0]) + "," + str(COORDENADAS_ACTUALES[1]) + ":" + str(TARGET_ATRACCION)
            send = encryptMessage(send)
            if send != "-1":
                producer.send("userinfo", send.encode(FORMAT))
        time.sleep(1)           




def getInfoMap(): 
    global ATTRACTIONS, USERS, LAST_TIMESTAMP, PARQUE_ONLINE, WEATHER, mapNotLegible
    consumer = KafkaConsumer("mapinfo", bootstrap_servers = KAFKA_SERVER)
    for message in consumer: 
        try:
            mapNotLegible = False
            value = message.value
            value = decryptMessage(value)
            value = value.split("#")

            PARQUE_ONLINE = 1
            LAST_TIMESTAMP = int(time.time())
            # Atracciones
            attractionString = value[0]
            attractionString = attractionString.split(",")
            at_list = list()
            for at in attractionString:
                res = at.split(":")
                at_list.append([int(res[0]), int(res[1]), int(res[2]), int(res[3]), int(res[4])])
            ATTRACTIONS = at_list
            # Usuarios
            userString = value[1]
            us_list = list()
            if "," in userString:
                userString = userString.split(",")
                for us in userString:
                    res = us.split(":")
                    us_list.append([res[0], int(res[1]), int(res[2]), int(res[3])])
            elif userString != "NONE":
                res = userString.split(":")
                us_list.append([res[0], int(res[1]), int(res[2]), int(res[3])])
            
            #Tiempo
            tiempo = value[2]
            tiempoString = tiempo.split(":")
            WEATHER[0] = tiempoString[0]
            WEATHER[1] = tiempoString[1]
            WEATHER[2] = tiempoString[2]
            WEATHER[3] = tiempoString[3] 

            USERS = us_list
        except Exception as e:
            mapNotLegible = True
            

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

def printMap():
    global USERS, ATTRACTIONS 
    global LAST_TIMESTAMP, mapNotLegible
    while 1:
        if  PARQUE_ONLINE == 1:
            MAP = np.copy(MAP_BASE)
            MAPat = np.copy(MAP_BASE)
            for u in USERS:
                if u[0] != MY_USERNAME:
                    if len(u[0]) > 1:
                        MAP[u[3]][u[2]] = u[0][0:2]
                    else:
                        MAP[u[3]][u[2]] = u[0]
            for a in ATTRACTIONS:
                if a[1] == -1:
                    MAPat[a[3]][a[2]] = "?"
                else:
                    MAPat[a[3]][a[2]] = str(a[1]) + " "
                
            #MAP[COORDENADAS_ACTUALES[1]][COORDENADAS_ACTUALES[0]] = "YO"

            clear = lambda: os.system('cls')
            clear()
            print(Fore.GREEN + "\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14\t15\t16\t17\t18\t19\t20")
            print(Fore.GREEN + "==============================================================================================================================================================================")
            for i in range(20):
                print(Fore.GREEN + str(i+1) + "|\t" + Fore.RESET, end = "")
                for j in range(20):
                    cuadrante = getCuadrante(i, j)
                    if cuadrante == 2:
                        cuadrante = 3
                    elif cuadrante == 3:
                        cuadrante = 2
                    temp = int(WEATHER[(cuadrante-1)])
                    if(temp == -1):
                        print(Fore.YELLOW, end="")
                    elif(temp < 20 or temp > 30):
                        print(Fore.RED, end="")
                    else:
                        print(Fore.WHITE, end="")
                    #print(MAP[i][j], end ="")

                    # Me encuentro en el usuario (YO)
                    if i == COORDENADAS_ACTUALES[1] and j == COORDENADAS_ACTUALES[0]:
                        print(Fore.YELLOW + "YO" + Fore.RESET, end = "")
                        if MAP[i][j] != "-\t":
                            print("|" + Fore.GREEN + MAP[i][j] + Fore.RESET, end = "")
                        if MAPat[i][j] != "-\t":
                            if MAPat[i][j] == "?":
                                print("|" + Fore.RED + Back.WHITE + MAPat[i][j] + Fore.RESET + Back.RESET + "\t", end = "")
                            else:
                                print("|" + Fore.CYAN + MAPat[i][j] + Fore.RESET + "\t", end = "")
                        else:
                            print("\t", end = "")
                    # Hay una atraccion
                    elif MAPat[i][j] != "-\t":
                        if MAP[i][j] != "-\t":
                            print(Fore.GREEN + MAP[i][j] + Fore.RESET + "|", end = "")
                        if MAPat[i][j] == "?":
                            print(Fore.RED + Back.WHITE +  MAPat[i][j] + Fore.RESET + Back.RESET + "\t", end = "")
                        else:
                            print(Fore.CYAN + MAPat[i][j] + Fore.RESET + "\t", end = "")
                    # Hay un usuario
                    elif MAP[i][j] != "-\t":
                        print(Fore.GREEN + MAP[i][j] + Fore.RESET + "\t", end = "")
                    else:
                        if(temp == -1):
                            print("?\t", end = "")
                        elif(temp < 20 or temp > 30):
                            print("X\t", end = "")
                        else:
                            print("-\t", end = "")
                        
                    
                print("")     
                print("")


            print("" + Fore.RESET)
            print("USUARIO\t\tPOSICION ACTUAL\t\tDESTINO\t\t")
            print("YO\t\t" + "[" + str(COORDENADAS_ACTUALES[0]+1) + ", " + str(COORDENADAS_ACTUALES[1]+1) + "]" + "\t\t\t", end="")
            if TARGET_ATRACCION != -1:
                print("[" + str(ATTRACTIONS[TARGET_ATRACCION][2]+1) + ", " + str(ATTRACTIONS[TARGET_ATRACCION][3]+1) + "]")
            else:
                print("None")
            for u in USERS:
                if u[0] != MY_USERNAME:
                    if len(u[0]) > 1:
                        print(u[0][0:2] + "\t\t",  end="")
                    else:
                        print(u[0] + "\t\t", end="")
                    print("[" + str(u[2]+1) + ", " + str(u[3]+1) + "]" + "\t\t\t", end="")
                    if u[3] != -1:
                        print("[" + str(ATTRACTIONS[u[1]][2]+1) + ", " + str(ATTRACTIONS[u[1]][3]+1) + "]")     
                        
                    else:
                        print("None")
            print(Fore.GREEN + "TIEMPO" + Fore.RESET)

            if int(WEATHER[0]) == -1:
                print(Fore.YELLOW + "Cuadrante 1 ARRIBA IZQUIERDA: ¡¡SIN INFORMACION!!")
            elif int(WEATHER[0]) < 20 or int(WEATHER[0]) > 30:
                print(Fore.RED + "Cuadrante 1 ARRIBA IZQUIERDA: ¡¡CERRADO POR LA TEMPERATURA!!: " + str(WEATHER[0]) + "ºC")
            else:
                print(Fore.BLUE + "Cuadrante 1 ARRIBA IZQUIERDA: " + Fore.WHITE + str(WEATHER[0]))

            if int(WEATHER[1]) == -1:
                print(Fore.YELLOW + "Cuadrante 2 ARRIBA DERECHA: ¡¡SIN INFORMACION!!")
            elif int(WEATHER[1]) < 20 or int(WEATHER[1]) > 30:
                print(Fore.RED + "Cuadrante 2 ARRIBA DERECHA: ¡¡CERRADO POR LA TEMPERATURA!!: " + str(WEATHER[1]) + "ºC")
            else:
                print(Fore.BLUE + "Cuadrante 2 ARRIBA DERECHA: " + Fore.WHITE + str(WEATHER[1]))
            
            if int(WEATHER[2]) == -1:
                print(Fore.YELLOW + "Cuadrante 3 ABAJO IZQUIERDA: ¡¡SIN INFORMACION!!")
            elif int(WEATHER[2]) < 20 or int(WEATHER[2]) > 30:
                print(Fore.RED + "Cuadrante 3 ABAJO IZQUIERDA: ¡¡CERRADO POR LA TEMPERATURA!!: " + str(WEATHER[2]) + "ºC")
            else:
                print(Fore.BLUE + "Cuadrante 3 ABAJO IZQUIERDA: " + Fore.WHITE + str(WEATHER[2]))

            if int(WEATHER[3]) == -1:
                print(Fore.YELLOW + "Cuadrante 4 ABAJO DERECHA: ¡¡SIN INFORMACION!!")
            elif int(WEATHER[3]) < 20 or int(WEATHER[3]) > 30:
                print(Fore.RED + "Cuadrante 4 ABAJO DERECHA: ¡¡CERRADO POR LA TEMPERATURA!!: " + str(WEATHER[3]) + "ºC")
            else:
                print(Fore.BLUE + "Cuadrante 4 ABAJO DERECHA: " + Fore.WHITE + str(WEATHER[3]))

                    
        elif PARQUE_ONLINE == 0:
    
            clear = lambda: os.system('cls')
            clear()
            print(Fore.GREEN)
            print("Esperando información del mapa por parte del servidor... " + Fore.RESET)
        else:
            clear = lambda: os.system('cls')
            clear()
            print(Fore.RED)
            print("Se ha perdido la conexion con el servidor... Esperando..." + Fore.RESET)

        if(mapNotLegible == True):
            print("")
            print(Fore.RED)
            print("La informacion que llega no es legible prueba revisando tu clave" + Fore.RESET)

        time.sleep(2)       


# Funcion que envia los datos del token mientras este no se ha recibido
def getToken(send):
    global MY_TOKEN, STOP, mapNotLegible
    while MY_TOKEN == "" and STOP == False:
        if MY_TOKEN == "" and mapNotLegible == False:
            producer = KafkaProducer(bootstrap_servers = KAFKA_SERVER) 
            send = encryptMessage(send)
            if send != "-1":
                producer.send("logindetails", send.encode(FORMAT))
            producer.close()
        time.sleep(3)


def updateToken(user): 
    global res1, MY_TOKEN, MY_USERNAME, TOKEN_END, STOP
    consumer = KafkaConsumer('logintoken',bootstrap_servers=KAFKA_SERVER)
    for message in consumer: 
        # usuario:token:3,1:1
        try:
            if STOP == True: 
                break
            valor = message.value
            valor = decryptMessage(valor)
            valor = valor.split(":")
            
            if(user == valor[0]):
                res1 = int(valor[1])
                MY_TOKEN = valor[2]
                MY_USERNAME = user
                if res1 == 1:
                    TOKEN_END = valor[3]
                break
        except:
            mapNotLegible = True
            break
            
def getKey():
    global cryptoKey
    last_mod = -1
    while 1: 
        try:
            if last_mod == -1 or  last_mod != os.stat('./key').st_mtime:
                print("[INFO] Getting key...")
                f = open("key", "r")
                cryptoKey = f.read().encode()
                last_mod = os.stat("./key").st_mtime
        except:
            print("[ERROR] Error opening the file key")
            quit()
        time.sleep(3)



def socketSend(client, msg): 
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
        
    
def editUser(host, port):
    ADDR_REGISTRO = (host, port)

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR_REGISTRO)
        print (f"Establecida conexión en [{ADDR_REGISTRO}]")



        print("")
        print("¿Qué desea modificar?")
        print("1 - Nombre de usuario")
        print("2 - Contraseña")
        print("3 - Salir")

        option = input()


        if option=='1':

            print("Nombre de usuario: ")
            usuario = input()
            print("Contraseña: ")
            password = input()
            print("Nombre de usuario nuevo: ")
            new_username = input()
            user_info = [1, usuario, password, new_username, 1]
            # print("Envio al servidor: ", usuario, password, new_username)

            socketSend(client, str(user_info))

            recibido = client.recv(2048).decode(FORMAT)

            if (recibido == "1"):
                print("PERFIL ACTUALIZADO")

            elif (recibido == "0"):
                print("USUARIO/CONTRASEÑA INCORRECTA")

        elif option=='2':

            contra = ""
            password_new = "/"
            print("Nombre de usuario: ")
            usuario = input()
            print("Contraseña: ")
            password = input()

            while contra != password_new:
                print("Contraseña nueva: ")
                contra = input()
                print("Repetir contraseña:")
                password_new = input()
                if(contra != password_new):
                    print("Las contraseñas no coinciden")



            user_info = [1, usuario, password, password_new, 2]
            print("Envio al servidor: ", usuario, password, password_new)
            socketSend(client, str(user_info))
            recibido2 = client.recv(2048).decode(FORMAT)

            if (recibido2 == "1"):
                print("PERFIL ACTUALIZADO")


            elif (recibido2 == "0"):
                print("USUARIO/CONTRASEÑA INCORRECTA")     

    except:
        print("Error al conectar con el servidor de Registro")

    client.close()

def registro(host, port):
    try:
        ADDR_REGISTRO = (host, port)  
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR_REGISTRO)

        print (f"Establecida conexión en [{ADDR_REGISTRO}]")


        print("Nombre de usuario: ")
        usuario = input()
        contra = "1"
        password = "2"
        while contra != password:
            print("Contraseña: ")
            password = input()
            print("Repetir contraseña: ")
            contra = input()
            if(contra != password):
                print("Las contraseñas no coinciden")

        user_info = [0, usuario, password]
        socketSend(client, str(user_info))

        if(client.recv(2048).decode(FORMAT) == "1"):
            print("USUARIO CREADO")
        elif client.recv(2048).decode(FORMAT) == "0":
            print("USUARIO YA EXISTE")

    except:
        print("Error al conectar con el servidor de Registro")
    client.close()

def registroAPI(host):
    try:
        print("Nombre de usuario: ")
        usuario = input()
        contra = "1"
        password = "2"
        while contra != password:
            print("Contraseña: ")
            password = input()
            print("Repetir contraseña: ")
            contra = input()
            if(contra != password):
                print("Las contraseñas no coinciden")


        response = requests.post("https://" + host + "/users", json={"name":usuario,"email":password}, verify='cert.pem')
        print(response)
        responseObj = response.json()

        if(responseObj == {"user":"registered."}):
            print("USUARIO CREADO")
        else:
            print("USUARIO YA EXISTE")

    except:
       print("Error al conectar con el servidor de Registro")

def editUserAPI(host):
    try:
        print("")
        print("¿Qué desea modificar?")
        print("1 - Nombre de usuario")
        print("2 - Contraseña")
        print("3 - Salir")

        option = input()


        if option=='1':

            print("Nombre de usuario: ")
            usuario = input()
            print("Contraseña: ")
            password = input()
            print("Nombre de usuario nuevo: ")
            new_username = input()

            response = requests.put("https://" + host + "/users", json={"option":option,"newname":new_username,"name":usuario,"email":password}, verify='cert.pem')
            print(response)
            responseObj = response.json()

            if (responseObj == {"user":"updated."}):
                print("PERFIL ACTUALIZADO")
            else:
                print("USUARIO/CONTRASEÑA INCORRECTA")
            
        if option=='2':

            print("Nombre de usuario: ")
            usuario = input()
            print("Contraseña: ")
            password = input()
            print("Contraseña nueva: ")
            new_password = input()

            response = requests.put("https://" + host +"/users", json={"option":option,"newpass":new_password,"name":usuario,"email":password}, verify='cert.pem')
            print(response)
            responseObj = response.json()

            if (responseObj == {"user":"updated."}):
                print("PERFIL ACTUALIZADO")
            else:
                print("USUARIO/CONTRASEÑA INCORRECTA")
                
    except:
        print("Error al conectar con el servidor de Registro")



def main(): 
    global et, res1, STOP
    global KAFKA_SERVER
    global updatedTimes
    global MY_TOKEN, MY_USERNAME
    if len(sys.argv) == 4:
        if ":" in sys.argv[1] and ":" in sys.argv[2] and ":" in sys.argv[3]:
            opcion = ""
            while(opcion != "6"):
                print("##########################################################################################################")
                print("## BIENVENIDO AL RESORT                                                                                 ##")
                print("##                                                                                                      ##")
                print("## Menu:                                                                                                ##")                                                                                                #")
                print("## 1. Entrar al parque                                                                                  ##")
                print("## 2. Editar perfil    (SOCKET)                                                                         ##")
                print("## 3. Registrarse (SOCKET)                                                                              ##")
                print("## 4. Registrarse (API)                                                                                 ##")
                print("## 5. Modificar perfil (API)                                                                            ##")
                print("## 6. Salir                                                                                             ##")
                print("##########################################################################################################")
                print("Introduce la opcion que quieras hacer: ")

                KAFKA_SERVER = sys.argv[2]
                res = input()
                opcion = res
                if res == "1": 
                    thread_key = threading.Thread(target=getKey)
                    thread_key.start()
                    print("Introduce tu nombre de usuario: ")
                    user = input()
                    print("Introduce tu contraseña: ")
                    password = input()
                    print("Estableciendo conexion con el parque...")
                    
                    send = user + ":" + password

                    MY_TOKEN = ""
                    res1 = -1
                    STOP = False
                    thread_Token = threading.Thread(target=getToken, args=(send,))
                    thread_Token.start()
                    
                    thread_Token2 = threading.Thread(target= updateToken, args = (user,))
                    thread_Token2.start()


                    # Esperamos a ver si recibimos el token
                    i = 0
                    while MY_TOKEN == "" and i < 11:
                        i = 1 + i
                        time.sleep(1)
                    time.sleep(1)
                    STOP = True
                    if(res1 == 1):
                        print("Success! La sesion expirara en " + str(int(int(TOKEN_END)-int(time.time()))) + " segundos!")
                        thread_1 = threading.Thread(target = getInfoMap)
                        thread_1.start()
                        time.sleep(2)

                        thread_2 = threading.Thread(target = printMap)
                        thread_2.start()
                        thread_3 = threading.Thread(target = getTarget)
                        thread_3.start()
                        thread_4 = threading.Thread(target = move)
                        thread_4.start()
                        thread_5 = threading.Thread(target= sendInfoToEngine)
                        thread_5.start()
                        thread_6 = threading.Thread(target = keepAlivePark)
                        thread_6.start()
                    else:
                        if mapNotLegible == True:
                            print("No se puede leer el mapa, identifica tu key")
                        if MY_TOKEN == "":
                            print("No se puede conectar con el servidor, esta apagado")
                        else:
                            print("Error! Obtuve el mensaje del parque: " + MY_TOKEN)
                elif res == "2": 
                    editUser(sys.argv[1].split(":")[0], int(sys.argv[1].split(":")[1]))
                elif res == "3":
                    registro(sys.argv[1].split(":")[0], int(sys.argv[1].split(":")[1]))
                elif res == "4":
                    registroAPI(sys.argv[3])
                elif res == "5": 
                    editUserAPI(sys.argv[3])
        else:
            print("Incorrect usage -> FWQ_Visitor ip:port(Registry) ip:port(Kafka) ip:port(API) ")
    else:
        print("Incorrect usage -> FWQ_Visitor ip:port(Registry) ip:port(Kafka) ip:port(API)")


if __name__ == "__main__":
    main()
