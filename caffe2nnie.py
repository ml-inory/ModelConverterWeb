# -*- coding: utf-8 -*-
import os, sys
import glob
import numpy as np
sys.path.append('/usr/local/python')
os.environ['GLOG_minloglevel'] = '0'
import caffe
import subprocess
from caffe.proto import caffe_pb2
from google.protobuf import text_format
caffe.set_mode_cpu()

__all__ = ['convert_to_nnie',]

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Caffe to NNIE model Converter')
    parser.add_argument('--output', help='generated model wk', required=True)
    parser.add_argument('--prototxt', help='caffe prototxt path', required=False)
    parser.add_argument('--caffemodel', help='caffe weight path', required=True)
    parser.add_argument('--image_dir', help='Image folder used for quantizing', required=True)
    parser.add_argument('--RGB', help='preprocess param: convert to RGB, default False', default=False, action='store_true')
    parser.add_argument('--scale', help='preprocess param: img = img * scale', default=1.0, type=float)
    parser.add_argument('--mean', help='preprocess param: img = img - mean', default=0, type=float, nargs='*')
    
    args = parser.parse_args()
    return args


def write_f(f, key, value):
    f.write(f'[{key}] {value}\n')

def gen_imageList(image_dir):
    with open('imageList.txt', 'w') as f:
        imgs = glob.glob(image_dir + '/*.jpg')
        for img in imgs:
            f.write(img + '\n')

def gen_mean(mean):
    with open('mean.txt', 'w') as f:
        if len(mean) == 1:
            f.write(f'{mean[0]}\n{mean[0]}\n{mean[0]}')
        else:
            f.write(f'{mean[0]}\n{mean[1]}\n{mean[2]}')

def convert_to_nnie(output, prototxt, caffemodel, image_dir, work_dir='../../mapper/', RGB=True, preprocess=True, scale=0.0078125, mean=[127.5], int8=True):
    cur_path = os.path.abspath(os.getcwd())

    os.chdir(work_dir)
    gen_imageList(os.path.join(cur_path, image_dir))

    model_name = os.path.splitext(os.path.basename(output))[0]
    cfg_file = model_name + '.cfg'
    with open(cfg_file, 'w') as f:
        write_f(f, 'prototxt_file', os.path.join(cur_path, prototxt))
        write_f(f, 'caffemodel_file', os.path.join(cur_path, caffemodel))
        write_f(f, 'net_type', 0)
        write_f(f, 'image_list', './imageList.txt')
        write_f(f, 'image_type', 1)
        write_f(f, 'instruction_name', model_name)

        if preprocess:
            write_f(f, 'norm_type', 5)
            write_f(f, 'data_scale', scale)
            gen_mean(mean)
            write_f(f, 'mean_file', './mean.txt')
        else:
            write_f(f, 'norm_type', 0)
            write_f(f, 'data_scale', '1.0')
            write_f(f, 'mean_file', 'null')


        if int8:
            write_f(f, 'compile_mode', 0)
        else:
            write_f(f, 'compile_mode', 1)

        if RGB:
            write_f(f, 'RGB_order', 'RGB')
        else:
            write_f(f, 'RGB_order', 'BGR')

    print(f'Generate {cfg_file}')
    
    # remember LD_LIBRARY_PATH
    tmp_ld = os.environ['LD_LIBRARY_PATH']
    # os.system('bash setup.sh')
    lib_path = os.path.abspath(os.path.join('./', 'lib'))
    os.environ['LD_LIBRARY_PATH'] = f'{lib_path}'
    print(os.environ['LD_LIBRARY_PATH'])
    try:
        subprocess.run(['./nnie_mapper_12', f'{cfg_file}'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        os.chdir(cur_path)
        return None, e.stdout.decode("utf-8") + e.stderr.decode("utf-8")
    os.chdir(cur_path)
    os.system(f'mv {work_dir}/{model_name}.wk {output}')
    os.environ['LD_LIBRARY_PATH'] = tmp_ld
    return output, ''

def main():
    if 'NNIE_MAPPER' not in os.environ.keys():
        print('Please export NNIE_MAPPER first! Set it to the path of nnie_mapper')
        sys.exit(-1)

    args = parse_args()
    work_dir = os.environ['NNIE_MAPPER']
    old_ptx = args.prototxt
    old_model = args.caffemodel
    convert_to_nnie(args.output, old_ptx, old_model, args.image_dir, work_dir, args.RGB, True, args.scale, args.mean, True)

if __name__ == '__main__':
    main()