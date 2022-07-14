import stomp
import time
import falcon

from app.log import LOG

app = falcon.API()

conn = stomp.Connection10()

# todo use this listener to listen to any new message on queue and trigger provider service from here
class SampleListener(object):
    def on_error(self, headers, msg):
        LOG.info("received an error ", msg)

    def on_message(self, headers, msg):
        app.add_route('/messages',msg)
        LOG.info("received a message ", msg)


conn.set_listener('SampleListener', SampleListener())
conn.connect()
conn.subscribe(destination='/queue/SampleTopic', id=1, ack='auto')

while True:
    time.sleep(0.2)
