from os import error, stat
from celery import Celery
from converter import Converter
from celery.signals import after_task_publish, before_task_publish
from celery.result import AsyncResult
from celery.states import *
from celery.exceptions import Ignore

cel = Celery(
        'tasks',
        backend='redis://localhost:9394/0',
        broker='redis://localhost:9394/1'
    )

@cel.task(bind=True)
def convert_model(self, params):
    ret = Converter.convert(params)
    if ret['msg'] != 'SUCCESS':
        raise RuntimeError('Convert %s to %s of name %s failed!\nerror message:\n%s\n' % (params['input_format'], params['output_format'], params['output_name'], ret['msg']))
    else:
        return ret
    

class TaskMonitor:
    tasks = {}

    def __init__(self):
        pass

    @staticmethod
    def append(username, task_id, date, output_format, output_name):
        if username not in TaskMonitor.tasks.keys():
            TaskMonitor.tasks[username] = []
        
        TaskMonitor.tasks[username].append(dict(task_id=task_id, date=date, output_format=output_format, output_name=output_name, state='PENDING', model_path='', err_msg=''))

    # 返回所有任务
    @staticmethod
    def query(username):
        if username not in TaskMonitor.tasks.keys():
            return []

        tasks = TaskMonitor.tasks[username]
        for t in tasks:
            task_id = t['task_id']
            result = AsyncResult(id=task_id, app=cel)
            # success = result.successful()
            t['state'] = result.state
            if t['state'] == 'SUCCESS':
                t['model_path'] = result.get()['model_path']
        return tasks

    @staticmethod
    def query(username, tid):
        if username not in TaskMonitor.tasks.keys():
            return None

        tasks = TaskMonitor.tasks[username]
        for t in tasks:
            task_id = t['task_id']
            if tid == task_id:
                result = AsyncResult(id=task_id, app=cel)
                # success = result.successful()
                t['state'] = result.state
                print('TASK ID: %s    state: %s' % (tid, t['state']))

                if t['state'] == 'SUCCESS':
                    t['model_path'] = result.get()['model_path']
                elif t['state'] == 'FAILURE':
                    t['err_msg'] = str(result.result)
                return t
        return None


@before_task_publish.connect
def task_send_handler(sender=None, headers=None, body=None, **kwargs):
    info = headers if 'task' in headers else body
    params = body[0][0]
    username = params['username']
    date = params['date']
    output_format = params['output_format']
    output_name = params['output_name']
    task_id = info['id']
    TaskMonitor.append(username, task_id, date, output_format, output_name)