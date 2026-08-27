import os
import json
import csv

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
data_dir = os.path.join(project_dir, "data")

print("==================================================")
print("             PROJECT DATASET AUDIT")
print("==================================================")

def scan_dir_recursive(path):
    subdirs = []
    files = []
    try:
        for entry in os.scandir(path):
            if entry.is_dir():
                subdirs.append(entry.path)
            elif entry.is_file():
                files.append(entry.path)
    except Exception as e:
        print(f"Error scanning {path}: {e}")
    
    print(f"\nDirectory: {path}")
    print(f"  Subdirectories ({len(subdirs)}): {[os.path.basename(sd) for sd in subdirs]}")
    print(f"  Files ({len(files)}):")
    for f in files:
        size = os.path.getsize(f)
        rel_path = os.path.relpath(f, project_dir)
        print(f"    - {rel_path} ({size:,} bytes)")

scan_dir_recursive(data_dir)
for root, dirs, files_list in os.walk(data_dir):
    for d in dirs:
        scan_dir_recursive(os.path.join(root, d))
