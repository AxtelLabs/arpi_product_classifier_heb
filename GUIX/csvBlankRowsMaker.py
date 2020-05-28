
import csv

with open("AbrilHEB.csv", 'r',encoding="latin-1") as input:
   readie=csv.reader(input, delimiter=',')
   with open("AbrilHEB_2.csv", 'wt', newline='',encoding="latin-1") as output:
       outwriter=csv.writer(output, delimiter=',')
       for row in readie:
           outwriter.writerow(row)
           outwriter.writerow([])