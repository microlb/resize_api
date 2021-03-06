from flask import jsonify, abort, request
from application.models import Tasks, User
from application.logic import add_task_to_db, get_image_in_db, delete_task, rename_image_in_db, get_all_identifier, add_new_user
from application import db
from application import app
from redis import Redis
import uuid
import rq

app.app_context().push()


def auth(username, password):
    '''Игрущечная авторизация пользователя'''
    user = db.session.query(User).filter(User.username == username).first()
    if user is None:
        #logger.info('User with this name does not exist.')
        return False
    if password != user.password:
        #logger.info('Incorrect password.')
        return False
    return user.id


@app.route('/resize/registration/', methods=['POST'])
def create_user():
    '''Регистрация нового пользователя'''
    if not request.json or not 'username' or not "password" in request.json:
        #logger.error('%s Incorrect request json', request.json)
        abort(400)

    username = request.json['username']
    password = request.json['password']

    answer, status = add_new_user(username, password)

    return jsonify(answer), status


@app.route('/resize/get_all_identifier/<string:username>/<string:password>/', methods=['GET'])
def get_db_identifier(username, password):
    '''Отправить пользователю все его индефикаторы.'''
    user_id = auth(username, password)
    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'}), 200

    answer, status = get_all_identifier(user_id)
    return jsonify(answer), status


@app.route('/resize/task_get/<string:username>/<string:password>/<string:identifier>/', methods=['GET'])
def get_db_img(identifier, username, password):
    '''Отправить картинку пользователю, если обработка закончена.'''
    user_id = auth(username, password)
    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'})

    answer, status = get_image_in_db(identifier, user_id)
    return jsonify(answer), status


@app.route('/resize/post_task/<string:username>/<string:password>/', methods=['POST'])
def create_db_task_(username, password):
    '''Обработка запроса на resize кортинки.'''
    user_id = auth(username, password)
    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'}), 200

    if not request.json or not 'name_pic' or not "pic_base64" in request.json:
        #logger.error('%s Incorrect request json', request.json)
        abort(400)
    if 'height' in request.json and type(request.json['height']) is not int or not (1 < request.json['height'] < 9999):
        #logger.error('%s Incorrect HEIGHT in request json', request.json)
        abort(400)
    if 'width' in request.json and type(request.json['width']) is not int or not (1 < request.json['width'] < 9999):
        #logger.error('%s Incorrect width in request json', request.json)
        abort(400)

    height = request.json['height'],
    width = request.json['width'],
    name_pic = request.json['name_pic'],
    pic_base64 = request.json.get('pic_base64', "")
    identifier = str(uuid.uuid4())  # Генерируем индефикатор для каждой задачи

    identifier = add_task_to_db(user_id, height, width, name_pic, identifier, pic_base64)

    queue = rq.Queue('api-tasks',
                     connection=Redis.from_url('redis://'))  # Вызывается обработка картинки в фоновом режиме
    queue.enqueue('application.tasks.scale_img_db', identifier, user_id)

    #logger.info('Task with identifier %s successfully processed', identifier)

    return jsonify({'Upload. Your personal ind = ': identifier}), 201


@app.route('/resize/delete_task/<string:username>/<string:password>/<string:identifier>/', methods=['DELETE'])
def delete_db_task(identifier, username, password):
    '''Удаляем задачу из базы данных по индефикатору'''
    user_id = auth(username, password)

    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'})

    answer, status = delete_task(identifier, user_id)
    return jsonify(answer), status


@app.route('/resize/rename_pic/<string:username>/<string:password>/<string:identifier>/', methods=['PUT'])
def rename_pic(identifier, username, password):
    '''Изменить название картинки'''
    user_id = auth(username, password)
    if not user_id:
        return jsonify({'Status': 'User is not exist or incorrect password'})

    new_name_pic = request.json['name_pic']
    answer, status = rename_image_in_db(identifier, user_id, new_name_pic)
    return jsonify(answer), status


if __name__ == "__main__":
    app.run(debug=True)
