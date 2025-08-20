from zip_file_utils import (
    unzip_pecha
)
import os
from typing import List

def get_base_text(base_folders: List[str], base_dir: str, pecha_id: str):
    if len(base_folders) >= 2:
        print(f"Multiple base folders found for pecha id: {pecha_id}")
        return None
    else:
        # There should be only one base folder or none
        if base_folders:
            base_folder_path = os.path.join(base_dir, base_folders[0])
            txt_files = [f for f in os.listdir(base_folder_path) if f.endswith('.txt')]
            if not txt_files:
                print(f"No .txt file found in {base_folder_path}")
                return None
            txt_path = os.path.join(base_folder_path, txt_files[0])
        else:
            # No subfolders, look for .txt directly in base_dir
            txt_files = [f for f in os.listdir(base_dir) if f.endswith('.txt')]
            if not txt_files:
                print(f"No .txt file found in {base_dir}")
                return None
            txt_path = os.path.join(base_dir, txt_files[0])

        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()
        return text

async def get_opf_base_text(pecha_id: str):
    print("Unzipping OPF for pecha id: ", pecha_id)
    await unzip_pecha(pecha_id=pecha_id)
    print("OPF unzipped successfully")
    print("Getting base text for pecha id: ", pecha_id)
    base_dir = f"temp_opf/{pecha_id}/base"
    if not os.path.exists(base_dir):
        print(f"Base directory not found for {pecha_id}")
        return None

    base_folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    
    base_text = get_base_text(base_folders=base_folders, base_dir=base_dir, pecha_id=pecha_id)
    if base_text is None:
        print(f"Base text not found for {pecha_id}")
        return None
    print("Base text fetched successfully for pecha id: ", pecha_id)
    print(f"Base text: {base_text}")
    return base_text

