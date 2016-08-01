from pymongo import MongoClient, GEOSPHERE
import pandas as pd
import os

MONGO_URL = os.environ["mongo_server"] # Dirección mlab para la base de datos

client = MongoClient(MONGO_URL)

db = client.datalab
locations = db.locations

def import_csv(path):
    outDataFrame= pd.DataFrame.from_csv(path, index_col = False)
    return outDataFrame

def return_geopoint(longitude, latitude):
    geopoint = {
        "type" : "Point",
        "coordinates" : [ float(longitude), float(latitude) ]
    }
    return geopoint

def remove_keys(list_keys, myDict):
    for key in list_keys:
        if key in myDict:
            del myDict[key]
    return myDict

def main():
    output_list = []
    print("Loading data")
    locations_dataframe  = import_csv("data/processed/refugios_nayarit.csv")
    print("Transforming to documents")
    for index, row in locations_dataframe.iterrows():
        row_document = dict(row)
        row_document["geopoint"] = return_geopoint(row_document["longitud_limpia"], row_document["latitud_limpia"])
        row_document["_id"] = row_document["no"]
        row_document = remove_keys(["longitud_limpia", "latitud_limpia","no"], row_document)
        output_list.append(row_document)
    print("Ensuring geo index")
    db.locations.create_index([("geopoint", GEOSPHERE)])
    print("Inserting Data")
    try:
        db.locations.insert_many(output_list)
    except:
        print("Documents already exist, Exiting.")

if __name__ == '__main__':
    main()
