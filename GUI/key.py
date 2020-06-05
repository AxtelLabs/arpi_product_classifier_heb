import tkinter as tk
from tkinter import ttk
import pandas as pd 
data = pd.read_csv("AbrilHEB.csv")
data = pd.DataFrame(data)




key = tk.Tk()  # key window name
key.title('Keyboard')  # title Name


exp = " "          # global variable 
# showing all data in display 

def press(num):
    global exp
    exp=exp + str(num)
    equation.set(exp)
# end 


# function clear button

def clear():
    global exp
    exp = " "
    equation.set(exp)

# end 


# Enter Button Work Next line Function

def action():
  #exp = " Next Line : "
  #print(equation, type(equation))
  equation.set(exp)
  print(equation.get()) 
  x = equation.get()
  df1 = data[data['Producto'].str.contains(x,case=False)] 

  print(df1)
  list1 = df1.iloc[:,0].values
  list2 = df1.iloc[:,1].values
  
  for i in range(len(list1)):
    print(list1[i], "            ", list2[i])
    
# end function coding

# Size window size
key.geometry('1020x250')         # normal size
key.maxsize(width=1180, height=300)      # maximum size
key.minsize(width= 1180 , height = 300)     # minimum size
# end window size

key.configure(bg = 'white')    #  add background color

# entry box
equation = tk.StringVar()
Dis_entry = ttk.Entry(key,state= 'readonly',textvariable = equation)
Dis_entry.grid(rowspan= 1 , columnspan = 1000, ipadx = 10 , ipady = 20)
# end entry box

# add all button line wise 

# First Line Button

q = ttk.Button(key,text = 'Q' , width = 6, command = lambda : press('Q'))
q.grid(row = 1 , column = 0, ipadx = 6 , ipady = 10)

w = ttk.Button(key,text = 'W' , width = 6, command = lambda : press('W'))
w.grid(row = 1 , column = 1, ipadx = 6 , ipady = 10)

E = ttk.Button(key,text = 'E' , width = 6, command = lambda : press('E'))
E.grid(row = 1 , column = 2, ipadx = 6 , ipady = 10)

R = ttk.Button(key,text = 'R' , width = 6, command = lambda : press('R'))
R.grid(row = 1 , column = 3, ipadx = 6 , ipady = 10)

T = ttk.Button(key,text = 'T' , width = 6, command = lambda : press('T'))
T.grid(row = 1 , column = 4, ipadx = 6 , ipady = 10)

Y = ttk.Button(key,text = 'Y' , width = 6, command = lambda : press('Y'))
Y.grid(row = 1 , column = 5, ipadx = 6 , ipady = 10)

U = ttk.Button(key,text = 'U' , width = 6, command = lambda : press('U'))
U.grid(row = 1 , column = 6, ipadx = 6 , ipady = 10)

I = ttk.Button(key,text = 'I' , width = 6, command = lambda : press('I'))
I.grid(row = 1 , column = 7, ipadx = 6 , ipady = 10)

O = ttk.Button(key,text = 'O' , width = 6, command = lambda : press('O'))
O.grid(row = 1 , column = 8, ipadx = 6 , ipady = 10)

P = ttk.Button(key,text = 'P' , width = 6, command = lambda : press('P'))
P.grid(row = 1 , column = 9, ipadx = 6 , ipady = 10)


clear = ttk.Button(key,text = 'Clear' , width = 6, command = clear)
clear.grid(row = 1 , column = 10, ipadx = 20 , ipady = 10)

# Second Line Button



A = ttk.Button(key,text = 'A' , width = 6, command = lambda : press('A'))
A.grid(row = 2 , column = 0, ipadx = 6 , ipady = 10)

S = ttk.Button(key,text = 'S' , width = 6, command = lambda : press('S'))
S.grid(row = 2 , column = 1, ipadx = 6 , ipady = 10)

D = ttk.Button(key,text = 'D' , width = 6, command = lambda : press('D'))
D.grid(row = 2 , column = 2, ipadx = 6 , ipady = 10)

F = ttk.Button(key,text = 'F' , width = 6, command = lambda : press('F'))
F.grid(row = 2 , column = 3, ipadx = 6 , ipady = 10)


G = ttk.Button(key,text = 'G' , width = 6, command = lambda : press('G'))
G.grid(row = 2 , column = 4, ipadx = 6 , ipady = 10)


H = ttk.Button(key,text = 'H' , width = 6, command = lambda : press('H'))
H.grid(row = 2 , column = 5, ipadx = 6 , ipady = 10)


J = ttk.Button(key,text = 'J' , width = 6, command = lambda : press('J'))
J.grid(row = 2 , column = 6, ipadx = 6 , ipady = 10)


K = ttk.Button(key,text = 'K' , width = 6, command = lambda : press('K'))
K.grid(row = 2 , column = 7, ipadx = 6 , ipady = 10)

L = ttk.Button(key,text = 'L' , width = 6, command = lambda : press('L'))
L.grid(row = 2 , column = 8, ipadx = 6 , ipady = 10)


Ñ = ttk.Button(key,text = 'Ñ' , width = 6, command = lambda : press('Ñ'))
Ñ.grid(row = 2 , column = 9, ipadx = 6 , ipady = 10)




enter = ttk.Button(key,text = 'Enter' , width = 6, command = action)
enter.grid(row = 3 , column = 10, ipadx = 50 , ipady = 10)

# third line Button

Z = ttk.Button(key,text = 'Z' , width = 6, command = lambda : press('Z'))
Z.grid(row = 3 , column = 0, ipadx = 6 , ipady = 10)


X = ttk.Button(key,text = 'X' , width = 6, command = lambda : press('X'))
X.grid(row = 3 , column = 1, ipadx = 6 , ipady = 10)


C = ttk.Button(key,text = 'C' , width = 6, command = lambda : press('C'))
C.grid(row = 3 , column = 2, ipadx = 6 , ipady = 10)


V = ttk.Button(key,text = 'V' , width = 6, command = lambda : press('V'))
V.grid(row = 3 , column = 3, ipadx = 6 , ipady = 10)

B = ttk.Button(key, text= 'B' , width = 6 , command = lambda : press('B'))
B.grid(row = 3 , column = 4 , ipadx = 6 ,ipady = 10)


N = ttk.Button(key,text = 'N' , width = 6, command = lambda : press('N'))
N.grid(row = 3 , column = 5, ipadx = 6 , ipady = 10)


M = ttk.Button(key,text = 'M' , width = 6, command = lambda : press('M'))
M.grid(row = 3 , column = 6, ipadx = 6 , ipady = 10)


space = ttk.Button(key,text = 'Space' , width = 6, command = lambda : press(' '))
space.grid(row = 4 , columnspan=14, ipadx = 180 , ipady = 10)

key.mainloop()  