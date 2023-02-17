import sys
from config import config
from rabbitmq_client import RabbitMQClient
from mylogging import logging
from datetime import datetime

rabbitmq_broker_ip = config.parser.get('RabbitMQ', 'broker_ip')
rabbitmq_broker_port = config.parser.get('RabbitMQ', 'broker_port')
rabbitmq_backup_size = config.parser.get('RabbitMQ', 'backup_size')
rabbitmq_backup_size = float(rabbitmq_backup_size)
rabbitmq_producer_exchange = config.parser.get('RabbitMQ', 'producer_exchange')

rabbitmq_producer = RabbitMQClient(rabbitmq_broker_ip, rabbitmq_broker_port, rabbitmq_backup_size)

def rabbitmq_producer_run():
    # produce
    logging.info('RabbitMQ producer connection starts...')
    start = datetime.now()
    rabbitmq_producer.connect('telegraf_producer', is_consumer=False)
    rabbitmq_producer.setup(rabbitmq_producer_exchange)
    end = datetime.now()
    logging.info('RabbitMQ producer connection takes %ss' % (end - start).total_seconds())


rabbitmq_producer_run()

for line in sys.stdin:
    rabbitmq_producer.publish(line)
