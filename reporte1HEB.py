#reporte 1 HEB

from azure.cosmos import CosmosClient, PartitionKey, exceptions
import json
import os
from timeit import timeit 


url = 'https://cosmos-arpiheb-dev.documents.azure.com:443/' #os.environ['ACCOUNT_URI']
key = 'xzvXRlcvgHViT47OJQEq2ylbwePcjf6ALJQRCYEg43yOFrnoPvIXwR4LKXZmTrZxGgiOJ4YenSPIGy4wRmgvhg=='
client = CosmosClient(url, credential=key)

database_name = 'arpi'#"testDatabase"
container_name = 'telemetry'#"testDatabase"

database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

Time = []
Fruit  = []
Percent  = []
# Enumerate the returned items

for item in container.query_items(query='SELECT t.EventProcessedUtcTime FROM telemetry t',
    enable_cross_partition_query=True):
    
    Time.append(json.dumps(item, indent=True))

for item in container.query_items(query='SELECT t.fruit1 FROM telemetry t',
    enable_cross_partition_query=True):
    
    Fruit.append(json.dumps(item, indent=True))

for item in container.query_items(query='SELECT t.percent1 FROM telemetry t',
    enable_cross_partition_query=True):
    
    Percent.append(json.dumps(item, indent=True))

for item in Time:

    if "EventProcessedUtcTime" in item:
        item.remove("EventProcessedUtcTime")
        print(item)

#print(Time)