import zipfile
import csv
import os
import pathlib
import io
import re
import pandas as pd
from pathlib import Path
from os import listdir
from os.path import isfile, join



def Table_Title_sanitisation_and_uniformisation(Title_string):
    title = Title_string.strip()
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", "_", title)
    title = title.strip("_")

    return title





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



#early cleanning and storing phase.
print("====early cleanning and storing phase =====\n")

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
            #this for loops find beginning of table line "," and the end first "" after ","
            # it select it as a table and stores the lines
            for i, line in enumerate(lines):
                if line.lstrip().startswith(","):
                    starts.append(i)
                    switch = 1

                    #this for helps look for the title which is right above table start
                    #goes back up until line == "" and that is concidered the title
                    for title_look_up_idx in range(i - 1, -1, -1):
                        title_look_up = lines[title_look_up_idx]
                        if title_look_up == "":
                            title_start_idx = title_look_up_idx + 1

                            title_end_idx = i-1

                            title = " ".join([l.strip() for l in lines[title_start_idx:title_end_idx + 1]])
                            title = Table_Title_sanitisation_and_uniformisation(title)
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


            #the stored line and titles are used to give panda the tables and stores them in a dictionnary
            if len(starts) == len(ends):
                # No_Table = 1
                for start_idx, x in enumerate(starts):
                    if len(starts) == 1:
                        df = pd.read_csv(io.StringIO("\n".join(lines[starts[start_idx]:ends[start_idx]])))
                        dataTables[filename] = df
                    else:
                        df = pd.read_csv(io.StringIO("\n".join(lines[starts[start_idx]:ends[start_idx]])))
                        dataTables[filename+"_"+str(Title_table_list[start_idx])] = df
                        # No_Table = No_Table + 1

            else:
                raise ValueError("error in table index starts ends index list mismatch, list not of same length, not possible")
                
            


    else:
        print(filename)
        print("no file name in file list _ else not supposed to happen investigate import and text clean 1st clean iterator")
        pass


print(len(dataTables))
for key, df in dataTables.items():
    print(key, df.shape)


# cleanning phase.
print("==== cleanning phase =====\n")


for Table_key, Df_table in dataTables.items():
    #Sanitizing tables column names
    #remove spaces from column strings
    Column_name_list = Df_table.columns.tolist()
    Column_name_list[0] = "date"
    Sanatized_Column_list_name = []
    for item in Column_name_list:
        item = item.strip()
        sanatized_item = item.replace(" ", "_")
        Sanatized_Column_list_name.append(sanatized_item)


    Df_table.columns = Sanatized_Column_list_name


    #standardizing column date format
    #int change to str
    column_date_text_string = Df_table["date"].astype(str)#select date column 
    column_dates_str_unique_length = column_date_text_string.str.len().unique()

    #check if date through the column have uniformed format through length
    assert len(column_dates_str_unique_length) == 1, f"{Table_key}: dates have different lengths {column_dates_str_unique_length}"
    #we work with 3 formats length 4 is year 6 year and month 8 is year month day 
    assert column_dates_str_unique_length[0] in (4, 6, 8), f"{Table_key}: unexpected date length {column_dates_str_unique_length[0]}"

    #by now there should be only 1 formart hence selecting the first item in list
    format_date_length_single = column_dates_str_unique_length[0]

    if format_date_length_single == 4:
        #the first part help panda recognise the text format and then change it to date
        #                                                                         # this last part is an offset that put the date either 
        #                                                                         #at the end of the year
        Df_table["date"] = pd.to_datetime(column_date_text_string, format="%Y") + pd.offsets.YearEnd(0)

    elif format_date_length_single == 6:                                            #or at the end of the month
        Df_table["date"] = pd.to_datetime(column_date_text_string, format="%Y%m") + pd.offsets.MonthEnd(0)

    elif format_date_length_single == 8:
        Df_table["date"] = pd.to_datetime(column_date_text_string, format="%Y%m%d")

    else:
        raise ValueError("Issues with date format length, error this else should never happen")
    #the offset is placed at end of year or month because only then is the rturn known at the end of a given date

    #check that not 2 dates are the same, and the monotonixc increasing check that they either are 
    # (the same date, which in this case in not possible) or go forward in time    
    assert Df_table["date"].is_unique and Df_table["date"].is_monotonic_increasing, f"{Table_key}: dates not unique or not in order"
    print(Table_key, Df_table["date"].iloc[0], Df_table["date"].iloc[-1])