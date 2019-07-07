#Dependencies-------------------------------------------------------------------------------------------------------
import csv
import json
import sys #to accept bash input parameter
#-------------------------------------------------------------------------------------------------------------------
#Static Variables:---------------------------------------------------------------------------------------------------
target_filename = 'top_books_'+sys.argv[1]
location = 'data/'
types_of_encoding = ["utf-8", "cp1252"]
#-------------------------------------------------------------------------------------------------------------------

with open(location+target_filename+'.csv', 'r', encoding='utf-8', errors ='replace') as f:
    reader = csv.DictReader(f)
    sortedtable = sorted(reader, key= lambda d: int(d['id'])) #sort the data based on ID
    writer = csv.DictWriter(open(location+'sorted_'+target_filename+'.csv', 'w',encoding='utf-8', errors ='replace'), reader.fieldnames) #write the .csv file to a new "sorted" .csv file
    writer.writeheader()
    writer.writerows(sortedtable)
    rows = list(sortedtable)

# converts .csv file into json
with open(location+'sorted_'+target_filename+'.json', 'w', encoding = "utf-8") as f:
    json.dump(rows, f, indent = 4, ensure_ascii = False) #use indentation to make it easier on the eyes. Don't force ascii as there are some fancy characters.