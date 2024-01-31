from confluent_kafka import Producer, Consumer, KafkaException, KafkaError 
import socket
import json
from flask import jsonify
import pandas as pd
import confluent_kafka.admin
from time import sleep
import random
from datetime import datetime

conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': socket.gethostname()
    }

kafka_admin = confluent_kafka.admin.AdminClient(conf)

def produce(msgs):

    if type(msgs) != list:
        msgs = [msgs]

    producer = Producer(conf)
    for msg in msgs:
        topic,key,value = msg['topic'],msg['key'],msg['value']

        producer.produce(topic, key=key, value=json.dumps(value))
        yield  str({'topic': topic, 'key': key, 'message': value})+'\n'
    producer.flush()

def get_utcnow():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def get_topics():
    return list(kafka_admin.list_topics().topics.keys())

def check_topic_was_removed(topic,attempt=1,retries=20):
    topics = get_topics()
    if topic not in topics:
        print(f'Topic {topic} successfully removed')
    else:
        if attempt==retries:
            print(f'Failed to remove {topic}')
            raise
        else:
            attempt+=1
            sleep(1)
            return check_topic_was_removed(topic,attempt=attempt,retries=retries)


def check_topic_was_added(topic,attempt=1,retries=10):
    topics = get_topics()
    if topic in topics:
        print(f'Topic {topic} successfully added')
    else:
        if attempt==retries:
            print(f'Failed to add {topic}')
        else:
            attempt+=1
            sleep(1)
            return check_topic_was_added(topic,attempt=attempt,retries=retries)

def create_topic(topic,partitions=1,replicas=1,recreate=True,compact=False):
    if recreate:
        kafka_admin.delete_topics([topic])
        check_topic_was_removed(topic)
    config = {}
    if compact:
        config['cleanup.policy']='compact'
    new_topic  = confluent_kafka.admin.NewTopic(topic=topic, num_partitions=partitions, replication_factor=replicas, config=config)
    result_dict = kafka_admin.create_topics([new_topic])
    for topic, future in result_dict.items():
        try:
            future.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))
    check_topic_was_added(topic)


def get_stations():
    stations_df = pd.read_csv('mariadb/data/input/stations.csv')
    stations_df = stations_df[stations_df['FareZones'].isin(['1'])]
    stations = stations_df['name'].to_list()
    return stations

def get_users(num=10):
    users_df = pd.read_csv('mariadb/data/input/users.csv')
    users_df = users_df.sample(num)
    users = users_df['name'].to_list()
    return users

def main():
    stations = get_stations()
    users = get_users(1000)
    network = []
    create_topic('entries')
    create_topic('exits')
    sleep(2)
    iter_period = 500
    t = 0
    while True:
        # add user to network
        if len(users)>0:
            iter_frac = t%iter_period/iter_period
            if random.random() < 1-iter_frac and random.random() < (1-len(network)/len(users)):
                user = random.choice(users)
                station = random.choice(stations)
                res = produce({
                    "topic": "entries",
                    "key": station,
                    "value": {"user": user, "station": station, "delta": 1, "@timestamp": get_utcnow()}
                })
                print(list(res)[0])
                users.remove(user)
                network.append(user)
                print(len(network))


        # remove user from network when it 
        if len(network)>0:
            if random.random() < iter_frac and random.random() < len(network)/len(users):
                user = random.choice(network)
                station = random.choice(stations)
                res = produce({
                    "topic": "exits",
                    "key": station,
                    "value": {"user": user, "station": station, "delta": -1, "@timestamp": get_utcnow()}
                })
                print(list(res)[0])
                network.remove(user)
                users.append(user)
                print(len(network))
        sleep(0.10)
        t+=1

if __name__ == '__main__':
    main()
        


        




