from gevent.queue import Queue
import json
import threading

CLOSE_STREAM = "SPECIAL_SIGNAL_STOP"


class Channel:
    def __init__(self, name):
        self.name = name
        self.subscribers = []

    def publish(self, message, event_type='default'):
        formatted_data = Channel.formart_message(message, event_type)
        for subscriber in self.subscribers[:]:
            subscriber.queue.put_nowait(formatted_data)

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)

    def close(self):
        [(subscriber.disconnect(), self.unsubscribe(subscriber))
         for subscriber in self.subscribers[:]]

    @staticmethod
    def formart_message(data, event_type):
        """Pack data in SSE format"""
        json_data = json.dumps(data)
        buffer = ''
        buffer += '%s: %s\n' % ('data', json_data)
        buffer += '%s: %s\n' % ('event', event_type)
        return buffer + '\n'


class Subscriber:
    def __init__(self):
        self.queue = Queue()

    def disconnect(self):
        self.queue.put(CLOSE_STREAM)


class Sse():
    def __init__(self):
        self.channels = {'default': Channel('default')}
        self.lock = threading.Lock()

    def add_subscriber(self, channel_name):
        with self.lock:
            new_user = Subscriber()
            self.channels[channel_name].subscribe(new_user)
            return new_user

    def add_channel(self, channel_name):
        with self.lock:
            channel = Channel(channel_name)
            self.channel[channel.name] = channel

    def get_channel(self, channel_name=None):
        with self.lock:
            if channel_name:
                return self.channels[channel_name]
            return self.channels

    def stream(self, subscriber):
        while True:
            data = subscriber.queue.get()
            if data is CLOSE_STREAM:
                return
            yield data


sse = Sse()
print("Loading...........")
