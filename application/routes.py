from flask import jsonify, abort, make_response, request
from logging.handlers import RotatingFileHandler
from application.models import Tasks, User
from application.logic import add_task_to_db, get_image_in_db
from application import db
from application import app
from redis import Redis
import logging
import uuid
import rq


app.app_context().push()

logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler('log_rest_app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)


@app.errorhandler(405)
def not_found(error):
    return make_response(jsonify({'error': 'Method not found'}), 405)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def auth(username, password):
    '''Игрущечная авторизация пользователя'''
    user = db.session.query(User).filter(User.username == username).first()
    if user is None:
        logger.info('User with this name does not exist.')
        return False
    if password != user.password:
        logger.info('Incorrect password.')
        return False
    return user.id


@app.route('/resize/registration/', methods=['POST'])
def create_user():
    '''Регистрация нового пользователя'''
    if not request.json or not 'username' or not "password" in request.json:
        logger.error('%s Incorrect request json', request.json)
        abort(400)

    username = request.json['username']
    password = request.json['password']
    user = db.session.query(User).filter(User.username == username).all()

    if len(user) == 0:
        user_add = User(username=username, password=password)
        db.session.add(user_add)
        db.session.commit()
        answer = username + ' registration passed'
        logger.info('%s successfully registered', username)
        return jsonify({'Status': answer}), 201
    logger.info('%s username with this name already exist', username)
    return jsonify({'Status': 'Username with this name already exist'})


@app.route('/resize/get_all_identifier/<string:username>/<string:password>/', methods=['GET'])
def get_db_identifier(username, password):
    '''Отправить пользователю все его индефикаторы.'''
    user_id = auth(username, password)
    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'})

    task_db = Tasks.query.filter(Tasks.user_id == user_id).all()
    ind_and_name = []
    for task in task_db:
        t = task
        ind_name = [t.identifier, t.name_pic, t.done]
        ind_and_name.append(ind_name)
    return jsonify({'Status': ind_and_name}), 200


@app.route('/resize/task_get/<string:username>/<string:password>/<string:identifier>/', methods=['GET'])
def get_db_img(identifier, username, password):
    '''Отправить картинку пользователю, если обработка закончена.'''
    user_id = auth(username, password)
    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'})

    answer = get_image_in_db(identifier, user_id)
    return jsonify(answer), 200


@app.route('/resize/post_task/<string:username>/<string:password>/', methods=['POST'])
def create_db_task_(username, password):
    '''Обработка запроса на resize кортинки.'''
    user_id = auth(username, password)
    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'}), 200

    if not request.json or not 'name_pic' or not "pic_base64" in request.json:
        logger.error('%s Incorrect request json', request.json)
        abort(400)
    if 'height' in request.json and type(request.json['height']) is not int or not (1 < request.json['height'] < 9999):
        logger.error('%s Incorrect HEIGHT in request json', request.json)
        abort(400)
    if 'width' in request.json and type(request.json['width']) is not int or not (1 < request.json['width'] < 9999):
        logger.error('%s Incorrect width in request json', request.json)
        abort(400)

    identifier = add_task_to_db(request, user_id)

    queue = rq.Queue('api-tasks', connection=Redis.from_url('redis://'))   #  Вызывается обработка картинки в фоновом режиме
    queue.enqueue('application.tasks.scale_img_db', identifier, user_id)

    logger.info('Task with identifier %s successfully processed', identifier)

    return jsonify({'Upload. Your personal ind = ': identifier}), 201


@app.route('/resize/delete_task/<string:username>/<string:password>/<string:identifier>/', methods=['DELETE'])
def delete_db_task_(identifier, username, password):
    '''Удаляем задачу из базы данных по индефикатору'''
    user_id = auth(username, password)
    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'})

    task_db = Tasks.query.filter(Tasks.identifier == identifier, Tasks.user_id == user_id).first()

    if task_db is None:
        logger.info('Identifier %s not found', identifier)
        return jsonify({'Status': 'Identifier not found'})

    db.session.delete(task_db)
    db.session.commit()
    logger.info('Task with identifier %s deleted', identifier)
    return jsonify({'Status': 'Task deleted'}), 201


@app.route('/resize/rename_pic/<string:username>/<string:password>/<string:identifier>/', methods=['PUT'])
def rename_pic(identifier, username, password):
    '''Изменить название картинки'''
    user_id = auth(username, password)
    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'})

    task_db = Tasks.query.filter(Tasks.identifier == identifier, Tasks.user_id == user_id).first()

    if task_db is None:
        logger.info('Identifier %s not found', identifier)
        return jsonify({'Status': 'Identifier not found'})

    new_name_pic = request.json['name_pic']
    old_name = task_db.name_pic
    task_db.name_pic = new_name_pic
    db.session.add(task_db)
    db.session.commit()
    logger.info('Name pic changed %s => %s, identifier = %s', old_name, new_name_pic,identifier)
    return jsonify({'Status': 'Name pic changed'})


if __name__ == "__main__":
    app.run(debug=True)
