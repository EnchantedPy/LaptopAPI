from celery import Celery
from config.settings import SAppSettings


app = Celery(name='worker', broker=SAppSettings.rmq_url) # in docker localhost ch to rabbitmq (container name)