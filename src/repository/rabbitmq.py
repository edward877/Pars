import pika


class RabbitMq(object):
    def __init__(self, host: str, port: int, user: str,
                 password: str, virtual_host: str, encoding: str):
        self.credentials = pika.PlainCredentials(user, password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host, port, virtual_host, self.credentials, heartbeat_interval=0))
        self.channel = self.connection.channel()
        self.encoding = encoding

    def declare_queue(self, queue_name: str, dl_queue_name=None):
        if dl_queue_name is None:
            return self.channel.queue_declare(queue_name, durable=True)
        return self.channel.queue_declare(queue_name, durable=True, arguments={
            "x-dead-letter-exchange": '',
            "x-dead-letter-routing-key": dl_queue_name
        })

    def publish_data(self, body: str, queue_name: str):
        if type(body) is not bytes:
            body = body.encode(self.encoding)
        self.channel.basic_publish(exchange='',
                                   routing_key=queue_name,
                                   body=body,
                                   properties=pika.BasicProperties(content_encoding=self.encoding, delivery_mode=2))