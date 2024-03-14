import os
import shutil

def rename_and_move_files(parent_directory):
    for subdir, dirs, files in os.walk(parent_directory):
        if subdir != parent_directory:  # Ignore the parent directory
            txt_files = [f for f in files if f.endswith('.txt')]
            if len(txt_files) == 1:  # Make sure there is exactly one text file
                old_file_path = os.path.join(subdir, txt_files[0])
                new_file_name = os.path.basename(subdir) + '.txt'
                new_file_path = os.path.join(parent_directory, new_file_name)
                
                # Rename and move the file
                shutil.move(old_file_path, new_file_path)
                print(f'Moved {old_file_path} to {new_file_path}')
            else:
                print(f'Skipped {subdir} because it does not contain exactly one .txt file')

parent_directory = r"C:\Users\antho\OneDrive\1 - Thesis Data - Master\1_Tensile Data\Seen\Not Seen\Tensile Data\50kN Load Frame Data\50kNLoadFrame\220207_cbPDMS"  # Replace with your actual parent directory path
rename_and_move_files(parent_directory)

