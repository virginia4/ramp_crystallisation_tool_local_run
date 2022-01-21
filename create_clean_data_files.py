import os 
import fnmatch
import glob
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import xlrd   
import pandas as pd
import pyDOE as doe
import numpy as np
import random as rnd
import shutil

# Define paths
dirty_folder_path= r'./MDL_screens_database/db_files'
clean_folder_path = r'./clean_data_files'

# Create empty folder to receive clean files
try:
	shutil.rmtree(clean_folder_path)
except FileNotFoundError:
	pass
os.mkdir(clean_folder_path)

# Create clean files
for file_name in os.listdir(dirty_folder_path):
	# Only clean xls/xlsx files
	if 'xls' in file_name:
		xls = pd.ExcelFile(f'{dirty_folder_path}/{file_name}')
		df = pd.read_excel(xls)
		

		# Manipulate dataframe here if needed


		split_file_name = file_name.split(' ')
		# Name of clean file is going to be just the first word of name of 
		# original file
		new_name = split_file_name[0]
		# If ECO is second word of title it's very likely that this is 
		# a mistake so we add it to name of clean file with dash "-"
		if len(split_file_name) > 1 and split_file_name[1] == 'ECO':
			new_name += f'-{split_file_name[1]}'
		# If "v2" is in name of file we add it to name of clean file
		if 'v2' in file_name:
			new_name += f'_v2' 
		print(new_name, list(df.columns))
		print('\n')
		new_name += f'.xlsx'
		# Create and save to clean file
		new_file_path = f'{clean_folder_path}/{new_name}'
		# new_file = open(new_file_path,'w')
		df.to_excel(new_file_path)
		# new_file.close()





