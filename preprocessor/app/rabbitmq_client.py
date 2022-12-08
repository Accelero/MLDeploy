import pika
import time
from mylogging import logging
import pandas as pd
from line_protocol_parser import parse_line

class RabbitMQClient():
    def __init__(self, broker_ip, broker_port, key='value'):
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.key = key
        logging.getLogger("pika").propagate = False
        self.connected = False
        self.body = None
        self.buffer = None
        self.buffer_full = False

    def connect(self, is_consumer=False):
        self.is_consumer = is_consumer
        params = pika.ConnectionParameters(self.broker_ip, self.broker_port)
        while not self.connected:
            try:
                self.connection = pika.BlockingConnection(params) # Connect to broker
                logging.info("RabbitMQ %s connected to RabbitMQ broker!" % ('consumer' if self.is_consumer else 'producer'))
                self.connected = True
                logging.getLogger("pika").setLevel(logging.WARNING)
            except: 
                time.sleep(0.1)

    def setup(self, exchange):
        self.exchange = exchange
        self.channel = self.connection.channel() # start a channel
        self.channel.exchange_declare(exchange=self.exchange, exchange_type='fanout')
        logging.info("RabbitMQ %s channel set up and exchange %s declared!" % ('consumer' if self.is_consumer else 'producer', self.exchange))
        if self.is_consumer:
            self.result = self.channel.queue_declare(queue='', exclusive=True)
            self.queue_name = self.result.method.queue
            self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name)
            logging.info("RabbitMQ %s queue binded to exchange %s!" % ('consumer' if self.is_consumer else 'producer', self.exchange))

    def publish(self, body):
        self.channel.basic_publish(
            exchange=self.exchange, 
            routing_key='',
            body=body)
        logging.debug("RabbitMQ %s published message to exchange %s!" % ('consumer' if self.is_consumer else 'producer', self.exchange))

    def subscribe(self, window_width=None, frequency=None, data_format=None):
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.__callback,
            auto_ack=True)
        logging.info("RabbitMQ %s subscribed to exchange %s!" % ('consumer' if self.is_consumer else 'producer', self.exchange))
        self.window_width = window_width
        self.frequency = frequency
        self.data_format = data_format
    
    def consume(self):
        self.channel.start_consuming()

    def disconnect(self):
        self.connection.close()
        self.connected = False
        logging.info("RabbitMQ %s disconnected!" % ('consumer' if self.is_consumer else 'producer'))

    def influx2df(self, body):
        body = [parse_line(b) for b in body.decode('utf-8').strip().split('\n')]
        body = pd.DataFrame(body)
        body['time'] = pd.to_datetime(body['time'], utc=True)
        body['value'] = body['fields'].apply(lambda x: x[self.key])
        body = body[['value', 'time']]
        return body

    def concat_buffer(self, body):
        self.buffer = pd.concat([self.buffer, body], ignore_index=True)
        self.buffer = self.buffer.sort_values(by='time')
        self.stop = self.buffer['time'].iloc[-1]
        self.start = self.stop - pd.to_timedelta(self.window_width)
        self.buffer = self.buffer.loc[self.buffer['time'] >= self.start]
        if self.buffer['time'].iloc[0] - self.start <= pd.to_timedelta(self.frequency):
            self.buffer_full = True

    def __callback(self, ch, method, properties, body):
        if not body == '':
            self.body = body
            if self.data_format == 'influx':
                self.body = self.influx2df(self.body)
            if not self.window_width is None or not self.frequency is None:
                if self.buffer is None:
                    self.buffer = self.body
                else:
                    self.concat_buffer(self.body)
        
    def get_buffer(self):
        buffer = self.buffer.copy()
        buffer['start'] = self.start
        buffer['stop'] = self.stop
        buffer.rename(
            columns={'time': '_time', self.key: '_' + self.key,'start': '_start', 'stop': '_stop'}, 
            inplace=True)
        return buffer



