import re
import os
from config import file_name, directory


def extract_elset_number(name):
    match = re.search(r'MAT(\d+)', name, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r'Set_(\d+)', name, re.IGNORECASE)
    return match.group(1) if match else None

def extract_material_number(name):
 
    match = re.search(r'material(\d+)', name, re.IGNORECASE)
    return match.group(1) if match else None

def extract_number(name):
    match = re.search(r'(\d+)', name)
    return match.group(1) if match else None

# --- Preprocess the input file ---
def preprocess_inp(input_file, output_file):
    elset_material_dict = {}
    with open(input_file, 'r') as infile, open(output_file, 'w+') as outfile:
        lines = infile.readlines()
        # First pass: record the elset–material number associations from *SOLID SECTION lines
        for line in lines:
            if line.strip().upper().startswith('*SOLID SECTION'):
                # Extract the ELSET and MATERIAL values
                elset_match = re.search(r'ELSET=([^,]+)', line, re.IGNORECASE)
                material_match = re.search(r'MATERIAL=([^,]+)', line, re.IGNORECASE)
                if elset_match and material_match:
                    elset_name = elset_match.group(1).strip()
                    material_name = material_match.group(1).strip()
                    elset_num = extract_elset_number(elset_name)
                    material_num = extract_material_number(material_name)
                    if elset_num is not None and material_num is not None:
                        elset_material_dict[elset_num] = material_num
        # Second pass: write out updated lines
        i = 0
        j = 0
        pre_elset_name = None
        while i < len(lines):
            line = lines[i].strip()
            # Process ELSET lines (those beginning with "*ELSET")
            if line.upper().startswith('*ELSET'):
                j += 1
                elset_match = re.search(r'ELSET=([^,]+)', line, re.IGNORECASE)
                if elset_match:
                    elset_name = elset_match.group(1).strip()
                    elset_num = extract_elset_number(elset_name)
                    if elset_num:
                        if j > 1 and pre_elset_name is not None:
                            pre_mat_num = elset_material_dict.get(pre_elset_name)
                            if pre_mat_num is not None:
                                # Write the corresponding SOLID SECTION for the previous elset
                                outfile.write(f"*SOLID SECTION, ELSET=Set_{pre_elset_name}, MATERIAL=tibia_dis_mat_material{pre_mat_num}\n")
                        new_elset_name = f"Set_{elset_num}"
                        outfile.write(f"*ELSET, ELSET={new_elset_name}, GENERATE\n")
                        pre_elset_name = elset_num
                    else:
                        outfile.write(line + '\n')
                else:
                    outfile.write(line + '\n')
                # Write out the element numbers until the next '*' line
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('*'):
                    outfile.write(lines[i])
                    i += 1
                continue
            if line.upper().startswith('*END PART'):
                if pre_elset_name is not None:
                    pre_mat_num = elset_material_dict.get(pre_elset_name)
                    if pre_mat_num is not None:
                        outfile.write(f"*SOLID SECTION, ELSET=Set_{pre_elset_name}, MATERIAL=tibia_dis_mat_material{pre_mat_num}\n")
                outfile.write(line + '\n')
                i += 1
                continue
            # Process MATERIAL lines (e.g., "*MATERIAL, NAME=tibia_dis_mat_material0")
            if line.upper().startswith('*MATERIAL'):
                material_match = re.search(r'NAME=([^,\n]+)', line, re.IGNORECASE)
                if material_match:
                    material_name = material_match.group(1).strip()
                    material_num = extract_material_number(material_name)
                    if material_num:
                        new_material_name = f"tibia_dis_mat_material{material_num}"
                        outfile.write(f"*MATERIAL, NAME={new_material_name}\n")
                    else:
                        outfile.write(line + '\n')
                else:
                    outfile.write(line + '\n')
                i += 1
                continue
            if line.startswith('** Section') or line.startswith(',') or line.upper().startswith('*SOLID SECTION'):
                i += 1
                continue
            outfile.write(line + '\n')
            i += 1

