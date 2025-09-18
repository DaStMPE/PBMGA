# =============================================================================
# Project Name: PBMGA Python Bone Modulus Grouping and Anisotropy
# File Name: Bonemat4_preprocessor.py
# Author: Daniel Strack
# E-Mail: dast@mpe.au.dk
# Description: This script will remove the density lines from the material mapped Bonemat V4 file to comply with PBMGA expected input configuration.
# 
# License: MIT License Copyright (c) 2024 Daniel Strack 
# (Refer to the LICENSE file for details)
# 
# 
# =============================================================================
import os
# from config import *
# from config import Material_Config
directory = r""
input_file = ".inp"
os.chdir(directory)


def remove_density_lines(inp_file_path):
    with open(inp_file_path, 'r') as file:
        lines = file.readlines()

    # List to store modified lines
    modified_lines = []
    skip_next_line = False

    for i, line in enumerate(lines):
        # If the line contains *Density, set flag to skip it and the next line
        if '*Density' in line:
            skip_next_line = True  # Skip the next line
            continue  # Skip this line
        elif skip_next_line:
            skip_next_line = False  # Reset the flag to stop skipping
            continue  # Skip the line immediately following *Density
        else:
            modified_lines.append(line)  # Keep the line if it's not to be skipped

    # Write the modified lines back to the same file (overwrite)
    with open(inp_file_path, 'w') as file:
        file.writelines(modified_lines)

    print(f"Processed file saved to {inp_file_path}")

remove_density_lines(input_file)
