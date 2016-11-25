from django.conf import settings
import os

BOT_INTRODUCTION_MESSAGE = [
	"Hi, I am a Visual Chatbot, capable of answering a sequence of questions about images. Please upload an image and fire away!",
]

NO_IMAGE_UPLOADED_MESSAGE = [
	"Umm....I think you forgot to upload an image.",
	"Please upload an image to ask questions.",
]

VQA_GPUID = 0

VQA_CONFIG = {
    'vqa_model': 'models/model_alternating_train-val_vgg.t7',
    'cnn_proto': 'models/VGG_ILSVRC_19_layers_deploy.prototxt',
    'cnn_model': 'models/VGG_ILSVRC_19_layers.caffemodel',
    'json_file': 'models/vqa_data_prepro_all.json',    
}

if VQA_GPUID == -1:
    VQA_CONFIG['backend'] = "nn"
else:
    VQA_CONFIG['backend'] = "cudnn"

VQA_LUA_PATH = "vicki_new.lua"

