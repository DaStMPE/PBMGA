# =============================================================================
# Project Name: PBMGA Python Bone Modulus Grouping and Anisotropy
# File Name: Recalculate_HU.py
# Author: Daniel Strack
# E-Mail: dast@mpe.au.dk
# Description: This code iterates through the provided Abaqus INP file and recalculates the HU based on the provided information in config
# 
# License: MIT License Copyright (c) 2024 Daniel Strack 
# (Refer to the LICENSE file for details)
# 
# Example Usage:
#     import in main:
#     from Recalculate_HU import process_material_data
#     usage in code:
#     df = process_material_data(file_name)
# =============================================================================
import pandas as pd

def process_material_data(file_name):
    with open(file_name, 'r') as file:
        file_contents = file.readlines()

    #------------------------------##Store all Material Data in a Dataframe##------------------------------
    materials = []
    current_material = None
    process_elastic_data = False
    elastic_values = []

    for line in file_contents:
        if line.startswith('*Material,'):
            if current_material is not None:
                if elastic_values:
                    current_material['E'], current_material['Nu'] = elastic_values
                    elastic_values = []  # Reset the elastic_values list
                materials.append(current_material)
            current_material = {'Name': line.split(',')[1].strip()}
            process_elastic_data = False
        elif current_material is not None:
            if process_elastic_data:
                values = line.strip().split(',')
                elastic_values.extend([float(val.strip()) for val in values])
                process_elastic_data = False
            elif line.startswith('*Elastic'):
                process_elastic_data = True

    # Add the last material to the list
    if current_material is not None:
        if elastic_values:
            current_material['E'], current_material['Nu'] = elastic_values
        materials.append(current_material)

    df_materials = pd.DataFrame(materials)
    df_materials.rename(columns={'Name': 'Mat', 'E': 'E_z'}, inplace=True)
    df_materials = df_materials.sort_values(by='E_z', ascending=False)
    df_materials["Mat"] = df_materials["Mat"].str.replace('name=', '')
    
    #------------------------------##Recalculate HU based on Youngs Modulus and recalculate E_z##------------------------------
    HU_series = []
    for E in df_materials["E_z"]:
        # Recalculate Hu Cell specific
        rho_ash_BM = (E / 4730) ** (1 / 1.56)
        rho_app_BM = rho_ash_BM / 0.001
        HU = (rho_app_BM - 47) / 1.122
        HU_series.append(HU)
    HU_data = pd.DataFrame({"HU": HU_series})
    df_materials['HU'] = HU_series

    # Apparent Densitys [Kg/m^3]:
    Rho_app_list = []
    Rho_ash_list = []
    for HU in df_materials["HU"]:
        if HU <= 0:
            Rho_app = 47
        else:
            Rho_app = 47 + 1.122 * HU
        Rho_app_list.append(Rho_app)
        # Ash density is in g/cm^3 to comply with reference calculation method 
        Rho_ash = (0.6 * Rho_app) * 0.001
        Rho_ash_list.append(Rho_ash)

    df_materials_recalculation = pd.DataFrame({"Rho_app [kg/m^3]": Rho_app_list, "Rho_ash [g/cm^3]": Rho_ash_list})
    df_materials_recalculation["Mat"] = df_materials["Mat"]
    df_materials_recalculation["HU"] = HU_series

    # Recalculate youngs modulus (E in MPa)
    E_z_list = []
    for Rho_app, HU in df_materials_recalculation[["Rho_app [kg/m^3]", "HU"]].values:
        if HU > 0.0001:
            E_z = 4730 * ((Rho_app * 0.001) ** 1.56)
        else:
            E_z = 1
        E_z_list.append(E_z)
    df_materials_recalculation["E_z"] = E_z_list
    df_materials_recalculation = df_materials_recalculation.sort_values(by='E_z', ascending=False)

    return df_materials_recalculation