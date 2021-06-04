# -*- coding: utf-8 -*-
import os
import onnx
from onnxsim import simplify


def onnx2onnx(params):
    print('onnx simplify')
    model = onnx.load(params['weight_path'])
    model_simp, check = simplify(model)
    if check:
        print('success')
        return model_simp
    else:
        print('failed')
        return None

class Converter:
    def __init__(self):
        pass

    @staticmethod
    def save(model, params):
        output_format = params['output_format']
        output_name = params['output_name']
        username = params['username']
        output_path = os.path.abspath(os.path.join('static', 'output', username))
        os.makedirs(output_path, exist_ok=True)
        if output_format == 'onnx':
            output_path = os.path.join(output_path, output_name + '.onnx')
            onnx.save(model, output_path)
        return str(output_path)

    @staticmethod
    def convert(params):
        input_format = params['input_format']
        output_format = params['output_format']
        func = eval(input_format + '2' + output_format)
        model = func(params)
        if model is None:
            return {'msg': 'FAILED'}
        model_path = Converter.save(model, params)
        return {'msg': 'SUCCESS', 
                'model_path': model_path, 
                'output_format': output_format,
                'date': params['date'],
                'output_name': params['output_name']}
        
    
    
