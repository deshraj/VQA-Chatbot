BOT_INTORDUCTION_MESSAGE = [
	"Welcome to CloudCV's Sequential Visual Question Answering. Upload an Image and you can ask me any question.",
]

NO_IMAGE_UPLOADED_MESSAGE = [
	"Umm....I think you forgot to upload an image.",
	"Please upload an image to ask questions.",
]


GRAD_CAM_RESPONSE_MESSAGE = [
	"Do you want to see at which portion of the image I looked to find the answer? See the following Image.",
	"",
	"",
]

VQA_GPUID = 0

VQA_CONFIG = {
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


if VQA_GPUID == -1:
    VQA_CONFIG['backend'] = "nn"
else:
    VQA_CONFIG['backend'] = "cudnn"
