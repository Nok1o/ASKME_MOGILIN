import multiprocessing
import os

bind = os.getenv('GUNICORN_BIND', '127.0.0.1:8000')
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
timeout = int(os.getenv('GUNICORN_TIMEOUT', '30'))

accesslog = '-'
errorlog = '-'
wsgi_app = 'askme_mogilin.wsgi:application'
