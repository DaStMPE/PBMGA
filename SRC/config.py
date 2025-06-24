# =============================================================================
# Project Name: PBMGA Python Bone Modulus Grouping and Anisotropy
# File Name: config.py
# Author: Daniel Strack
# E-Mail: dast@mpe.au.dk
# Description: This is the config file in which the user can state all inputs, especially those used to relate initial Youngs Modulus from HU.
# 
# License: MIT License Copyright (c) 2024 Daniel Strack 
# (Refer to the LICENSE file for details)
# 
# Example Usage:
#     Import file in main e.g.:
#       from config import *
#       from config import Material_Config
#     
# 
# =============================================================================
# Options
# Directory and file name settings
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
directory = dir_path.rstrip('\SRC') + '\Tutorial\MaterialMappedMeshes' #Normal String, Change to your own directory where your data is located
file_name1 = 'L3_Bonemat3_0MPa' #Filename without inp ending
file_name = file_name1 + '.inp' #Normal String
#Grouping Methods: "Percentual_Thresholding", "None", "Kmeans_Clustering, "Equidistant"
Grouping_Method = "Kmeans_Clustering" #Normal String

#Options for Adaptive Clustering / KMeans Clustering for Visualization
plot_cluster_on = False #Boolean
plot_percentual_diff_on = False
# Amount of groups for KMeans
num_clusters = 50  # Adjust as needed

# Percentual Threshold 
threshold = 10
threshold_percentage = threshold / 100

#Options for Equidistant Histogram Visualization
plot_equidistant_histogram_on = False
# Amount of groups for Equidistant grouping
num_equidistant_groups = 10

class Material_Config:
    # Bonemat HU Calculation Parameters
    a_Qct = 47
    b_Qct = 1.122
    a_Ash = 0
    b_Ash = 0.001

    #Additional parameter not used in bonemat to linearly scale RhoApp to derive RhoAsh
    c_Ash = 0.0006

    a_Youngs = 0
    b_Youngs = 4730
    c_Youngs = 1.56

    #Material Characterization
    anisotropy_enabled = True
    plasticity_enabled = True

    #Youngs Modulus anisotropy
    Scale_E_x = 0.333 
    Scale_E_y = 0.333

    #Shear Modulus Scaling
    Scale_G_xy = 0.121 
    Scale_G_xz = 0.157 
    Scale_G_yz = 0.157

    #Poisson Ratio, directly assigned
    Ass_V_xy = 0.381
    Ass_V_xz = 0.104
    Ass_V_yz = 0.104

    #Plasticity Parameters
    #Plastic Strain
    a_Plastic_Strain = -0.00315
    b_Plastic_Strain = 0.0728
    threshold_Plastic_Strain = 0.0433
    #Maximum Principal Stress
    threshold_Plastic_Stress = 0.317
    a_Plastic_Stress = 137
    b_Plastic_Stress = 1.88
    c_Plastic_Stress = 114
    d_Plastic_Stress = 1.72
    #Minimum principal stress
    a_Min_Stress =  65.1
    b_Min_Stress = 1.93
    #Plastic Modulus
    a_Plastic_E = -4000
    b_Plastic_E = 2.05




