import asyncio
import json
import os
from OPF_downloader import download_opf
from class_model import (
    TranslationPayload,
    AiDetails,
    Translator
)
from text_metadata_extractor import (
    get_root_text_id,
    get_related_translation_texts,
    get_text_metadata,
    get_annotation_details
)
from OPF_utils import (
    get_opf_base_text
)
from zip_file_utils import (
    delete_zip_file,
    delete_extracted_folder,
    unzip_pecha
)
from typing import List

async def _remove_unwanted_annotation_(pecha_id: str, dir_name: str, keep: str) -> None:
    """
    Remove all annotation files under the layers directory for a given pecha,
    keeping only the file specified by `keep` which is a path relative to the
    layers directory (e.g., "26E4/alignment-FBB4.json").
    """
    layers_dir = f"pipeline/{dir_name}/{pecha_id}/layers"
    if not os.path.exists(layers_dir):
        print(f"Layers directory not found: {layers_dir}")
        return

    keep_path = os.path.normpath(os.path.join(layers_dir, keep))

    if not os.path.isfile(keep_path):
        print(f"Keep file not found: {keep_path}")
        return

    def _remove_files_except_keep():
        for root, _dirs, files in os.walk(layers_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if os.path.normpath(file_path) == keep_path:
                    continue
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                except OSError as e:
                    print(f"Failed to remove {file_path}: {e}")
        # Clean up empty directories while preserving the ancestors of the keep file
        keep_dir = os.path.dirname(keep_path)
        preserved = set()
        current_dir = keep_dir
        while True:
            preserved.add(os.path.normpath(current_dir))
            if os.path.normpath(current_dir) == os.path.normpath(layers_dir):
                break
            current_dir = os.path.dirname(current_dir)
        for root, dirs, files in os.walk(layers_dir, topdown=False):
            norm_root = os.path.normpath(root)
            if norm_root in preserved:
                continue
            if not dirs and not files:
                try:
                    os.rmdir(root)
                    print(f"Removed empty directory: {root}")
                except OSError:
                    pass

    await asyncio.to_thread(_remove_files_except_keep)

async def _download_and_preprocess_pecha_root_and_translation_(translation_text: dict):
    translation_text_id = translation_text['id']
    root_text_id = translation_text['translation_of']
    

    if (not await download_opf(pecha_id=translation_text_id, dir_name="translation_opf")):
        return
    if (not await download_opf(pecha_id=root_text_id, dir_name="original_opf")):
        return
    
    await unzip_pecha(pecha_id=root_text_id, dir_name="original_opf")

    translation_annotation_detail = await get_annotation_details(pecha_id=translation_text_id)

    await _remove_unwanted_annotation_(pecha_id=root_text_id, dir_name="original_opf", keep=translation_annotation_detail['aligned_to'])

def write_json_file(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _generate_translation_model_(translation_language: str, translation_base_text: str, translation_text_metadata) -> TranslationPayload:
    return TranslationPayload(
        language=translation_language,
        content=translation_base_text,
        title=translation_text_metadata['title'][translation_language],
        translator=Translator(
            ai=AiDetails(
                model="GPT-4",
                workflow="Workflow-001",
            )
        ),
        original_annotation="original annotation",
        translation_annotation="translation annotation"
    )
    
async def get_translation_payloads(related_transation_text: List[dict]) -> List[TranslationPayload]:
    translation_payloads: List[TranslationPayload] = []
    for translation_text in related_transation_text:
       
        translation_text_id = translation_text['id']
        translation_text_metadata = await get_text_metadata(text_id=translation_text_id)

        await _download_and_preprocess_pecha_root_and_translation_(translation_text=translation_text)
        
        translation_base_text = await get_opf_base_text(pecha_id=translation_text_id, dir_name="translation_opf") 

        translation_language = translation_text_metadata['language']



        translation_pyaload = _generate_translation_model_(translation_language=translation_language, translation_base_text=translation_base_text, translation_text_metadata=translation_text_metadata)
        
        translation_payloads.append(translation_pyaload)
        break

        delete_zip_file(pecha_id=translation_text_id)
        delete_extracted_folder(pecha_id=translation_text_id)
        await asyncio.sleep(2)

        print('Done for ', translation_text_id)

    return translation_payloads

async def generate_translation_payload():

    text_id = input("Enter the pecha id: ")

    root_text_id = await get_root_text_id(text_id=text_id)

    related_transation_text = await get_related_translation_texts(text_id=root_text_id)

    translation_payloads = await get_translation_payloads(related_transation_text=related_transation_text)

    print("Translation payloads: \n", translation_payloads)

if __name__ == "__main__":
    asyncio.run(generate_translation_payload())

