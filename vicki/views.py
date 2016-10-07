from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from vicki.sender import svqa
from vicki.utils import log_to_terminal, get_random_images

import vicki.constants as constants

import uuid
import os
import traceback
import random
import urllib2


def home(request, template_name="vicki/index.html"):
    socketid = uuid.uuid4()

    random_images = get_random_images(constants.COCO_IMAGES)

    intro_message = random.choice(constants.BOT_INTORDUCTION_MESSAGE)
    if request.method == "POST":
        try:
            socketid = request.POST.get("socketid")
            question = request.POST.get("question")
            img_path = request.POST.get("img_path")
            input_answer = ""
            img_path = urllib2.unquote(img_path)
            abs_image_path = str(img_path)
            out_dir = os.path.dirname(abs_image_path)

            response = svqa(str(question), str(input_answer), str(abs_image_path), str(out_dir+"/"), socketid)

        except Exception, err:
            log_to_terminal(socketid, {"terminal": traceback.print_exc()})

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
