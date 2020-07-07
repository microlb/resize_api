import requests
import json
from io import BytesIO
from PIL import Image
import base64
import io


'''Описание работы api.

Интерфейс получился не особо дружелюбным.
Изображение отправляется в json формате, в base64
(не самый хороший вариант, изображение занимают больше памяти
плюс и пользователю и серверу нужно заниматся кадировкой)

-----------------------------------------------------------------
Регистрация 
-----------------------------------------------------------------
'/resize/registration/'    POST 

json_reg = {'username': 'Pol',
            'password': '1234'}
            
-----------------------------------------------------------------
Отправить картинку для изменения размеров изображения
-----------------------------------------------------------------
/resize/post_task/<string:username>/<string:password>/  
POST

json_post_task = {
         'height': 100,
         'width': 100,
         'name_pic': 'dansing',
         'pic_base64': img_base64_str,
        }
        
В ответ получаем индификатор.

-----------------------------------------------------------------
Запрос на получение картинки 
-----------------------------------------------------------------
/resize/task_get/<string:username>/<string:password>/<string:identifier>/  
GET

Если обработка закончена то высылается изображение,
иначе сообщение о том, что картинка в обработке

-----------------------------------------------------------------
Получение всех индификаторов пользователя
-----------------------------------------------------------------
Если пользователь потерял идентификатор или хочет узнать статус всех запросов

/resize/get_all_identifier/<string:username>/<string:password>/  
GET

В ответ получаем json со всеми индефикаторами, именами изображений и статусом готовности

-----------------------------------------------------------------
Удаление картинки по идентификатору
-----------------------------------------------------------------
/resize/delete_task/<string:username>/<string:password>/<string:identifier>/    
DELETE

Удаляется все данные о изображении по идентификатору

-----------------------------------------------------------------
Изменение имени картинки
----------------------------------------------------------------
/resize/rename_pic/<string:username>/<string:password>/<string:identifier>/
PUT

Изменяем имя картинки.
'''




'''
******************************************************************************************
Небольшой пример работы api
'''


url = 'http://127.0.0.1:5000/'

'''Регистрация нового пользователя'''

url_reg = url + '/resize/registration/'

json_reg = {'username': 'Jac',
            'password': '1234'}

r_reg = requests.post(url_reg, json=json_reg)
print(r_reg.text, r_reg)

'''
Ответ при успешной регистрации
{  "Status": "Pol registration passed" }
 <Response [201]> 
 
 Если попытаемя зарегестрироватся еще раз с тем же именем, то 
 
 { "Status": "Username with this name already exist" }
 <Response [200]>
 
 '''

'''Отправка изображения.
   В uri указываем имя пользователя и пароль.'''

def img_to_base64str(image):
    img = Image.open(image)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    img_str_utf8 = img_str.decode("utf-8")
    return img_str_utf8

image = "dancing.jpg"
img_base64_str = img_to_base64str(image)

'''Как упоменалось выше нужно перекадировать изображение в base64'''

json_post_task = {
         'height': 100,
         'width': 100,
         'name_pic': 'dansing',
         'pic_base64': img_base64_str,
        }

url_post_task = url + '/resize/post_task/Pol/1234/'
r_post_task = requests.post(url_post_task, json=json_post_task)
print(r_post_task.text, r_post_task)
post_task = json.loads(r_post_task.text)
idf = post_task['Upload. Your personal ind = ']


'''
{  "Upload. Your personal ind = ": "c1fc31df-abfe-4966-a45a-472a27ac65c7"}
 <Response [200]>
'''

url_get_image = url + '/resize/task_get/Pol/1234/c1fc31df-abfe-4966-a45a-472a27ac65c7/'
r_get_image = requests.get(url_get_image)
print(r_get_image.text, r_get_image)

'''
{
  "Status": {
    "height": 100, 
    "name_pic": "dansing", 
    "pic_base64": "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", 
    "width": 100
  }
}

'''


