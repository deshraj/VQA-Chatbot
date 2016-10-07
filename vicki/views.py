from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from vicki.utils import log_to_terminal, get_random_images
from vicki.models import UserDetail

import vicki.constants as constants

import uuid
import os
import traceback
import random
import urllib2
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def home(request, template_name="vicki/index.html"):
    socketid = uuid.uuid4()

    random_images = get_random_images(constants.COCO_IMAGES)
    target_image = random.choice(random_images)
    r.set("target_{}".format(str(socketid)), target_image)

    UserDetail.objects.create(uuid = socketid, target_image = target_image)
    intro_message = random.choice(constants.BOT_INTORDUCTION_MESSAGE)
    return render(request, template_name, {
        "socketid": socketid,
        "bot_intro_message": intro_message,
        "random_images": random_images
    })


def upload_image(request):
    if request.method == "POST":
        image = request.FILES['file']
        socketid = request.POST.get('socketid')
        output_dir = os.path.join(settings.MEDIA_ROOT, 'svqa', socketid)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        img_path = os.path.join(output_dir, str(image))
        handle_uploaded_file(image, img_path)
        print request.POST
    return JsonResponse({"file_path": img_path})


def handle_uploaded_file(f, path):
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
