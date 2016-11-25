require 'torch'
require 'nn'
require 'nngraph'
require 'io'
require 'rnn'
require 'image'
require 'maskSoftmax'
require 'loadcaffe'
utils = dofile('utils.lua');
cjson = require('cjson')


-- cmd = torch.CmdLine()
-- cmd:text()
-- cmd:text('Test the s-vqa model for retrieval')
-- cmd:text()
-- cmd:text('Options')

-- -- Data input settings
-- cmd:option('-input_json','data/chat_processed_params.json','json path with info and vocab')

-- cmd:option('-load_path', 'models/mn-qih-g-102.t7', 'path to saved model')
-- cmd:option('-result_path', 'results', 'path to save generated results')

-- -- Optimization params
-- cmd:option('-gpuid', 0, 'GPU id to use')
-- cmd:option('-backend', 'cudnn', 'nn|cudnn')

-- -- CNN parameters
-- cmd:option('-proto_file', 'models/VGG_ILSVRC_16_layers_deploy.prototxt')
-- cmd:option('-model_file', 'models/VGG_ILSVRC_16_layers.caffemodel')

-- opt = cmd:parse(arg);
-- print(opt)


local TorchModel = torch.class('VisDialTorchModel')

function TorchModel:__init()

  opt = {}
  opt['input_json'] = 'data/chat_processed_params.json'
  opt['load_path'] = 'models/mn-qih-g-102.t7'
  opt['result_path'] = 'results'
  opt['gpuid'] = 0
  opt['backend'] = 'cudnn'
  opt['proto_file'] = 'models/VGG_ILSVRC_16_layers_deploy.prototxt'
  opt['model_file'] = 'models/VGG_ILSVRC_16_layers.caffemodel'

  self.input_json = 'data/chat_processed_params.json'
  self.load_path = 'models/mn-qih-g-102.t7'
  self.result_path = 'results'
  self.gpuid = 0
  self.backend = 'cudnn'
  self.proto_file = 'models/VGG_ILSVRC_16_layers_deploy.prototxt'
  self.model_file = 'models/VGG_ILSVRC_16_layers.caffemodel'


  -- seed for reproducibility
  torch.manualSeed(1234);

  -- set default tensor based on gpu usage
  if opt.gpuid >= 0 then
      require 'cutorch'
      require 'cunn'
      --if opt.backend == 'cudnn' then require 'cudnn' end
      -- torch.setdefaulttensortype('torch.CudaTensor');
  -- else
      -- torch.setdefaulttensortype('torch.DoubleTensor');
  end

  -- load model checkpoint
  local savedModel = torch.load(opt.load_path);

  -- transfer all options to model
  local modelParams = savedModel.modelParams;
  opt.img_norm = modelParams.img_norm;
  opt.model_name = modelParams.model_name;
  print(opt.model_name)

  -- add flags for various configurations
  if string.match(opt.model_name, 'h') then opt.useHistory = true; end
  if string.match(opt.model_name, 'i') then opt.useIm = true; end

  -- load CNN
  cnn = loadcaffe.load(opt.proto_file, opt.model_file, opt.backend)
  cnn:evaluate()
  cnn:remove()
  cnn:remove()
  cnn:add(nn.Normalize(2))

  if opt.gpuid >= 0 then
      cnn = cnn:cuda()
  end

  -- Setup the model
  require 'model'
  print('Using models from '..modelParams.model_name)
  svqaModel = SVQAModel(modelParams);

  -- copy the weights from loaded model
  svqaModel.wrapperW:copy(savedModel.modelW);

  -- Initialize dataloader
  dataloader = dofile('dataloader.lua')
  dataloader:initialize(self)
  collectgarbage()

  self.cnn = cnn
  self.svqaModel = svqaModel
  self.dataloader = dataloader
  self.opt = opt
end


function TorchModel:predict(img, history, question)

    print("History table length in lua")
    print(table.getn(history))
    img_path = img -- storing the image path to send back to client side

    history_concat = ''
    for i = 1, #history do
        history_concat = history_concat .. history[i] .. '||||'
    end
    -- print(history_concat)

    local cmd = 'python prepro_ques.py -question "' .. question .. '" -history "' .. history_concat .. '"'
    os.execute(cmd)
    file = io.open('ques_feat.json')
    text = file:read()
    file:close()
    feats = cjson.decode(text)
    
    -- print(feats.question)
    -- print('history length', #feats.history)

    ques_vector = utils.wordsToId(feats.question, self.dataloader.word2ind)
    hist_tensor = torch.LongTensor(#history, 15)
    for i = 1, #feats.history do
        -- print(utils.wordsToId(feats.history[i], dataloader.word2ind, 15))
        hist_tensor[i] = utils.wordsToId(feats.history[i], self.dataloader.word2ind, 15)
    end

    img = utils.preprocess(img, 224, 224)
    -- print(#img)

    if opt.gpuid >= 0 then
        img = img:cuda()
        ques_vector = ques_vector:cuda()
        hist_tensor = hist_tensor:cuda()
    end

    img_feats = self.cnn:forward(img)
    -- print(#img_feats)

    preds = self.svqaModel:predict(img_feats, ques_vector, hist_tensor, self.dataloader)
    answer_string = utils.idToWords(preds, self.dataloader.ind2word)
    result = {}
    result['answer'] = answer_string
    result['question'] = question
    if history_concat == "||||" then
      history_concat = ""
    end
    result['history'] = history_concat .. question .. " " .. answer_string
    result['input_image'] = img_path
    return result
end
