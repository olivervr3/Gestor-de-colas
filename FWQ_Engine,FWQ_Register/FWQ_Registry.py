import sys
import socket 
import threading
import sqlite3


HEADER = 64
PORT = int(sys.argv[1])
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FIN = "FIN"
MAX_CONEXIONES = 10

def handle_client(conn, addr):

    print(f"[NUEVA CONEXION] {addr} connected.")
    i = 0
    connected = True
    
    msg_length = conn.recv(HEADER).decode(FORMAT)
    try:
        msg_length = int(msg_length)
    except:
        msg_length = 0
    data = conn.recv(msg_length).decode(FORMAT)
    user_info = eval(data)
    print(user_info)
    if user_info[0]==0:
        # Crear usuario
        try:  
            sqliteConnection = sqlite3.connect('./bd/basededatos.db')
            cursor = sqliteConnection.cursor()
            print("[DATABASE] Successfully Connected to SQLite")
            cursor.execute('''insert into users(username,password) values (?,?);''',(user_info[1], user_info[2]))
            sqliteConnection.commit()
            print("[USER MANAGER] USUARIO CREADO")
            conn.send("1".encode(FORMAT))
            cursor.close()
        except sqlite3.Error as error:
            print("[USER MANAGER] USUARIO YA EXISTE")
            conn.send("0".encode(FORMAT))
            print("Error while connecting to sqlite", error)
        finally:
            if sqliteConnection:
                sqliteConnection.close()
                print("The SQLite connection is closed")
    elif user_info[0]==1:
        # Editar perfil
        if user_info[4]==1:
            # Editar nombre de usuario
            try:
                sqliteConnection = sqlite3.connect('./bd/basededatos.db')
                cursor = sqliteConnection.cursor()
                print("Successfully Connected to SQLite")

                userNew = [user_info[3], user_info[1], user_info[2]]
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = (?) AND password = (?)", (userNew[1],userNew[2]))
                sqliteConnection.commit()
                data = cursor.fetchall()
                print(data)
                if data==[(0,)]:
                    raise sqlite3.Error()
                print("USUARIO LOGGEADO")
                cursor.execute("UPDATE users SET username = (?) WHERE username = (?) AND password = (?)", userNew)
                sqliteConnection.commit()
                conn.send("1".encode(FORMAT))
                cursor.close()
            except sqlite3.Error as error:
                print("USUARIO/CONTRASEÑA INCORRECTA")
                conn.send("0".encode(FORMAT))
                print("Error while connecting to sqlite", error)
            finally:
                if sqliteConnection:
                    sqliteConnection.close()
                    print("The SQLite connection is closed")
        elif user_info[4]==2:
            # Editar password de usuario
            try:
                sqliteConnection = sqlite3.connect('./bd/basededatos.db')
                cursor = sqliteConnection.cursor()
                print("Successfully Connected to SQLite")

                userNew = [user_info[3], user_info[1], user_info[2]]
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = (?) AND password = (?)", (userNew[1],userNew[2]))
                sqliteConnection.commit()
                data = cursor.fetchall()
                print(data)
                if data==[(0,)]:
                    raise sqlite3.Error()
                print("USUARIO LOGGEADO")
                cursor.execute("UPDATE users SET password = (?) WHERE username = (?) AND password = (?)", userNew)
                sqliteConnection.commit()
                conn.send("1".encode(FORMAT))
                cursor.close()
            except sqlite3.Error as error:
                print("USUARIO/CONTRASEÑA INCORRECTA")
                conn.send("0".encode(FORMAT))
                print("Error while connecting to sqlite", error)
            finally:
                if sqliteConnection:
                    sqliteConnection.close()
                    print("The SQLite connection is closed")               
        return

    print("ADIOS. TE ESPERO EN OTRA OCASION")
    conn.close()
    
        

def start():
    server.listen()
    print(f"[LISTENING] Servidor a la escucha en {SERVER}")
    CONEX_ACTIVAS = threading.active_count()-1
    print(CONEX_ACTIVAS)
    while True:
        conn, addr = server.accept()
        CONEX_ACTIVAS = threading.active_count()
        if (CONEX_ACTIVAS <= MAX_CONEXIONES): 
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[CONEXIONES ACTIVAS] {CONEX_ACTIVAS}")
            print("CONEXIONES RESTANTES PARA CERRAR EL SERVICIO", MAX_CONEXIONES-CONEX_ACTIVAS)
        else:
            print("OOppsss... DEMASIADAS CONEXIONES. ESPERANDO A QUE ALGUIEN SE VAYA")
            conn.send("OOppsss... DEMASIADAS CONEXIONES. Tendrás que esperar a que alguien se vaya".encode(FORMAT))
            conn.close()
            CONEX_ACTUALES = threading.active_count()-1
        

######################### MAIN ##########################


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

print("[STARTING] Servidor inicializándose...")

start()
