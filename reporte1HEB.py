#reporte 1 HEB

from azure.cosmos import CosmosClient, PartitionKey, exceptions
import json
import os

url = 'https://cosmos-arpiheb-dev.documents.azure.com:443/' #os.environ['ACCOUNT_URI']
key = 'xzvXRlcvgHViT47OJQEq2ylbwePcjf6ALJQRCYEg43yOFrnoPvIXwR4LKXZmTrZxGgiOJ4YenSPIGy4wRmgvhg=='
client = CosmosClient(url, credential=key)

database_name = 'cosmos-arpiheb-dev'#"testDatabase"
container_name = 'arpi'#"testDatabase"

database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

# Enumerate the returned items
for item in container.query_items(query='SELECT * FROM c'):
    print(json.dumps(item, indent=True))