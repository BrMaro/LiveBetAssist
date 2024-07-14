import os
import pandas as pd

csv_file = 'dryrun.csv'

# Check if the file exists
if os.path.exists(csv_file):
    # Check if the script has read permissions for the file
    if os.access(csv_file, os.R_OK):

        try:
            cols_read = ["Date", "Time", "Home", "Away", "Expected Winner"]
            df = pd.read_csv(csv_file, usecols=cols_read)
            print(df)



        except Exception as e:
            print(f"An error occurred: {e}")
            print(f"An error occurred while reading the file: {e}")
    else:
        print(f"The script does not have read permissions for the file: {csv_file}")
else:
    print(f"The file does not exist: {csv_file}")
