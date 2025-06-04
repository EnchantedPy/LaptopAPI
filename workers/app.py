from celery import Celery
from config.settings import Settings


app = Celery(name='worker', broker=Settings.rmq_url)