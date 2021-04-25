# реализация rest-API для User

import flask
from flask import jsonify

from . import db_session
from .user import User
from flask import request

blueprint = flask.Blueprint('users_api', __name__, template_folder="templates")
params = ["id", "login", "hashed_password", "links"]


@blueprint.route('/api/users')
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify({
        'users': [item.to_dict(only=params)
                  for item in users]
    })


@blueprint.route('/api/users/<int:users_id>', methods=['GET'])
def get_job(users_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(users_id)
    if not user:
        return jsonify({
            "error": "not found"
        })
    else:
        return jsonify({
            'user': user.to_dict(
                only=params)})


@blueprint.route('/api/users', methods=['POST'])
def add_job():
    if not request.json:
        return jsonify({"error": 'Empty request'})
    elif not all(key in request.json for key in params):
        return jsonify({"error": "Bad request"})
    db_sess = db_session.create_session()
    user = User(id=request.json['id'], login=request.json['login'],
                hashed_password=request.json['hashed_password'])
    db_sess.add(user)
    db_sess.commit()
    return jsonify({"success": "ok"})


@blueprint.route('/api/users/<int:users_id>', methods=['DELETE'])
def delete_user(users_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(users_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})
