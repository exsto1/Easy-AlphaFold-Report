def input_parse(IDs):
    with open("../data/Pfam-A.clans.tsv") as file_h:
        file = file_h.readlines()

    file = [i.rstrip().split("\t") for i in file]
    file = [[i0.lower() for i0 in i] for i in file]

    families = []
    PDB = []
    uniprot_raw = []

    IDs = [i.lower() for i in IDs]
    for id in IDs:
        found_pfam = False
        if id[:2] == "CL":
            found_pfam = True
            families = []
            for row in file:
                if id == row[1]:
                    if row[0] not in families:
                        families.append(row[0])
        else:
            for row in file:
                for val in row:
                    if id == val:
                        found_pfam = True
                        if row[0] not in families:
                            families.append(row[0])

        if not found_pfam:
            if len(id) == 4:
                PDB.append(id)
            else:
                uniprot_raw.append(id)

    print(families)
    print(PDB)
    print(uniprot_raw)

    return families, PDB, uniprot_raw


if __name__ == '__main__':
    input_parse(["Q5VSL9", "CL0057", "PF01402", "PAN domain", "7SB4"])
