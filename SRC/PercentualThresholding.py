# =============================================================================
# Project Name: PBMGA Python Bone Modulus Grouping and Anisotropy
# File Name: PercentualThresholding.py
# Author: Daniel Strack
# E-Mail: dast@mpe.au.dk
# Description: This is the code for one of the grouping methods called Percentual Thresholding.
# 
# License: MIT License Copyright (c) 2024 Daniel Strack 
# (Refer to the LICENSE file for details)
# 
# Example Usage:
#     import in main:
#     from PercentualThresholding import process_data 
#     usage in code:
#     threshold_grouping_df = process_data(file_name, df, threshold_percentage,Material_Config)
#     the input df to the clustering algorithm is the one obtained after running the recalculate HU script
# =============================================================================
import re
import pandas as pd
import numpy as np

def extract_material_name(line):
    # Define the regular expression pattern to match "Mat_x"
    pattern = r"Mat_\d{1,6}"
    
    # Search for the pattern in the line
    match = re.search(pattern, line)
    
    # Extract and return the matched material name, or return None if no match is found
    return match.group() if match else None

def extract_data_from_file(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    data = []
    current_set = None
    current_numbers = []
    current_solid_section = None
    

    for line in lines:
        elset_match = re.match(r'\*Elset,\s*elset=(Set_\d+)',line)
        solid_section_match = re.match(r'\*Solid Section,\s*elset=(Set_\d+),\s*material=(Mat_\d+)',line)
        if elset_match:
            current_set = elset_match.group(1)
            current_numbers = []
            current_solid_section = None
        
        if current_set and not solid_section_match and not elset_match:
            current_numbers.append(line.strip("\n"))
        
        if solid_section_match and current_set:
            current_solid_section = extract_material_name(line)#line.strip("*Solid Section, elset=Set_, material=")
            data.append([current_set, ' '.join(map(str, current_numbers)), current_solid_section])



    df = pd.DataFrame(data, columns=['Elset Information', 'Numbers', 'Solid Section Information'])
    return df

# Function to count numbers separated by commas in a row
def count_numbers_in_row(row):
    return len(row.split(','))

# Generate Groups based on highest Young Modulus
def generate_values(max_value, min_value, threshold_percentage):
    values = []
    current_value = max_value
    while current_value > min_value:
        values.append(current_value)
        current_value *= (1 - threshold_percentage)
    values.append(current_value)  # Append the value close to or zero
    return values

def find_closest_row(row, df):
    distances = np.abs(df['E_z'] - row['E_z'])
    closest_index = distances.idxmin()
    return df.loc[closest_index]

def join_list_elements(lst):
    return [', '.join(lst)]

def process_data(file_name, df_materials_inp, threshold_percentage):
    df = extract_data_from_file(file_name)
    df['count_column'] = df['Numbers'].apply(count_numbers_in_row)
    merged_df = pd.concat([df_materials_inp.set_index('Mat'), df.set_index('Solid Section Information')], axis=1)
    merged_df.drop(columns=['Elset Information'], inplace=True)

    max_value = merged_df["E_z"][0]
    min_values = merged_df["E_z"][(merged_df['E_z'] > 0.001)].sort_values()
    min_value = min_values[0]

    # Use the original generate_values function
    values_list = generate_values(max_value, min_value, threshold_percentage)
    values_list.append(0.001)
    threshold_grouping = {"E_z": values_list}
    threshold_grouping_df = pd.DataFrame(threshold_grouping)

    threshold_grouping_df["count_column"] = 0
    threshold_grouping_df["Numbers"] = [[] for _ in range(len(values_list))]
    squared_errors = []
    error_list = []
    for _, row in merged_df.iterrows():
        closest_row = find_closest_row(row, threshold_grouping_df)
        threshold_grouping_df.at[closest_row.name, 'count_column'] += row['count_column']
        threshold_grouping_df.at[closest_row.name, 'Numbers'].append(row['Numbers'])
        # compute the raw error
        error = threshold_grouping_df.at[closest_row.name, 'E_z'] - row['E_z']
        error_list.append(abs(error))
        # store the squared error
        squared_errors.append(error**2)

    # once the loop is done, compute RMSE
    rmse = np.sqrt(np.mean(squared_errors))
    threshold_grouping_df['Numbers'] = threshold_grouping_df['Numbers'].apply(join_list_elements)
    threshold_grouping_df['PercentualDiff'] = threshold_grouping_df['E_z'].pct_change() * 100
    threshold_grouping_df['PercentualDiff'] = threshold_grouping_df['PercentualDiff'].round(2)
    threshold_grouping_df = threshold_grouping_df[threshold_grouping_df['count_column'] != 0]
    # Calculate summary statistics
    mean_error = sum(error_list) / len(error_list)
    max_error = max(error_list)
    
    # Print the statistics to the console
    #print('Mean Grouping Error', mean_error)
    #print('Max Grouping Error', max_error)s
    threshold_grouping_df2 = threshold_grouping_df.reset_index(drop=True)
    merged_df =merged_df.reset_index(drop=True)
    
    report_df2 = pd.DataFrame()
    report_df2['E_z'] = merged_df['E_z']
    #report_df2['New E_z'] = threshold_grouping_df['E_z']
    report_df2['Grouping_error'] = error_list
    report_df2['Element_ID'] = merged_df['Numbers']
    report_df2['E_z after Grouping'] = threshold_grouping_df2['E_z']
    report_df2['Amount of Elements in Group'] = threshold_grouping_df2['count_column']
    print('Threshold grouping df: \n ', threshold_grouping_df2)
    print(report_df2)
    print(threshold_grouping_df['count_column'])
    csv_name = file_name.rstrip('.inp')+'_' +str(threshold_percentage*100)+'Per' +"_MaterialStatistics.csv"
    report_df2.to_csv(csv_name, index=False)
    # Write the statistics into a text file
    with open(file_name.rstrip('.inp')+'_' +str(threshold_percentage*100)+'Per' + "_grouping_error_stats.txt", "w") as file:
        file.write(f"RMSE: {rmse}\n")
        file.write(f"Mean Grouping Error: {mean_error}\n")
        file.write(f"Max Grouping Error: {max_error}\n")
    return threshold_grouping_df



