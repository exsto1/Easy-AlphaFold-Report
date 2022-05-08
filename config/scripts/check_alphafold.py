def alphafold_verify(UNI_IDs):
    with open("../data/AlphaFold_metadata.txt") as file_h:
        file = file_h.readlines()
        file = [i.split(",")[0] for i in file]

    found_IDS = []
    for i in UNI_IDs:
        if i in file:
            found_IDS.append(i)

    return found_IDS


if __name__ == '__main__':
    res = alphafold_verify(["B0BNG7", "B5R6I4", "XXXXXX"])
