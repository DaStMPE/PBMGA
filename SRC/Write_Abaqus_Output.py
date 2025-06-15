# =============================================================================
# Project Name: PBMGA Python Bone Modulus Grouping and Anisotropy
# File Name: Write_Abaqus_Output.py
# Author: Daniel Strack
# E-Mail: dast@mpe.au.dk
# Description: This file writes out the new Abaqus file. Based on the options chosen 
#              in confict according Keywords will be written to the file. In case grouping
#              methods have been activated, the element sets will be adapted automatically as well.
# License: MIT License Copyright (c) 2024 Daniel Strack 
# (Refer to the LICENSE file for details)
# 
# Example Usage:
#     import in main:
#     from Write_Abaqus_Output import process_aniso_material_file
#     usage in code:
#     process_aniso_material_file(df_materials_aniso, file_name, Grouping_Method,file_name1,num_clusters,threshold_percentage, Material_Config)
#    
# =============================================================================
import shutil
import pandas as pd
import re
import math
import os

def copy_file(source, destination):
    shutil.copy(source, destination)

def prepare_input_lines():
    return ['**', "*Assembly, name=Assembly", '**', "*Instance, name=PART-1-1, part=PART-1", "*End Instance", '**', "*End Assembly", '**', "** MATERIALS", '**']

def update_material_file(df_materials_aniso, input_file, output_file, grouping_method,  config):
    replacement_lines = ['Replacement Line 1']
    
    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open(output_file, 'w') as file:
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('*Material, name='):
                name = line.split('=')[1]
                matching_row = df_materials_aniso.loc[df_materials_aniso['Mat'] == name]
                if grouping_method == "Percentual_Thresholding":
                    if not matching_row['count_column'].empty:
                        checker = matching_row['count_column'].iloc[0]
                        if checker > 0:
                            write_material_block(file, matching_row, line,  config)
                else:
                    write_material_block(file, matching_row, line, config)
                i += 3  # Skip the original line and the two lines being replaced
            else:
                file.write(line + '\n')
                i += 1

def write_material_block(file, matching_row, line, config):
    file.write(line + '\n')
    for replacement_line in ['Replacement Line 1']:
        if not matching_row.empty:
            # Write Density
            file.write("*Density" + '\n')
            Density = matching_row['Density [ton/mm^3]'].iloc[0]
            input_density = f'{Density} \n'
            file.write(input_density)
            if config.anisotropy_enabled == True:
                # Write elastic parameters
                E_x = matching_row['E_x'].iloc[0]
                E_y = matching_row['E_y'].iloc[0]
                E_z = matching_row['E_z'].iloc[0]
                G_xy = matching_row['G_xy'].iloc[0]
                G_xz = matching_row['G_xz'].iloc[0]
                G_yz = matching_row['G_yz'].iloc[0]
                V_xy = matching_row['V_xy'].iloc[0]
                V_xz = matching_row['V_xz'].iloc[0]
                V_yz = matching_row['V_yz'].iloc[0]
                file.write("*Elastic, type=ENGINEERING CONSTANTS" + '\n')
                input_line = f' {E_x},{E_y},{E_z},{V_xy},{V_xz},{V_yz},{G_xy},{G_xz},\n {G_yz},\n'
                file.write(input_line)

            elif config.anisotropy_enabled == False:
                E_z = matching_row['E_z'].iloc[0]
                V_xy = matching_row['V_xy'].iloc[0]
                file.write("*Elastic" + '\n')
                input_line = f' {E_z}, {V_xy}\n'
                file.write(input_line)

            if config.plasticity_enabled == True:
                # Write plastic parameters
                file.write("*Plastic" + '\n')
                Yield_1 = matching_row["Yield Stress 1"].iloc[0]
                Strain_1 = matching_row["Plastic strain 1"].iloc[0]
                Yield_2 = matching_row["Yield Stress 2"].iloc[0]
                Strain_2 = matching_row["Plastic strain 2"].iloc[0]
                Yield_3 = matching_row["Yield Stress 3"].iloc[0]
                Strain_3 = matching_row["Plastic strain 3"].iloc[0]
                input_plastic = f' {Yield_1},{Strain_1}\n {Yield_2},{Strain_2}\n {Yield_3},{Strain_3}\n'
                file.write(input_plastic)

                # Write potential parameters, only necessary if combined with anisotropy
                if config.anisotropy_enabled == True:
                    file.write("*Potential" + '\n')
                    input_potential = f'{"1."},{"1."},{"1."},{"1."},{"1."},{"1."}\n'
                    file.write(input_potential)
            elif config.plasticity_enabled == False:
                file.write("")
        
