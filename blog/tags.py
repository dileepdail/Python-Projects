from database import Tag, User, db, Article
from flask import Flask, jsonify, request
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

@app.route('/tags', methods=['POST'])
@auth.login_required
def addTags():
    post_data = request.get_json()
    url = post_data.get('article_url')
    exists = db.session.query(Article.query.filter(Article.article_url == url).exists()).scalar()
    if exists :
        tags = post_data.get("tags")
        for tag in tags :
            db.session.add(Tag(article_url= url, tag=tag))
            db.session.commit()

        response_object = {
            'status': 'success',
            'message': f'{tags} was added!'
        }
        return jsonify(response_object), 201

    else :
        response_object = {
            'status': 'Failure',
            'message': 'Schema constraint error'
        }
        return jsonify(response_object), 409

@app.route('/tags/<article_url>', methods=['GET'])
def getTagsByUrl(article_url):
    tags = db.session.query(Tag).filter(Tag.article_url == article_url).all()
    if (tags  == []):
        response_object = {
            'status': 'Failure',
            'message': "Article Url: "+ article_url+" does not exist"
        }
        return jsonify(response_object), 404
    response_object = {
        'status': 'success',
        'data': {
            'tags': [tag.tag for tag in tags]
        }
    }
    return jsonify(response_object), 200

@app.route('/tags/article-url/<tag>', methods=['GET'])
def getUrlsBytag(tag):
    urls = db.session.query(Tag).filter(Tag.tag == tag).all()
    if (urls  == []):
        response_object = {
            'status': 'Failure',
            'message': "Tag :"+ tag+" does not exist"
        }
        return jsonify(response_object), 404
    response_object = {
        'status': 'success',
        'urls': {
            'article_urls': [url.article_url for url in urls]
        }
    }
    return jsonify(response_object), 200

@app.route('/tags', methods=['DELETE'])
@auth.login_required
def deleteTagsFromUrl():
    delete_data = request.get_json()
    article_url = delete_data.get('article_url')
    tags = db.session.query(Tag).filter(Tag.article_url == article_url).all()
    if (tags == []):
        response_object = {
            'status': 'Failure',
            'message': "Article Url: " + article_url + " does not exist"
        }
        return jsonify(response_object), 404
    tags = delete_data.get('tags')
    for tag in tags:
        db.session.query(Tag).filter(Tag.article_url == article_url).filter( Tag.tag == tag ).delete()

    db.session.commit()
    response_object = {
        'status': 'success',
        'data': {
            'tags deleted': [tags]
        }
    }
    return jsonify(response_object), 200

# if __name__ == '__main__':
#     app.run( port=5003, debug=True)
