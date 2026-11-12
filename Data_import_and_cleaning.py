import zipfile
import csv
import os
import pathlib
import io
import re
import pandas as pd
import numpy as np
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
                No_Table = 1
                for start_idx, x in enumerate(starts):
                    if len(starts) == 1:
                        df = pd.read_csv(io.StringIO("\n".join(lines[starts[start_idx]:ends[start_idx]])))
                        dataTables[filename] = df
                    else:
                        df = pd.read_csv(io.StringIO("\n".join(lines[starts[start_idx]:ends[start_idx]])))
                        if Title_table_list[start_idx] != "":
                            dataTables[filename+"_"+str(Title_table_list[start_idx])] = df
                        else:
                            dataTables[filename+"_"+"Untitled_table_No_"+str(No_Table)] = df
                    
                    No_Table = No_Table + 1

            else:
                raise ValueError("error in table index starts ends index list mismatch, list not of same length, not possible")
                
            


    else:
        print(filename)
        print("files that are not csv")
        pass


print(len(dataTables))
for key, df in dataTables.items():
    print(key, df.shape)


# cleanning phase.
print("==== cleanning phase =====\n")


for Table_key, Df_table in dataTables.items():
    ###
    ###Sanitizing tables column names
    ###
    #remove spaces from column strings
    Column_name_list = Df_table.columns.tolist()
    Column_name_list[0] = "date"
    Sanatized_Column_list_name = []
    for item in Column_name_list:
        item = item.strip()
        sanatized_item = item.replace(" ", "_")
        Sanatized_Column_list_name.append(sanatized_item)


    Df_table.columns = Sanatized_Column_list_name

    ###
    ###standardizing column date format###
    ###
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
    print("date heck: "+Table_key, Df_table["date"].iloc[0], Df_table["date"].iloc[-1])

    ###
    ###removing -99.99 or -999 which represent missin gvalues and changing them to NaN###
    ###
    # the names: every column except "date"
    number_columns = Df_table.columns[1:]
    # the values under those names
    numbers = Df_table[number_columns]

    codes_before = numbers.isin([-99.99, -999]).sum().sum()
    nan_before = numbers.isna().sum().sum()

    # assigning back changes the table
    Df_table[number_columns] = numbers.replace([-99.99, -999], np.nan)

    nan_after = Df_table[number_columns].isna().sum().sum()
    assert nan_after == codes_before + nan_before, f"{Table_key}: NaN count doesn't match the codes"
    assert not (Df_table[number_columns] <= -99).any().any(), f"{Table_key}: a code is still there"
    print("NaN check: "+Table_key, codes_before, nan_after)



    ###
    ###standardizing values in percentage except firm count and firm size which stay in million of dollars###
    ###
    # put verything out of percentage that is a return ?
    if "returns" in Table_key or Table_key.startswith("F-F_"):
        Df_table[number_columns] = Df_table[number_columns] / 100

        assert not (Df_table[number_columns] <= -1).any().any(), f"{Table_key}: a return of -100% or worse"
        print("Value Check: "+Table_key, Df_table[number_columns].min().min(), Df_table[number_columns].max().max())

    
    print("===\n")


# saving phase phase.
print("==== Saving phase =====\n")

if os.path.isdir("./data/3_cleaned") == False:
    os.mkdir("./data/3_cleaned")
    print("folder created")
else:
    print("folder already exist")
    pass



for Table_key, Df_table in dataTables.items():

    Table_key = Table_key.replace(".csv", "")

    
    Df_table.to_parquet("./data/3_cleaned/" + Table_key + ".parquet", index=False)
    #check the export correspond to the table in memory 
    pd.testing.assert_frame_equal(pd.read_parquet("./data/3_cleaned/" + Table_key + ".parquet"), Df_table)




# dealing with Siccodes49.txt ^^'
print("==== Siccodes49 phase =====\n")

# Siccodes49.txt is not a csv: each industry is a title line "1 Agric  Agriculture"
# followed by its SIC code ranges "0100-0199 Agricultural production - crops",
# and a blank line closes the industry. utf-8 because of an en dash and a curly apostrophe
with open(file_path + "Siccodes49.txt", encoding="utf-8") as f:
    lines = f.read().splitlines()

Siccodes_tables = {}
Siccodes_title_list = []
starts = []
ends = []
switch = 0

