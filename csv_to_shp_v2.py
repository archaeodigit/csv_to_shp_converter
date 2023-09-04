import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import zipfile
import tempfile
import os

def convert_csv_to_shapefile():
    # Open file dialog to select CSV file
    csv_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if csv_file_path:
        # Read the CSV file using pandas
        df = pd.read_csv(csv_file_path)

        # Get the selected shapefile filename from the combobox
        shapefile_filename = shapefile_combobox.get()

        # Get the prefix and photobatch no entered in the text boxes
        prefix = prefix_entry.get()
        photobatch = photobatch_entry.get()

        # Filter the DataFrame to select records starting with the prefix
        filtered_df = df[df['Name'].str.startswith(prefix)]

        if not filtered_df.empty:
            # Create a GeoDataFrame from the filtered DataFrame
            geometry = [Point(x, y, z) for x, y, z in
                        zip(filtered_df['Easting'], filtered_df['Northing'], filtered_df['Elevation'])]
            gdf = gpd.GeoDataFrame(filtered_df, geometry=geometry, crs='EPSG:32635')

            # Set the default filename for the ZIP file
            default_filename = f"{shapefile_filename}_coded_targets_{photobatch}.shp.zip"

            # Open file dialog to save the ZIP file
            zip_file_path = filedialog.asksaveasfilename(defaultextension=".zip",
                                                         filetypes=[("ZIP Files", "*.zip")],
                                                         initialfile=default_filename)

            if zip_file_path:
                # Create a temporary directory to store the shapefile and CSV files
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save the GeoDataFrame as a shapefile in the temporary directory
                    shapefile_dir = os.path.join(temp_dir, "shapefile")
                    os.makedirs(shapefile_dir)
                    shapefile_name = f"{shapefile_filename}_coded_targets_{prefix}_{photobatch}"
                    shapefile_path = os.path.join(shapefile_dir, shapefile_name + ".shp")
                    gdf.to_file(shapefile_path)

                    # Export the filtered DataFrame to a separate CSV file
                    csv_filename = f"{shapefile_filename}_coded_targets_{photobatch}.csv"
                    csv_filepath = os.path.join(temp_dir, csv_filename)
                    filtered_df.to_csv(csv_filepath, index=False)

                    # Create the ZIP file using Python's zipfile module
                    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                        # Add the shapefile files to the ZIP file
                        for file_name in os.listdir(shapefile_dir):
                            file_path = os.path.join(shapefile_dir, file_name)
                            zipf.write(file_path, os.path.basename(file_path))

                        # Add the CSV file to the ZIP file
                        zipf.write(csv_filepath, csv_filename)

                    result_text.insert(tk.END, f"Shapefile saved as {zip_file_path}\n")
                    result_text.insert(tk.END, f"CSV exported as {csv_filepath}\n")
            else:
                result_text.insert(tk.END, "ZIP file save path not selected.\n")
        else:
            result_text.insert(tk.END, "No records found with the specified prefix.\n")
    else:
        result_text.insert(tk.END, "CSV file not selected.\n")


# Create the main window
window = tk.Tk()
window.title("CSV to Shapefile Converter")
window.configure(bg="#F0F0F0")  # Set background color of the window

# Create a frame for the button, labels, and text boxes
frame = tk.Frame(window, padx=10, pady=10, bg="#F0F0F0")  # Set background color of the frame
frame.pack()

# Add a label for the prefix text box
prefix_label = tk.Label(frame, text="Prefix:", bg="#F0F0F0")
prefix_label.pack()

# Add a text box for entering the prefix
prefix_entry = tk.Entry(frame)
prefix_entry.pack()

# Add a label for the photobatch text box
photobatch_label = tk.Label(frame, text="Photobatch No:", bg="#F0F0F0")
photobatch_label.pack()

# Add a text box for entering the photobatch number
photobatch_entry = tk.Entry(frame)
photobatch_entry.pack()

# List of shapefile filename options for the dropdown (combobox)
shapefile_filename_options = ["86_540", "97_541"]

# Create a label for the shapefile filename selection
shapefile_label = tk.Label(frame, text="Shapefile Filename:", bg="#F0F0F0")
shapefile_label.pack()

# Create a combobox for selecting the shapefile filename
shapefile_combobox = ttk.Combobox(frame, values=shapefile_filename_options, state="readonly")
shapefile_combobox.pack()
shapefile_combobox.set(shapefile_filename_options[0])  # Set the default selection

# Add a button to trigger the conversion
convert_button = tk.Button(frame, text="Convert CSV to Shapefile", command=convert_csv_to_shapefile,
                           padx=10, pady=10, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white")
convert_button.pack()

# Add a text box for displaying the result
result_text = tk.Text(frame, height=5, width=40)
result_text.pack()

# Add a footnote label
footnote_label = tk.Label(window, text="Created by Alper Aşınmaz, 2023")
footnote_label.pack(side="bottom", pady=5)

# Start the main event loop
window.mainloop()
