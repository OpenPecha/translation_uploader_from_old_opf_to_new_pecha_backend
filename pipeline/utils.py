import os
import asyncio
import json

from class_model import (
    TranslationPayload,
    Translator,
    Annotation
)

from text_metadata_extractor import (
    get_annotation_details
)
from zip_file_utils import (
    unzip_pecha,
    delete_zip_file,
    delete_extracted_folder
)
from OPF_downloader import (
    download_opf
)
from OPF_utils import (
    get_opf_base_text
)
from parse_annotation import (
    scan_opf_directory,
    update_alignment
)
from person_utils import (
    PersonUtils
)

class Utils:

    @staticmethod
    async def handle_non_ai_translation_text(translation_text: dict, translation_text_metadata: dict, translation_text_id: str, original_text_metadata: dict):
        print("--------------------------------")
        print("Handling non-ai translation text -> ", translation_text_id)
        print("--------------------------------")
        
        original_text_language = original_text_metadata['language']
        root_text_id = translation_text['translation_of']
        translation_language = translation_text_metadata['language']

        person_name = None
        for author in translation_text_metadata['author']:
            person_name = translation_text_metadata['author'][author]

        all_persons_data = await PersonUtils.get_all_persons()
        
        is_person_exists = PersonUtils.search_person_by_name(person_name=person_name, language=translation_language, all_persons_data=all_persons_data)

        person_id = None

        if is_person_exists is None:
            print(f"Person {person_name} does not exist in the database. Creating a new person.")
            person_detail = await PersonUtils.create_person(person_name=person_name, language=translation_language)
            person_id = person_detail['_id']
        else:
            person_id = is_person_exists

        if person_id is None:
            print("Failed to create a new person. Person ID is none. Translation id: ", translation_text_id)
            return


        if not await Utils.download_and_preprocess_pecha_root_and_translation(translation_text=translation_text):
            return
        
        translation_base_text = await get_opf_base_text(pecha_id=translation_text_id, dir_name="translation_opf") 


        Utils.write_original_annotation_to_a_json_file(pecha_id=root_text_id, language=original_text_language, dir_name="original_opf")
        Utils.write_translation_annotation_to_a_json_file(pecha_id=translation_text_id, language=translation_language, dir_name="translation_opf")

        translation_payload_model = Utils.generate_translation_model_for_none_ai_translation(
            translation_text_id=translation_text_id, 
            root_text_id=root_text_id, 
            translation_language=translation_language, 
            translation_base_text=translation_base_text, 
            translation_text_metadata=translation_text_metadata,
            person_id=person_id
        )

        Utils.write_json_file(
            path=os.path.join("pipeline/post_payloads", f"{translation_text_id}_payload.json"),
            data=translation_payload_model.dict()
        )

        delete_zip_file(pecha_id=translation_text_id, dir_name="translation_opf")
        delete_extracted_folder(pecha_id=translation_text_id, dir_name="translation_opf")
        

    @staticmethod
    async def handle_ai_translation_text(translation_text: dict, translation_text_metadata: dict, translation_text_id: str, original_text_metadata: dict):
        print("--------------------------------")
        print("Handling ai translation text -> ", translation_text_id)
        print("--------------------------------")

        original_text_language = original_text_metadata['language']
        root_text_id = translation_text['translation_of']

        if not await Utils.download_and_preprocess_pecha_root_and_translation(translation_text=translation_text):
            return
        
        translation_base_text = await get_opf_base_text(pecha_id=translation_text_id, dir_name="translation_opf") 

        translation_language = translation_text_metadata['language']

        Utils.write_original_annotation_to_a_json_file(pecha_id=root_text_id, language=original_text_language, dir_name="original_opf")
        Utils.write_translation_annotation_to_a_json_file(pecha_id=translation_text_id, language=translation_language, dir_name="translation_opf")

        translation_payload_model = Utils.generate_translation_model_for_ai_translation(translation_text_id=translation_text_id, root_text_id=root_text_id, translation_language=translation_language, translation_base_text=translation_base_text, translation_text_metadata=translation_text_metadata)

        Utils.write_json_file(
            path=os.path.join("pipeline/post_payloads", f"{translation_text_id}_payload.json"),
            data=translation_payload_model.dict()
        )

        delete_zip_file(pecha_id=translation_text_id, dir_name="translation_opf")
        # delete_zip_file(pecha_id=root_text_id, dir_name="original_opf")
        delete_extracted_folder(pecha_id=translation_text_id, dir_name="translation_opf")
        # delete_extracted_folder(pecha_id=root_text_id, dir_name="original_opf")

    @staticmethod
    def get_required_annotations(new_annotations: dict):
        required_annotations = []
        if 'segmentation' in new_annotations:
            return []
        try:
            for ann in new_annotations['alignment']:
                temp = {
                    "Span": ann['Span'],
                    "index": ann['index'],
                    "alignment_index": ann['alignment_index']
                }
                required_annotations.append(temp)
            return required_annotations
        except Exception:
            print("ERROR OCCURED -> ", new_annotations)
            return []

    @staticmethod
    def write_annotations_to_json(annotations: list[dict], pecha_id: str, directory: str):
        """
        Writes the list of annotation dictionaries to a JSON file named <pecha_id>.json in the given directory.
        """
        directory = f"pipeline/{directory}"
        print(directory)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"{pecha_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(annotations, f, ensure_ascii=False, indent=2)

    @staticmethod
    def write_original_annotation_to_a_json_file(pecha_id: str, language: str, dir_name: str):
        original_pecha_configs = scan_opf_directory(dir_name=dir_name)
        for config in original_pecha_configs:
            new_annotations = update_alignment(config=config, language=language)
            
            final_annotations = Utils.get_required_annotations(new_annotations=new_annotations)

            Utils.write_annotations_to_json(annotations=final_annotations, pecha_id=pecha_id, directory=dir_name)
    
    @staticmethod
    def write_translation_annotation_to_a_json_file(pecha_id: str, language: str, dir_name: str):
        translation_pecha_configs = scan_opf_directory(dir_name=dir_name)
        for config in translation_pecha_configs:
            new_annotations = update_alignment(config=config, language=language)
            print("NEW ANNOTATIONS -> ", new_annotations)
            final_annotations = Utils.get_required_annotations(new_annotations=new_annotations)
            Utils.write_annotations_to_json(annotations=final_annotations, pecha_id=pecha_id, directory=dir_name)

    @staticmethod
    def generate_translation_model_for_ai_translation(translation_text_id: str, root_text_id: str, translation_language: str, translation_base_text: str, translation_text_metadata) -> TranslationPayload:

        # Read the JSON file from pipeline/original_opf/{the_id}.json
        original_opf_path = os.path.join("pipeline", "original_opf", f"{root_text_id}.json")
        with open(original_opf_path, "r", encoding="utf-8") as f:
            original_annotations = json.load(f)
        translation_opf_path = os.path.join("pipeline", "translation_opf", f"{translation_text_id}.json")
        with open(translation_opf_path, "r", encoding="utf-8") as f:
            translation_annotations = json.load(f)

        response = TranslationPayload(
            language=translation_language,
            content=translation_base_text,
            title=translation_text_metadata['title'][translation_language],
            translator=Translator(
                ai_id="translation_workflow_v1.0.0_claude_3_7_sonnet",
            ),
            original_annotation=[
                Annotation(
                    span=annotation['Span'],
                    index=annotation['index'],
                    alignment_index=annotation['alignment_index']
                )
                for annotation in original_annotations
            ],
            translation_annotation=[
                Annotation(
                    span=annotation['Span'],
                    index=annotation['index'],
                    alignment_index=annotation['alignment_index']
                )
                for annotation in translation_annotations
            ]
        )

        return response

    @staticmethod
    def generate_translation_model_for_none_ai_translation(translation_text_id: str, root_text_id: str, translation_language: str, translation_base_text: str, translation_text_metadata, person_id: str) -> TranslationPayload:

        # Read the JSON file from pipeline/original_opf/{the_id}.json
        original_opf_path = os.path.join("pipeline", "original_opf", f"{root_text_id}.json")
        with open(original_opf_path, "r", encoding="utf-8") as f:
            original_annotations = json.load(f)
        translation_opf_path = os.path.join("pipeline", "translation_opf", f"{translation_text_id}.json")
        with open(translation_opf_path, "r", encoding="utf-8") as f:
            translation_annotations = json.load(f)

        response = TranslationPayload(
            language=translation_language,
            content=translation_base_text,
            title=translation_text_metadata['title'][translation_language],
            translator=Translator(
                person_id=person_id,
            ),
            original_annotation=[
                Annotation(
                    span=annotation['Span'],
                    index=annotation['index'],
                    alignment_index=annotation['alignment_index']
                )
                for annotation in original_annotations
            ],
            translation_annotation=[
                Annotation(
                    span=annotation['Span'],
                    index=annotation['index'],
                    alignment_index=annotation['alignment_index']
                )
                for annotation in translation_annotations
            ]
        )

        return response

    @staticmethod
    def write_json_file(path: str, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    async def download_and_preprocess_pecha_root_and_translation(translation_text: dict) -> bool:
        translation_text_id = translation_text['id']
        root_text_id = translation_text['translation_of']
        

        if (not await download_opf(pecha_id=translation_text_id, dir_name="translation_opf")):
            return False
        if (not await download_opf(pecha_id=root_text_id, dir_name="original_opf")):
            return False
        
        await unzip_pecha(pecha_id=root_text_id, dir_name="original_opf")


        

        translation_annotation_detail = await get_annotation_details(pecha_id=translation_text_id)

        aligned_to = translation_annotation_detail.get('aligned_to', '')
        # Check if the aligned_to value contains 'alignment'
        if 'alignment' not in aligned_to and 'segmentation' not in aligned_to:
            print(f"aligned_to is not an alignment nor segmentation: {aligned_to}. Stopping the process.")
            return False

        await Utils.remove_unwanted_annotation(pecha_id=root_text_id, dir_name="original_opf", keep=translation_annotation_detail['aligned_to'])

        return True

    @staticmethod
    async def remove_unwanted_annotation(pecha_id: str, dir_name: str, keep: str) -> None:
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