def remove_lines_between_markers(input_filename, output_filename, start_marker, end_marker):
    with open(input_filename, 'r') as input_file:
        lines = input_file.readlines()

    with open(output_filename, 'w') as output_file:
        removing = False
        for line in lines:
            if line.strip().startswith(start_marker):
                removing = True
                
                continue
            elif line.strip().startswith(end_marker):
                removing = False
                continue
            if not removing:
                output_file.write(line)

def add_newline_after_16th_comma(input_string):
    chunk_size = 16
    result = ""
    comma_count = 0

    for char in input_string:
        result += char
        if char == ',':
            comma_count += 1
            if comma_count % chunk_size == 0:
                result += '\n'

    return result
            
def insert_newlines(line, max_width=80):
    return '\n'.join(line[i:i + max_width] for i in range(0, len(line), max_width))

def find_and_insert_blocks(input_filename, output_filename, target_marker, new_elset_blocks):
    with open(input_filename, 'r') as input_file:
        lines = input_file.readlines()

    with open(output_filename, 'w') as output_file:
        i = 0
        
        inserted = False  # Flag to track if new_elset_blocks has been inserted
        for line in lines:
            if line.startswith(target_marker):
                if not inserted:
                    for key in new_elset_blocks:
                        for elset_line in new_elset_blocks[key]:
                                if elset_line.startswith(tuple(str(i) for i in range(0, 10))):
                                    line1 = insert_newlines(elset_line)                                    
                                    modified_line = add_newline_after_16th_comma(elset_line)
                                    output_file.write(modified_line)
                                else:
                                    output_file.write(elset_line)
                        inserted = True
            output_file.write(line)

def modify_string(s):
    s = s.replace('.', '_')
    if s.endswith('0'):
        s = s[:-1]
        if s.endswith('_'):
           s = s[:-1]
    return s

