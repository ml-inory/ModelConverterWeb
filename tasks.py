from os import stat
from celery import Celery
from converter import Converter
from celery.signals import after_task_publish, before_task_publish
from celery.result import AsyncResult

cel = Celery(
        'tasks',
        backend='redis://localhost:9394/0',
        broker='redis://localhost:9394/1'
    )

@cel.task
def convert_model(params):
    return Converter.convert(params)

class TaskMonitor:
    tasks = {}

    def __init__(self):
        pass

    @staticmethod
    def append(username, task_id, date, output_format, output_name):
        if username not in TaskMonitor.tasks.keys():
            TaskMonitor.tasks[username] = []
        
        TaskMonitor.tasks[username].append(dict(task_id=task_id, date=date, output_format=output_format, output_name=output_name, success=False, model_path=''))

    # 返回所有任务
    @staticmethod
    def query(username):
        if username not in TaskMonitor.tasks.keys():
            return []

        tasks = TaskMonitor.tasks[username]
        for t in tasks:
            task_id = t['task_id']
            result = AsyncResult(id=task_id, app=cel)
            success = result.successful()
            t['success'] = success
            if success:
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
                success = result.successful()
                t['success'] = success
                if success:
                    t['model_path'] = result.get()['model_path']
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