from datetime import datetime
from urllib import request
import gzip
import os


def ver_check():
    def update_data():
        url1 = "http://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.clans.tsv.gz"
        url2 = "http://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam.version.gz"
        p1gz = "../data/Pfam-A.clans.gz"
        p1 = "../data/Pfam-A.clans.tsv"
        p2gz = "../other/Pfam.version.gz"
        p2 = "../other/Pfam.version"

        try:
            request.urlretrieve(url1, p1gz)

            with gzip.open(p1gz, 'rb') as f:
                file_content = f.read()
                with open(p1, "w") as outfile:
                    outfile.write(file_content)

            os.remove(p1gz)

            request.urlretrieve(url2, p2gz)

            with gzip.open(p2gz, 'rb') as f:
                file_content = f.read()
                print(file_content)
                with open(p2, "w") as outfile:
                    outfile.write(file_content)

            os.remove(p2gz)
        except:
            return
        return


    with open("../other/Pfam.version") as file_h:
        file = file_h.readlines()
        date_file = file[2].split(": ")[1].strip()
        date_file = datetime.strptime(date_file, "%Y-%m")

        now = datetime.now()

        if now > date_file:
            return
        else:
            update_data()
            return


if __name__ == '__main__':
    ver_check()
