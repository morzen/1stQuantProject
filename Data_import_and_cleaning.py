import zipfile
import csv
import os
import pathlib
import io
import pandas as pd
from pathlib import Path
from os import listdir
from os.path import isfile, join

#unpacking phase.

zip_file_path = "./data/1_zipped/"
zipped_files_list = [f for f in listdir(zip_file_path) if isfile(join(zip_file_path, f))]

if os.path.isdir("./data/2_raw") == False:
    os.mkdir("./data/2_raw")
    print("folder created")
else:
    print("folder already exist")
    pass


zip_file_path = "./data/1_zipped/"
zipped_files_list = [f for f in listdir(zip_file_path) if isfile(join(zip_file_path, f))]
# print(zipped_files_list)

for filename in zipped_files_list:
    with zipfile.ZipFile(zip_file_path+filename, 'r') as zip_ref:
        zip_ref.extractall("./data/2_raw")

print("files extracted \n")



#cleaning phase.
print("====Cleanning phase =====\n")

file_path = "./data/2_raw/"
files_list = [f for f in listdir(file_path) if isfile(join(file_path, f))]

dataTables = {}

# This iterator serves as an import of the files into panda datafrmae as well as selecting the tables
# within the csv files which are (impractically) not pure table and have some text at the top
for filename in files_list:
    if filename.endswith(".csv"):
        path = file_path + filename
        with open(path) as f:
            lines = f.read().splitlines()
            Title_table_list = []
            starts = []
            ends = []
            switch = 0
            for i, line in enumerate(lines):
                if line.lstrip().startswith(","):
                    starts.append(i)
                    switch = 1

                    for title_look_up_idx in range(i - 1, -1, -1):
                        title_look_up = lines[title_look_up_idx]
                        if title_look_up == "":
                            title_start_idx = title_look_up_idx + 1

                            title_end_idx = i-1

                            title = " ".join([l.strip() for l in lines[title_start_idx:title_end_idx + 1]])
                            Title_table_list.append(title)

                            break
                            


                elif switch == 1 and line.lstrip()== "":
                    ends.append(i)
                    switch = 0
                elif switch == 1 and i == len(lines)-1:
                    ends.append(len(lines))
                    switch = 0
                else:
                    pass



            if len(starts) == len(ends):
                No_Table = 1
                for start_idx, x in enumerate(starts):
                    if len(starts) == 1:
                        df = pd.read_csv(io.StringIO("\n".join(lines[starts[start_idx]:ends[start_idx]])))
                        dataTables[filename] = df
                    else:
                        df = pd.read_csv(io.StringIO("\n".join(lines[starts[start_idx]:ends[start_idx]])))
                        dataTables[filename+"_"+str(Title_table_list[start_idx])] = df
                        No_Table = No_Table + 1

            else:
                print("error in table index starts ends index list mismatch, list not of same length, not possible")
                break
                
            


    else:
        print(filename)
        print("no file name in file list _ else not supposed to happen investigate import and text clean 1st clean iterator")
        pass


print(len(dataTables))
for key, df in dataTables.items():
    print(key, df.shape)