def process_aniso_material_file(df_materials_aniso, file_name, grouping_method,file_name1, num_clusters,threshold_percentage,num_equidistant_groups, config):
    output_file = "mapped_aniso_material.inp"
    copy_file(file_name, output_file)
    update_material_file(df_materials_aniso, output_file, output_file, grouping_method,config)
    if grouping_method == "None":
        os.rename('mapped_aniso_material.inp', file_name1 + '_aniso' + '.inp')
    elif grouping_method == "Percentual_Thresholding":
        new_elset_blocks = {}
        
        for index, row in df_materials_aniso.iterrows():
            set_name = row["Set_Name"]
            node_list = row["Numbers"]
            material = row["Mat"]  # Correctly format the material information
            
            new_elset_blocks[set_name] = ["*Elset, elset={}\n".format(set_name)]
            node_lines = (node_list)
            for line in node_lines:
                line = line.replace(' ', '')
                line = line.replace('\t', '')
                new_elset_blocks[set_name].append(line + '\n')
            new_elset_blocks[set_name].append("*Solid Section, elset={}, material={}\n".format(set_name, material))
        target_marker = '*Material, name=Mat_1'
        start_marker = '*Elset, elset=Set_1'
        end_marker = '**'
        remove_lines_between_markers(output_file, output_file, start_marker, end_marker)
        find_and_insert_blocks(output_file, output_file, target_marker, new_elset_blocks)

        with open(output_file, 'r') as file:
            removal_lines = file.readlines()

        max_value_Mat = int(list(new_elset_blocks.keys())[-1].strip("Set_"))
        pattern = r'\*Material, name=Mat_(\d+)'
        filtered_lines = [line for line in removal_lines if not re.search(pattern, line) or int(re.search(pattern, line).group(1)) <= max_value_Mat]

        with open(output_file, 'w') as file:
            file.writelines(filtered_lines)
        threshold = str(threshold_percentage * 100)
        threshold = modify_string(threshold)
        os.rename('mapped_aniso_material.inp', file_name1 + '_' + threshold + 'per' + '.inp')
    elif grouping_method == "Equidistant":
        new_elset_blocks = {}
        
        for index, row in df_materials_aniso.iterrows():
            set_name = row["Set_Name"]
            node_list = row["Numbers"]
            material = row["Mat"]  # Correctly format the material information
            #print(material)
            new_elset_blocks[set_name] = ["*Elset, elset={}\n".format(set_name)]
            node_lines = (node_list)
            for line in node_lines:
                new_elset_blocks[set_name].append(line + '\n')
            new_elset_blocks[set_name].append("*Solid Section, elset={}, material={}\n".format(set_name, material))
        target_marker = '*Material, name=Mat_1'
        start_marker = '*Elset, elset=Set_1'
        end_marker = '**'
        remove_lines_between_markers(output_file, output_file, start_marker, end_marker)
        find_and_insert_blocks(output_file, output_file, target_marker, new_elset_blocks)
        # ---------------------------
        defined_materials = set()
        for index, row in df_materials_aniso.iterrows():
            mat = row["Mat"]
            if isinstance(mat, str) and mat.startswith("Mat_"):
                try:
                    mat_num = int(mat.split("_")[1])
                    defined_materials.add(mat_num)
                except ValueError:
                    # Skip if conversion fails
                    continue
        #----------------------------
        with open(output_file, 'r') as file:
            removal_lines = file.readlines()

        max_value_Mat = int(list(new_elset_blocks.keys())[-1].strip("Set_"))
        pattern = r'\*Material, name=Mat_(\d+)'
        # filtered_lines = [line for line in removal_lines if not re.search(pattern, line) or int(re.search(pattern, line).group(1)) <= max_value_Mat]
        # print(filtered_lines)

        # with open(output_file, 'w') as file:
        #     file.writelines(filtered_lines)
        filtered_lines = []
        for line in removal_lines:
            match = re.search(pattern, line)
            if match:
                mat_num = int(match.group(1))
                # Only keep the line if the material number is defined in your DataFrame.
                if mat_num in defined_materials:
                    filtered_lines.append(line)
            else:
                filtered_lines.append(line)

        with open(output_file, 'w') as file:
            file.writelines(filtered_lines)
        
        os.rename('mapped_aniso_material.inp', file_name1 + '_' + str(num_equidistant_groups) + 'EqiGroups' + '.inp')
    elif grouping_method =="Kmeans_Clustering":
        new_elset_blocks = {}
        df_materials_aniso["Numbers"] = df_materials_aniso["Numbers"].apply(lambda x: [x])
        for index, row in df_materials_aniso.iterrows():
            set_name = row["Set_Name"]
            node_list = row["Numbers"]
            node_list = list(node_list)
            material = row["Mat"]  
            new_elset_blocks[set_name] = ["*Elset, elset={}\n".format(set_name)]
            node_lines = (node_list)
            for line in node_lines:
                line = line.replace(' ', '')
                line = line.replace('\t', '')
                new_elset_blocks[set_name].append(line + '\n')
                
            new_elset_blocks[set_name].append("*Solid Section, elset={}, material={}\n".format(set_name, material))
        target_marker = '*Material, name=Mat_1'
        start_marker = '*Elset, elset=Set_1'
        end_marker = '**'
        remove_lines_between_markers(output_file, output_file, start_marker, end_marker)
        find_and_insert_blocks(output_file, output_file, target_marker,  new_elset_blocks)


        with open(output_file, 'r') as file:
            removal_lines = file.readlines()
        max_value_Mat = int(list(new_elset_blocks.keys())[-1].strip("Set_"))
        pattern = r'\*Material, name=Mat_(\d+)'
        filtered_lines = [line for line in removal_lines if not re.search(pattern, line) or int(re.search(pattern, line).group(1)) <= max_value_Mat]
        with open(output_file, 'w') as file:
            file.writelines(filtered_lines)
        os.rename('mapped_aniso_material.inp', file_name1 + '_' + str(num_clusters) +'C' + '.inp')





    

