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


def add_task_to_db(request, user_id):
    height = request.json['height'],
    width = request.json['width'],
    name_pic = request.json['name_pic'],                # Генерируем индефикатор для каждой задачи()
    pic_base64 = request.json.get('pic_base64', ""),    # (этого можно было в ручную не делать,
    identifier = str(uuid.uuid4())                      # а взять индефикатор задачи RQ)

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
    task_db = Tasks.query.filter(Tasks.identifier == identifier, Tasks.user_id == user_id).first()
    if task_db is None:
        answer = {'Status': 'Identifier not found'}
        return answer

    if task_db.done:
        task = {
            'height': task_db.height,
            'width': task_db.width,
            'name_pic': task_db.name_pic,
            'pic_base64': task_db.pic_base64,
        }
        answer = {'Status': task}
        return answer
    answer = {'Status': 'Your image is not ready'}
    return answer