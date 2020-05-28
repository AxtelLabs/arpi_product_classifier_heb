# Author: Miguel Martinez Lopez
# Version: 0.8
# Modified by: Israel Melendez Montoya
import pandas as pd
import re

try:
    from Tkinter import StringVar, Entry, Frame, Listbox, Scrollbar, Text, Label
    from Tkconstants import *
except ImportError:
    from tkinter import StringVar, Entry, Frame, Listbox, Scrollbar, Text, Label
    from tkinter.constants import *

i = 0

def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
    sbar.set(first, last)


class Combobox_Autocomplete(Entry, object):
    def __init__(self, master, list_of_items, string,autocomplete_function=None,listbox_width=430, listbox_height=9, ignorecase_match=False, startswith_match=False, vscrollbar=False, hscrollbar=False, **kwargs):
        if hasattr(self, "autocomplete_function"):
            if autocomplete_function is not None:
                raise ValueError("Combobox_Autocomplete subclass has 'autocomplete_function' implemented")
        else:
            if autocomplete_function is not None:
                self.autocomplete_function = autocomplete_function
                #print(self.autocomplete_function)
            else:
                if list_of_items is None:
                    raise ValueError("If not given complete function, list_of_items can't be 'None'")

                if ignorecase_match:
                    if startswith_match:
                        def matches_function(entry_data, item):
                            return item.startswith(entry_data)
                    else:
                        def matches_function(entry_data, item):
                            return item in entry_data

                    self.autocomplete_function = lambda entry_data: [item for item in self.list_of_items if matches_function(entry_data, item)]
                    #print(self.autocomplete_function)
                else:
                    if startswith_match:
                        def matches_function(escaped_entry_data, item):
                            if re.match(escaped_entry_data, item, re.IGNORECASE):
                                return True
                            else:
                                return False
                    else:
                        def matches_function(escaped_entry_data, item):
                            if re.search(escaped_entry_data, item, re.IGNORECASE):
                                return True
                            else:
                                return False
                    
                    def autocomplete_function(entry_data):
                        escaped_entry_data = re.escape(entry_data)
                       # print(escaped_entry_data)
                        df1 = [item for item in self.list_of_items if matches_function(escaped_entry_data, item)]
                        df4 = [" "  for row in range(len(df1))]
                        df6 = [val for pair in zip(df1, df4) for val in pair]
                        df6.insert(0, " ")
                        df6.append(" ")
                        return df6#[item for item in self.list_of_items if matches_function(escaped_entry_data, item)]

                    def autocomplete_function2(entry_data):
                        escaped_entry_data = re.escape(entry_data)
                       # print(escaped_entry_data)
                        return escaped_entry_data

                    self.autocomplete_function = autocomplete_function

        
        self._listbox_height = int(listbox_height)
        self._listbox_width = listbox_width

        self.list_of_items = list_of_items
        
        self._use_vscrollbar = vscrollbar
        self._use_hscrollbar = hscrollbar

        kwargs.setdefault("background", "white")

        if "textvariable" in kwargs:
            self._entry_var = kwargs["textvariable"]
        else:
            self._entry_var = kwargs["textvariable"] = string#self.equation

        Entry.__init__(self, master, **kwargs, width=45)
        
        
        self._trace_id = self._entry_var.trace('w', self._on_change_entry_var)
        
        self._listbox = None

        self.bind("<Tab>", self._on_tab)
        self.bind("<Up>", self._previous)
        self.bind("<Down>", self._next)
        self.bind('<Control-n>', self._next)
        self.bind('<Control-p>', self._previous)

        self.bind("<Return>", self._update_entry_from_listbox)
        self.bind("<Escape>", lambda event: self.unpost_listbox())
         
    def _on_tab(self, event):
        self.post_listbox()
        return "break"
 
    
    def _on_change_entry_var(self, name, index, mode):
        
        entry_data = self._entry_var.get()
        print(entry_data)
        if entry_data == '':
            self.unpost_listbox()
            self.focus()
        else:
            values = self.autocomplete_function(entry_data)
            if values:
                if self._listbox is None:
                    self._build_listbox(values)
                else:
                    self._listbox.delete(0, END)

                    height = min(self._listbox_height, len(values))
                    self._listbox.configure(height=height)

                    for item in values:
                        self._listbox.insert(END, item)
                
            else:
                self.unpost_listbox()
                self.focus()

    def _build_listbox(self, values):
        listbox_frame = Frame()

        self._listbox = Listbox(listbox_frame, background="#e6e6e6", fg="#666666",selectmode=SINGLE, activestyle="none", exportselection=False, font=("Helvetica", 16), height=10, yscrollcommand=True)
        self._listbox.configure(justify=LEFT)
        self._listbox.grid(row=0, column=0,sticky = N+E+W+S)

        self._listbox.bind("<ButtonRelease-1>", self._update_entry_from_listbox)
        self._listbox.bind("<Return>", self._update_entry_from_listbox)
        self._listbox.bind("<Escape>", lambda event: self.unpost_listbox())
        
        self._listbox.bind('<Control-n>', self._next)
        self._listbox.bind('<Control-p>', self._previous)

        if self._use_vscrollbar:
            vbar = Scrollbar(listbox_frame, orient=VERTICAL, command= self._listbox.yview)
            vbar.grid(row=0, column=1, sticky=N+S)
            
            self._listbox.configure(yscrollcommand= lambda f, l: autoscroll(vbar, f, l))
            
        if self._use_hscrollbar:
            hbar = Scrollbar(listbox_frame, orient=HORIZONTAL, command= self._listbox.xview)
            hbar.grid(row=1, column=0, sticky=E+W)
            
            self._listbox.configure(xscrollcommand= lambda f, l: autoscroll(hbar, f, l))

        listbox_frame.grid_columnconfigure(0, weight= 1)
        listbox_frame.grid_rowconfigure(0, weight= 1)

        x = -self.cget("borderwidth") - self.cget("highlightthickness") 
        y = self.winfo_height()-self.cget("borderwidth") - self.cget("highlightthickness")

        if self._listbox_width:
            width = self._listbox_width
        else:
            width=self.winfo_width()

        listbox_frame.place(in_=self, x=x, y=y, width=width)
        
        height = min(self._listbox_height, len(values)+10)
        self._listbox.configure(height=height)

        for item in values:
            self._listbox.insert(END, item)

    def post_listbox(self):
        if self._listbox is not None: return

        entry_data = self._entry_var.get()
        if entry_data == '': return

        values = self.autocomplete_function(entry_data)
        if values:
            self._build_listbox(values)

    def unpost_listbox(self):
        if self._listbox is not None:
            self._listbox.master.destroy()
            self._listbox = None

    def get_value(self):
        return self._entry_var.get()

    def set_value(self, text, close_dialog=False):
        self._set_var(text)

        if close_dialog:
            self.unpost_listbox()

        self.icursor(END)
        self.xview_moveto(1.0)
        
    def _set_var(self, text):
        self._entry_var.trace_vdelete("w", self._trace_id)
        self._entry_var.set(text)
        self._trace_id = self._entry_var.trace('w', self._on_change_entry_var)
        



    def _update_entry_from_listbox(self, event):
        if self._listbox is not None:
            current_selection = self._listbox.curselection()
           # print(current_selection)#prints listbox index of the selection
            if current_selection:
                
                text = self._listbox.get(current_selection)
               # print(text)
                text= text.replace("  "," ")
                #text = re.sub(r"([0-9]+(\.[0-9]+)?)",r" \1 ", text).strip()
                #text = text.replace(" ", "      ")
                #if productAndPlu is True:
                #    print(productAndPlu)

                """self.productAndPlu = Label(self.master,text=" "*95, font=("Helvetica", 14))
                self.productAndPlu.place(relx=0.12, rely=.15, relwidth= .2, relheight=.1)
                #self.productAndPlu.place(x= 100, y= 420)
                self.productAndPlu.focus()"""

                self.productAndPlu = Label(self.master,text=text, font=("Helvetica", 14), bg= "#27AB37", fg= "#FFFFFF" )
                #self.productAndPlu = Label(self.master,text=text, font=("Helvetica", 14))
                self.productAndPlu.place(relx=0.070, rely=.40, relwidth= .35, relheight=.06)
                #self.productAndPlu.place(relx=0.070, rely=.23, relwidth= .35, relheight=.06)
                self.productAndPlu.focus()
                
                entry_data = self._entry_var.get()

                #self._set_var(text)
                self._set_var(entry_data)
                

                
            self._listbox.master.destroy()
            self._listbox = None

            self.focus()
            self.icursor(END)
            self.xview_moveto(1.0)
            
        return "break"


    def getShownSelection(self, event):
        if self._listbox is not None:
            current_selection = self._listbox.curselection()
        # print(current_selection)#prints listbox index of the selection
            if current_selection:

                text = self._listbox.get(current_selection)
                
                text= text.replace("  "," ")
            else:
                text = "None"
        return 






    def _previous(self, event):
        if self._listbox is not None:
            current_selection = self._listbox.curselection()

            if len(current_selection)==0:
                self._listbox.selection_set(0)
                self._listbox.activate(0)
            else:
                index = int(current_selection[0])
                self._listbox.selection_clear(index)

                if index == 0:
                    index = END
                else:
                    index -= 1

                self._listbox.see(index)
                self._listbox.selection_set(first=index)
                self._listbox.activate(index)

        return "break"

    def _next(self, event):
        if self._listbox is not None:

            current_selection = self._listbox.curselection()
            if len(current_selection)==0:
                self._listbox.selection_set(0)
                self._listbox.activate(0)
            else:
                index = int(current_selection[0])
                self._listbox.selection_clear(index)
                
                if index == self._listbox.size() - 1:
                    index = 0
                else:
                    index +=1
                    
                self._listbox.see(index)
                self._listbox.selection_set(index)
                self._listbox.activate(index)
        return "break"

