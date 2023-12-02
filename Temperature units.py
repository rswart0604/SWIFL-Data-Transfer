# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 21:21:26 2023

@author: aparule2
"""

from flask import Flask, render_template, request, send_file
import pandas as pd
import xarray as xr  # for handling NetCDF files
import tempfile
import os

app = Flask(__name__)

# Define a temporary directory for storing uploaded files
UPLOAD_FOLDER = tempfile.mkdtemp()


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/success", methods=["POST"])
def success():
    if request.method == "POST":
        # Check if a file was uploaded
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]

        # If the user does not select a file, the browser will also submit an empty part without filename
        if file.filename == "":
            return "No selected file"

        if file:
            # Save the uploaded file to the temporary directory
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Check file extension to determine its type
            _, file_extension = os.path.splitext(file.filename)

            if file_extension.lower() == ".csv":
                # Perform data cleaning using pandas 
                try:
                    df = pd.read_csv(file_path)
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
                cleaned_file_path = os.path.join(UPLOAD_FOLDER, f"cleaned_{file.filename}")
                df.to_csv(cleaned_file_path, index=False)

                num_rows = len(df)
                num_columns = len(df.columns)
                columns = ", ".join(df.columns)
                metadata_before_cleaning = f"Before cleaning:<br>Number of rows: {num_rows}<br>Number of columns: {num_columns}<br>Columns: {columns}"

                # Provide a link to download the cleaned CSV file
                return f"CSV file cleaned successfully.<br>{metadata_before_cleaning}<br><a href='/download/{cleaned_file_path}'>Download cleaned file</a>"

            elif file_extension.lower() == ".nc":
                # Perform data cleaning using xarray for NetCDF files
                try:
                    ds = xr.open_dataset(file_path)
                    # Add NetCDF data cleaning steps here if needed
                except Exception as e:
                    return f"Error cleaning NetCDF data: {str(e)}"

                # Create a cleaned NetCDF file
                cleaned_file_path = os.path.join(UPLOAD_FOLDER, f"cleaned_{file.filename}")
                ds.to_netcdf(cleaned_file_path)

                # Provide a link to download the cleaned NetCDF file
                return f"NetCDF file cleaned successfully.<br><a href='/download/{cleaned_file_path}'>Download cleaned file</a>"

            else:
                return "Unsupported file type. Please upload a CSV or NetCDF file."


@app.route("/download/<path:file_path>")
def download(file_path):
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=False)
