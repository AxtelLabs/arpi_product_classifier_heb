"""
list = ['\\pineapple 100.000%', '\\purpleonion 0.000%', '\\banana 0.000%']
list = [str.replace("\\", "") for str in list]
print(list)
"""
from translation import d, products
import platform
import os

def GetDict(F):
    # Define the type of dash to be used ("\" or "/") depending on OS. # <-- Final GUI change
    if platform.system() == "Windows":
        dash = "\\"
    else:
        dash = "/"
    # Establish main path for files # <-- Final GUI change
    path = dash.join(os.path.realpath(__file__).split(dash)[:-1]) + dash
        #myDict = {}
    newDict = {}
    keys = ["name", "PLU", "path"]
    newKey = [0,1,2]
    for i in range(len(F)):
        values = [str(d.get(F[i])), str(products.get(d.get(F[i]))) ,path + "imgs/"+F[i] +".png" ]

        myDict = dict(zip(keys, values))  
        print(myDict)

        newDict[i] = myDict
    return newDict
    
predic = ["cucumber", "purpleonion", "onion"]
z= (predic[0])

print ("Producto:", d.get(z))
x= d.get(z)
print("PLU:", products.get(x))