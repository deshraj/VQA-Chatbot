#!/bin/sh

cd models

# VGG-19
wget -c https://gist.githubusercontent.com/ksimonyan/3785162f95cd2d5fee77/raw/bb2b4fe0a9bb0669211cf3d0bc949dfdda173e9e/VGG_ILSVRC_19_layers_deploy.prototxt
wget -c http://www.robots.ox.ac.uk/~vgg/software/very_deep/caffe/VGG_ILSVRC_19_layers.caffemodel

cd ..

# VQA
cd VQA_LSTM_CNN
wget -c https://filebox.ece.vt.edu/~jiasenlu/codeRelease/vqaRelease/train_only/data_train_val.zip
wget -c https://filebox.ece.vt.edu/~jiasenlu/codeRelease/vqaRelease/train_only/pretrained_lstm_train_val.t7.zip
unzip data_train_val.zip
unzip pretrained_lstm_train_val.t7.zip
cd ..
