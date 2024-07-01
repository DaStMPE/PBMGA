# =============================================================================
# Project Name: PBMGA Python Bone Modulus Grouping and Anisotropy
# File Name: Calculate_Material_Parameters.py
# Author: Daniel Strack
# E-Mail: dast@mpe.au.dk
# Description: In this file the nonlinear and anisotropic material parameters are calculated and added to the dataframe.
# 
# License: MIT License Copyright (c) 2024 Daniel Strack 
# (Refer to the LICENSE file for details)
# 
# Example Usage:
#     The file must be imported in the main file and called with a df obtained from the Recalculate_HU.py function
#     Additionally the Material_Config class from the config.py file needs to be handed over
#     CalculateMaterial(df,Material_Config)
# 
# =============================================================================
import pandas as pd
import numpy as np
import math

def calculate_HU_series(df_materials_aniso,config):
    HU_series_aniso = []
    for E in df_materials_aniso["E_z"]:
        rho_ash_BM = ((E - config.a_Youngs )/ config.b_Youngs) ** (1 / config.c_Youngs)
        rho_app_BM = (rho_ash_BM - config.a_Ash)/ config.b_Ash
        HU = (rho_app_BM - config.a_Qct) / config.b_Qct
        HU_series_aniso.append(HU)
    df_materials_aniso['HU'] = HU_series_aniso
    return df_materials_aniso

def calculate_densities(df_materials_aniso,config):
    Rho_app_list = []
    Rho_ash_list = []
    for HU in df_materials_aniso["HU"]:
        if HU <= 0:
            Rho_app = config.a_Qct
        else:
            Rho_app = config.a_Qct + config.b_Qct * HU
        Rho_app_list.append(Rho_app)
        Rho_ash = (config.c_Ash * Rho_app) * config.b_Ash
        Rho_ash_list.append(Rho_ash)
    df_materials_aniso['Mat'] = df_materials_aniso.apply(lambda row: f"Mat_{row.name + 1}", axis=1)
    df_materials_aniso['Set_Name'] = df_materials_aniso.apply(lambda row: f"Set_{row.name + 1}", axis=1)
    df_materials_aniso["Rho_app [kg/m^3]"] = Rho_app_list
    df_materials_aniso["Rho_ash [g/cm^3]"] = Rho_ash_list
    Density = df_materials_aniso["Rho_app [kg/m^3]"] * 0.000000000001
    df_materials_aniso["Density [ton/mm^3]"] = Density
    return df_materials_aniso

def calculate_anisotropic_parameters(df_materials_aniso,config):
    E_z_list = []
    E_x_list = []
    E_y_list = []
    G_xy_list = []
    G_xz_list = []
    G_yz_list = []
    for E_z in df_materials_aniso["E_z"]:
        E_x = config.Scale_E_x * E_z
        E_y = config.Scale_E_y * E_z
        E_z_list.append(E_z)
        E_y_list.append(E_y)
        E_x_list.append(E_x)

        G_xy = config.Scale_G_xy * E_z
        G_xz = config.Scale_G_xz * E_z
        G_yz = config.Scale_G_yz * E_z
        G_xy_list.append(G_xy)
        G_xz_list.append(G_xz)
        G_yz_list.append(G_yz)

    df_materials_aniso["E_x"] = E_x_list
    df_materials_aniso["E_y"] = E_y_list
    df_materials_aniso["E_z"] = E_z_list
    df_materials_aniso["G_xy"] = G_xy_list
    df_materials_aniso["G_xz"] = G_xz_list
    df_materials_aniso["G_yz"] = G_yz_list

    V_xy = config.Ass_V_xy
    V_xz = config.Ass_V_xz
    V_yz = config.Ass_V_yz
    df_materials_aniso["V_xy"] = V_xy
    df_materials_aniso["V_xz"] = V_xz
    df_materials_aniso["V_yz"] = V_yz
    return df_materials_aniso