# this for loop finds the title line of each industry (start) and the first blank line after it (end)
for i, line in enumerate(lines):
    words = line.split()

    # a title line starts with a number: its first word is only digits ("1", "49")
    # the range lines also start with a number once the spaces are gone,
    # but their first word has a "-" in it ("0100-0199") so isdigit() is False for them
    if len(words) > 0 and words[0].isdigit():
        starts.append(i)
        switch = 1

        # the title is everything after the number, split() then " ".join() turns every run of spaces into 1 space
        title = " ".join(words[1:])
        Siccodes_title_list.append(title)

    elif switch == 1 and line.strip() == "":
        ends.append(i)
        switch = 0
    elif switch == 1 and i == len(lines)-1:
        # the last industry has no blank line after it, the file just ends
        ends.append(len(lines))
        switch = 0
    else:
        pass


# the starts and ends are used to build one table per industry, stored in a dictionary with the title as key
# columns: on a range line only the first space is a column break, everything after it is the description
# (so " - " stays inside the description), and the "-" without spaces in "0100-0199" splits low and high codes
if len(starts) == len(ends):
    for table_idx, start in enumerate(starts):
        rows = []
        for line in lines[start + 1:ends[table_idx]]:
            sic_range, sic_description = line.split(maxsplit=1)
            sic_low, sic_high = sic_range.split("-")
            # same space rule as the titles (2 descriptions have a double space, 1 ends with a tab)
            sic_description = " ".join(sic_description.split())
            rows.append([int(sic_low), int(sic_high), sic_description])

        Siccodes_tables[Siccodes_title_list[table_idx]] = pd.DataFrame(rows, columns=["sic_low", "sic_high", "sic_description"])

else:
    raise ValueError("error in Siccodes starts ends index list mismatch, list not of same length, not possible")


###
###checks
###
# number of ranges in each industry table
Ranges_per_industry = pd.Series({title: len(df) for title, df in Siccodes_tables.items()})
Non_blank_lines = len([line for line in lines if line.strip() != ""])

# two industries with the same title would overwrite each other in the dictionary
assert len(Siccodes_tables) == len(starts), "Siccodes: two industries got the same title"
# every non blank line was used exactly once, either as a title or as a row
assert len(Siccodes_tables) + Ranges_per_industry.sum() == Non_blank_lines, "Siccodes: some lines were not read"
# a range never goes backwards
for title, df in Siccodes_tables.items():
    assert (df["sic_low"] <= df["sic_high"]).all(), f"{title}: a range goes backwards"

# the first word of each title is the short name, they must be the industry columns
# of every 49 industry table, in the same order
Short_names = [title.split()[0] for title in Siccodes_tables]
Tables_checked = 0
for Table_key, Df_table in dataTables.items():
    if Table_key.startswith("49_Industry_Portfolios"):
        assert Df_table.columns[1:].tolist() == Short_names, f"{Table_key}: industry columns don't match the Siccodes short names"
        Tables_checked = Tables_checked + 1

print("Siccodes check:", len(Siccodes_tables), "industries,", Ranges_per_industry.sum(), "SIC ranges")
print("fewest ranges:", Ranges_per_industry.idxmin(), Ranges_per_industry.min())
print("most ranges:", Ranges_per_industry.idxmax(), Ranges_per_industry.max())
print("short names match the industry columns of", Tables_checked, "tables")



###
###saving Siccodes49 as one table
###
# the 49 industry tables are stacked into one table, with the industry number, short name and long name as columns
Siccodes_stack_list = []
for table_idx, title in enumerate(Siccodes_title_list):
    # the industry number is the first word of the title line in the file (starts holds that line's index)
    industry_number = int(lines[starts[table_idx]].split()[0])
    # the short name is the first word of the title, the long name is the rest
    short_name, long_name = title.split(maxsplit=1)

    # copy so the tables in Siccodes_tables stay as they are
    # insert(position, column name, value) adds a column at that position, same value on every row
    Industry_df = Siccodes_tables[title].copy()
    Industry_df.insert(0, "industry_number", industry_number)
    Industry_df.insert(1, "short_name", short_name)
    Industry_df.insert(2, "long_name", long_name)
    Siccodes_stack_list.append(Industry_df)

# ignore_index=True numbers the rows 0 to 597, without it every industry would restart at 0
Siccodes_df = pd.concat(Siccodes_stack_list, ignore_index=True)

# no empty cell after stacking, and the industry numbers read in the file run from 1 to 49 in order
assert not Siccodes_df.isna().any().any(), "Siccodes: empty cells after stacking"
assert Siccodes_df["industry_number"].unique().tolist() == list(range(1, len(Siccodes_tables) + 1)), "Siccodes: industry numbers are not 1 to 49 in order"

Siccodes_df.to_parquet("./data/3_cleaned/Siccodes49.parquet", index=False)
#check the export correspond to the table in memory
pd.testing.assert_frame_equal(pd.read_parquet("./data/3_cleaned/Siccodes49.parquet"), Siccodes_df)
print("Siccodes49 saved:", Siccodes_df.shape)