# =============================================================================
# Project Name: PBMGA Python Bone Modulus Grouping and Anisotropy 
# Subproject: Simpleware Scan IP Preprocessor
# File Name: Simpleware_inp_translation.py
# Author: Daniel Strack
# E-Mail: dast@mpe.au.dk
# Description: This is the config file for the Simpleware ScanIp preprocessor
# The output file that should be used for input into PBMGA is ending on translated_reorderd_Set.inp

# License: MIT License Copyright (c) 2024 Daniel Strack 
# (Refer to the LICENSE file for details)
# =============================================================================

import re
import os
from config import file_name, directory


def extract_number(name):
    match = re.search(r'(\d+)', name)
    return match.group(1) if match else None


def ensure_trailing_comma_if_needed(cur_line: str, next_line: str) -> str:
    """
    If cur_line starts with a number (i.e. is part of an element list),
    does NOT already end with a comma, and next_line also starts with a number,
    then add a comma to the end of cur_line.
    Otherwise, leave cur_line untouched.
    """
    # Does this line start (after whitespace) with a digit?
    is_elem_line = bool(re.match(r'^\s*\d', cur_line))
    # Does the next line also start with a digit?
    next_is_elem = bool(re.match(r'^\s*\d', next_line))
    next_is_set = False
    if next_line.startswith('*'):
        next_is_set = True
    if is_elem_line and next_is_elem:
        core = cur_line.rstrip('\n').rstrip()
        if not core.endswith(','):
            return core + ',\n'
    if next_is_set and cur_line.endswith(',') or cur_line.endswith(',\n'):
        return cur_line.rstrip(',\n') + '\n'
    return cur_line


def preprocess_inp(input_file, output_file):
    elsets = {}
    materials = {}

    with open(input_file, 'r') as infile, open(output_file, 'w+') as outfile:
        lines = infile.readlines()
        solid_sections = []
        elset_material_dict = {}

        # First pass: collect mapping of elset to material numbers
        for line in lines:
            if line.startswith('*Solid Section'):
                elset_match = re.search(r'elset=(\w+)', line)
                material_match = re.search(r'material=(\w+)', line)

                if elset_match and material_match:
                    elset_name = elset_match.group(1)
                    material_name = material_match.group(1)

                    elset_num = extract_number(elset_name)
                    material_num = extract_number(material_name)

                    if elset_num is not None and material_num is not None:
                        elset_material_dict[elset_num] = material_num

        i = 0
        j = 0
        pre_elset_name = None

        # Second pass: write transformed lines
        while i < len(lines):
            line = lines[i].strip()
            SKIP_PREFIXES = (
                '** PARTS', 
                '** ASSEMBLY',         # catches '** PARTS', '** ASSEMBLY', and any other **-lines
                '*Part',
                '*End Part',
                '*End Instance',
                '*End Assembly',
                '*Assembly',
                '*Instance',
            )

            # then inside your loop, replace all of those if’s with just:
            
            # Handle *Elset sections
            if line.startswith('*Elset'):
                j += 1
                elset_name = re.search(r'elset=(.*)', line).group(1)
                elset_num = extract_number(elset_name)
                if elset_num:
                    if j > 1 and pre_elset_name:
                        pre_mat_name = elset_material_dict.get(pre_elset_name)
                        outfile.write(f"*Solid Section, elset=Set_{pre_elset_name}, material=Mat_{pre_mat_name}\n")
                    new_elset_name = f'Set_{elset_num}'
                    outfile.write(f"*Elset, elset={new_elset_name}\n")
                    pre_elset_name = elset_num
                else:
                    outfile.write(lines[i])

                # Write element numbers, adding commas only for true continuations
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('*'):
                    nxt = lines[i+1] if i+1 < len(lines) else ''
                    fixed = ensure_trailing_comma_if_needed(lines[i], nxt)
                    outfile.write(fixed)
                    i += 1
                continue

            # Handle end of part to close last section
            if line.startswith('*End Part'):
                if pre_elset_name:
                    pre_mat_name = elset_material_dict.get(pre_elset_name)
                    outfile.write(f"*Solid Section, elset=Set_{pre_elset_name}, material=Mat_{pre_mat_name}\n")

            # Process materials
            if line.startswith('*Material'):
                material_name = re.search(r'name=(.*)', lines[i]).group(1)
                material_num = extract_number(material_name)
                if material_num:
                    new_material_name = f'Mat_{material_num}'
                    materials[material_name] = new_material_name
                    outfile.write(f"*Material, name={new_material_name}\n")
                else:
                    outfile.write(lines[i])
                i += 1
                continue

            # Skip unwanted lines
            if line.startswith('** Section') or line.startswith(',') or line.startswith('*Solid Section') or  line.startswith(SKIP_PREFIXES):
                i += 1
                continue

            # Default: write the line unchanged
            outfile.write(lines[i])
            i += 1

