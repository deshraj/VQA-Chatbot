#!/bin/sh

cd models

# VGG-19
wget -c https://gist.githubusercontent.com/ksimonyan/3785162f95cd2d5fee77/raw/bb2b4fe0a9bb0669211cf3d0bc949dfdda173e9e/VGG_ILSVRC_19_layers_deploy.prototxt
wget -c http://www.robots.ox.ac.uk/~vgg/software/very_deep/caffe/VGG_ILSVRC_19_layers.caffemodel
wget -c https://filebox.ece.vt.edu/~jiasenlu/codeRelease/co_atten/data_file/vqa_data_prepro_all.json
wget -c https://filebox.ece.vt.edu/~jiasenlu/codeRelease/co_atten/model/vqa_model/model_alternating_train-val_vgg.t7

cd ..
