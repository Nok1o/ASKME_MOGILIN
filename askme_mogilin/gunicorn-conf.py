bind = '127.0.0.1:8000'
workers = 2

accesslog = '/var/tmp/askme.gunicorn.log'

wsgi_app = 'askme_mogilin.wsgi:application'