import os
from zipfile import ZipFile, ZIP_DEFLATED
from typing import Optional

def export_project(name: str, path: Optional[str] = None):
    project_folder = os.path.join("projects", name)
    if path is None:
        path = "."
    filename = os.path.join(path, f"{name}.zip")
    export_folders = [("PPlayMaps", "."), ("tilesets", [project_folder]), ("maps", [project_folder])]
    with ZipFile(filename, "w", ZIP_DEFLATED) as zip_file:
        for folder, param in export_folders:
            rel = os.path.join(*param)
            location = os.path.join(rel, folder)
            for root, dirs, files in os.walk(location):
                if not "__pycache__" in root:
                    for file in files:
                        dest = os.path.relpath(root, rel)
                        arcname = os.path.join(dest, file)
                        zip_file.write(os.path.join(root, file), arcname)