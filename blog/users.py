from flask import Flask, jsonify, make_response
from database import User, db
from flask import Flask, jsonify, request
import os
import simplejson as json
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from datetime import datetime

auth = HTTPBasicAuth()


app = Flask(__name__)

db.init_app(app)
baseDir = os.path.abspath(os.path.dirname('_file_'))

# Configuring Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(baseDir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@auth.verify_password
def verify_password(username, password):
    #print("username: ",request.authorization.username)
    user = User.query.filter_by(username = username).first()
    if not user or not user.verify_user(username) or not user.verify_password(password):
        return False
    return True

@app.route("/", methods=['GET'])
def hello():
    ''' Greet the user '''

    return "Hey! The service is up, how about doing something useful"

@app.route('/users', methods=['GET'])
def users():
    ''' Returns the list of users '''
    with app.app_context():

        response_object = {
            'status': 'success',
            'data': {
                'users': [user.to_json() for user in db.session.query(User).all()]
            }
        }
        return jsonify(response_object), 200

@app.route('/users', methods=['POST'])
def addUser():
    post_data = request.get_json()
    username = post_data.get('username')
    email_id = post_data.get('email_id')
    password = post_data.get('password')

    new_user = User(username=username, email_id=email_id)
    new_user.hash_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        response_object = {
        'status': 'fail',
        'message': 'Error while adding user'
        }
        return jsonify(response_object), 409
    response_object = {
        'status': 'success',
        'message': f'{email_id} was added!'
    }
    return jsonify(response_object), 201

#deleting user
@app.route('/users/<id>', methods=['DELETE'])
@auth.login_required
def deleteUser(id):
    user = User.query.get(id)
    if not user:
        response_object = {
        'status': 'fail',
        'message': 'No user exist of given ID!!'
        }
        return jsonify(response_object), 404
    else:
        if user.verify_user(user.username):
            try:
                db.session.delete(user)
                db.session.commit()
            except:
                response_object = {
                'status': 'fail',
                'message': 'Error while deleting user'
                }
                return jsonify(response_object), 409

            response_object = {
                'status': 'success',
                'message': f'{user.username} is deleted!'
            }
            return jsonify(response_object), 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'Invalid ID passed in URL'
            }
            return jsonify(response_object), 404

# Update a user's password
@app.route('/users/<id>', methods=['PUT'])
@auth.login_required
def updateUser(id):

    password = request.json['password']
    user = User.query.get(id)
    if not user:
        response_object = {
        'status': 'fail',
        'message': 'No user exist for given ID!!'
        }
        return jsonify(response_object), 404
    else:
        if user.verify_user(user.username):
            user.hash_password(password)
            user.modified_timestamp = datetime.now()

            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{user.username} password is modified'
            }
            return jsonify(response_object), 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'Invalid ID passed in URL'
            }
            return jsonify(response_object), 404

# if __name__ == '__main__':
#     app.run( port=5000, debug=True)


# python app.py
