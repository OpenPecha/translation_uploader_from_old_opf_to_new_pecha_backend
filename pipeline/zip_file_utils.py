import os
import zipfile
import asyncio
import shutil


def is_zip_present(pecha_id: str, dir_name: str) -> bool:
    """
    Check if a zip file with the name of the pecha_id exists in the current directory.
    """
    return os.path.isfile(f"pipeline/{dir_name}/{pecha_id}.zip")

async def unzip_pecha(pecha_id: str, dir_name: str):
    zip_path = f"pipeline/{dir_name}/{pecha_id}.zip"
    extract_dir = f"pipeline/{dir_name}/{pecha_id}"

    if os.path.exists(zip_path):
        def _unzip():
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        await asyncio.to_thread(_unzip)
        print(f"Unzipped {zip_path} to {extract_dir}")
    else:
        print(f"Zip file {zip_path} does not exist.")

def delete_zip_file(pecha_id: str, dir_name: str):
    
    zip_path = f"pipeline/{dir_name}/{pecha_id}.zip"
    

    # Delete zip file
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"Deleted {zip_path}")
    else:
        print(f"Zip file {zip_path} does not exist.")

    

def delete_extracted_folder(pecha_id: str, dir_name: str):
    folder_path = f"pipeline/{dir_name}/{pecha_id}"
    # Delete extracted folder
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted folder {folder_path}")
    else:
        print(f"Folder {folder_path} does not exist.")