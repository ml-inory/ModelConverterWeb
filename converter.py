# -*- coding: utf-8 -*-
import os
import onnx
from onnxsim import simplify


def onnx2onnx(params):
    model = onnx.load(params['weight_path'])
    model_simp, check = simplify(model)
    output_name = params['output_name']
    if check:
        output_path = os.path.join(Converter.model_root, output_name + '.onnx')
        onnx.save(model_simp, output_path)
        return output_path
    else:
        return None

def onnx2tengine(params):
    onnx_file = params['weight_path']
    output_name = params['output_name']
    tmfile = os.path.join(Converter.model_root, output_name + '.tmfile')
    os.system('convert_tool -f onnx -m {} -o {}'.format(onnx_file, tmfile))
    return tmfile

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
        model_path = func(params)
        if model_path is None:
            return {'msg': 'FAILED'}
        return {'msg': 'SUCCESS', 
                'model_path': model_path, 
                'output_format': output_format,
                'date': params['date'],
                'output_name': params['output_name']}
        
    
    
