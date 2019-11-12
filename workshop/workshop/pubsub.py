import json
import time
from google.cloud import pubsub_v1

GCLOUD_PROJECT_ID = 'oi-hackaton-vtk2019'
HOTELS_PUBSUB_TOPIC_NAME = 'hotels'
RATES_PUBSUB_TOPIC_NAME = 'rates'

publisher = pubsub_v1.PublisherClient()
hotels_topic_path = publisher.topic_path(GCLOUD_PROJECT_ID, HOTELS_PUBSUB_TOPIC_NAME)
rates_topic_path = publisher.topic_path(GCLOUD_PROJECT_ID, RATES_PUBSUB_TOPIC_NAME)

futures = dict()


def send_hotels_message(message: dict):
    message_as_string = json.dumps(message)
    message_as_bytes = message_as_string.encode('utf-8')

    future = publisher.publish(hotels_topic_path, data=message_as_bytes)

    _ = future.result()


def send_rates_message(message: dict):
    message_as_string = json.dumps(message)
    message_as_bytes = message_as_string.encode('utf-8')

    future = publisher.publish(rates_topic_path, data=message_as_bytes)

    _ = future.result()
