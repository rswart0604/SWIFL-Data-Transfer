# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 14:10:43 2023

@author: aparule2
"""

from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import tempfile

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
            file_path = f"{UPLOAD_FOLDER}/{file.filename}"
            file.save(file_path)

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
                return f"Error cleaning data: {str(e)}"

            # Create a cleaned CSV file
            cleaned_file_path = f"{UPLOAD_FOLDER}/cleaned_{file.filename}"
            df.to_csv(cleaned_file_path, index=False)
            
            num_rows = len(df)
            num_columns = len(df.columns)
            columns = ", ".join(df.columns)
            metadata_before_cleaning = f"Before cleaning:<br>Number of rows: {num_rows}<br>Number of columns: {num_columns}<br>Columns: {columns}"

            # Provide a link to download the cleaned file
            return f"File cleaned successfully.<br>{metadata_before_cleaning}<br><a href='/download/{cleaned_file_path}'>Download cleaned file</a>"

@app.route("/download/<path:file_path>")
def download(file_path):
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=False)
