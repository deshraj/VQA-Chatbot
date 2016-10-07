from django.conf import settings
import os

COCO_IMAGES = os.path.join(settings.MEDIA_ROOT, 'vicki', 'coco', 'val2014')

BOT_INTORDUCTION_MESSAGE = [
	"Hi, My name is Vicki. Upload an image and you can ask me any number of questions related to that image.",
]

NO_IMAGE_UPLOADED_MESSAGE = [
	"Umm....I think you forgot to upload an image.",
	"Please upload an image to ask questions.",
]


GRAD_CAM_RESPONSE_MESSAGE = [
	"Do you want to see at which portion of the image I looked to find the answer? See the following Image.",
]

SVQA_GPUID = 0

SVQA_CONFIG = {
    'proto_file': 'models/VGG_ILSVRC_19_layers_deploy.prototxt',
    'model_file': 'models/VGG_ILSVRC_19_layers.caffemodel',
    'input_sz': 224,
    'backend': '',
    'layer_name': 'relu5_4',
    'model_path': 'VQA_LSTM_CNN/lstm.t7',
    'input_encoding_size': 200,
    'rnn_size': 512,
    'rnn_layers': 2,
    'common_embedding_size': 1024,
    'num_output': 1000,
    'seed': 123,
    'image_dir': os.path.join(settings.BASE_DIR, 'media', 'svqa')
}


if SVQA_GPUID == -1:
    SVQA_CONFIG['backend'] = "nn"
else:
    SVQA_CONFIG['backend'] = "cudnn"

SVQA_LUA_PATH = "svqa.lua"
