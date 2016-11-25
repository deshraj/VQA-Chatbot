from __future__ import absolute_import
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vqa.settings')
import django
django.setup()


from django.utils import timezone
from django.conf import settings

from chat.utils import log_to_terminal
from chat.models import UserDetail, QuestionAnswer

import chat.constants as constants
import PyTorch
import PyTorchHelpers
import pika
import time
import yaml
import json
import traceback

# Close the database connection in order to make sure that MYSQL Timeout doesn't occur
# django.db.close_old_connections()

# Loading the VQA Model forever
VQAModel = PyTorchHelpers.load_lua_class(constants.VQA_LUA_PATH, 'VqaChatbotTorchModel')
VQATorchModel = VQAModel(
    constants.VQA_CONFIG['vqa_model'],
    constants.VQA_CONFIG['cnn_proto'],
    constants.VQA_CONFIG['cnn_model'],
    constants.VQA_CONFIG['json_file'],
    constants.VQA_CONFIG['backend'],
    constants.VQA_GPUID,
)

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='vqa_chatbot_task', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    try:
        print(" [x] Received %r" % body)
        body = yaml.safe_load(body) # using yaml instead of json.loads since that unicodes the string in value
        print body
        result = VickiTorchModel.predict(body['image_path'], body['input_question'])
        log_to_terminal(body['socketid'], {"terminal": json.dumps(result)})
        log_to_terminal(body['socketid'], {"result": json.dumps(result)})
        log_to_terminal(body['socketid'], {"terminal": "Completed VQA Chatbot task"})

        # Close the database connection in order to make sure that MYSQL Timeout doesn't occur
        django.db.close_old_connections()

        user = UserDetail.objects.get(uuid=body['socketid'])
        # question_answer = QuestionAnswer.objects.filter(user = user, question = body['input_question'])[0]
        # question_answer.bot_answer = result['answer']
        # question_answer.bot_answer_time = timezone.now()
        # question_answer.save()

        # Close the database connection in order to make sure that MYSQL Timeout doesn't occur
        # django.db.close_old_connections()


        ch.basic_ack(delivery_tag = method.delivery_tag)
    except Exception, err:
        log_to_terminal(body['socketid'], {"terminal": json.dumps({"Traceback": str(traceback.print_exc())})})

channel.basic_consume(callback,
                      queue='vqa_chatbot_task')

channel.start_consuming()
