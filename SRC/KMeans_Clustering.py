# =============================================================================
# Project Name: PBMGA Python Bone Modulus Grouping and Anisotropy
# File Name: KMeans_Clustering.py
# Author: Daniel Strack
# E-Mail: dast@mpe.au.dk
# Description: This is the code for one of the grouping methods called Adaptive Clustering based on Kmeans Clustering.
# 
# License: MIT License Copyright (c) 2024 Daniel Strack 
# (Refer to the LICENSE file for details)
# 
# Example Usage:
#     import in main:
#     from KMeans_Clustering import process_clustering
#     usage in code:
#     Kmeans_clustering_df = process_clustering(file_name, df, num_clusters, plot_cluster_on, plot_percentual_diff_on)
#     the input df to the clustering algorithm is the one obtained after running the recalculate HU script
# =============================================================================
import re
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from matplotlib import rcParams

def extract_material_name(line):
    pattern = r"Mat_\d{1,6}"
    match = re.search(pattern, line)
    return match.group() if match else None

def extract_data_from_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data = []
    current_set = None
    current_numbers = []
    current_solid_section = None

    for line in lines:
        elset_match = re.match(r'\*Elset,\s*elset=(Set_\d+)', line)
        solid_section_match = re.match(r'\*Solid Section,\s*elset=(Set_\d+),\s*material=(Mat_\d+)', line)
        if elset_match:
            current_set = elset_match.group(1)
            current_numbers = []
            current_solid_section = None

        if current_set and not solid_section_match and not elset_match:
            current_numbers.append(line.strip("\n"))

        if solid_section_match and current_set:
            current_solid_section = extract_material_name(line)
            data.append([current_set, ' '.join(map(str, current_numbers)), current_solid_section])

    df = pd.DataFrame(data, columns=['Elset Information', 'Numbers', 'Solid Section Information'])
    return df

def count_numbers_in_row(row):
    return len(row.split(','))

def perform_clustering(df_materials_aniso, num_clusters):
    columns_for_clustering = ['count_column', 'E_z']
    X = df_materials_aniso[columns_for_clustering]

    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    df_materials_aniso['New_Grouping'] = kmeans.fit_predict(X)
    return df_materials_aniso

def calculate_cluster_means(df_materials_aniso):
    cluster_means = df_materials_aniso.groupby('New_Grouping')['E_z'].mean()
    cluster_means_df = cluster_means.reset_index()
    cluster_means_df.columns = ['New_Grouping', 'mean_E_z']
    return cluster_means_df

def merge_cluster_means(df_materials_aniso, cluster_means_df):
    result_df = pd.merge(df_materials_aniso, cluster_means_df, on='New_Grouping')
    return result_df

def plot_clustering(df_materials_aniso, plot_cluster_on):
    if plot_cluster_on:
        plt.scatter(df_materials_aniso['E_z'], df_materials_aniso['count_column'], c=df_materials_aniso['New_Grouping'], cmap='rainbow')
        plt.xlabel('E_z')
        plt.ylabel('count_column')
        plt.title('KMeans Clustering Visualization')
        plt.show()

def regroup_data(result_df):
    regrouping_df = result_df[['New_Grouping', 'mean_E_z', 'Numbers', 'count_column']]
    regrouping_df = regrouping_df.groupby('New_Grouping', as_index=False).agg({'mean_E_z': 'mean', 'count_column': 'sum', 'Numbers': list})
    regrouping_df['Numbers'] = regrouping_df['Numbers'].apply(lambda x: ', '.join(x))
    regrouping_df = regrouping_df.rename(columns={'New_Grouping': 'Group', 'mean_E_z': 'E_z'})
    regrouping_df = regrouping_df.sort_values(by='E_z', ascending=False).reset_index(drop=True)
    regrouping_df['Percentual_diff'] = abs(regrouping_df['E_z'].pct_change() * 100)
    return regrouping_df

def plot_percentual_diff(df_materials_aniso, plot_df, plot_percentual_diff_on):
    if plot_percentual_diff_on:
        fig, ax1 = plt.subplots()
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['Arial']
        ax1.scatter(plot_df['E_z'], plot_df['count_column'], c=plot_df['New_Grouping'], cmap='rainbow')
        ax1.set_xlabel('Young Modulus [MPa]', fontsize=20)
        ax1.set_ylabel('Frequency of Modulus in Elements', fontsize=20)
        ax1.tick_params(labelcolor='Black', labelsize=16)
        ax1.legend(loc='upper left')

        ax2 = ax1.twinx()
        ax2.plot(df_materials_aniso["E_z"], df_materials_aniso['Percentual_diff'], color='Black', linewidth=3)
        ax2.set_ylabel('Percentual diff', color='Black', fontsize=20)
        ax2.tick_params(axis='y', labelcolor='Black', labelsize=16)
        ax2.legend(loc='upper right')

        plt.show()

def process_clustering(file_name, df_materials_inp, num_clusters, plot_cluster_on, plot_percentual_diff_on):
    df = extract_data_from_file(file_name)
    df['count_column'] = df['Numbers'].apply(count_numbers_in_row)
    merged_df = pd.concat([df_materials_inp.set_index('Mat'), df.set_index('Solid Section Information')], axis=1).reset_index()
    merged_df.drop(columns=['Elset Information'], inplace=True)

    df_materials_aniso = perform_clustering(merged_df, num_clusters)
    cluster_means_df = calculate_cluster_means(df_materials_aniso)
    result_df = merge_cluster_means(df_materials_aniso, cluster_means_df)

    plot_clustering(df_materials_aniso, plot_cluster_on)

    regrouping_df = regroup_data(result_df)
    plot_percentual_diff(regrouping_df, df_materials_aniso, plot_percentual_diff_on)

    return regrouping_df