# --- Remove density lines ---
def remove_density_lines(inp_file_path):
    with open(inp_file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    skip_next_line = False
    for i, line in enumerate(lines):
        if '*DENSITY' in line.upper():
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

# --- Update numbering if a “zero‐index” exists ---
def update_materials_in_line(line):
    pattern = r'tibia_dis_mat_material(\d+)'
    def replacement(match):
        old_number = int(match.group(1))
        new_number = old_number + 1
        return f"tibia_dis_mat_material{new_number}"
    return re.sub(pattern, replacement, line, flags=re.IGNORECASE)

def update_sets_in_line(line):
    pattern = r'Set_(\d+)'
    def replacement(match):
        old_number = int(match.group(1))
        new_number = old_number + 1
        return f"Set_{new_number}"
    return re.sub(pattern, replacement, line)

def process_file(input_filename, output_filename):
    with open(input_filename, 'r') as infile:
        lines = infile.readlines()
    update_materials_flag = any("tibia_dis_mat_material0" in line for line in lines)
    update_sets_flag = any("Set_0" in line for line in lines)
    if update_materials_flag:
        print("Found 'tibia_dis_mat_material0' in the file. Updating materials...")
    else:
        print("No 'tibia_dis_mat_material0' found in the file. Materials remain unchanged.")
    if update_sets_flag:
        print("Found 'Set_0' in the file. Updating sets...")
    else:
        print("No 'Set_0' found in the file. Sets remain unchanged.")
    updated_lines = []
    for line in lines:
        if update_materials_flag:
            line = update_materials_in_line(line)
        if update_sets_flag:
            line = update_sets_in_line(line)
        updated_lines.append(line)
    with open(output_filename, 'w') as outfile:
        outfile.writelines(updated_lines)

# --- Extract Young's modulus values from *MATERIAL blocks ---
def extract_material_moduli(filename):
    materials = {}
    with open(filename, 'r') as f:
        lines = f.readlines()
    current_material = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper().startswith("*MATERIAL"):
            match = re.search(r'NAME\s*=\s*([^\s,]+)', stripped, re.IGNORECASE)
            if match:
                current_material = match.group(1)
            else:
                current_material = None
        elif stripped.upper().startswith("*ELASTIC") and current_material:
            if i + 1 < len(lines):
                modulus_line = lines[i + 1].strip()
                parts = modulus_line.split(',')
                if parts:
                    try:
                        modulus = float(parts[0].strip())
                        materials[current_material] = modulus
                    except ValueError:
                        print(f"Warning: could not parse modulus from line: {modulus_line}")
            current_material = None
    return materials, lines

# --- Build new mappings based on descending modulus ---
def build_mappings(materials):
    sorted_materials = sorted(materials.items(), key=lambda item: item[1], reverse=True)
    new_mat_mapping = {}
    new_set_mapping = {}
    for rank, (old_mat, modulus) in enumerate(sorted_materials, start=1):
        new_mat = f"Mat_{rank}"
        new_mat_mapping[old_mat] = new_mat
        match = re.search(r'material(\d+)', old_mat, re.IGNORECASE)
        if match:
            number = match.group(1)
            old_set = f"Set_{number}"
            new_set = f"Set_{rank}"
            new_set_mapping[old_set] = new_set
    return new_mat_mapping, new_set_mapping, sorted_materials

# --- Replace names throughout the file using the new mappings ---
def replace_materials(line, mapping):
    def mat_repl(match):
        number = match.group(1)
        old_mat = f"tibia_dis_mat_material{number}"
        if old_mat in mapping:
            return mapping[old_mat]
        else:
            return match.group(0)
    return re.sub(r'tibia_dis_mat_material(\d+)', mat_repl, line, flags=re.IGNORECASE)

def replace_sets(line, mapping):
    def set_repl(match):
        number = match.group(1)
        old_set = f"Set_{number}"
        if old_set in mapping:
            return mapping[old_set]
        else:
            return match.group(0)
    return re.sub(r'Set_(\d+)', set_repl, line)
    
def reorder_Set_and_Youngs(input_filename, output_filename):
    materials, lines = extract_material_moduli(input_filename)
    if not materials:
        print("No material moduli found. Exiting without changes.")
        return
    new_mat_mapping, new_set_mapping, sorted_materials = build_mappings(materials)
    print("Renaming materials (and sets) based on descending Young's modulus:")
    for old_mat, modulus in sorted_materials:
        new_name = new_mat_mapping[old_mat]
        print(f"  {old_mat} (modulus = {modulus}) -> {new_name}")
    updated_lines = []
    for line in lines:
        line = replace_materials(line, new_mat_mapping)
        line = replace_sets(line, new_set_mapping)
        updated_lines.append(line)
    with open(output_filename, 'w') as f:
        f.writelines(updated_lines)
    print(f"Processed file written to '{output_filename}'.")

# --- Main processing sequence ---
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
