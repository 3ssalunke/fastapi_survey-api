import re as _re
import datetime as _dt
import base64 as _bs64
import os as _os


def save_image(image_data, slug):
    image_path = "no_image"
    pattern = _re.match(r'^data:image\/(\w+);base64', image_data)
    if pattern is not None:
        ext = pattern[1]
        image_data = image_data.split(",")[1]
        image_path = f"./images/{slug}_{_dt.datetime.now().microsecond}.{ext}"
        with open(image_path, "wb") as imgFile:
            imgFile.write(_bs64.b64decode(image_data))

    return image_path


def delete_image(image_path):
    print(image_path)
    if _os.path.exists(image_path):
        _os.remove(image_path)
    else:
        raise Exception("The file does not exist")
