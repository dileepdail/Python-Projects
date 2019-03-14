from database import Comment, User, Article, db
from flask import Flask, jsonify, request
from sqlalchemy import desc
from flask_httpauth import HTTPBasicAuth
import os

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

@app.route("/comments/<id>", methods=['DELETE'])
@auth.login_required
def deleteComment(id):
    comment = db.session.query(Comment).get(id)
    if (comment == None):
        response_object = {
            'status': 'Failure',
            'message': "Comment with Id: " + id + " does not exist"
        }
        return jsonify(response_object), 404
    db.session.delete(comment)
    db.session.commit()
    response_object = {
        'status': 'success'
    }

    return jsonify(response_object), 200

@app.route('/comments', methods=['POST'])
def addComment():
    post_data = request.get_json()
    body = post_data.get('body')
    article_id = db.session.query(Article).filter(Article.article_url == post_data.get('article_url')).all()
    if (article_id  == []):
        response_object = {
            'status': 'Failure',
            'message': "Article Url "+post_data.get('article_url')+" does not exist"
        }
        return jsonify(response_object), 404
    authenticated = False if request.authorization == None else verify_password(request.authorization.username, request.authorization.password)
    owner_id = None if authenticated == False else db.session.query(User).filter(User.username == request.authorization.username).all()[0].id
    db.session.add(Comment(body=body,article_id = article_id[0].id,owner_id = owner_id ))
    db.session.commit()
    response_object = {
        'status': 'success',
        'message': "Comment"+body+" was added!"
    }

    return jsonify(response_object), 201

@app.route('/comments/<article_url>', methods=['GET'])
def getNumberOfCommentsFromArticleUrl(article_url):
    article_id = db.session.query(Article).filter(Article.article_url == article_url).all()
    if (article_id == []):
        response_object = {
            'status': 'Failure',
            'message': "Article Url " + article_url + " does not exist"
        }
        return jsonify(response_object), 404
    count = len(db.session.query(Comment).filter(Comment.article_id == article_id[0].id).all())

    response_object = {
        'count': str(count)
    }
    return jsonify(response_object), 200

@app.route('/comments/<article_url>/<recent>', methods=['GET'])
def getCommentsFromArticleUrl(article_url,recent):
    article_id = db.session.query(Article).filter(Article.article_url == article_url).all()
    if (article_id == []):
        response_object = {
            'status': 'Failure',
            'message': "Article Url " + article_url + " does not exist"
        }
        return jsonify(response_object), 404

    response_object = {
        'status': 'success',
        'data': {
            'comments': [comment.to_json() for comment in db.session.query(Comment).filter(Comment.article_id == article_id[0].id).order_by(desc(Comment.created_timestamp)).limit(recent).all()]
        }
    }
    return jsonify(response_object), 200


# if __name__ == '__main__':
#     app.run( port=5002, debug=True)
