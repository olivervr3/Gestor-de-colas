import sys
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

users = []

DB_ROUTE = "./bd/basededatos.db"

# routes
@app.route('/users', methods=['GET'])
def get_users():
	return jsonify(users), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
	user_log = ""
	text_file = open("LOGS.txt", "a")
	date = datetime.now()
	ip_address = request.remote_addr

	try:
		sqliteConnection = sqlite3.connect(DB_ROUTE)
		cursor = sqliteConnection.cursor()
		print("Successfully Connected to SQLite")

		cursor.execute("SELECT username, password FROM users WHERE id = ?", (user_id,))
		sqliteConnection.commit()
		data = cursor.fetchall()
		return jsonify({"user":data[0][0], "password":data[0][1]}), 201


	except sqlite3.Error as error:
		print("USUARIO INCORRECTO")
		# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
		user_log = str(date)+" | "+str(ip_address)+" | ERROR | USUARIO INCORRECTO | "
		text_file.write(user_log+'\n')
		text_file.close()
		return jsonify({'user': "incorrect."}), 404
	finally:
		if sqliteConnection:
			sqliteConnection.close()
			print("The SQLite connection is closed")		

# REGISTRO
@app.route('/users', methods=['POST'])
def create_user():
	user_log = ""
	text_file = open("LOGS.txt", "a")
	date = datetime.now()
	ip_address = request.remote_addr
	try: 
		sqliteConnection = sqlite3.connect(DB_ROUTE)
		cursor = sqliteConnection.cursor()
		print("Successfully Connected to SQLite")
		if not request.json:
			cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',"UNKNOWN",(date,str(ip_address),"ERROR","application/json body missing or empty", "API_Registry"))
			sqliteConnection.commit()
			cursor.close()
			user_log = str(date)+" | "+str(ip_address)+" | ERROR | application/json body missing or empty | "
			text_file.write(user_log+'\n')
			text_file.close()
			return jsonify({'message': '\'application/json\' body missing or empty'}), 400
			# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
			

		if not 'name' in request.json:
			cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',"UNKNOWN",(date,str(ip_address),"ERROR","name property missing", "API_Registry"))
			sqliteConnection.commit()
			cursor.close()
			user_log = str(date)+" | "+str(ip_address)+" | ERROR | name property missing | "
			text_file.write(user_log+'\n')
			text_file.close()
			return jsonify({'message': '\'name\' property missing'}), 400
			# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
			

		if not 'email' in request.json:
			cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',"UNKNOWN",(date,str(ip_address),"ERROR","application/json body missing or empty", "API_Registry"))
			sqliteConnection.commit()
			cursor.close()
			user_log = str(date)+" | "+str(ip_address)+" | ERROR | email property missing | "
			text_file.write(user_log+'\n')
			text_file.close()
			return jsonify({'message': '\'email\' property missing'}), 400
			# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
			

		users.append({
			'id': len(users),
			'name': request.json['name'],
			'email': request.json['email']
		})

	# Crear usuario 
		cursor.execute('''insert into users(username,password) values (?,?);''',(request.json['name'], generate_password_hash(request.json['email'])))
		sqliteConnection.commit()
		print("USUARIO CREADO")
		cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',(date,request.json['name'],str(ip_address),"ALTA","usuario dado de alta", "API_Registry"))
		sqliteConnection.commit()
		# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
		user_log = str(date)+" | "+request.json['name']+" -- "+str(ip_address)+" | ALTA | usuario dado de alta | "
		text_file.write(user_log+'\n')
		text_file.close()


		cursor.close()
	except sqlite3.Error as error:
		print("USUARIO YA EXISTE")


		cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',(date,request.json['name'],str(ip_address),"ERROR","usuario ya existe", "API_Registry"))
		sqliteConnection.commit()	
		cursor.close()
		# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
		user_log = str(date)+" | "+request.json['name']+" -- "+str(ip_address)+" | ERROR | USUARIO YA EXISTE | "
		text_file.write(user_log+'\n')
		text_file.close()

		return jsonify({'user': "exists."}), 400
	finally:
		if sqliteConnection:
			sqliteConnection.close()
			print("The SQLite connection is closed")



	return jsonify({'user': "registered."}), 201


