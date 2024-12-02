Instructions to execute the Interactive Notebook created to obtain the configuration files for D-Eco Impact.

Last update: 13/09/2023
For any questions, contact: jimena.medinarubio@deltares.nl

**Using anaconda to install required modules:**

If you don't have Anaconda installed, download and install it from the official website: 
https://docs.anaconda.com/free/anaconda/install/windows.html

#Open your terminal or Anaconda prompt and follow these instructions:

1. Create new environment

conda create --name my_env  

Replace my_env by the chosen name of your environment 


2. Activate environment

conda activate my_env


3. Install the required environments using Conda

conda install -c condo-forge numpy ipywidgets matplotlib ipython yaml

#Running the python script on Jupyter Notebook
If you have not installed jupyter notebook, do so by activating the created environment and installing it with conda:

conda install -c condo-forge jupyter notebook


1. Open a Jupyter Notebook within your Anaconda environment or activate environment and launch from terminal running this command:

jupyter notebook


2. On one of the cells, run the python script:

%run directory/script.py

Replace directory by the path location of the script and script.py by the actual name. 

Currently, the directory is:

	P:/11209182-edito-internships/6. InteractiveTool/ 

The two available scripts that can be run as interactive notebooks are:
	ProNotebook.py
	BasicNotebook.py 