def remove_density_lines(inp_file_path):
    with open(inp_file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    skip_next_line = False

    for line in lines:
        if '*Density' in line:
            skip_next_line = True
            continue
        elif skip_next_line:
            skip_next_line = False
            continue
        else:
            modified_lines.append(line)

    with open(inp_file_path, 'w') as file:
        file.writelines(modified_lines)

    print(f"Processed file saved to {inp_file_path}")

def update_materials_in_line(line):
    pattern = r'Mat_?(\d+)'
    def replacement(match):
        old_number = int(match.group(1))
        new_number = old_number + 1
        return f"Mat_{new_number}"
    return re.sub(pattern, replacement, line)

def update_sets_in_line(line):
    pattern = r'Set_?(\d+)'
    
    def replacement(match):
        old_number = int(match.group(1))
        new_number = old_number + 1
        return f"Set_{new_number}"
    
    return re.sub(pattern, replacement, line)

def process_file(input_filename, output_filename):
    # Read the entire file into a list of lines.
    with open(input_filename, 'r') as infile:
        lines = infile.readlines()

    # Determine if we need to update materials and/or sets.
    update_materials = any("Mat_0" in line for line in lines)
    update_sets = any("Set_0" in line for line in lines)

    if update_materials:
        print("Found 'Mat_0' in the file. Updating materials...")
    else:
        print("No 'Mat_0' found in the file. Materials remain unchanged.")

    if update_sets:
        print("Found 'Set_0' in the file. Updating sets...")
    else:
        print("No 'Set_0' found in the file. Sets remain unchanged.")

    updated_lines = []
    for line in lines:
        # Update materials if required.
        if update_materials:
            line = update_materials_in_line(line)
        # Update sets if required.
        if update_sets:
            line = update_sets_in_line(line)
        updated_lines.append(line)
    
    # Write the (possibly updated) lines to the output file.
    with open(output_filename, 'w') as outfile:
        outfile.writelines(updated_lines)


def extract_material_moduli(filename):

    materials = {}  
    with open(filename, 'r') as f:
        lines = f.readlines()

    current_material = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower().startswith("*material"):
            match = re.search(r'name\s*=\s*([^\s,]+)', stripped, re.IGNORECASE)
            if match:
                mat_name = match.group(1)
                if mat_name.startswith("Mat") and not mat_name.startswith("Mat_"):
                    mat_name = "Mat_" + mat_name[3:]
                current_material = mat_name
            else:
                current_material = None
        elif stripped.lower().startswith("*elastic") and current_material:
            if i + 1 < len(lines):
                modulus_line = lines[i + 1].strip()
                parts = modulus_line.split(',')
                if parts:
                    try:
                        modulus = float(parts[0].strip())
                        materials[current_material] = modulus
                    except ValueError:
                        print(f"Warning: could not parse modulus from line: {modulus_line}")
            # Reset current_material after processing the elastic block.
            current_material = None
    return materials, lines

def build_mappings(materials):

    # Sort materials by modulus descending (highest first)
    sorted_materials = sorted(materials.items(), key=lambda item: item[1], reverse=True)
    new_mat_mapping = {}
    new_set_mapping = {}
    
    for rank, (old_mat, modulus) in enumerate(sorted_materials, start=1):
        new_mat = f"Mat_{rank}"
        new_mat_mapping[old_mat] = new_mat
        # Derive the corresponding set name.
        # (Assume that a material "Mat_x" corresponds to a set named "Set_x".)
        parts = old_mat.split("_")
        if len(parts) >= 2:
            number = parts[1]
            old_set = f"Set_{number}"
            new_set = f"Set_{rank}"
            new_set_mapping[old_set] = new_set
    return new_mat_mapping, new_set_mapping, sorted_materials

def replace_materials(line, mapping):
    def mat_repl(match):
        number = match.group(1)
        canonical = f"Mat_{number}"
        if canonical in mapping:
            return mapping[canonical]
        else:
            return match.group(0)
    return re.sub(r'Mat_?(\d+)', mat_repl, line)

def replace_sets(line, mapping):
    def set_repl(match):
        number = match.group(1)
        canonical = f"Set_{number}"
        if canonical in mapping:
            return mapping[canonical]
        else:
            return match.group(0)
    return re.sub(r'Set_?(\d+)', set_repl, line)

def reorder_Set_and_Youngs(input_filename, output_filename):
    # First, extract the materials and their moduli.
    materials, lines = extract_material_moduli(input_filename)
    if not materials:
        print("No material moduli found. Exiting without changes.")
        return
    new_mat_mapping, new_set_mapping, sorted_materials = build_mappings(materials)
    
    print("Renaming materials (and sets) based on descending Young's modulus:")
    for old_mat, modulus in sorted_materials:
        new_name = new_mat_mapping[old_mat]
        print(f"  {old_mat} (modulus = {modulus}) -> {new_name}")

    # Update every line in the file using the mapping for materials and sets.
    updated_lines = []
    for line in lines:
        line = replace_materials(line, new_mat_mapping)
        line = replace_sets(line, new_set_mapping)
        updated_lines.append(line)
    
    with open(output_filename, 'w') as f:
        f.writelines(updated_lines)
    print(f"Processed file written to '{output_filename}'.")


if __name__ == "__main__":
    os.chdir(directory)
    input_file = file_name
    output_file = input_file.rstrip(".inp") + "translated.inp"
    output_file2 = input_file.rstrip(".inp") + "translated_updated_Set.inp"
    output_file3 = input_file.rstrip(".inp") + "translated_reorderd_Set.inp"
    preprocess_inp(input_file, output_file)
    remove_density_lines(output_file)
    process_file(output_file, output_file2)
    reorder_Set_and_Youngs(output_file2, output_file3)
  
