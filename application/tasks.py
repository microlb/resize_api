from application.logic import base64str_to_img_b, img_b_to_base64str, scale_image
from application.models import Tasks
from rq import get_current_job
from application import app
from application import db
import time


app.app_context().push()


def scale_img_db(identifier, user_id):
    '''Преобразует картинку и сохраняет в базу данных с изменением статуса'''
    task_db = Tasks.query.filter(Tasks.identifier == identifier, Tasks.user_id == user_id).first()
    job = get_current_job()

    image = task_db.pic_base64
    width = task_db.width
    height = task_db.height

    image_b = base64str_to_img_b(image)
    image_scale = scale_image(image_b, width=width, height=height)
    image_scale_b = img_b_to_base64str(image_scale)

    task_db.pic_base64 = str(image_scale_b)

    job.save_meta()
    task_db.done = True
    db.session.add(task_db)
    db.session.commit()
    time.sleep(50)
    print('Task completed')