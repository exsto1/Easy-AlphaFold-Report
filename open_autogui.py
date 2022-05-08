import os
import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import time


xsize = 800
ysize = 500


def main_run_execution(data):
    def insert_message(text):
        text_box.configure(state=NORMAL)
        text_box.insert("end", text + "\n")
        text_box.configure(state=DISABLED)

    info_frame = Frame(root, height=150)
    info_frame.pack(fill=X, side=BOTTOM, padx=10, pady=5, expand=False)
    info_frame.propagate(False)
    scrollbar = Scrollbar(info_frame, orient="vertical")
    scrollbar.pack(side=RIGHT, fill=Y)
    text_box = Text(info_frame, height=20, state=DISABLED, yscrollcommand=scrollbar.set)
    # scrollbar.configure(command=text_box.yview)
    text_box.pack()

    run_frame = Frame(root)
    run_frame.pack(fill=BOTH, side=BOTTOM, padx=10)
    progress_bar = Progressbar(run_frame, orient=HORIZONTAL, length=100, mode="determinate")
    progress_bar.pack(expand=True, fill=X)

    insert_message("a")
    insert_message("a")
    insert_message("a")
    insert_message("a")

    for i in range(100):
        # progress_bar["value"] += 1
        insert_message("b")
        insert_message("b")
        insert_message("b")
        insert_message("b")

    insert_message("c")
    insert_message("c")
    insert_message("c")




def add_file():
    directory = filedialog.askopenfilenames()
    for i in directory:
        box.insert(END, i)


def add_id():
    id_from_entry = free_entry_box.get()
    box.insert(END, id_from_entry)


def add_id_bind(e):
    add_id()


def remove_file():
    try:
        selection = box.curselection()
        box.delete(selection)
    except:
        pass


def start_run():
    list_of_files = []
    stan = True
    i = 0
    while stan:
        if box.get(i):
            list_of_files.append(box.get(i))
            i += 1
        else:
            stan = False
    if len(list_of_files) > 0:
        # root.destroy()
        start["state"] = "disabled"
        for i in list_of_files:
            base = i
            to_search = []
            files = []
            IDs = []
            if os.path.exists(base):
                print("FILE: ", base)
                files.append(base)
            else:
                print("ID: ", base)
                IDs.append(base)
            to_search = [files, IDs]
            main_run_execution(to_search)



root = Tk()
root.geometry(f'{xsize}x{ysize}')
root.minsize(height=500)
root.resizable(width=0, height=0)
root.title('Easy AlphaFold Report')

top = Frame(root)
bottom_main1 = Frame(root)
bottom_main2 = Frame(root)
bottom1 = Frame(bottom_main1)
bottom2 = Frame(bottom_main1)
bottom3 = Frame(bottom_main1)
bottom4 = Frame(bottom_main2)

top.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=10)
bottom_main1.pack(side=TOP)
bottom_main2.pack(side=TOP, pady=10)
bottom1.pack(side=LEFT, padx=(10, 1))
bottom2.pack(side=LEFT, padx=(10, 1))
bottom3.pack(side=LEFT, padx=(10, 1))
bottom4.pack(side=LEFT)

box = Listbox(root)
box.pack(in_=top, fill=BOTH, expand=1)

add_button = Button(text="Add file", command=add_file).pack(in_=bottom1, side=LEFT)

free_entry_box = Entry()
free_entry_box.bind("<Return>", add_id_bind)
free_entry_box.pack(in_=bottom2, side=LEFT)

add_id_button = Button(text="Add ID", command=add_id).pack(in_=bottom2, side=LEFT)

remove_button = Button(text="Remove entry", command=remove_file).pack(in_=bottom3, side=LEFT)

start = Button(text="Start search", command=start_run)
start.pack(in_=bottom4, side=LEFT)
root.mainloop()
