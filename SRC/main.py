# =============================================================================
# Project Name: PBMGA Python Bone Modulus Grouping and Anisotropy
# File Name: main.py
# Author: Daniel Strack
# E-Mail: dast@mpe.au.dk
# Description: This is the main file which should be run from console.
# 
# License: MIT License Copyright (c) 2024 Daniel Strack 
# (Refer to the LICENSE file for details)
# 
# Example Usage:
#     locate the directory in which this file is saved in a terminal and enter
#     command: python main.py
# 
# =============================================================================

import os
from config import *
from config import Material_Config
from Recalculate_HU import process_material_data
from PercentualThresholding import process_data 
from Calculate_Material_Parameters import CalculateMaterial
from Write_Abaqus_Output import process_aniso_material_file
from KMeans_Clustering import process_clustering
def main():
   os.chdir(directory)
   df = process_material_data(file_name)
   if Grouping_Method == "None":
      df_materials_aniso = CalculateMaterial(df,Material_Config)
      print(df_materials_aniso)
      process_aniso_material_file(df_materials_aniso, file_name, Grouping_Method,file_name1,num_clusters,threshold_percentage, Material_Config)
      print("No reorganizing of material grouping") 
   elif Grouping_Method == "Percentual_Thresholding":
      print("Percentual Threshold Grouping Enabled")
      threshold_grouping_df = process_data(file_name, df, threshold_percentage)
      df_materials_aniso = CalculateMaterial(threshold_grouping_df,Material_Config)
      process_aniso_material_file(df_materials_aniso, file_name, Grouping_Method,file_name1,num_clusters,threshold_percentage, Material_Config)

      print("Grouping Finished")
   elif Grouping_Method == "Kmeans_Clustering":
      Kmeans_clustering_df = process_clustering(file_name, df, num_clusters, plot_cluster_on, plot_percentual_diff_on)
      df_materials_aniso = CalculateMaterial(Kmeans_clustering_df,Material_Config)
      print(df_materials_aniso)
      process_aniso_material_file(df_materials_aniso, file_name, Grouping_Method,file_name1,num_clusters,threshold_percentage,Material_Config)
      print("Kmeans Clustering Enabled") 
   elif Grouping_Method != ("KMeans_Clustering" or "Percentual_Thresholding" or "None"):
      print("Error no/wrong grouping method provided, check spelling in config.py")
   
   
   print("Finished")
if __name__ == "__main__":
    main()
    