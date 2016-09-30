
from __future__ import absolute_import
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'svqa.settings')

from django.conf import settings
from chat.utils import log_to_terminal

import chat.constants as constants
import PyTorch
import PyTorchHelpers
import pika
import time
import yaml
import json
import traceback

# Loading the VQA Model forever
SVQAModel = PyTorchHelpers.load_lua_class(constants.SVQA_LUA_PATH, 'SVQATorchModel')
SVqaTorchModel = SVQAModel(
    constants.SVQA_CONFIG['proto_file'],
    constants.SVQA_CONFIG['model_file'],
    constants.SVQA_CONFIG['input_sz'],
    constants.SVQA_CONFIG['backend'],
    constants.SVQA_CONFIG['layer_name'],
    constants.SVQA_CONFIG['model_path'],
    constants.SVQA_CONFIG['input_encoding_size'],
    constants.SVQA_CONFIG['rnn_size'],
    constants.SVQA_CONFIG['rnn_layers'],
    constants.SVQA_CONFIG['common_embedding_size'],
    constants.SVQA_CONFIG['num_output'],
    constants.SVQA_CONFIG['seed'],
    constants.SVQA_GPUID,
)

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='svqa_task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    try:
        print(" [x] Received %r" % body)
        body = yaml.safe_load(body) # using yaml instead of json.loads since that unicodes the string in value

        result = SVqaTorchModel.predict(body['image_path'], constants.SVQA_CONFIG['input_sz'], constants.SVQA_CONFIG['input_sz'], body['input_question'], body['input_answer'], body['output_dir'])
        result['input_image'] = str(result['input_image']).replace(settings.BASE_DIR, '')
        result['svqa_gcam'] = str(result['svqa_gcam']).replace(settings.BASE_DIR, '')
        result['svqa_gcam_raw'] = str(result['svqa_gcam_raw']).replace(settings.BASE_DIR, '')
        result['svqa_gb'] = str(result['svqa_gb']).replace(settings.BASE_DIR, '')
        result['svqa_gb_gcam'] = str(result['svqa_gb_gcam']).replace(settings.BASE_DIR, '')

        log_to_terminal(body['socketid'], {"terminal": json.dumps(result)})
        log_to_terminal(body['socketid'], {"result": json.dumps(result)})
        log_to_terminal(body['socketid'], {"terminal": "Completed the Grad-CAM VQA task"})

        ch.basic_ack(delivery_tag = method.delivery_tag)
    except Exception, err:
        log_to_terminal(body['socketid'], {"terminal": json.dumps({"Traceback": str(traceback.print_exc())})})

channel.basic_consume(callback,
                      queue='svqa_task_queue')

channel.start_consuming()