if __name__ == '__main__':
    try:
        from Tkinter import Tk
    except ImportError:
        from tkinter import Tk


    df = pd.read_csv("AbrilHEB.csv")
    df = pd.DataFrame(df)

    df1 = df['Producto'].to_list()
    df1 = [product.strip() for product in df1]
    df1 = [product.replace("  ", " ") for product in df1]
    # strip trailing and leading whitespaces
    df2 = df["PLU"].to_list()
    df2 = [product.strip() for product in df2]
    # remove traiing and leading whitespaces

    concatLen = 0
    # initialize concat space length
    spaceList = [ len(s) for s in df1]
    # measure the length of each string in Product

    concatLen = max(spaceList) + 5
    # Each space is accounted for with respect to the maximum length of the longest string
    spaceList = [concatLen-len(s) for s in df1]
    # Number of spaces will be max ( all strs in Product)
    df2Right = [df2[i].rjust(spaceList[i]) for i in range(len(df2))]
    # create the left spaces for the PLUs (justify right accordingly)
    df1 = [df1[i]+df2Right[i] for i in range(len(df2Right))]
    # Products and new justified PLUs unite
    list_of_items =  df1 

    root = Tk()
    root.geometry("800x300")

    combobox_autocomplete = Combobox_Autocomplete(root, list_of_items, highlightthickness=1)
    combobox_autocomplete.pack()
    

    root.mainloop()