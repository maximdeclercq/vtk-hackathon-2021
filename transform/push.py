import os
from google.cloud import pubsub_v1
import json

publisher = pubsub_v1.PublisherClient()
topic_name = 'projects/erudite-river-707/topics/test_mathieu_workshop'

# publisher.create_topic(topic_name)


if __name__ == "__main__":
    for x in range(100):
        msg = {"content": {'name': 'Blabla', 'rate': x}}
        msg_bytes = json.dumps(msg)
        publisher.publish(topic_name, msg_bytes.encode('utf-8'))