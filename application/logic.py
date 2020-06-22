from io import BytesIO
from PIL import Image
import base64
import io



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
    #print('The original image size is {wide} wide x {height} '
    #     'high'.format(wide=w, height=h))

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
    width, height = scaled_image.size
    #scaled_image.show()  вывод получившейся картинки на экран(для наглядной проверки)
    # print('The scaled image size is {wide} wide x {height} '
    #      'high'.format(wide=width, height=height))
    return scaled_image