def calculate_stresses_and_strains(df_materials_aniso,config):
    Sigma_min_list = []
    E_p_list = []
    for Rho_ash in df_materials_aniso["Rho_ash [g/cm^3]"]:
        Sigma_min = config.a_Min_Stress * (Rho_ash ** config.b_Min_Stress)
        Sigma_min_list.append(Sigma_min)
        E_p = config.a_Plastic_E * Rho_ash**(config.b_Plastic_E)
        E_p_list.append(E_p)
    df_materials_aniso["Sigma_min"] = Sigma_min_list
    df_materials_aniso["E_p"] = E_p_list

    Epsilon_ab_list = []
    for Rho_ash in df_materials_aniso["Rho_ash [g/cm^3]"].astype(float).values:
        if Rho_ash >= config.threshold_Plastic_Strain:
            Epsilon_ab = config.a_Plastic_Strain + config.b_Plastic_Strain * Rho_ash
        else:
            Epsilon_ab = 0
        Epsilon_ab_list.append(Epsilon_ab)
    df_materials_aniso["Epsilon_ab"] = Epsilon_ab_list

    Sigma_list = []
    for Rho_ash in df_materials_aniso["Rho_ash [g/cm^3]"]:
        if Rho_ash <= config.threshold_Plastic_Stress:
            Sigma = config.a_Plastic_Stress  * (Rho_ash ** config.b_Plastic_Stress)
        else:
            Sigma = config.c_Plastic_Stress * (Rho_ash ** config.d_Plastic_Stress)
        Sigma_list.append(Sigma)
    df_materials_aniso["Sigma"] = Sigma_list

    Epsilon_a_list = []
    for Sigma, E_z in df_materials_aniso[["Sigma", "E_z"]].values:
        Epsilon_a = Sigma/E_z
        Epsilon_a_list.append(Epsilon_a)
    df_materials_aniso["Epsilon_a"] = Epsilon_a_list

    Epsilon_c_list = []
    for Epsilon_a, Sigma, Sigma_min, E_p, Epsilon_ab in df_materials_aniso[["Epsilon_a", "Sigma", "Sigma_min", "E_p", "Epsilon_ab"]].values:
        Epsilon_c = ((Sigma_min - Sigma) / E_p) + (Epsilon_a + Epsilon_ab)
        Epsilon_c_list.append(Epsilon_c)
    df_materials_aniso["Epsilon_c"] = Epsilon_c_list

    return df_materials_aniso

def calculate_yield_stresses_and_strains(df_materials_aniso):
    Yield_1_list = []
    Plastic_strain_1_list = []
    for Epsilon_a, Sigma in df_materials_aniso[["Epsilon_a", "Sigma"]].values:
        Yield_1 = (Epsilon_a + 1) * Sigma 
        Yield_1_list.append(Yield_1)
        Plastic_strain_1_list.append(0)
    df_materials_aniso["Yield Stress 1"] = Yield_1_list
    df_materials_aniso["Plastic strain 1"] = Plastic_strain_1_list

    Yield_2_list = []
    Plastic_strain_2_list = []
    for Epsilon_a, Epsilon_ab, Sigma in df_materials_aniso[["Epsilon_a", "Epsilon_ab", "Sigma"]].values:
        Yield_2 = (Epsilon_a + Epsilon_ab + 1) * Sigma 
        Yield_2_list.append(Yield_2)
        x = (-Epsilon_a + (Epsilon_ab + Epsilon_a)) + 1
        Plastic_strain_2 = math.log(x) if x > 0 else np.nan
        Plastic_strain_2_list.append(Plastic_strain_2)
    df_materials_aniso["Yield Stress 2"] = Yield_2_list
    df_materials_aniso["Plastic strain 2"] = Plastic_strain_2_list

    Yield_3_list = []
    Plastic_strain_3_list = []
    for Epsilon_c, Epsilon_a, Sigma_min in df_materials_aniso[["Epsilon_c", "Epsilon_a", "Sigma_min"]].values:
        Yield_3 = (Epsilon_c + 1) * Sigma_min 
        Yield_3_list.append(Yield_3)
        x = (Epsilon_c - Epsilon_a) + 1
        ln_x = np.log(x) if x > 0 else np.nan
        Plastic_strain_3 = ln_x
        Plastic_strain_3_list.append(Plastic_strain_3)
    df_materials_aniso["Yield Stress 3"] = Yield_3_list
    df_materials_aniso["Plastic strain 3"] = Plastic_strain_3_list

    return df_materials_aniso

def validate_yield_stresses(df_materials_aniso):
    for index, (yield_1, yield_2, yield_3) in df_materials_aniso[["Yield Stress 1","Yield Stress 2", "Yield Stress 3"]].iterrows():
        if yield_1 >= yield_2:
            print("Warning in ", index, " yield 1 > yield 2")
            print(yield_1, yield_2)
        if yield_2 <= yield_3:
            print("Warning in ", index, " yield 2 > yield 3")
            print(yield_2, yield_3)
    for index, (Strain_1, Strain_2, Strain_3) in df_materials_aniso[["Plastic strain 1", "Plastic strain 2", "Plastic strain 3"]].iterrows():
        if Strain_1 >= Strain_2:
            print("Warning in", index, "Strain 1 > Strain 2")
            print(Strain_1, Strain_2)
            df_materials_aniso.at[index, 'Plastic strain 2'] = Strain_2 + 1E-3
        if Strain_2 >= Strain_3:
            print("Warning in ", index, "Strain 2 > Strain 3")
            print(Strain_2, Strain_3)
            df_materials_aniso.at[index, 'Plastic strain 3'] = Strain_3 + 1E-3
    return df_materials_aniso

def CalculateMaterial(df_materials_aniso,config):
    
    df_materials_aniso = calculate_HU_series(df_materials_aniso,config)
    df_materials_aniso = calculate_densities(df_materials_aniso,config)
    df_materials_aniso = calculate_anisotropic_parameters(df_materials_aniso,config)
    df_materials_aniso = calculate_stresses_and_strains(df_materials_aniso,config)
    df_materials_aniso = calculate_yield_stresses_and_strains(df_materials_aniso)
    df_materials_aniso = validate_yield_stresses(df_materials_aniso)
    return df_materials_aniso
