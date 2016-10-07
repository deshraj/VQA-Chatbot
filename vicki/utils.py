from django.conf import settings
from channels import Group
import json
import os
import random
import traceback


def log_to_terminal(socketid, message):
    Group(socketid).send({"text": json.dumps(message)})


def get_random_images(images_path):
    try:
        print images_path
        images_list = os.listdir(images_path)
        print images_list
        demo_images = [random.choice(images_list) for i in range(24)]
        demo_images = [os.path.join(settings.MEDIA_URL, 'vicki', 'coco', x) for x in demo_images]
        return demo_images
    except Exception:
        print traceback.format_exc()
