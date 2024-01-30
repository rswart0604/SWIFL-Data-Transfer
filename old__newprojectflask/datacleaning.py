# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 14:10:43 2023

@author: aparule2
"""

from flask import Flask, render_template, request, send_file
import pandas as pd
import tempfile
import xarray as xr

app = Flask(__name__)

# Define a temporary directory for storing uploaded files


ACCEPTED_EXTENSIONS = ['nc', 'csv']


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/success", methods=["POST"])
def success():

    upload_folder = tempfile.mkdtemp()

    if request.method == "POST":
        # Check if a file was uploaded
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]

        # If the user does not select a file, the browser will also submit an empty part without filename
        if file.filename == "" or not file:
            return "No selected file"

        # Check file extension to determine its type
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ACCEPTED_EXTENSIONS:
            return "File type not supported"

        # Save the uploaded file to the temporary directory
        file_path = f"{upload_folder}/{file.filename}"
        file.save(file_path)

        if file_extension == "csv":
            # Perform data cleaning using pandas
            try:
                df = pd.read_csv(file_path)
                num_rows = len(df)
                num_columns = len(df.columns)
                df.drop_duplicates(inplace=True)

                # Remove null values
                df.dropna(inplace=True)

                # Text Data Processing for text columns
                for column in df.columns:
                    if df[column].dtype == 'object':
                        df[column] = df[column].str.replace('[^a-zA-Z\s]', '').str.lower()
            except Exception as e:
                return f"Error cleaning CSV data: {str(e)}"

            # Create a cleaned CSV file
            cleaned_file_path = file_path.replace(file.filename, 'cleaned_' + file.filename)
            df.to_csv(cleaned_file_path, index=False)

            new_num_rows = len(df)
            new_num_columns = len(df.columns)
            columns = ", ".join(df.columns)
            metadata_before_cleaning = f"Before cleaning:<br>Number of rows: {num_rows}<br>Number of columns: " + \
                                       f"{num_columns}<br>Columns: {columns}"
            metadata_after_cleaning = f"After cleaning:<br>Number of rows: {new_num_rows}<br>Number of columns: " + \
                                      f"{new_num_columns}<br>"

            # Provide a link to download the cleaned CSV file
            return f"CSV file cleaned successfully.<br>{metadata_before_cleaning}<br><br>{metadata_after_cleaning}" + \
                f"<br><a href='/download/{cleaned_file_path}'>Download cleaned file</a>"

        elif file_extension == "nc":

            vars_changed = []

            # Perform data cleaning using xarray for NetCDF files
            try:
                ds = xr.open_dataset(file_path)
                if ds['T2'].units == 'K':
                    ds['T2'] = ds['T2'] - 273.15
                    ds['T2']['units'] = 'C'
                    vars_changed.append('Kelvin changed to Celsius')
            except Exception as e:
                return f"Error cleaning NetCDF data: {str(e)}"

            # Create a cleaned NetCDF file
            cleaned_file_path = file_path.replace(file.filename, 'cleaned_' + file.filename)
            ds.to_netcdf(cleaned_file_path)

            # Provide a link to download the cleaned NetCDF file
            return f"NetCDF file cleaned successfully.<br>{'br'.join(vars_changed)}<br><a href='/download/{cleaned_file_path}'>Download cleaned file</a>"

        else:
            return "Unsupported file type. Please upload a CSV or NetCDF file."


@app.route("/download/<path:file_path>")
def download(file_path):
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=False)
