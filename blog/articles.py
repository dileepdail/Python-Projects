from flask import Flask, jsonify, make_response
from flask import Flask, jsonify, request
import os
import simplejson as json
from database import User, Article, db
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
from sqlalchemy import desc

auth = HTTPBasicAuth()

app = Flask(__name__)

db.init_app(app)
baseDir = os.path.abspath(os.path.dirname('_file_'))

# Configuring Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(baseDir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.verify_user(username) or not user.verify_password(password):
        return False
    return True


@app.route('/articles/<n>', methods=['GET'])
def articlesByNumber(n):
    ''' Returns the list of n most recent users '''
    with app.app_context():

        response_object = {
            'status': 'success',
            'data': {
                'articles': [article.to_json() for article in db.session.query(Article).order_by(desc(Article.created_timestamp)).limit(n).all()]
            }
        }
        return jsonify(response_object), 200

@app.route('/articlesMetaData/<n>', methods=['GET'])
def articlesMetaData(n):
    with app.app_context():

        response_object = {
            'status': 'success',
            'data': {
                'articles': [article.to_json_data() for article in db.session.query(Article).order_by(desc(Article.created_timestamp)).limit(n).all()]
            }
        }
        return jsonify(response_object), 200

@app.route('/article/<id>', methods=['GET'])
def article(id):
    ''' Returns the individual article based on user '''
    article = Article.query.get(id)
    if not article:
        response_object = {
        'status': 'fail',
        'message': 'No article exist of given ID!!'
        }
        return jsonify(response_object), 404
    else:
        response_object = {
            'status': 'success',
            'title': article.title,
            'body': article.body,
            'author': article.author
        }
        return jsonify(response_object), 200

@app.route('/articles', methods=['POST'])
@auth.login_required
def addArticle():
    post_data = request.get_json()
    title = post_data.get('title')
    body = post_data.get('body')
    #user_name = post_data.get('user_name')
    user_name = request.authorization.username
    article_url = post_data.get('article_url')
    #user_id = post_data.get('user_id')
    #base_url = "http://127.0.0.1:5001/articles/"
    #article_url = base_url+article_url
    user = User.query.filter_by(username = user_name).first()
    if not user:
        response_object = {
        'status': 'fail',
        'message': 'Invaid user_name!!!'
        }
        return jsonify(response_object), 404
    else:
        author = user.username
        user_id = user.id
        try:
            db.session.add(Article(title=title, body=body,author=author,article_url= article_url, user_id=user_id))
            db.session.commit()
        except:
            response_object = {
            'status': 'fail',
            'message': 'Error while adding article'
            }
            return jsonify(response_object), 409

        response_object = {
            'status': 'success',
            'message': 'article '+title +' was added!'
        }
        return jsonify(response_object), 201

# Update any article
@app.route('/article/<id>', methods=['PUT'])
@auth.login_required
def updateArticle(id):

    post_data = request.get_json()
    title = post_data.get('title')
    body = post_data.get('body')

    article = Article.query.get(id)
    if not article:
        response_object = {
        'status': 'fail',
        'message': 'No article exist for given ID!!'
        }
        return jsonify(response_object), 404
    else:
        user = User.query.get(article.user_id)
        if not user:
            response_object = {
            'status': 'fail',
            'message': 'No user exist for given ID!!'
            }
            return jsonify(response_object), 404
        else:
            if user.verify_user(user.username):

                article.title = title
                article.body = body
                article.modified_timestamp = datetime.now()

                db.session.commit()
                response_object = {
                    'status': 'success',
                    'message': f'{title} is updated!!'
                }

                return jsonify(response_object), 200
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'Invalid ID passed in URL'
                }
                return jsonify(response_object), 404


#deleting article
@app.route('/article/<id>', methods=['DELETE'])
@auth.login_required
def deleteArticle(id):
    article = Article.query.get(id)
    if not article:
        response_object = {
        'status': 'fail',
        'message': 'No article exist of given ID!!'
        }
        return jsonify(response_object), 404
    else:
        user = User.query.get(article.user_id)
        if not user:
            response_object = {
            'status': 'fail',
            'message': 'No user exist for given ID!!'
            }
            return jsonify(response_object), 404
        else:
            if user.verify_user(user.username):
                try:
                    db.session.delete(article)
                    db.session.commit()
                except:
                    response_object = {
                    'status': 'fail',
                    'message': 'Error while deleting user'
                    }
                    return jsonify(response_object), 409

                response_object = {
                    'status': 'success',
                    'message': f'{article.title} is deleted!'
                }
                return jsonify(response_object), 200
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'Invalid ID passed in URL'
                }
                return jsonify(response_object), 404

# if __name__ == '__main__':
#     app.run( port=5001, debug=True)
