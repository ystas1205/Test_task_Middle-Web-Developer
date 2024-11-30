from celery.worker.control import conf

broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
conf.broker_connection_retry_on_startup = True