import json
import os
from functools import partial
import arrow

from google.cloud import bigquery, pubsub_v1

project_name = 'oi-hackaton-vtk2019'
subscriber = pubsub_v1.SubscriberClient()
topic_name = 'projects/oi-hackaton-vtk2019/topics/rates'
subscription_name = 'projects/oi-hackaton-vtk2019/subscriptions/rates'
# subscriber.create_subscription(name=subscription_name, topic=topic_name)

bigquery_client = bigquery.Client(project=project_name)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

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


def bq_get_or_create_rates_table(dataset_ref):
    table_ref = dataset_ref.table('rates')

    try:
        table = bigquery_client.get_table(table_ref)
    except Exception as e:
        # print("Error:", e)
        # exit(1)
        schema = [
            bigquery.SchemaField('hash', 'STRING', mode='REQUIRED'),
            bigquery.SchemaField('dt_inserted', 'DATETIME', mode='REQUIRED'),
            bigquery.SchemaField('arrival_date', 'DATE', mode='REQUIRED'),
            bigquery.SchemaField('departure_date', 'DATE', mode='REQUIRED'),
            bigquery.SchemaField('hotel_id', 'INTEGER', mode='REQUIRED'),
            bigquery.SchemaField('room_name', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('currency', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('amount', 'FLOAT64', mode='NULLABLE'),
            bigquery.SchemaField('breakfast_included', 'BOOL', mode='NULLABLE'),
            bigquery.SchemaField('refundable', 'BOOL', mode='NULLABLE'),
            bigquery.SchemaField('number_guests', 'INTEGER', mode='NULLABLE'),
            bigquery.SchemaField('destination', 'STRING', mode='REQUIRED'),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        table = bigquery_client.create_table(table)
        print('Table {} created.'.format(table.table_id))
    return table

count = 0

def callback(bg_table, message):
    global count
    msg = json.loads(message.data)

    try:
        bq_row = (
            '_'.join([str(msg['hotel_id']), arrow.get(msg['arrival_date']).format('YYYY-MM-DD'), arrow.get(msg['departure_date']).format('YYYY-MM-DD'), str(msg['number_guests'])]),
            arrow.utcnow().datetime,
            msg['arrival_date'],
            msg['departure_date'],
            msg['hotel_id'],
            msg['room_name'],
            msg['currency'],
            msg['amount'],
            msg['breakfast_included'],
            msg['refundable'],
            msg['number_guests'],
            msg['destination'],
        )
    except:
        print("Bad message: {}".format(msg))
        return
    
    print(bq_row)

    rows_to_insert = [
        bq_row,
    ]

    # errors = []
    errors = bigquery_client.insert_rows(bg_table, rows_to_insert)  # API request
    if errors:
        print(f'BQ insert error on msg {msg}: {errors}')
        exit(1)

    # print(f'processed msg {message.message_id}')

    count += 1
    if count % 100 == 0:
        print(f'Processed {count} messages')

    message.ack()


dataset = bq_get_or_create_dataset()
table = bq_get_or_create_rates_table(dataset)
cb = partial(callback, table)

future = subscriber.subscribe(subscription_name, cb)

# if __name__ == "__main__":
#     try:
#         future.result()
#     except KeyboardInterrupt:
#         future.cancel()

if __name__ == "__main__":
    with open('/Users/mhindery/Downloads/sqlite-tools-osx-x86-3300100/all_rates.json') as json_file:
        rates = json.load(json_file)

    rows_to_insert = []
    for rate in rates:
        bq_row = (
            '_'.join([
                rate['their_hotel_id'],
                rate['from_date_local'],
                rate['to_date_local'],
                str(rate['price_max_persons']),
            ]),
            arrow.utcnow().datetime,
            rate['from_date_local'],
            rate['to_date_local'],
            rate['their_hotel_id'],
            rate['room_name'],
            rate['price_currency'],
            rate['price_price_value'],
            rate['meal_type_include'] != 'NONE',
            rate['price_refundable'] == "True",
            rate['price_max_persons'],
            rate['destination_id'],
            )
        rows_to_insert.append(bq_row)

    print("Loaded Json of rates. Starting BQ insert...")

    # errors = []
    for batch_num, batch_of_rows in enumerate(chunks(rows_to_insert, 10000)):
        errors = bigquery_client.insert_rows(table, batch_of_rows)
        if errors:
            print("Error: {}".format(errors))
            exit(1)
        print("Loaded batch {}".format(batch_num))
    print("Loaded rates to BQ")