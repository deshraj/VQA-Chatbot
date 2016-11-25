require 'torch'
require 'hdf5'
require 'xlua'
require 'cunn';
require 'rnn'
require 'optim'
require 'image'
require 'loadcaffe'
cjson = require('cjson')

local eval = require 'eval'
local models = require 'models'
local utils = require 'utils'


local TorchModel = torch.class('SVQATorchModel')

function TorchModel:__init(rnn_size, embedding_size, image_input_dim, model_type, num_lstm_layers, epoch, use_gpu, batch_size, epochs, learning_rate, learning_rate_decay, learning_rate_decay_after, seed, save_every, data_file_train, data_file_val, checkpoint_dir, savefile, temperature, proto_file, model_file, backend)

  self.rnn_size = rnn_size
  self.embedding_size = embedding_size
  self.image_input_dim = image_input_dim
  self.model_type = model_type
  self.num_lstm_layers = num_lstm_layers
  self.epoch = epoch
  self.use_gpu = use_gpu
  self.batch_size = batch_size
  self.epochs = epochs
  self.learning_rate = learning_rate
  self.learning_rate_decay = learning_rate_decay
  self.learning_rate_decay_after = learning_rate_decay_after
  self.seed = seed
  self.save_every = save_every
  self.data_file_train = data_file_train
  self.data_file_val = data_file_val
  self.checkpoint_dir = checkpoint_dir
  self.savefile = savefile
  self.temperature = temperature
  self.proto_file = proto_file
  self.model_file = model_file
  self.backend = backend

  torch.manualSeed(self.seed)

  -- load and invert the dictionary
  local cjson = require "cjson"
  local file = io.open('data/dict_0.5.json', 'r')
  local text = file:read()
  file:close()
  _dict = cjson.decode(text)
  dict = {}
  for k,v in pairs(_dict) do
      dict[v] = k
  end

  print('Loading model...')
  -- cnn stuff
  cnn = loadcaffe.load(self.proto_file, self.model_file, self.backend)
  cnn:evaluate()
  cnn:remove()
  cnn:remove()

  -- model
  model_filename =  "checkpoints/0.5_imseq2seq2qi_512_300_epoch_36.t7"
  print('loading', model_filename)
  model = torch.load(model_filename).model

  im_net = model[1]
  embedding_net = model[2]
  final_model_enc = model[3]
  final_model_dec = model[4]

  im_net:evaluate()
  embedding_net:evaluate()
  final_model_enc:evaluate()
  final_model_dec:evaluate()

  if self.use_gpu then
      cnn = cnn:cuda()
      im_net = im_net:cuda()
      embedding_net = embedding_net:cuda()
      final_model_enc = final_model_enc:cuda()
      final_model_dec = final_model_dec:cuda()
  end

  self.final_model_enc = final_model_enc
  self.final_model_dec = final_model_dec
  self.cnn = cnn
  self.embedding_net = embedding_net
  self.dict = dict
  self.im_net = im_net

end


function TorchModel:predict(input_image_path, history, question)
    -- Tokenize question
  function vector_to_string(vector, dict)
      local steps = vector:size(1)
      local string = ''
      for i=1,steps do
          if (dict[vector[i]] ~= 'PAD') then
              string = string .. ' ' .. dict[vector[i]]
          end
      end
      return string
  end

    local cmd = 'python prepro_ques.py -question "'.. question..'"'
    os.execute(cmd)
    file = io.open('ques_feat.json')
    text = file:read()
    file:close()
    q_feats = cjson.decode(text)

    enc_input = utils.right_align(torch.LongTensor{q_feats.ques}, torch.LongTensor{q_feats.ques_length})

    img = utils.preprocess(input_image_path, 224, 224)

    -- move everything to GPU
    if self.use_gpu then
        enc_input = enc_input:cuda()
        img = img:cuda()
    end

    self.final_model_enc:remember()
    self.final_model_dec:remember()

    enc_out = self.final_model_enc:forward(enc_input:t())
    models.forward_connect(self.final_model_enc, self.final_model_dec)

    im_feats = self.cnn:forward(img)
    im_out = self.im_net:forward(im_feats)

    prev_t = torch.DoubleTensor(1, 1):cuda()
    prev_t[{{1},{1}}] = 10002 -- start
    dec = {}
    ans_len = 0
    for i = 1, 50 do
        if i == 1 then
            self.final_model_dec:forward(im_out:view(1, 1, im_out:size(1)))
        else
            prev_embed = self.embedding_net:forward(prev_t)
            oo = self.final_model_dec:forward(prev_embed)
            -- _, idx = torch.max(oo, 3)
            oo:div(self.temperature)
            oo:exp()
            idx = torch.multinomial(oo[1][1], 1, true)
            -- prev_t[{{1},{1}}] = idx[1][1][1]
            prev_t[{{1},{1}}] = idx[1]
            -- if idx[1][1][1] == 10003 then
            if idx[1] == 10003 then
                break
            end
            -- table.insert(dec, idx[1][1][1])
            table.insert(dec, idx[1])
            ans_len = ans_len + 1
        end
    end

    dec_f = torch.FloatTensor(1, ans_len):fill(0)
    for i = 1, ans_len do
        dec_f[1][i] = dec[i]
    end

    answer = vector_to_string(dec_f[1], self.dict)

    self.final_model_enc:forget()
    self.final_model_dec:forget()

    result = {}
    result['answer'] = answer
    result['question'] = question
    result['input_image'] = input_image_path

    if history == "" then
      result['history'] = question.."? "..answer.."***"
    else
      result['history'] = history.." "..question.."? "..answer.."***"
    end
    print(result['history'])
    return result
end