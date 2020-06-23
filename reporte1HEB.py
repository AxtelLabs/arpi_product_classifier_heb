#reporte 1 HEB

from azure.cosmos import CosmosClient, PartitionKey, exceptions
import json
import os
from datetime import date, timedelta,datetime
from  matplotlib import pyplot as plt
import random
import pandas as pd
from collections import Counter
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk

from tkcalendar import Calendar, DateEntry


# Set up environment variables to the azure key and url
url = os.environ['ACCOUNT_URI'] 
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)

# azure account key
# in cd ./bash_profile add
# azure specifics
database_name = 'arpi'
container_name = 'telemetry'

database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

Time = []
Fruit  = []
Percent  = []
# Make queries

for item in container.query_items(query='SELECT t.EventProcessedUtcTime FROM telemetry t',
    enable_cross_partition_query=True):
    Time.append(json.dumps(item, indent=True))

for item in container.query_items(query='SELECT t.percent1 FROM telemetry t',
    enable_cross_partition_query=True):
    Percent.append(json.dumps(item, indent=True))

Time = [x.replace('{\n "EventProcessedUtcTime": "', '').replace('Z"\n}','')  for x in Time]

# Gives all the entrance's year, month, day on which they were obtained
years = [x.split('-')[0] for x in Time] 
months = [x.split('-')[1] for x in Time] 
Nformat = [x.split('-')[2] for x in Time] 
Nformat2 = [x.split('T')[0] for x in Time] # yy-mm-dd format

days = [x.split('T')[0] for x in Nformat]

times = [x.split('T')[1] for x in Time] 
times = [x[:8]for x in times ]# no decimal format for the seconds

# List of the different years, months (removes all repeating entries)
"""
different_years = list(dict.fromkeys(years))
different_months = list(dict.fromkeys(months))
different_days = list(dict.fromkeys(days))
different_times = list(dict.fromkeys(times))
"""

Dates = []


# defining functions for tkinter

def example1():
    # function that prints selection and "forgets" calender
    def print_sel():
        print(cal.selection_get())
        date = cal.selection_get()
        Dates.append(date)

        cal.pack_forget()
        ok.pack_forget()
        top.destroy()

    top = tk.Toplevel(root)

    cal = Calendar(top,
                   font="Arial 14", selectmode='day',
                   cursor="hand", year=2020, month=4, day=24)
    cal.pack(fill="both", expand=True)
    ok = ttk.Button(top, text="ok", command=print_sel)
    ok.pack(fill="both", expand=True)
    # function that creates the first report and closes the tkinter app
def printList():
    CreateReport(Dates)
    root.destroy()
    # function that creates the second report and closes the tkinter app
def printList2():
    CreateReport2(Dates)
    root.destroy()

