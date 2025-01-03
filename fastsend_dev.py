import os
import shutil
import json
import time

def log_error(message, processed_path):
    """Function to log errors to a text file in the processed path."""
    log_file_path = os.path.join(processed_path, "error_log.txt")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

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
    # Define error directory inside processed_path
    error_path = os.path.join(processed_path, "_Error")
    
    # Function to move folders with the same prefix, copy image-type contents to Completed,
    # and move processed folders to _MOVED
    for processed_folder in os.listdir(processed_path):
        processed_folder_path = os.path.join(processed_path, processed_folder)
        
        if os.path.isdir(processed_folder_path):
            if processed_folder == "_Error":
                # Skip processing folders named "_Error"
                continue

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
                    # Move the processed folder to another folder
                    shutil.move(processed_folder_path, done_path)

                    # Optionally, remove the prefix folder from the Completed folder
                    shutil.rmtree(os.path.join(completed_parent_folder, processed_folder), ignore_errors=True)

                    print("Program Executed Successfully...")
                except Exception as e:
                    # Log error to text file
                    log_error(f"Error in if block (moving folder): {e}", processed_path)
                    
                    # Create Error directory defined above & move it there
                    os.makedirs(error_path, exist_ok=True)
                    if os.path.exists(processed_folder_path):
                        shutil.move(processed_folder_path, error_path)
                    else:
                        shutil.move(processed_folder_path, error_path)

            else:
                try:
                    # Create Error directory defined above & move it there
                    os.makedirs(error_path, exist_ok=True)
                    if os.path.exists(processed_folder_path):
                        shutil.move(processed_folder_path, error_path)
                    else:
                        shutil.move(processed_folder_path, error_path)

                    print(f"Warning: {processed_folder} skipped, folder not found in incoming!")
                except Exception as e:
                    # Log error to text file
                    log_error(f"Error in else block (moving folder to error directory): {e}", processed_path)

def delete_error_log(processed_path):
    # Deletes error_log.txt if it exists in the processed path.
    log_file_path = os.path.join(processed_path, "error_log.txt")
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
        print(f"{log_file_path} has been deleted.")
    else:
        print("No error log to delete.")

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

        # Delete error log at startup
        delete_error_log(config["processed_path"])

        try:
            move_folders_and_copy_images(config["incoming_path"], config["completed_path"], config["processed_path"], config["done_path"])
        except Exception as e:
            # Log error to text file
            log_error(f"Error in main: {e}", config["processed_path"])
        time.sleep(60)

if __name__ == "__main__":
    main()