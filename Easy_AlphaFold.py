import os
import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import pandas as pd
import argparse

from config.scripts.check_alphafold import *
from config.scripts.gather_data_from_alphafold import *
from config.scripts.verify_input import *
from config.scripts.batch_uniprot import *
from config.scripts.version_control import *


def main_non_gui(input_p, SUMMARY_PATH, download):
    ver_check()
    print("Databse version checked.")

    IDS = []
    with open(input_p, "r") as ff:
        IDS.extend(ff.read().strip().split("\n"))

    if not IDS:
        print("ERROR! No input detected! Make sure you picked correct files!")

    print("Data loaded.")

    FAMILIES, PDB, UNIPROT = input_parse(IDS)
    print(FAMILIES, PDB, UNIPROT)
    print("Data types parsed.")
    print("------------------------------------")
    print(f"""Found data:
    Pfam families provided   | {len(FAMILIES)}
    PDB IDs provided         | {len(PDB)}
    Uniprot IDs provided     | {len(UNIPROT)}
    Found Uniprot IDs        | """, end="")

    uniprot_tsv = uniprot_to_file(pfam=FAMILIES, pdb=PDB, uniprot=UNIPROT)
    if not uniprot_tsv:
        print("Error: Empty report.")
        exit()

    # Data from uniprot is stored in config/data/uniprot_data.tsv and
    # in val uniprot_tsv (StringIO ready to open in pandas df)

    df = pd.read_csv(uniprot_tsv, sep="\t")
    df["first"] = df['Taxonomic lineage'].str.split(' \(').str[0]
    df["superkingdom"] = df['Taxonomic lineage'].str.split(',').str[-2].str.split(" \(").str[0]

    # PARSE DATA IN UNIPROT - GET ALL UNI IDS AND STATISTICS
    RES_UP2 = df["Entry"].values.tolist()

    print(f"{len(RES_UP2)}\nFound AlphaFold IDs      | ", end="")

    ALPHA_IDS = alphafold_verify(RES_UP2)

    print(f""" {len(ALPHA_IDS)}\n
    % of Uniprot IDS in AlphaFold | {len(ALPHA_IDS) / len(RES_UP2) * 100}
    ------------------------------------
    Gathering data and preparing summary...""")

    plddt_data = gather_alphafold_data(ALPHA_IDS, save=download)

    # PLOTS

    # Generate summary
    print("Done.")
    print(f"Output summary generated in: {SUMMARY_PATH}")
    
    
def main_gui():
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
        progress = Progressbar(info_frame, orient=HORIZONTAL, length=100, mode='determinate')
        progress.pack(expand=True, fill=X)
        scrollbar = Scrollbar(info_frame, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)
        text_box = Text(info_frame, height=20, state=DISABLED, yscrollcommand=scrollbar.set)
        scrollbar.configure(command=text_box.yview)
        text_box.pack()

        run_frame = Frame(root)
        run_frame.pack(fill=BOTH, side=BOTTOM, padx=10)
        root.update()

        ver_check()
        insert_message("Databse version checked.")
        progress["value"] += 5
        root.update()

        # ------------------------------------------------------------------------------------------------------------

        IDS = data[1]
        FILES = data[0]

        if FILES:
            for path in FILES:
                with open(path, "r") as ff:
                    IDS.extend(ff.read().strip().split("\n"))

        if not IDS:
            insert_message("ERROR! No input detected! Make sure you picked correct files!")

        insert_message("Data loaded.")
        progress["value"] += 5
        root.update()

        # ------------------------------------------------------------------------------------------------------------

        FAMILIES, PDB, UNIPROT = input_parse(IDS)
        insert_message("Data types parsed.")

        uniprot_tsv = uniprot_to_file(pfam=FAMILIES, pdb=PDB, uniprot=UNIPROT)
        if not uniprot_tsv:
            insert_message("Error: No IDs found. Please check your input and internet connection and try again.")
            return
        progress["value"] += 5
        root.update()

        # ------------------------------------------------------------------------------------------------------------

        # Data from uniprot is stored in config/data/uniprot_data.tsv and
        # in val uniprot_tsv (StringIO ready to open in pandas df)

        df = pd.read_csv(uniprot_tsv, sep="\t")

        # PARSE DATA IN UNIPROT - GET ALL UNI IDS AND STATISTICS
        RES_UP2 = df["Entry"].values.tolist()

        insert_message("Verified input pt.1.")
        progress["value"] += 15
        root.update()

        # ------------------------------------------------------------------------------------------------------------
        insert_message("Verifing AlphaFold data... Please be patient.")
        root.update()

        batch_size = 5000
        ALPHA_IDS = []
        tick = 50 / (len(RES_UP2) / batch_size)
        for i in range(0, len(RES_UP2), batch_size):
            ALPHA_IDS_temp = alphafold_verify(RES_UP2[i:i+batch_size])
            ALPHA_IDS.extend(ALPHA_IDS_temp)
            progress["value"] += tick
            root.update()

        insert_message("Verified input pt.2.")
        root.update()

        # ------------------------------------------------------------------------------------------------------------

        plddt_data = gather_alphafold_data(ALPHA_IDS)
        insert_message("Data collected.")
        progress["value"] += 15
        root.update()

        # ------------------------------------------------------------------------------------------------------------

        insert_message("Preparing summary")
        root.update()

        SUMMARY_PATH = "test.html"
        # PLOTS

        # Generate summary
        progress["value"] += 5
        insert_message("Done.")
        insert_message(f"Output summary generated in: {SUMMARY_PATH}")

    def add_file():
        directory = filedialog.askopenfilenames()
        for i in directory:
            box.insert(END, i)

    def add_id():
        id_from_entry = free_entry_box.get()
        if id_from_entry:
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
        def get_data():
            list_of_files = []
            stan = True
            i = 0
            while stan:
                if box.get(i):
                    list_of_files.append(box.get(i))
                    i += 1
                else:
                    stan = False
            return list_of_files

        def split_to_ID_file(list_of_files):
            files = []
            IDs = []
            for i in list_of_files:
                base = i
                if os.path.exists(base):
                    files.append(base)
                else:
                    IDs.append(base)
            to_search = [files, IDs]
            return to_search

        list_of_files = get_data()
        if len(list_of_files) > 0:
            start["state"] = "disabled"
            to_search = split_to_ID_file(list_of_files)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input")
    parser.add_argument("-o", help="Output")
    parser.add_argument("-g", help="GUI [True]", action="store_false")
    parser.add_argument("-d", help="Download [False]", action="store_true")
    args = parser.parse_args()

    input_path = args.i
    output_path = args.o
    gui = args.g
    download = args.d

    if gui:
        main_gui()
    else:
        if not input_path or not output_path:
            print("Please provide input and output filepath!")
            exit(1)
        else:
            main_non_gui(input_path, output_path, download)
