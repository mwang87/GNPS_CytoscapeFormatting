from celery import Celery

print("Before Celery App")
celery_instance = Celery('cytoscape_tasks', backend='redis://redis', broker='redis://redis')

@celery_instance.task
def test_celery(input_value):
    return input_value + 10