# Transport for London with Kafka

## Streaming Patterns

Several patterns are common in streaming. In increasing order of maturity these are:
1. Event Sink. Your business is already using streams. These can be ingested straight into your data warehouse to complement existing batch workloads, e.g. Marketing
2. Replication. Replicate data from one place to another. Useful for serving data as a product or creating more fault-tolerant systems.
3. Replication. Your business needs real time analytics for immediate decision making, e.g. Supply Chain & Logistics
3. Microservices. Your business needs to operate in real time and has different services that need to talk to each other, e.g. Fraud Detection

The objective of this project is to demonstrate some of these patterns in Kafka

## Case Study

Transport for London needs to be able to ingest IoT and operational data for use in real time dashboards and for offline analysis. 

The solution architecture is shown below.

![Architecture Diagram](TfL.png?raw=True)

## Set Up

### Step 1 - Download connectors
Download, unzip and save under connect-plugins/

- https://www.confluent.io/hub/confluentinc/kafka-connect-jdbc
- https://www.confluent.io/hub/confluentinc/kafka-connect-elasticsearch

Save under `connect-plugins/kafka-connect-jdbc-10.7.4/jars`
- https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.3.0/mysql-connector-j-8.3.0.jar

### Step 2 - Start containers

```
docker compose up --build
```
In addition to setting up the Confluent environemnt for Kafka, a mariadb will be spun with dummy stations and users loaded.


### Step 3 - Stream from MariaDB

Kafka Connect looks for drivers under CONNECT_PLUGIN_PATH

Stream from mariadb to Kafka

```
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
        "name": "jdbc_source_mariadb_01",
        "config": {
                "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
                "connection.url": "jdbc:mysql://mariadb:3306/tfl",
                "connection.user": "root",
                "connection.password": "root123",
                "topic.prefix": "",
                "catalog.pattern": "tfl",
                "numeric.mapping": "best_fit",
                "mode":"timestamp",
                "timestamp.column.name": "modified_date",
                "transforms":"copyFieldToKey,extractKeyFromStruct",
                "transforms.copyFieldToKey.type":"org.apache.kafka.connect.transforms.ValueToKey",
                "transforms.copyFieldToKey.fields":"name",
                "transforms.extractKeyFromStruct.type":"org.apache.kafka.connect.transforms.ExtractField$Key",
                "transforms.extractKeyFromStruct.field":"name"
                }
        }' | json_pp
```

List connectors
```
curl localhost:8083/connectors
```
Check a service is healthy
```
curl -s localhost:8083/connectors/jdbc_source_mariadb_01/status | json_pp
```

### Step 4 - Set up the Python environment

```
python3 -m venv .env
. .env/bin/activate
pip install -r requirements.txt
```

### Step 5 - Produce events

```
python produce_iot_to_kafka.py
```

### Step 6 - Process streams using ksql

Open the ksqldb-cli 

```
docker compose exec -it ksqldb-cli ksql http://ksqldb-server:8088
```

Join stations with entries and exits

```
set 'auto.offset.reset' = 'earliest';
drop stream if exists `station_entries`;
drop stream if exists `station_exits`;
drop stream if exists entries;
drop stream if exists exits;
drop table if exists stations_tb;
create table stations_tb (
    key STRING PRIMARY KEY,
    `name` STRING,
    `location` STRING
    ) 
WITH ( 
    kafka_topic = 'stations',
    key_format = 'KAFKA',  
    value_format = 'AVRO')
    ;
create stream entries (
    key STRING KEY, 
    `user` STRING,
    `delta` INT
) WITH ( 
    kafka_topic = 'entries',  
    value_format = 'JSON'
);
create stream exits (
    key STRING KEY, 
    `user` STRING, 
    `delta` INT
)  WITH ( 
    kafka_topic = 'exits', 
    value_format = 'JSON');
create stream `station_entries` as 
    select 
        e.key, 
        format_timestamp(from_unixtime(e.rowtime), 'yyyy-MM-dd''T''HH:mm:ss.SSSX', 'UTC') as "@timestamp", 
        e."user", 
        e."delta", 
        s."name" as "station", 
        s."location" 
    from entries e 
    join stations_tb s on e.key = s.key 
    emit changes; 
create stream `station_exits` as 
    select 
        e.key, 
        format_timestamp(from_unixtime(e.rowtime), 'yyyy-MM-dd''T''HH:mm:ss.SSSX', 'UTC') as "@timestamp", 
        e."user", 
        e."delta", 
        s."name" as "station", 
        s."location" 
    from exits e 
    join stations_tb s on e.key = s.key 
    emit changes; 
```

### Step 7 - Define index patterns for Elasticsearch

Open the elasticsearch CLI at http://localhost:5601/app/dev_tools#/console.

Defines mappings

```
PUT _component_template/barrier_mappings
{
  "template": {
    "mappings": {
      "properties": {
        "user": {
          "type": "keyword",
          "time_series_dimension": true
        },
        "station": {
          "type": "keyword",
          "time_series_dimension": true
        },
        "delta": {
          "type": "byte",
          "time_series_metric": "gauge"
        },
        "@timestamp": {
          "type": "date"},
        "location": {
          "type": "geo_point"}
      }
    }
  },
  "_meta": {
    "description": "Mappings for entry data"
  }
}
```

Define pattern matching and set mode to time-series
```
PUT _index_template/barrier_template
{
  "index_patterns": ["station_entries","station_exits"],
  "data_stream": { },
  "template": {
    "settings": {
      "index.mode": "time_series",
      "index.routing_path": [ "station", "user" ]
    }
  },
  "composed_of": [ "barrier_mappings"],
  "priority": 500,
  "_meta": {
    "description": "Template for entries data"
  }
}
```

### Step 8 - Consume into Elasticsearch

Kafka Connect does have plugins for Elasticsearch but Python is a lot easier.

```
python consume_kafka_to_elasticsearch.py
```

### Step 9 - Create Kibana dasbhoard

Set up data views to match station_entries and station_exits. Elastic search prefers denormalised streams.

![Kibana Dasbhoard](Kibana.png?raw=true)

## To Do

1. Set up Kafka Schema Registry
2. Stream into PostreSQL