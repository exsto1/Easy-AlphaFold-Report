import os
import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import pandas as pd
import argparse
from datetime import timedelta
import threading

from config.scripts.check_alphafold import *
from config.scripts.gather_data_from_alphafold import *
from config.scripts.verify_input import *
from config.scripts.batch_uniprot import *
from config.scripts.version_control import *
from summary.summary import generate_summary


def main_non_gui(input_p, download):
    print("""
---+############################+---
      ~~~~ Easy AlphaFold ~~~~       
---+############################+---
""")
    ver_check()

    section_lengths = [0, 0]
    IDS = []
    if os.path.exists(input_p):
        section_lengths = [1, 0]
        with open(input_p, "r") as ff:
            IDS.extend(ff.read().strip().split("\n"))
    else:
        section_lengths = [0, 1]
        IDS.append(input_p)

    if not IDS:
        print("ERROR! No input detected! Make sure you picked correct files!")

    FAMILIES, PDB, UNIPROT = input_parse(IDS)
    print(f"""Parameters
Input file                     | {input_p}
Download                       | {download}""")
    print("------------------------------------")
    print(f"""Found data:
Pfam families provided         | {len(FAMILIES)}
PDB IDs provided               | {len(PDB)}
Uniprot IDs provided           | {len(UNIPROT)}""")

    Uni_number, single_time = uniprot_quick_check(pfam=FAMILIES, pdb=PDB, uniprot=UNIPROT)

    if not Uni_number:
        print("Error: No IDs found. Please check your input and internet connection and try again.")
        return
    td = str(timedelta(seconds=(Uni_number // 500) * single_time)).split(":")

    print(f"Found Uniprot IDs              | {Uni_number}")
    print(f"Uniprot pages                  | {(Uni_number // 500) + 1}")
    print(f"Estimated time                 | {td[0]} Hours, {td[1]} Minutes, {td[2]} Seconds")

    Uni_data, Uni_state = uniprot_check(pfam=FAMILIES, pdb=PDB, uniprot=UNIPROT)
    Uni_data["PDB"] = Uni_data.apply(lambda row: [i for i in row["PDB"].split(";") if i], axis=1)

    if not Uni_state:
        print("Error: Empty report.")
        exit()


    Uni_IDs = Uni_data["Entry"].values.tolist()

    print(f"Found AlphaFold IDs            | ", end="")

    ALPHA_IDS = alphafold_verify(Uni_IDs)

    print(f"""{len(ALPHA_IDS)}
% of Uniprot IDS in AlphaFold  | {round(len(ALPHA_IDS) / len(Uni_IDs) * 100, 2)}
------------------------------------
Gathering data and preparing summary...""")

    count_found = 0
    type_df_data = []

    if FAMILIES:
        fams = list(Uni_data["Pfam"].apply(tuple).unique())
        print(fams)
        for i in range(len(FAMILIES)):
            found = False
            for i1 in range(len(fams)):
                if found:
                    break
                for i2 in range(len(fams[i1])):
                    if FAMILIES[i] == fams[i1][i2].lower():
                        count_found += 1
                        type_df_data.append([FAMILIES[i], "Pfam"])
                        found = True
                        break
            if not found:
                type_df_data.append([FAMILIES[i], "None"])


    if PDB:
        PDBs = list(Uni_data["PDB"].apply(tuple).unique())
        print(PDBs)
        for i in range(len(PDB)):
            found = False
            for i1 in range(len(PDBs)):
                if found:
                    break
                for i2 in range(len(PDBs[i1])):
                    if PDB[i] == PDBs[i1][i2].lower():
                        count_found += 1
                        type_df_data.append([PDB[i], "PDB"])
                        found = True
                        break
            if not found:
                type_df_data.append([PDB[i], "None"])


    if UNIPROT:
        Unis = list(Uni_data["Entry"].unique())
        print(Unis)
        for i in range(len(UNIPROT)):
            found = False
            for i1 in range(len(Unis)):
                if UNIPROT[i] == Unis[i1].lower():
                    count_found += 1
                    type_df_data.append([UNIPROT[i], "Uni"])
                    found = True
                    break

            if not found:
                type_df_data.append([UNIPROT[i], "None"])

    """
    -- extra_info
    
    [Pfam, PDB, Uniprot, Uniprot found, AlphaFold found, found from the input]
    
    -----------------------------------------
    
    -- type_df
    
    ID      | Base type
    -------------------
    ABCD    | PDB
    XAXA    | None
    PF01402 | Pfam
    ABCDE   | Uni
    
    -----------------------------------------
    
    -- plddt_data
    
    ID    | pLDDT
    ----------------
    ABCDE | [12.34, 45.67, 67.78]
    ABCDE | [12.34, 45.67, 67.78]
    ABCDE | [12.34, 45.67, 67.78]
    """

    extra_info = [count_found, len(FAMILIES), len(PDB), len(UNIPROT), len(Uni_IDs), len(ALPHA_IDS)]
    type_df = pd.DataFrame(type_df_data, columns=["ID", "Database"])
    plddt_data = gather_alphafold_data(ALPHA_IDS, save=download)
    
    # PLOTS
    SUMMARY_PATH = "https://127.0.0.1:8052"
    generate_summary(section_lengths, extra_info, plddt_data, Uni_data)

    # Generate summary
    print("\nProgram finished!")
    
    
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

        progress["value"] += 5
        root.update()

        # ------------------------------------------------------------------------------------------------------------

        FAMILIES, PDB, UNIPROT = input_parse(IDS)
        insert_message(f"Found data:")
        insert_message(f"Pfam families provided         | {len(FAMILIES)}")
        insert_message(f"PDB IDs provided               | {len(PDB)}")
        insert_message(f"Uniprot IDs provided           | {len(UNIPROT)}")
        insert_message("------------------------------------")
        progress["value"] += 5
        root.update()

        Uni_number, single_time = uniprot_quick_check(pfam=FAMILIES, pdb=PDB, uniprot=UNIPROT)

        if not Uni_number:
            insert_message("Error: No IDs found. Please check your input and internet connection and try again.")
            return
        td = str(timedelta(seconds=(Uni_number // 500) * single_time)).split(":")
        insert_message(f"Found Uniprot IDs              | {Uni_number}")
        insert_message(f"Uniprot pages                  | {(Uni_number // 500) + 1}")
        insert_message(f"Estimated time                 | {td[0]} Hours, {td[1]} Minutes, {td[2]} Seconds")

        root.update()

        Uni_data, Uni_state = uniprot_check(pfam=FAMILIES, pdb=PDB, uniprot=UNIPROT)

        # ------------------------------------------------------------------------------------------------------------

        Uni_IDs = Uni_data["Entry"].values.tolist()


        progress["value"] += 15
        root.update()

        # ------------------------------------------------------------------------------------------------------------

        batch_size = 5000
        ALPHA_IDS = []
        tick = 50 / ((len(Uni_IDs) // batch_size) + 1)
        for i in range(0, len(Uni_IDs), batch_size):
            ALPHA_IDS_temp = alphafold_verify(Uni_IDs[i:i+batch_size])
            ALPHA_IDS.extend(ALPHA_IDS_temp)
            progress["value"] += tick
            root.update()

        insert_message(f"Found AlphaFold IDs            | {len(ALPHA_IDS)}")
        insert_message(f"% of Uniprot IDS in AlphaFold  | {round(len(ALPHA_IDS) / len(Uni_IDs) * 100, 2)}")
        root.update()

        # ------------------------------------------------------------------------------------------------------------

        plddt_data = gather_alphafold_data(ALPHA_IDS)
        insert_message("------------------------------------")
        insert_message("Collecting data from AlphaFold")
        progress["value"] += 15
        root.update()

        """
        "ID", "pLDDT"
        ABCDE, [12.23, 95.56, 76.45,...]
        ABCDE, [12.23, 95.56, 76.45,...]
        ABCDE, [12.23, 95.56, 76.45,...]
        ABCDE, [12.23, 95.56, 76.45,...]
        """
        # ------------------------------------------------------------------------------------------------------------

        count_found = 0
        type_df_data = []

        if FAMILIES:
            fams = list(Uni_data["Pfam"].apply(tuple).unique())
            print(fams)
            for i in range(len(FAMILIES)):
                found = False
                for i1 in range(len(fams)):
                    if found:
                        break
                    for i2 in range(len(fams[i1])):
                        if FAMILIES[i] == fams[i1][i2].lower():
                            count_found += 1
                            type_df_data.append([FAMILIES[i], "Pfam"])
                            found = True
                            break
                if not found:
                    type_df_data.append([FAMILIES[i], "None"])
        if PDB:
            PDBs = list(Uni_data["PDB"].unique())
            PDBs = [i0.split(";") for i0 in PDBs]
            print(PDBs)
            for i in range(len(PDB)):
                found = False
                for i1 in range(len(PDBs)):
                    if found:
                        break
                    for i2 in range(len(PDBs[i1])):
                        if PDB[i] == PDBs[i1][i2].lower():
                            count_found += 1
                            type_df_data.append([PDB[i], "PDB"])
                            found = True
                            break
                if not found:
                    type_df_data.append([PDB[i], "None"])

        if UNIPROT:
            Unis = list(Uni_data["Entry"].unique())
            print(Unis)
            for i in range(len(UNIPROT)):
                found = False
                for i1 in range(len(Unis)):
                    if UNIPROT[i] == Unis[i1].lower():
                        count_found += 1
                        type_df_data.append([UNIPROT[i], "Uni"])
                        found = True
                        break

                if not found:
                    type_df_data.append([UNIPROT[i], "None"])

        """
        -- extra_info

        [Pfam, PDB, Uniprot, Uniprot found, AlphaFold found, found from the input]

        -----------------------------------------

        -- type_df

        ID      | Base type
        -------------------
        ABCD    | PDB
        XAXA    | None
        PF01402 | Pfam
        ABCDE   | Uni

        -----------------------------------------

        -- plddt_data

        IDs    | pLDDT
        ----------------
        ABCDE | [12.34, 45.67, 67.78]
        ABCDE | [12.34, 45.67, 67.78]
        ABCDE | [12.34, 45.67, 67.78]
        """

        extra_info = [count_found, len(FAMILIES), len(PDB), len(UNIPROT), len(Uni_IDs), len(ALPHA_IDS)]
        type_df = pd.DataFrame(type_df_data, columns=["ID", "Database"])
        print(type_df)
        print(extra_info)
        # PLOTS

        # ------------------------------------------------------------------------------------------------------------

        insert_message("Preparing summary")
        root.update()

        SUMMARY_PATH = "https://127.0.0.1:8052"

        section_lengths = [len(i0) for i0 in data]
        # PLOTS
        generate_summary(section_lengths, extra_info, plddt_data, Uni_data)
        # Generate summary
        progress["value"] += 5
        insert_message("Done!")
        insert_message(f"Output summary generated in: {SUMMARY_PATH}")
        return

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

    start = Button(text="Start search", command=threading.Thread(target=start_run).start)
    start.pack(in_=bottom4, side=LEFT)
    root.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input")
    parser.add_argument("-g", help="GUI [True]", action="store_false")
    parser.add_argument("-d", help="Download [False]", action="store_true")
    args = parser.parse_args()

    input_path = args.i
    gui = args.g
    download = args.d

    if gui:
        main_gui()
    else:
        if not input_path:
            print("Please provide input filepath!")
            exit(1)
        else:
            main_non_gui(input_path, download)
