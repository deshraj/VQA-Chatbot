from django.conf import settings
from chat.utils import log_to_terminal

import os
import pika
import sys
import json

def vqa_sender(input_question, image_path, socketid):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='vqa_chatbot_task', durable=True)
    message = {
        'image_path': image_path,
        'input_question': input_question,
        'socketid': socketid,
    }

    log_to_terminal(socketid, {"terminal": "Publishing job to VQA Chatbot Queue"})
    channel.basic_publish(exchange='',
                      routing_key='vqa_chatbot_task',
                      body=json.dumps(message),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))

    print(" [x] Sent %r" % message)
    log_to_terminal(socketid, {"terminal": "Job published successfully"})
    connection.close()
