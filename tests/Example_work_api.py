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

json_reg = {'username': 'Pol',
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
print(r_post_task.text, r_reg)
post_task = json.loads(r_post_task.text)
idf = post_task['Upload. Your personal ind = ']


'''
{  "Upload. Your personal ind = ": "c1fc31df-abfe-4966-a45a-472a27ac65c7"}
 <Response [200]>
'''

url_get_image = url + '/resize/task_get/Pol/1234/c1fc31df-abfe-4966-a45a-472a27ac65c7/'
r_get_image = requests.get(url_get_image)
print(r_get_image.text)
