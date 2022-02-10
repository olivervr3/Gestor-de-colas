from kafka import KafkaConsumer
import sys
import random
import threading
import time as time 
import socket
import json
from datetime import datetime

# DEFAULT
topic = "sensorinfo"
HEADER = 64
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 10

et = list()
updatedTimes = list()



# Calculadora de tiempos
def calculateTimes(attractions, kafkaServer): 
    global et
    consumer = KafkaConsumer('sensorinfo',bootstrap_servers=kafkaServer)
    for message in consumer: 
        valor = message.value.decode(FORMAT)
        valor = valor.split(":")
        atId = int(valor[0])
        atValue = int(valor[1])
        if atId <= len(et):
            estimatedTime = int(atValue/attractions[atId-1][2])*attractions[atId-1][1]
            et[atId-1] = estimatedTime
            updatedTimes[atId-1] = datetime.now()
            print("[TIMES] The attraction " + str(atId) + " has a estimated time of " + str(int(atValue/attractions[atId-1][2])*attractions[atId-1][1]) + " mins")


# Keep Alive con los sensores
def keepAlive():
    global updatedTimes
    global et
    while(1): 
        for i in range(len(updatedTimes)):
            if(et[i] != -1):
                date1 = updatedTimes[i]
                dateNow = datetime.now()
                dif = (dateNow-date1).total_seconds()
                if dif >= 5:
                    print("[KEEP ALIVE] Connection lost with sensor id = " + str(i+1))
                    et[i] = -1
        time.sleep(1)

# Imprimir los tiempos
def printList():
    global et
    while(1):
        print("[INFO] Estimated times: ", end = "")
        print(et)
        time.sleep(10)

# Send info
def sendInfo(conn, addr):
    print(f"[SERVER] {addr} connected.")
    global et

    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == "info":
                    msg_send = ""
                    for i in range(len(et)):
                        msg_send = msg_send + str(et[i])
                        if i != len(et)-1:
                            msg_send = msg_send + ":"
                    conn.send(f"{msg_send}".encode(FORMAT))
                    print("[SERVER] Sending the information!")

                elif msg == "exit":
                    connected = False
                elif msg == "keepalive":
                    conn.send(f"1".encode(FORMAT))
                else:
                    conn.send(f"Please type info to get all the estimated times or exit!".encode(FORMAT))
        except:
            print("[SERVER] Connection closed by the client :(")
            connected = False
            
    print("[SERVER] Disconnected user")
    conn.close()



        



def main(): 
    global et
    global updatedTimes
    if len(sys.argv) == 3:
        if ":" in sys.argv[2]:
            kafkaServer = sys.argv[2]
            SERVER = socket.gethostbyname(socket.gethostname())
            PORT = int(sys.argv[1])
            print("[INFO] Launching server on " + SERVER + " connecting with Kafka on: " + kafkaServer)
            print("[INFO] Reading information of attractions.json...")
            try:
                print("[INFO] Getting info from attractions.json...")
                attractions = list()
                with open('./config/attractions.json') as json_file:
                    data = json.load(json_file)
                    for p in data['attractions']:
                        attractions.append([p["id"], p["cycleTime"], p["cycleUsers"]])
                print("[INFO] Loaded " + str(len(attractions)) + " attraction/s")
            except:
                print("[ERROR] Error opening the file attractions.json")
                quit()
            
            for i in range(len(attractions)):
                et.append(-1)
                updatedTimes.append(0)



            thread_calculateTimes = threading.Thread(target= calculateTimes, args = (attractions,kafkaServer,))
            thread_calculateTimes.start()

            thread_keepAlive = threading.Thread(target= keepAlive)
            thread_keepAlive.start()

            thread_print = threading.Thread(target= printList)
            thread_print.start()


            ADDR = (SERVER, PORT)
            print("[SERVER] Starting Socket Server on " + SERVER)
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(ADDR)
            CONEX_ACTIVAS = threading.active_count()-4
            server.listen()
            print("[SERVER] Active connections: " + str(CONEX_ACTIVAS))
            while (1):
                conn, addr = server.accept()
                CONEX_ACTIVAS = threading.active_count()-3
                #print("[SERVER] Active connections: " + str(CONEX_ACTIVAS))
                if(CONEX_ACTIVAS <= MAX_CONEXIONES):
                    print("[SERVER] Starting client handling...")
                    print("[SERVER] Active connections: " + str(CONEX_ACTIVAS))
                    thread = threading.Thread(target=sendInfo, args=(conn, addr))
                    thread.start()

                else:
                    print("[ERROR] Active connections limit exceeded")
                    conn.send("ACTIVE_CONNECTIONS_LIMIT_EXCEEDED".encode(FORMAT))
                    conn.close()
                    CONEX_ACTUALES = threading.active_count()-4
        else:
            print("Incorrect usage -> FWQ_WaitingTimeServer serverPort ip:port(Kafka) ")
    else:
        print("Incorrect usage -> FWQ_WaitingTimeServer serverPort ip:port(Kafka)")


if __name__ == "__main__":
    main()
