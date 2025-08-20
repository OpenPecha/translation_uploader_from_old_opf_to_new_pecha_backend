import asyncio
import json
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
    delete_extracted_folder
)



def write_json_file(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



async def generate_translation_payload():

    text_id = input("Enter the pecha id: ")

    root_text_id = await get_root_text_id(text_id=text_id)

    related_transation_text = await get_related_translation_texts(text_id=root_text_id)

    for translation_text in related_transation_text:
        translation_text_id = translation_text['id']
        translation_text_metadata = await get_text_metadata(text_id=translation_text_id)
        
        if (not await download_opf(pecha_id=translation_text_id)):
            return

        base_text = await get_opf_base_text(pecha_id=translation_text_id)

        translation_language = translation_text_metadata['language']
        translation_pyaload = TranslationPayload(
            language=translation_language,
            content=base_text,
            title=translation_text_metadata['title'][translation_language],
            translator=Translator(
                ai=AiDetails(
                    model="GPT-4",
                    workflow="translation",
                    prompt_id="translate-v1"
                )
            )
        )

        delete_zip_file(pecha_id=translation_text_id)
        delete_extracted_folder(pecha_id=translation_text_id)

        await asyncio.sleep(2)

        return

        print('Done for ', translation_text_id)


if __name__ == "__main__":
    asyncio.run(generate_translation_payload())