# nnie_mapper

## 安装

`apt-get install -y libjpeg-dev libpng-dev libtiff-dev`

## 使用

### 优化模型

`python3 caffe_optim.py --prototxt xxx.prototxt --caffemodel xxx.caffemodel`

脚本依赖Caffe，在[这里](https://gitee.com/ml-inory/Caffe)

### 转换模型

`./nnie_mapper_12 example_config.txt`

example_config.txt是转换模型的配置文件，请自行修改。



若提示库找不到，请先执行`source setup.sh`