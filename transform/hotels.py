import json
import os
from functools import partial
import arrow

from google.cloud import bigquery, pubsub_v1

project_name = 'oi-hackaton-vtk2019'
subscriber = pubsub_v1.SubscriberClient()
topic_name = 'projects/oi-hackaton-vtk2019/topics/hotels'
subscription_name = 'projects/oi-hackaton-vtk2019/subscriptions/hotels'
# subscriber.create_subscription(name=subscription_name, topic=topic_name)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

bigquery_client = bigquery.Client(project=project_name)

def bq_get_or_create_dataset():
    dataset_ref = bigquery_client.dataset('workshop')

    try:
        dataset = bigquery_client.get_dataset(dataset_ref)
    except Exception as e:
        # print("Error:", e)
        # exit(1)
        dataset = bigquery.Dataset(dataset_ref)
        dataset = bigquery_client.create_dataset(dataset)
        print('Dataset {} created.'.format(dataset.dataset_id))
    
    return dataset_ref


def bq_get_or_create_hotels_table(dataset_ref):
    table_ref = dataset_ref.table('hotels')

    try:
        table = bigquery_client.get_table(table_ref)
    except Exception as e:
        # print("Error:", e)
        # exit(1)
        schema = [
            bigquery.SchemaField('hotel_id', 'INTEGER', mode='REQUIRED'),
            bigquery.SchemaField('hotel_name', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('dt_inserted', 'DATETIME', mode='REQUIRED'),
            bigquery.SchemaField('room_count', 'INTEGER', mode='NULLABLE'),
            bigquery.SchemaField('destination', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('currency', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('stars', 'INTEGER', mode='NULLABLE'),

            bigquery.SchemaField('address', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('latitude', 'FLOAT', mode='REQUIRED'),
            bigquery.SchemaField('longitude', 'FLOAT', mode='REQUIRED'),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        table = bigquery_client.create_table(table)
        print('Table {} created.'.format(table.table_id))
    return table

count = 0

def callback(bq_table, message):
    global count
    msg = json.loads(message.data)

    bq_row = (
        msg['hotel_id'],
        msg['hotel_name'],
        arrow.utcnow().datetime,
        msg['num_rooms'],
        msg['destination'],
        msg['currency'],
        msg['stars'],

        msg.get('address'),
        msg.get('latitude', 0),
        msg.get('longitude', 0),
    )

    print(bq_row)

    rows_to_insert = [
        bq_row,
    ]

    # errors = []
    errors = bigquery_client.insert_rows(bq_table, rows_to_insert)  # API request
    if errors:
        print(f'BQ insert error on msg {msg}: {errors}')
        exit(1)

    # print(f'processed msg {message.message_id}')

    count += 1
    if count % 100 == 0:
        print(f'Processed {count} messages')

    message.ack()


dataset = bq_get_or_create_dataset()
table = bq_get_or_create_hotels_table(dataset)
cb = partial(callback, table)

future = subscriber.subscribe(subscription_name, cb)

# if __name__ == "__main__":
#     try:
#         future.result()
#     except KeyboardInterrupt:
#         future.cancel()

if __name__ == "__main__":
    with open('/Users/mhindery/Downloads/sqlite-tools-osx-x86-3300100/all_hotels.json') as json_file:
        hotels = json.load(json_file)

    rows_to_insert = []
    for hotel in hotels:
        bq_row = (
            hotel['their_hotel_id'],
            hotel['name'],
            arrow.utcnow().datetime,
            hotel['room_count'],
            hotel['destination_id'],
            hotel['latitude'],
            hotel['stars'],
            
            hotel['address'],
            hotel['latitude'],
            hotel['longitude'],
            )
        rows_to_insert.append(bq_row)

    # errors = []
    for batch_num, batch_of_rows in enumerate(chunks(rows_to_insert, 1000)):
        errors = bigquery_client.insert_rows(table, batch_of_rows)  # API request
        if errors:
            print("Error: {}".format(errors))
            exit(1)
        print("Loaded batch {}".format(batch_num))
    
    print("Hotels loaded to BQ")
