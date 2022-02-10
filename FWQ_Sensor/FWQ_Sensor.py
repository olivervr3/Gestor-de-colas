from kafka import KafkaProducer
import sys
import random
import threading
import time as time 

# DEFAULT
users = 0 
topic = "sensorinfo"
sensorId = -1

# Funcion que calcula cuantos usuarios hay
def sensorUsers():
    global users
    while(1):
        try: 
            res = input()
            if int(res) <= 0: 
                # gen random number
                users = random.randint(0, 200)
            else:
                users = int(res)
            
            print("[USER MANAGER] There is/are " + str(users) + " waiting right now!")
        except:
            print("[ERROR] Type a natural number")

# Funcion que envia los datos al gestor de Colas
def sendInfo(producer): 
    while(1): 
        send = str(sensorId) + ":" + str(users)
        print("[INFO] Sending the info: " + send + " to the topic: " + topic)
        producer.send(topic, send.encode('utf-8'))
        time1 = 1
        time.sleep(time1)


def main(): 
    global sensorId
    global users
    if len(sys.argv) == 3:
        if ":" in sys.argv[1]:
            sensorId = int(sys.argv[2])
            if sensorId >= 0:
                print("[INFO] Launching sensor on " + str(sensorId) + " attraction, connection to " + sys.argv[1])

                producer = KafkaProducer(bootstrap_servers = sys.argv[1])
                print("[USER MANAGER] Setting random users on the attraction ")
                users = random.randint(0, 200)
                print("[USER MANAGER] By default there is " + str(users) + " users waiting right now")

                thread_sensorUsers = threading.Thread(target=sensorUsers)
                thread_sensorUsers.start()
                thread_sendInfo = threading.Thread(target= sendInfo, args = (producer,))
                thread_sendInfo.start()
                
            else:
                print("The id has to be > 0")
        else:
            print("Incorrect usage -> FWQ_Sensor ip:port attractionId ")
    else:
        print("Incorrect usage -> FWQ_Sensor ip:port attractionId")


if __name__ == "__main__":
    main()
