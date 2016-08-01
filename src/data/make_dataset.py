# -*- coding: utf-8 -*-
import urllib
import re
import geocoder
import unicodedata


import pandas as pd
from xlrd import open_workbook

def download_dataset(url, path):
    try:
        urllib.request.urlretrieve(url, path)
        success=True
    except:
        success=False
    return success

def convert_excel_dataframe(path):
    book = open_workbook(path,on_demand=True)
    output_list = []
    col_names = ["no", "refugio", "municipio","direccion","uso","servicios","capacidad", "latitud", "longitud","altitud","responsable","telefono" ]
    for name in book.sheet_names():
        output_dict = {}
        sheet = book.sheet_by_name(name)
        for i in range(6,sheet.nrows-1,1):
            output_dict = { col_names[j]: sheet.row(i)[j].value for j in range(0,12,1)}
            output_list.append(output_dict)
    data_df = pd.DataFrame.from_dict(output_list)
    return data_df

def try_address(address):
    g = geocoder.google(address)
    latitude, longitude = g.latlng[0], g.latlng[1]
    return latitude, longitude

def normalize_data(s):
    s = s.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')

def get_geo_code(row):
    address = normalize_data(row["refugio"] + ", "+ row["direccion"]+", " + row["municipio"]+ ", nayarit, mexico")
    try:
        #Intentar con toda la información.
        latitude, longitude = try_address(address)
    except:
        try:
            # Intentar con solo el nombre del refugio.
            address = normalize_data(row["refugio"] + ", " + row["municipio"]+ ", nayarit, mexico")
            latitude, longitude = try_address(address)
        except:
            try:
                # Intentar con la dirección.
                address = normalize_data( row["direccion"]+", " + row["municipio"]+ ", nayarit, mexico")
                latitude, longitude = try_address(address)
            except:
                # Ya de perdis, con la pura ciudad.
                address = normalize_data(row["municipio"]+ ", nayarit, mexico")
                latitude, longitude = try_address(address)
                print("Llené con municipio")
    return(latitude, longitude)

def coords_converter(coordinate_list):
    degrees = float(coordinate_list[0])
    minutes = float(coordinate_list[1])
    seconds = float(coordinate_list[2]+"."+coordinate_list[3])
    decimal_coords = degrees + minutes/60.0 + seconds/3600
    return decimal_coords

def clean_coordinates(row):
    matches_latitude = re.findall('[0-9]+',row["latitud"])
    matches_longitude = re.findall('[0-9]+',row["longitud"])
    if len(matches_longitude)!=4 or len(matches_latitude)!=4:
        new_latitude, new_longitude = get_geo_code(row)
    else:
        new_latitude = coords_converter(matches_latitude)
        new_longitude = coords_converter(matches_longitude)
        if new_longitude < new_latitude:
            switcharoo = new_latitude
            new_latitude = new_longitude
            new_longitude = switcharoo
        new_longitude = - new_longitude  # - por estar en el oeste.
    return new_latitude, new_longitude

def clean_row(row):
    row["latitud_limpia"], row["longitud_limpia"] = clean_coordinates(row)
    return row


def save_histogram(s, path):
    ax = s.hist()  # s is an instance of Series
    fig = ax.get_figure()
    fig.savefig(path)
    fig.clf()

def main():
    data_url = 'http://gob.us13.list-manage.com/track/click?u=3bb8ae2f6ecc6f3954eb8b21b&id=f7bd9e57eb&e=aeba065c1a'
    excel_path = 'data/raw/refugios_nayarit.xlsx'
    csv_path = 'data/processed/refugios_nayarit.csv'
    histogram_path ='reports/figures/'
    print("Downloading Dataset")
    download_dataset(data_url, excel_path)
    print("Converting to excel file")
    data_df = convert_excel_dataframe(excel_path)
    print("Cleaning long/lat file")
    df_cleaned = data_df.apply(clean_row, axis=1)
    print("Saving to csv")
    df_cleaned.to_csv(csv_path, index = False)
    print("Saving histograms to " + histogram_path)
    save_histogram(df_cleaned["longitud_limpia"],histogram_path+"longitud_limpia.pdf")
    save_histogram(df_cleaned["latitud_limpia"],histogram_path+"latitud_limpia.pdf")
    print("Finished Downloading Data and Saving to "+ csv_path)




if __name__ == '__main__':
    main()
