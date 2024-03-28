from xml.dom import minidom
import os
import pandas as pd
import numpy as np
import shutil
import sys

def meta_data_reader(path_to_data):

    metadatafilename =  os.path.join(path_to_data,'MeasurementData.mlf')
    mydoc = minidom.parse(metadatafilename)
    PATH_TO_FILES = os.path.split(metadatafilename)[0]
    items = mydoc.getElementsByTagName('bts:MeasurementRecord')
    metadatafilename_mrf = os.path.join(path_to_data,'MeasurementDetail.mrf')
    mydoc_mrf = minidom.parse(metadatafilename_mrf)
    PATH_TO_FILES = os.path.split(metadatafilename_mrf)[0]
    items_mrf = mydoc_mrf.getElementsByTagName('bts:MeasurementChannel')

    df_cols = ["ImageName", "column", "row", "time_point", "field_index", "z_slice", "channel", 
               "x_coordinates", "y_coordinates","z_coordinate", "action_index", "action", "Type", "Time", "PixPerMic"]
    rows = []

    for i in range(items.length):

        fullstring = items[i].firstChild.data
        substring = "Error"

        if fullstring.find(substring) == -1:
            if items[i].attributes['bts:Type'].value=='IMG':
                rows.append({

                     "ImageName": os.path.join(PATH_TO_FILES, items[i].firstChild.data), 
                     "column": items[i].attributes['bts:Column'].value, 
                     "row": items[i].attributes['bts:Row'].value, 
                     "time_point": items[i].attributes['bts:TimePoint'].value, 
                     "field_index": items[i].attributes['bts:FieldIndex'].value, 
                     "z_slice": items[i].attributes['bts:ZIndex'].value, 
                     "channel": items[i].attributes['bts:Ch'].value,
                     "x_coordinates": items[i].attributes['bts:X'].value,
                     "y_coordinates": items[i].attributes['bts:Y'].value,
                     "z_coordinate": items[i].attributes['bts:Z'].value,
                     "action_index": items[i].attributes['bts:ActionIndex'].value,
                     "action": items[i].attributes['bts:Action'].value, 
                     "Type": items[i].attributes['bts:Type'].value, 
                     "Time": items[i].attributes['bts:Time'].value,
                     "PixPerMic": items_mrf[0].attributes['bts:HorizontalPixelDimension'].value
                })

    out_df = pd.DataFrame(rows, columns = df_cols)
    
    return out_df

def get_and_save_metadata(input_path, well):

    metadatafilename = os.path.join(input_path, 'MeasurementData.mlf')
    mydoc = minidom.parse(metadatafilename)

    # Create a new XML document for the output
    newdoc = minidom.Document()

    # Create the root element with a namespace prefix
    new_root = newdoc.createElementNS('http://www.yokogawa.co.jp/BTS/BTSSchema/1.0', 'bts:MeasurementData')
    new_root.setAttribute('bts:Version', '1.0')
    new_root.setAttribute('xmlns:bts', 'http://www.yokogawa.co.jp/BTS/BTSSchema/1.0')  # Ensure namespace is set

    # Append the root element to the document
    newdoc.appendChild(new_root)

    items = mydoc.getElementsByTagName('bts:MeasurementRecord')
    df_cols = ["ImageName", "out_ImageName", "column", "row", "time_point", "field_index", "z_slice", "channel", 
                   "x_coordinates", "y_coordinates","z_coordinate", "action_index", "action", "Type", "Time"]
    rows = []
    for i in range(items.length):
        # print(items[i].attributes['bts:ZIndex'].value)
        if items[i].attributes['bts:Column'].value==well.split('_')[0][3:]:
            if items[i].attributes['bts:Row'].value==well.split('_')[1][3:]:
            # Clone the node and append to the new XML document
                new_root.appendChild(items[i].cloneNode(True))
        fullstring = items[i].firstChild.data
        substring = "Error"


        if fullstring.find(substring) == -1:
            if items[i].attributes['bts:Type'].value=='IMG':
                if items[i].attributes['bts:Column'].value==well.split('_')[0][3:]:
                    if items[i].attributes['bts:Row'].value==well.split('_')[1][3:]:

                        rows.append({

                             "ImageName": items[i].firstChild.data, 
                             "column": items[i].attributes['bts:Column'].value, 
                             "row": items[i].attributes['bts:Row'].value, 
                             "time_point": items[i].attributes['bts:TimePoint'].value, 
                             "field_index": items[i].attributes['bts:FieldIndex'].value, 
                             "z_slice": items[i].attributes['bts:ZIndex'].value, 
                             "channel": items[i].attributes['bts:Ch'].value,
                             "x_coordinates": items[i].attributes['bts:X'].value,
                             "y_coordinates": items[i].attributes['bts:Y'].value,
                             "z_coordinate": items[i].attributes['bts:Z'].value,
                             "action_index": items[i].attributes['bts:ActionIndex'].value,
                             "action": items[i].attributes['bts:Action'].value, 
                             "Type": items[i].attributes['bts:Type'].value, 
                             "Time": items[i].attributes['bts:Time'].value,

                        })

    # Save the filtered XML data to a new file
    output_file_path = os.path.join(input_path, well + "_MeasurementData.mlf")
    with open(output_file_path, "w", encoding='utf-8') as f:
        xml_str = newdoc.toprettyxml(indent="\t")
        # Ensure XML declaration is correct
        xml_str = xml_str.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>')
        f.write(xml_str)

    out_df = pd.DataFrame(rows, columns=df_cols)
    
    return out_df

input_path = str(sys.argv[1])
metadata_df = meta_data_reader(input_path)
for col in metadata_df["column"].unique():
    for row in metadata_df["row"].unique():
        sub_df = metadata_df.loc[(metadata_df["column"]==col) & (metadata_df["row"]==row)]
        well = "col" + str(col) + "_row" + str(row)
        if sub_df.empty==False:
            
            get_and_save_metadata(input_path, well)
