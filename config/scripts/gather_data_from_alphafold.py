from urllib import request
import pandas as pd

def gather_alphafold_data(CORRECT_IDS, filename_base="config/data/temp"):
    save = False

    all_data = []
    for id in CORRECT_IDS:
        url = f"https://alphafold.ebi.ac.uk/files/AF-{id}-F1-model_v2.cif"
        filename = f"{filename_base}/{id}.cif"
        data = request.urlopen(url).read()
        data = data.decode("utf-8")

        if save:
            with open(filename, "w") as outfile:
                outfile.write(data)


        data = data.split("_ma_qa_metric_local.ordinal_id")[1].split("_ma_software_group.group_id    1")[0].split("\n")[1:-2]
        data = [i0.split(" ") for i0 in data]
        data = [[i0 for i0 in i if i0] for i in data]
        data = [float(i[4]) for i in data]
        all_data.append(data)

    result = {"IDs": CORRECT_IDS, "pLDDT": all_data}
    result = pd.DataFrame(data=result)

    print(result)
    return all_data


if __name__ == '__main__':
    gather_alphafold_data(["A9WG76", "Q5VSL9"])
