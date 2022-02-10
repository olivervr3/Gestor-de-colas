import sys
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
import json
import time

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

RUTE_DB = "./bd/basededatos.db"

# REGISTRO
@app.route('/map/attractions', methods=['GET'])
def getAttractions():
    conDb = sqlite3.connect(RUTE_DB)
    cur = conDb.cursor()
    attractions = {
        "attractions": []
    }
    e = list()
    for row in cur.execute('SELECT * FROM map_attractions'):
        x = {
            "id": row[0],
            "X": row[1],
            "Y": row[2],
            "et": row[3],
            "cuadrante": row[4]
        }
        e.append(x)

    attractions["attractions"] = e
    conDb.close()
    return(jsonify(attractions)), 200   


@app.route('/map/users', methods=['GET'])
def getUsers():
    conDb = sqlite3.connect(RUTE_DB)
    cur = conDb.cursor()
    users = {
        "users": []
    }
    e = list()
    for row in cur.execute('SELECT * FROM map_users'):
        x = {
            "id": row[0],
            "at": row[1],
            "X": row[2],
            "Y": row[3],
            "nombre": row[4]
        }
        e.append(x)

    users["users"] = e
    conDb.close()
    return(jsonify(users)), 200   

@app.route('/map/cities', methods=['GET'])
def getCities():
    conDb = sqlite3.connect(RUTE_DB)
    cur = conDb.cursor()
    cities = {
        "cities": []
    }
    e = list()
    for row in cur.execute('SELECT * FROM map_cities'):
        x = {
            "id": row[0],
            "temp": row[1],
        }
        e.append(x)

    cities["cities"] = e
    conDb.close()
    return(jsonify(cities)), 200   

@app.route('/map/info', methods=['GET'])
def getInfo():
    conDb = sqlite3.connect(RUTE_DB)
    cur = conDb.cursor()

    cur =  cur.execute('SELECT * FROM map_info')
    row = cur.fetchone()
    tiempo = int(row[0])
    conDb.close()

    if(time.time()-tiempo > 10):
        return jsonify({"online": 0}), 200
    else:
        return jsonify({"online": 1}), 200

@app.route('/map', methods=['GET'])
def getAll():
    conDb = sqlite3.connect(RUTE_DB)
    cur = conDb.cursor()

    cur =  cur.execute('SELECT * FROM map_info')
    row = cur.fetchone()
    tiempo = int(row[0])
    map = {}

    if(time.time()-tiempo > 10):
        map["online"] = 0
    else:
        map["online"] = 1


    e = list()
    for row in cur.execute('SELECT * FROM map_attractions'):
        x = {
            "id": row[0],
            "X": row[1],
            "Y": row[2],
            "et": row[3],
            "cuadrante": row[4]
        }
        e.append(x)

    map["attractions"] = e

    e = list()
    for row in cur.execute('SELECT * FROM map_users'):
        x = {
            "id": row[0],
            "at": row[1],
            "X": row[2],
            "Y": row[3],
            "nombre": row[4]
        }
        e.append(x)

    map["users"] = e

    e = list()
    for row in cur.execute('SELECT * FROM map_cities'):
        x = {
            "id": row[0],
            "temp": row[1],
        }
        e.append(x)

    map["cities"] = e

    return jsonify(map), 200


# run
if __name__ == '__main__':
    app.run(host=sys.argv[1].split(":")[0], port=int(sys.argv[1].split(":")[1]),ssl_context=('./cert/cert.pem', './cert/key.pem'))