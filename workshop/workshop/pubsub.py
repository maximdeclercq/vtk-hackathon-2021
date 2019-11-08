import json
import time
from google.cloud import pubsub_v1

GCLOUD_PROJECT_ID = 'erudite-river-707'
PUBSUB_TOPIC_NAME = 'test_mathieu_workshop'

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GCLOUD_PROJECT_ID, PUBSUB_TOPIC_NAME)

futures = dict()


def send_message(message: dict):
    message_as_string = json.dumps(message)
    message_as_bytes = message_as_string.encode('utf-8')

    future = publisher.publish(topic_path, data=message_as_bytes)

    _ = future.result()
