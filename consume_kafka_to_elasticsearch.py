from confluent_kafka import Producer, Consumer, KafkaException, KafkaError 
import time
import json
import requests

def handle(message):
    print(json.dumps(message['msg']))
    try:
        r = requests.post(f'http://localhost:9200/{message["topic"]}/_doc', json = message['msg'])
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        raise



def read_topic(topics,groupid=None):

    if not groupid:
        groupid = str(int(time.time()))

    print(f'Consuming from group id {groupid}')
    conf = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'a',
            'enable.auto.commit': 'false',
            'auto.offset.reset': 'earliest'
        }
    MIN_COMMIT_COUNT = 10

    consumer = Consumer(conf)
    try:
        msg_count = 0
        consumer.subscribe(topics)
        print("Starting consumer loop")
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: 
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    print('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                message = dict(
                    topic = msg.topic(),
                    key = msg.key().decode('utf-8'),
                    msg = json.loads(msg.value())
                    )
                handle(message)
                msg_count += 1
                if msg_count % MIN_COMMIT_COUNT == 0:
                    consumer.commit(asynchronous=False)

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
        print('Exited gracefully')

if __name__ == '__main__':
    for i in read_topic(['station_entries','station_exits'],'CG1'):
        print(i)