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
import subprocess
Simpleware_Abaqus =  'Path to the Simpleware_Preprocessor_Abaqus.py file'  #Regular String
Simpleware_Translate = r'Path to the Simpleware_inp_translation.py file' #Raw String
command = [abaqus_path, 'cae', 'noGUI=' + Simpleware_Abaqus]



def main():
   
   try:
    subprocess.run(command)
    print(f'{Simpleware_Abaqus} executed successfully.')
   except subprocess.CalledProcessError as e:
      print(f'Error while running the script: {e}')
   try:
      subprocess.run(["python",Simpleware_Translate])
      print(f'{Simpleware_Translate} executed successfully.')
   except subprocess.CalledProcessError as e:
      print(f'Error while running the script: {e}')

   
   
   print("Finished")
if __name__ == "__main__":
    main()
    