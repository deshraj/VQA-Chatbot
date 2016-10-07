from django.utils import timezone
from django.conf import settings
from vicki.utils import log_to_terminal
from vicki.models import UserDetail, QuestionAnswer, Prediction
from vicki.sender import vqa_sender

from channels import Group

import json
import redis
import datetime
import os
import shutil
import pdb


r = redis.StrictRedis(host='localhost', port=6379, db=0)

def ws_connect(message):
    print "User connnected via Socket"


def ws_message(message):
    body = json.loads(message.content['text'])
    print "INCOMING REQUEST"
    if body["event"] == "ConnectionEstablished":
        Group(body["socketid"]).add(message.reply_channel)
        log_to_terminal(body["socketid"], {"info": "User added to the Channel Group"})

    elif body["event"] == "start":
        user = UserDetail.objects.get(uuid = body["socketid"])
        current_datetime = timezone.now()
        user.start_time = current_datetime
        user.name = body["username"]
        user.save()
        r.set("start_time_{}".format(body["socketid"]), current_datetime.strftime("%I:%M%p on %B %d, %Y"))

    elif body["event"] == "questionSubmitted":
        user = UserDetail.objects.get(uuid = body["socketid"])
        print "recieved question at the backend"
        QuestionAnswer.objects.create(user = user, question = body["question"])
        target_image = r.get("target_{}".format(body["socketid"]))
        target_image_abs_path = os.path.join(settings.BASE_DIR, target_image[1:])

        output_dir = os.path.join(settings.MEDIA_ROOT, 'vicki', body["socketid"])

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            shutil.copy(target_image_abs_path, output_dir)

        vqa_sender(body['question'], "", target_image_abs_path, output_dir, body["socketid"])

    elif body["event"] == "end":
        user = UserDetail.objects.get(uuid = body["socketid"])
        current_datetime = timezone.now()
        target_image = r.get("target_{}".format(body["socketid"]))
        predicted_image = body["predicted_image"]
        Prediction.objects.create(user = user, predicted_image = predicted_image)

        if target_image == predicted_image:
            time_elapsed = current_datetime - user.start_time
            time_elapsed_in_minutes = "{0:.2f}".format(time_elapsed.total_seconds()/60)
            log_to_terminal(body["socketid"], {"finalResult": True, "time_elapsed": time_elapsed_in_minutes})
        else:
            log_to_terminal(body["socketid"], {"finalResult": False })


# Connected to websocket.disconnect
def ws_disconnect(message):
    print message.content
    # Group("chat").discard(message.reply_channel)