# EDITAR USUARIO
@app.route('/users', methods=['PUT'])
def update_user():
	user_log = ""
	text_file = open("LOGS.txt", "a")
	date = datetime.now()
	ip_address = request.remote_addr
	sqliteConnection = sqlite3.connect(DB_ROUTE)
	cursor = sqliteConnection.cursor()
	print("Successfully Connected to SQLite")

	try:
		if not request.json:
			cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',"UNKNOWN",(date,str(ip_address),"ERROR","application/json body missing or empty", "API_Registry"))
			sqliteConnection.commit()
			cursor.close()
			user_log = str(date)+" | "+str(ip_address)+" | ERROR | application/json body missing or empty | "
			text_file.write(user_log+'\n')
			text_file.close()
			return jsonify({'message': '\'application/json\' body missing or empty'}), 400
			# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
			

		if request.json['option'] == '1':
			# Editar usuario
			try:
				userNew = [request.json['newname'], request.json['name'], request.json['email']]
				print(userNew[1])
				cursor.execute("SELECT password FROM users WHERE username = ?", (userNew[1],))
				sqliteConnection.commit()
				data = cursor.fetchall()

				if data==[]:
					raise sqlite3.Error()

				if check_password_hash(data[0][0], userNew[2]):
					print("USUARIO LOGGEADO")
					cursor.execute("UPDATE users SET username = ? WHERE username = ?", (userNew[0], userNew[1],))
					sqliteConnection.commit()
					print("USUARIO ACTUALIZADO")
					cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',(date,request.json['name'],str(ip_address),"MODIFICACIÓN","usuario ha modificado nombre de usuario a" + request.json["newname"], "API_Registry"))
					sqliteConnection.commit()
					# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
					user_log = str(date)+" | "+userNew[0]+" -- "+str(ip_address)+" | MODIFICACION | Usuario ha modificado su nombre de usuario | "
					text_file.write(user_log+'\n')
					text_file.close()
				else:
					raise sqlite3.Error()

				cursor.close()
			except sqlite3.Error as error:
				print("USUARIO/CONTRASEÑA INCORRECTA")


				cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',(date,request.json['name'],str(ip_address),"ERROR","usuario usuario/contraseña incorrecta", "API_Registry"))
				sqliteConnection.commit()	
				cursor.close()
				# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
				user_log = str(date)+" | "+userNew[0]+" -- "+str(ip_address)+" | ERROR | USUARIO/CONTRASEÑA INCORRECTA | "
				text_file.write(user_log+'\n')
				text_file.close()
				return jsonify({'user': "incorrect."}), 404
			finally:
				if sqliteConnection:
					sqliteConnection.close()
					print("The SQLite connection is closed")

		elif request.json['option'] == '2':
			# Editar contraseña
			try:
				sqliteConnection = sqlite3.connect(DB_ROUTE)
				cursor = sqliteConnection.cursor()
				print("Successfully Connected to SQLite")

				userNew = [request.json['newpass'], request.json['name'], request.json['email']]
				print(userNew[1])
				cursor.execute("SELECT password FROM users WHERE username = ?", (userNew[1],))
				sqliteConnection.commit()
				data = cursor.fetchall()

				if data==[]:
					raise sqlite3.Error()

				if check_password_hash(data[0][0], userNew[2]):
					print("USUARIO LOGGEADO")
					cursor.execute("UPDATE users SET password = ? WHERE username = ?", (generate_password_hash(userNew[0]), userNew[1],))
					sqliteConnection.commit()
					print("USUARIO ACTUALIZADO")
					cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',(date,request.json['name'],str(ip_address),"MODIFICACIÓN","usuario ha modificado su contraseña", "API_Registry"))
					sqliteConnection.commit()
					# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
					user_log = str(date)+" | "+userNew[0]+" -- "+str(ip_address)+" | MODIFICACION | Usuario ha modificado su contraseña | "
					text_file.write(user_log+'\n')
					text_file.close()
				else:
					raise sqlite3.Error()

				cursor.close()
			except sqlite3.Error as error:
				print("USUARIO/CONTRASEÑA INCORRECTA")

				cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',(date,request.json['name'],str(ip_address),"ERROR","usuario usuario/contraseña incorrecta", "API_Registry"))
				sqliteConnection.commit()	
				cursor.close()
				# AUDITORIA DE USUARIO, CREAR STRING PONER EN LOGS.txt
				user_log = str(date)+" | "+userNew[0]+" -- "+str(ip_address)+" | ERROR | USUARIO/CONTRASEÑA INCORRECTA | "
				text_file.write(user_log+'\n')
				text_file.close()

				return jsonify({'user': "incorrect."}), 404
			finally:
				if sqliteConnection:
					sqliteConnection.close()
					print("The SQLite connection is closed")	
	except sqlite3.Error as error:
		print("sql query error")	
		cursor.execute('''insert into logs(DATE,USUARIO,IP,ACCION_USER,DESC_USER,MODULE) values (?,?,?,?,?,?);''',"UNKNOWN",(date,str(ip_address),"ERROR","application/json body missing or empty", "API_Registry"))
		sqliteConnection.commit()
		cursor.close
	finally:
		if sqliteConnection:
			sqliteConnection.close()
			print("The SQLite connection is closed")

	return jsonify({"user":"updated."}), 201

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
	for i, user in enumerate(users):
		if user['id'] == user_id:
			del users[i]

			return jsonify({}), 200

	return jsonify({'message': 'User not found'}), 404

# run
if __name__ == '__main__':
    app.run(host=sys.argv[1].split(":")[0], port=int(sys.argv[1].split(":")[1]),ssl_context=('./reg_certs/cert.pem', './reg_certs/key.pem'))