# -*- coding: utf-8 -*-
import os
import onnx
from onnxsim import simplify
import subprocess
from onnx2caffe import getGraph, convertToCaffe, optimize
from caffe2nnie import convert_to_nnie

class Converter:
    model_root = ''

    def __init__(self):
        pass

    @staticmethod
    def build_dir(username):
        output_path = os.path.abspath(os.path.join('static', 'output', username))
        os.makedirs(output_path, exist_ok=True)
        Converter.model_root = output_path

    @staticmethod
    def convert(params):
        Converter.build_dir(params['username'])

        input_format = params['input_format']
        output_format = params['output_format']
        func = eval(input_format + '2' + output_format)
        model_path, err_msg = func(params)
        if model_path is None:
            return {'msg': err_msg}
        return {'msg': 'SUCCESS', 
                'model_path': model_path, 
                'output_format': output_format,
                'date': params['date'],
                'output_name': params['output_name']}


def onnx2onnx(params):
    model = onnx.load(params['weight_path'])
    model_simp, check = simplify(model)
    output_name = params['output_name']
    if check:
        output_path = os.path.join(Converter.model_root, output_name + '.onnx')
        onnx.save(model_simp, output_path)
        return output_path, ''
    else:
        return None, ''

def onnx2tengine(params):
    onnx_file = params['weight_path']
    output_name = params['output_name']
    tmfile = os.path.join(Converter.model_root, output_name + '.tmfile')
    try:
        subprocess.run(['convert_tool', '-f', 'onnx', '-m', onnx_file, '-o', tmfile], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        return None, e.stdout.decode("utf-8") + e.stderr.decode("utf-8")
    return tmfile, ''

def onnx2caffe(params):
    onnx_file = params['weight_path']
    output_name = params['output_name']
    old_ptx = os.path.join(Converter.model_root, output_name + '.prototxt')
    old_model = os.path.join(Converter.model_root, output_name + '.caffemodel')
    new_ptx = old_ptx.replace('.prototxt', '_optim.prototxt')
    new_model = old_model.replace('.caffemodel', '_optim.caffemodel')
    graph = getGraph(onnx_file)
    try:
        convertToCaffe(graph, old_ptx, old_model, save_prototxt=True)
        optimize(old_ptx, old_model, new_ptx, new_model)
    except Exception as e:
        print(str(e))
        return None
    return new_ptx, new_model

# 解压缩图片集合
def uncompress_img_archive(params):
    import zipfile, tarfile
    img_archive = params['img_archive']
    output_path = os.path.join(Converter.model_root, os.path.basename(img_archive))
    os.makedirs(output_path, exist_ok=True)
    if img_archive.endswith('.zip'):
        #zipfile解压
        try:
            z = zipfile.ZipFile(img_archive, 'r')
            z.extractall(path=output_path)
            z.close()
        except:
            return None
    else:
        try:
            tar = tarfile.open(img_archive, 'r')
            tar.extractall(path=output_path)  # 可设置解压地址
            tar.close()
        except:
            return None
    return output_path

def caffe2nnie(caffe_output, params):
    cf_ptx, cf_model = caffe_output
    output_name = params['output_name']
    wk = os.path.join(Converter.model_root, output_name + '.wk')
    # 解压图片
    image_dir = uncompress_img_archive(params)
    if image_dir is None:
        return False
    work_dir = './nnie_mapper'
    is_rgb = params['order'] == 'RGB'
    scale = params['scale']
    mean = params['mean']
    return convert_to_nnie(wk, cf_ptx, cf_model, image_dir, work_dir, tmp_dir=os.path.abspath(os.path.join('static', 'input', params['username'])), RGB=is_rgb, preprocess=True, scale=scale, mean=[mean], int8=True)

def onnx2nnie(params):
    caffe_output = onnx2caffe(params)
    if caffe_output is None:
        return None, ''
    wk, err_msg = caffe2nnie(caffe_output, params)
    return wk, err_msg
    
