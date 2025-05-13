from abaqus import *
from abaqusConstants import *
import job
import sys
from config import file_name, directory
import os


# Define the INP file and job name

inp_file_path = file_name  # Change this to your .inp file path
model_name = 'Model-1'  # The name of the model you want to assign
job_name = file_name.rstrip(".inp")  # The job name you want to use
os.chdir(directory)
# Create a new model by importing the INP file
mdb.ModelFromInputFile(name=model_name, inputFileName=inp_file_path)
# Access the model
model = mdb.models[model_name]

# Check if an assembly already exists and delete it
if 'Assembly' in model.rootAssembly.instances.keys():
    del model.rootAssembly.features
    model.rootAssembly = mdb.models[model_name].rootAssembly
    model.rootAssembly.regenerate()

# Get the first part in the model (assuming there is only one part)
part_name = model.parts.keys()[0]
part = model.parts[part_name]

# Create a new assembly and add the part to it
assembly = model.rootAssembly
instance_name = part_name + '-1'
assembly.Instance(name=instance_name, part=part, dependent=ON)


# Create a new job for the imported model
mdb.Job(name=job_name, model=model_name)

# Write out the job file
mdb.jobs[job_name].writeInput()
