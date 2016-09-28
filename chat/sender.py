from django.conf import settings
from chat.utils import log_to_terminal

import os
import pika
import sys
import json


def svqa(input_question, input_answer, image_path, out_dir, socketid):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='svqa_task_queue', durable=True)
    message = {
        'image_path': image_path,
        'input_question': input_question,
        'input_answer': input_answer,
        'output_dir': out_dir,
        'socketid': socketid,
    }

    log_to_terminal(socketid, {"terminal": "Publishing job to SVQA Queue"})
    channel.basic_publish(exchange='',
                      routing_key='svqa_task_queue',
                      body=json.dumps(message),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))

    print(" [x] Sent %r" % message)
    log_to_terminal(socketid, {"terminal": "Job published successfully"})
    connection.close()