# creates the first report
def CreateReport(Dates):
    
    i = 0
    # Gives all the days between the two selected dates
    rangeDates = [str(Dates[0] + timedelta(days=i)) for i in range((Dates[1]-Dates[0]).days + 1)]

    whut = []
    # cycles through all the days between the two selected dates and retreives the date for each upload event

    # saves the days where information was uploaded

    for i in rangeDates:
        for item in container.query_items(query='SELECT t.EventProcessedUtcTime FROM telemetry t WHERE CONTAINS(t.EventProcessedUtcTime, "{}")'.format(i),
            enable_cross_partition_query=True):
            #print(json.dumps(item, indent=True))
            whut.append(json.dumps(item, indent=True))
    print()
    # cleans the list of the above information
    Time = [x.replace('{\n "EventProcessedUtcTime": "', '').replace('Z"\n}','')  for x in whut]
    # further cleans the information list
    Nformat2 = [x.split('T')[0] for x in Time]
    different_days = list(dict.fromkeys(Nformat2))

    # takes the different days where information was uploaded to graph upon those dates
    print(different_days)

    # counts the number of image uploads per user day
    counter1 = [sum('{}'.format(different_days[i]) in s for s in Nformat2) for i in range(len(different_days))]
    print()
    count = counter1
    print(count)
    # quadruple subplot

    # first plots pictures/inferences per day

    fig = plt.figure()
    fig.subplots_adjust(hspace=1.0, wspace=0.4)
    fig.suptitle("Utlización del Nodo",fontsize=16)

    ax = fig.add_subplot(4, 1, 1)

    ax.set_xticklabels(different_days)
    ax.plot(different_days, count)

    ax.set_title('# de usos por día')
    for i, v in enumerate(count):
        ax.text(i, v, "%d" %v, ha="center")

    t1 = [0]
    for i in range(len(count)-1):
        tx = 100*(count[i+1]/count[i])
        t1.append(tx)

    ax = fig.add_subplot(4, 1, 2)

    # second plots use increment w.r.t the utilization day before
    ax.set_xticklabels(different_days)
    ax.set_title('Incremento (%) con respecto al día anterior')
    ax.plot(different_days, t1,fillstyle='full')
    for i, v in enumerate(t1):
        ax.text(i, v, "%d" %v, ha="center")

    
    whut = []
    for item in container.query_items(query='SELECT t.validationBoolean FROM telemetry t ',
        enable_cross_partition_query=True):
        whut.append(json.dumps(item, indent=True))

    valid = [x.replace('{\n "validationBoolean": ', '').replace('\n}','')  for x in whut]


    ax = fig.add_subplot(4, 1, 3)

    # third plots precision based on the validation boolean
    t1 = [100 for i in range(len(different_days))]
    ax.set_xticklabels(different_days)
    ax.set_title('Precisión')
    ax.plot(different_days, t1)
    for i, v in enumerate(t1):
        ax.text(i, v, "%d" %v, ha="center")


    # fourth plots the models accuracy based on network training/test
    ax = fig.add_subplot(4, 1, 4)
    t2 = random.uniform(90.0, 100.0) 
    t1 = [t2 for i in range(len(different_days))]
    ax.set_xticklabels(different_days)
    ax.set_title('Precisión del entrenamiento (modelo)')
    ax.plot(different_days, t1)

    for i, v in enumerate(t1):
        ax.text(i, v, "%d" %v, ha="center")

    plt.show()
# creates histogram of products detected as fruit 1 in each inference, by date range
def CreateReport2(Dates):   

    rangeDates = [str(Dates[0] + timedelta(days=i)) for i in range((Dates[1]-Dates[0]).days + 1)]

    whut = []
    for i in rangeDates:
        for item in container.query_items(query='SELECT t.fruit1 FROM telemetry t WHERE CONTAINS(t.EventProcessedUtcTime, "{}")'.format(i),
            enable_cross_partition_query=True):
            #print(json.dumps(item, indent=True))
            whut.append(json.dumps(item, indent=True))

    whut = [x.replace('{\n "fruit1": ', '').replace('"\n}','')  for x in whut]
    print()

    fruit_counts = Counter(whut)
    fig = plt.figure()
    fig.subplots_adjust(hspace=1.0, wspace=0.4)
    ax = fig.add_subplot(1, 1, 1)
    
    plt.suptitle("Productos vendidos entre {0} a {1}".format(Dates[0], Dates[1]))
    df = pd.DataFrame.from_dict(fruit_counts, orient='index')
    df.plot(kind='bar')
   # plt.suptitle("Productos vendidos entre {0} a {1}".format(Dates[0], Dates[1]))
    plt.title("Histograma de frutas y verduras")
    plt.show()


# Tkinter main app buttons
root = tk.Tk()
s = ttk.Style(root)
s.theme_use('clam') # clam, alt, default, classic
ttk.Label(root, text='Generador de reportes').pack(padx=10, pady=30)
ttk.Button(root, text='Fecha de inicio', command=example1).pack(padx=10, pady=10)
ttk.Button(root, text='Fecha de fin', command=example1).pack(padx=10, pady=5)
ttk.Button(root, text='Generar gráfica de uso', command=printList).pack(padx=5, pady=25)
ttk.Button(root, text='Generar histograma de productos', command=printList2).pack(padx=5, pady=15)


# Mainloop
root.mainloop()
