from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash # encriptar
from bson import json_util
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost/flask-mongo'
mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def welcome():
    return {'mensaje': 'Bienvenido a mi api Flask'}

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    # Recibiendo datos
    nick = request.json['nick']
    contrasena = request.json['contrasena']
    email = request.json['email']
    if nick and contrasena and email:
        # Ciframos
        hashed_contrasena = generate_password_hash(contrasena)
        id = mongo.db.usuarios.insert(
            {'nick': nick, 'contrasena': contrasena, 'email': email}
        )
        response = jsonify({
            '_id': str(id),
            'nick': nick,
            'contrasena': contrasena,
            'email': email
        })
        response.status_code = 201
        return response
    else:
        return not_found()

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = mongo.db.usuarios.find()
    response = json_util.dumps(usuarios)
    return Response(response, mimetype='application/json')

@app.route('/usuario/<id>', methods=['GET'])
def get_user(id):
    user = mongo.db.usuarios.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(user)
    return Response(response, mimetype='application/json')

@app.route('/usuario/<id>', methods=['DELETE'])
def delete_user(id):
    mongo.db.usuarios.delete_one({'_id': ObjectId(id)})
    response = jsonify({
        'mensaje': 'Usuario con id : ' + id + ' eliminado'
    })
    return response

@app.route('/usuario/<id>', methods=['PUT'])
def update_user(id):
    nick = request.json['nick']
    contrasena = request.json['contrasena']
    email = request.json['email']
    if nick and contrasena and email:
        hashed_contrasena = generate_password_hash(contrasena)
        mongo.db.usuarios.update_one({'_id': ObjectId(id)}, {'$set': {
            'nick': nick,
            'contrasena': hashed_contrasena,
            'email': email
        }})
        response = jsonify({'mensaje': 'Usuario actualizado'})
        return response
    else:
        return not_found()
   
@app.errorhandler(404)
def not_found(error=None):
    response_err = jsonify({
        'message': 'Recurso no encontrado' + request.url,
        'status':404
    })
    response_err.status_code = 404
    return response_err

if __name__ == '__main__':
    app.run(debug=True, port=4000)
