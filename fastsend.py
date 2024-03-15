from asyncio.windows_events import NULL
import os
import shutil
import json
import time
from turtle import done, goto

def get_user_input(prompt, default=None):
    # Function to get user input with an optional default value
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    user_input = input(prompt).strip()

    if not user_input and default:
        return default
    else:
        return user_input

def find_completed_parent_folder(incoming_path, completed_path, prefix):
    # Function to find the parent folder in Completed Images based on prefix
    for root, dirs, files in os.walk(incoming_path):
        if prefix in dirs:
            relative_path = os.path.relpath(root, incoming_path)
            return os.path.join(completed_path, relative_path)
    return None

def copy_images_to_completed(source, destination):
    # Function to copy only image files with ".jpg" extension to the destination
    for file in os.listdir(source):
        if file.lower().endswith(".jpg"):
            source_file = os.path.join(source, file)
            destination_file = os.path.join(destination, file)
            shutil.copy2(source_file, destination_file)

def extract_images_and_delete_prefix(source, destination):
    # Function to extract images from folders and delete the prefix folder
    for root, dirs, files in os.walk(source):
        for file in files:
            if file.lower().endswith(".jpg"):
                source_file = os.path.join(root, file)
                destination_file = os.path.join(destination, file)
                shutil.copy2(source_file, destination_file)
    shutil.rmtree(source, ignore_errors=True)

def move_folders_and_copy_images(incoming_path, completed_path, processed_path, done_path):
    # Function to move folders with the same prefix, copy image-type contents to Completed,
    # and move processed folders to _MOVED
    for processed_folder in os.listdir(processed_path):
        processed_folder_path = os.path.join(processed_path, processed_folder)

        if os.path.isdir(processed_folder_path):
            # Extract the first word (e.g., G01, G02, D01) from the processed folder name
            words = processed_folder.split()[:1]  # Extract the first word
            prefix = ' '.join(words)  # Keep the original letter case

            # Find the corresponding parent folder in Completed Images for the prefix
            completed_parent_folder = find_completed_parent_folder(incoming_path, completed_path, prefix)

            if not completed_parent_folder:
                # If the first word is not found, try with the first two words
                words = processed_folder.split()[:2]  # Extract the first two words
                prefix = ' '.join(words)  # Keep the original letter case
                completed_parent_folder = find_completed_parent_folder(incoming_path, completed_path, prefix)

            if completed_parent_folder:
                # Copy only image-type contents of the moved folder to the Completed folder
                copy_images_to_completed(processed_folder_path, completed_parent_folder)

                try:
                    if os.path.exists(done_path):
                        shutil.rmtree(done_path)  # Remove existing destination folder
                        shutil.move(processed_folder_path, done_path)  # Move the processed folder

                    # Optionally, remove the prefix folder from the Completed folder
                    shutil.rmtree(os.path.join(completed_parent_folder, processed_folder), ignore_errors=True)

                    print("Program Executed Successfully...")
                    
                except Exception as e:
                    print(f"An error occurred: {e}")

            else:
                print(f"Warning: {processed_folder} diskip,Folder tidak ada di incoming!.")

def main():
    while True:
        # Check if there is a previous configuration
        if os.path.exists("config.json"):
            use_previous = 'y'
        else:
            use_previous = 'n'

        if os.path.exists("config.json"):
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
        else:
            config = {
                "incoming_path": get_user_input("Enter the path to Incoming Folder"),
                "completed_path": get_user_input("Enter the path to Completed Images"),
                "processed_path": get_user_input("Enter the path to QC On Progress Images"),
                "done_path": get_user_input("Enter the path to QC'ed Images")
            }

            # Save the configuration for future use
            with open("config.json", "w") as config_file:
                json.dump(config, config_file)
        
        move_folders_and_copy_images(config["incoming_path"], config["completed_path"], config["processed_path"], config["done_path"])
        time.sleep(10)

if __name__ == "__main__":
    main()