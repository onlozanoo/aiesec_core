import pandas as pd
import logging
from typing import Dict, List

# Basic logging configuration (can be moved or handled centrally)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the known AIESEC program codes/names you expect to find
# Adjust this list based on the actual values present in your data
KNOWN_PROGRAMS: List[str] = ['IGV', 'IGTa', 'IGTe', 'OGV', 'OGTa', 'OGTe']

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the data in the DataFrame.
    """
    print(df.head())
    # Convert the 'Date' column to datetime
    #df['Date'] = pd.to_datetime(df['Date'])

    # Drop the rows where the first column is empty or have the following values:
    # [Closed], Closed, (Closed)
    df = df[~df.iloc[:, 2].isin(['[Closed]', 'Closed', '(Closed)', 'closed', 'CLOSED', '(Closed Expansion)', '-', '.'])]

    # Create the columns names by status process: "Common", "Sign up", "Applicant", "Accepted" "Approved", "Realized", "Completed"
    # and by program: "OGV", "OGTa", "OGTe", "IGTa", "IGTe", "IGV"
    common_cols = ['Country_Name', 'Country_Region', "LC_name"]
    signup_cols = ["Total Signups", "Signups OGV", "Signups OGTa", "Signups OGTe"]
    applicant_cols = ["Total Applicants", "Applicants IGV", "Applicants IGTa", "Applicants IGTe", "Applicants OGV", "Applicants OGTa", "Applicants OGTe"]
    accepted_cols = ["Total Accepted", "Accepted IGV", "Accepted IGTa", "Accepted IGTe", "Accepted OGV", "Accepted OGTa", "Accepted OGTe"]
    approved_cols = ["Total Approved", "Approved IGV", "Approved IGTa", "Approved IGTe", "Approved OGV", "Approved OGTa", "Approved OGTe"]
    realized_cols = ["Total Realized", "Realized IGV", "Realized IGTa", "Realized IGTe", "Realized OGV", "Realized OGTa", "Realized OGTe"]
    finished_cols = ["Total Finished", "Finished IGV", "Finished IGTa", "Finished IGTe", "Finished OGV", "Finished OGTa", "Finished OGTe"]
    completed_cols = ["Total Completed", "Completed IGV", "Completed IGTa", "Completed IGTe", "Completed OGV", "Completed OGTa", "Completed OGTe"]
    
    cols = common_cols + signup_cols + applicant_cols + accepted_cols + approved_cols + realized_cols + finished_cols + completed_cols
    
    # Create the DataFrame with the new columns
    df.columns = cols
    
    # Drop then total columns
    df = df.drop(columns=['Total Signups', 'Total Applicants', 'Total Accepted', 'Total Approved', 'Total Realized', 'Total Finished', 'Total Completed'])
    print(df.head())
    
    # For all the columns but the two first ones, convert to int
    df.iloc[:, 3:] = df.iloc[:, 3:].applymap(int)
    
    # Group by program
    
    # Initialize an empty list to store processed dataframes
    program_dfs = []
    
    # Process each program separately
    for program in KNOWN_PROGRAMS:
        # Select columns relevant for this program
        # For incoming programs (i), set Signups to 0 since they don't have signups
        if program.startswith('I'):
            df[f'Signups {program}'] = 0
            
        program_df = df[['Country_Name', 'Country_Region', 'LC_name',
                        f'Signups {program}',
                        f'Applicants {program}', 
                        f'Accepted {program}',
                        f'Approved {program}',
                        f'Realized {program}',
                        f'Finished {program}',
                        f'Completed {program}']]
        
        # Rename columns to remove program prefix
        program_df.columns = ['Country_Name', 'Country_Region', 'LC_name',
                            'Signups', 'Applicants', 'Accepted',
                            'Approved', 'Realized', 'Finished', 'Completed']
        
        # Add program type column
        program_df['Program'] = program
        
        program_dfs.append(program_df)
    
    # Combine all program dataframes
    df = pd.concat(program_dfs, ignore_index=True)
    
    # Group by country, LC and program to ensure one row per LC per program
    df = df.groupby(['Country_Name', 'Country_Region', 'LC_name', 'Program']).agg({
        'Signups': 'sum',
        'Applicants': 'sum', 
        'Accepted': 'sum',
        'Approved': 'sum',
        'Realized': 'sum',
        'Finished': 'sum',
        'Completed': 'sum'
    }).reset_index()
    
    # Add a timestamp column with the current date but not the time
    df['Date'] = pd.Timestamp.now().strftime('%Y-%m-%d')

    return df