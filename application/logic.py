from application.models import Tasks, User
from application import db
from io import BytesIO
from PIL import Image
import logging
import base64
import io
import uuid


def img_b_to_base64str(image_b):
    '''Функция преобразует байтовое представление картинки в
        base64 и соханяет как строку в кодировке UTF-8'''
    buffered = BytesIO()
    image_b.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    img_str_utf8 = img_str.decode("utf-8")
    return img_str_utf8


def base64str_to_img_b(img_str_utf8):
    '''Функция декодирует строку UTF-8 в байтовое представление'''
    img_str = img_str_utf8.encode("utf-8")
    img_b = base64.b64decode(img_str)
    return img_b


def scale_image(image_b, width=None, height=None):
    '''Преобразует картинку в байтовом виде, по заданным высоте и ширине
        в пикселях. Но не больше исходного размера'''
    original_image = Image.open(io.BytesIO(image_b))
    w, h = original_image.size
    if width and height:
        max_size = (width, height)
    elif width:
        max_size = (width, h)
    elif height:
        max_size = (w, height)
    else:
        # No width or height specified
        raise RuntimeError('Width or height required!')
    original_image.thumbnail(max_size, Image.ANTIALIAS)
    scaled_image = original_image
    return scaled_image


def add_new_user(username, password):
    user = User.query.filter(User.username == username).first()

    if user is None:
        user_add = User(username=username, password=password)
        db.session.add(user_add)
        db.session.commit()
        answer = username + ' registration passed'
        #logger.info('%s successfully registered', username)
        return {'Status': answer}, 201
    #logger.info('%s username with this name already exist', username)
    return {'Status': 'Username with this name already exist'}, 200


def get_task_in_db(identifier, user_id):
    task_db = Tasks.query.filter(Tasks.identifier == identifier, Tasks.user_id == user_id).first()
    return task_db


def add_task_to_db(user_id, height, width, name_pic, identifier, pic_base64):

    task = Tasks(name_pic=name_pic[0],
                 height=height[0],
                 width=width[0],
                 pic_base64=pic_base64[0],
                 identifier=identifier,
                 user_id=user_id)
    db.session.add(task)
    db.session.commit()
    return identifier


def get_image_in_db(identifier, user_id):
    task_db = get_task_in_db(identifier, user_id)

    if task_db is None:
        return {'Status': 'Identifier not found'}, 200

    if task_db.done:
        task = {
            'height': task_db.height,
            'width': task_db.width,
            'name_pic': task_db.name_pic,
            'pic_base64': task_db.pic_base64,
        }
        return {'Status': task}, 200
    return {'Status': 'Your image is not ready'}, 200


def delete_task(identifier, user_id):
    task_db = get_task_in_db(identifier, user_id)

    if task_db is None:
        #logger.info('Identifier %s not found', identifier)
        return {'Status': 'Identifier not found'}, 200

    db.session.delete(task_db)
    db.session.commit()
    #logger.info('Task with identifier %s deleted', identifier)
    return {'Status': 'Task deleted'}, 201


def rename_image_in_db(identifier, user_id, new_name_pic):
    task_db = get_task_in_db(identifier, user_id)

    if task_db is None:
        # logger.info('Identifier %s not found', identifier)
        return {'Status': 'Identifier not found'}, 200

    old_name = task_db.name_pic
    task_db.name_pic = new_name_pic
    db.session.add(task_db)
    db.session.commit()
    #logger.info('Name pic changed %s => %s, identifier = %s', old_name, new_name_pic, identifier)
    return {'Status': 'Name pic changed'}, 201


def get_all_identifier(user_id):
    task_db = Tasks.query.filter(Tasks.user_id == user_id).all()
    ind_and_name = []
    for task in task_db:
        t = task
        ind_name = [t.identifier, t.name_pic, t.done]
        ind_and_name.append(ind_name)
    return {'Status': ind_and_name}, 200

