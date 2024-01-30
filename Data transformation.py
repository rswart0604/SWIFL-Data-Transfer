import pandas as pd
import xarray as xr
# from netCDF4 import Dataset
import os


def read_input_file(input_file):
    # Determine the file format (NetCDF or CSV)
    file_extension = os.path.splitext(input_file)[-1].lower()

    if file_extension == '.nc':
        # Read NetCDF file
        ds = xr.open_dataset(input_file)
        # Convert NetCDF data to DataFrame
        df = ds.to_dataframe()
    elif file_extension == '.csv':
        # Read CSV file
        df = pd.read_csv(input_file)

    return df


def clean_data(input_df):
    # Handling Duplicates
    input_df.drop_duplicates(inplace=True)

    # Remove null values
    input_df.dropna(inplace=True)

    # Text Data Processing for text columns
    for column in input_df.columns:
        if input_df[column].dtype == 'object':
            input_df[column] = input_df[column].str.replace('[^a-zA-Z\s]', '').str.lower()

    return input_df


if __name__ == '__main__':
    input_file = input("Enter the path to the input NetCDF or CSV file: ")
    output_file = input("Enter the path to save the cleaned CSV file: ")

    input_df = read_input_file(input_file)
    cleaned_df = clean_data(input_df)

    # Save cleaned data to CSV
    cleaned_df.to_csv(output_file, index=False)
    print("Cleaned data saved to", output_file)
