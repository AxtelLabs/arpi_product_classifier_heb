#reporte 1 HEB

from azure.cosmos import CosmosClient, PartitionKey, exceptions
import json
import os
from datetime import date, timedelta,datetime
from  matplotlib import pyplot as plt
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk

from tkcalendar import Calendar, DateEntry

url = 'https://cosmos-arpiheb-dev.documents.azure.com:443/' #os.environ['ACCOUNT_URI']
key = 'xzvXRlcvgHViT47OJQEq2ylbwePcjf6ALJQRCYEg43yOFrnoPvIXwR4LKXZmTrZxGgiOJ4YenSPIGy4wRmgvhg==' #os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)

database_name = 'arpi'#"testDatabase"
container_name = 'telemetry'#"testDatabase"

database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

Time = []
Fruit  = []
Percent  = []
# Enumerate the returned items

free = []
for item in container.query_items(query='SELECT t.EventProcessedUtcTime FROM telemetry t WHERE CONTAINS(t.EventProcessedUtcTime, "2020")',enable_cross_partition_query=True):
    A = json.dumps(item, indent=True)  
    print(A) 
    #free.append(A)

"""
container.query_items(query='DECLARE @json NVARCHAR(MAX)' ,
    enable_cross_partition_query=True)

container.query_items(query="SET @json='{}'".format(free) ,
    enable_cross_partition_query=True)

for item in container.query_items(query='SELECT * FROM OPENJSON(@json)',
    enable_cross_partition_query=True):
    print(json.dumps(item, indent=True))
"""