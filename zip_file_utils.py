import os
import zipfile
import asyncio

def is_zip_present(pecha_id: str) -> bool:
    """
    Check if a zip file with the name of the pecha_id exists in the current directory.
    """
    return os.path.isfile(f"{pecha_id}.zip")

async def unzip_pecha(pecha_id: str):
    zip_path = f"{pecha_id}.zip"
    extract_dir = pecha_id

    if os.path.exists(zip_path):
        def _unzip():
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        await asyncio.to_thread(_unzip)
        print(f"Unzipped {zip_path} to {extract_dir}")
    else:
        print(f"Zip file {zip_path} does not exist.")

def delete_zip_file(pecha_id: str):
    zip_path = f"{pecha_id}.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"Deleted {zip_path}")
    else:
        print(f"Zip file {zip_path} does not exist.")