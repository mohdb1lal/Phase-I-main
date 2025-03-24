import os
import datetime

def get_file_details(file_path):
    try:
        stats = os.stat(file_path)
        file_size = stats.st_size
        last_modified_time = datetime.datetime.fromtimestamp(stats.st_mtime)
        return {
            "path": file_path,
            "size (bytes)": file_size,
            "last modified": last_modified_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {"path": file_path, "error": str(e)}

def list_files(directory, exclude_dirs):
    file_details = []
    for root, dirs, files in os.walk(directory):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs]
        
        for name in files:
            file_path = os.path.join(root, name)
            file_details.append(get_file_details(file_path))
        for name in dirs:
            dir_path = os.path.join(root, name)
            file_details.append({
                "path": dir_path,
                "size (bytes)": "N/A",
                "last modified": "N/A",
                "type": "directory"
            })
    return file_details

def save_file_details(file_details, output_file):
    with open(output_file, 'w') as f:
        for detail in file_details:
            f.write(f"Path: {detail['path']}\n")
            f.write(f"Size (bytes): {detail.get('size (bytes)', 'N/A')}\n")
            f.write(f"Last Modified: {detail.get('last modified', 'N/A')}\n")
            f.write(f"Type: {detail.get('type', 'file')}\n")
            f.write("\n")

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))  # Directory where the script is located
    exclude_dirs = [
        os.path.join(script_directory, 'emotions'),  # Add directories to exclude here
    ]
    output_file = 'file_details.txt'
    
    file_details = list_files(script_directory, exclude_dirs)
    save_file_details(file_details, output_file)
    
    print(f"File details have been saved to {output_file}")
