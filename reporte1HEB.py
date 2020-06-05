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
#print(Time) example 
#'{\n "EventProcessedUtcTime": "2020-04-24T23:40:02.3479481Z"\n}', 
Time = [x.replace('{\n "EventProcessedUtcTime": "', '').replace('Z"\n}','')  for x in Time]

# Gives all the entrance's year, month, day on which they were obtained
years = [x.split('-')[0] for x in Time] 
months = [x.split('-')[1] for x in Time] 
Nformat = [x.split('-')[2] for x in Time] 
Nformat2 = [x.split('T')[0] for x in Time] # yy-mm-dd format

days = [x.split('T')[0] for x in Nformat]

times = [x.split('T')[1] for x in Time] 
#print(Nformat2)

times = [x[:8]for x in times ]# no decimal format for the seconds

# List of the different years, months (removes all repeating entries)
"""
different_years = list(dict.fromkeys(years))
different_months = list(dict.fromkeys(months))
different_days = list(dict.fromkeys(days))
different_times = list(dict.fromkeys(times))
"""
#print(different_days)


Dates = []

def example1():
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
    
def printList():
    #print(Dates)

   
    CreateReport(Dates)
    root.destroy()



def CreateReport(Dates):
    Diff = Dates[1] - Dates[0]
    Diff = [Dates[0]+timedelta(days=i) for i in range(Diff.days+1)]
    #print(Diff)

    def daterange(date1, date2):
        for n in range(int ((date2 - date1).days)+1):
            yield date1 + timedelta(n)
    i = 0
    #print(Nformat2)
    #allDates = [str(x) for x in Nformat2]
    
    #rangeDates = [str(Dates[0] + timedelta(days=i)) for i in range((Dates[1]-Dates[0]).days + 1)]

    rangeDates = [str(Dates[0] + timedelta(days=i)) for i in range((Dates[1]-Dates[0]).days + 1)]

    whut = []
    for i in rangeDates:
        for item in container.query_items(query='SELECT t.EventProcessedUtcTime FROM telemetry t WHERE CONTAINS(t.EventProcessedUtcTime, "{}")'.format(i),
            enable_cross_partition_query=True):
            print(json.dumps(item, indent=True))
            whut.append(json.dumps(item, indent=True))
    #print(whut)
    #print(Nformat3)
    #print(allDates)
    print()
    #print(rangeDates)
    print()
    #for i in allDates:
        #for j in rangeDates:
            #print(i, j)

           

    Time = [x.replace('{\n "EventProcessedUtcTime": "', '').replace('Z"\n}','')  for x in whut]

    Nformat2 = [x.split('T')[0] for x in Time]
    different_days = list(dict.fromkeys(Nformat2))
    print(different_days)

    #count1 =

    #different_days = [None,None, None]+different_days

    fig = plt.figure()
    fig.subplots_adjust(hspace=0.4, wspace=0.4)
    fig.suptitle("Utlización del Nodo",fontsize=16)
    for i in range(1, 4):
        ax = fig.add_subplot(3, 1, i)

        ax.set_xticklabels(different_days,fontdict={'horizontalalignment': 'center'})
        ax.plot()
        #ax.text(0.5, 0.5, str((3, 1, i)),
        #    fontsize=18, ha='center')
    plt.show()

root = tk.Tk()
s = ttk.Style(root)
s.theme_use('clam') # clam, alt, default, classic
ttk.Label(root, text='Generador de reportes').pack(padx=10, pady=30)
ttk.Button(root, text='Fecha de inicio', command=example1).pack(padx=10, pady=10)
ttk.Button(root, text='Fecha de fin', command=example1).pack(padx=10, pady=5)
ttk.Button(root, text='Terminar', command=printList).pack(padx=5, pady=25)



root.mainloop()
