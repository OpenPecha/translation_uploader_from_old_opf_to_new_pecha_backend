import asyncio

from utils import Utils

from text_metadata_extractor import (
    get_root_text_id,
    get_related_translation_texts,
    get_text_metadata
)
from typing import List


async def generate_original_and_translation_payloads(related_transation_text: List[dict], root_text_id: str) -> None:
    for translation_text in related_transation_text:
        if translation_text['id'] == root_text_id:
            print("Skipping the root text")
            continue
        
        translation_text_id = translation_text['id']
        translation_text_metadata = await get_text_metadata(text_id=translation_text_id)
        original_text_metadata = await get_text_metadata(text_id=root_text_id)

        is_ai_translation = False

        for _ in translation_text_metadata['author']:
            if translation_text_metadata['author'][_] == 'Openpecha AI' or translation_text_metadata['author'][_] == 'Openpecha':
                is_ai_translation = True

        if is_ai_translation:
            await Utils.handle_ai_translation_text(
                translation_text_metadata=translation_text_metadata, 
                translation_text_id=translation_text_id,
                original_text_metadata=original_text_metadata,
                translation_text=translation_text
            )
        else:
            print()
            print("Non AI -> ", translation_text_id)
            print()
            await Utils.handle_non_ai_translation_text()
        
        
        await asyncio.sleep(2)

        print('Done for ', translation_text_id)
        print("\n\n")


async def generate_translation_payload():

    text_id = input("Enter the pecha id: ")

    root_text_id = await get_root_text_id(text_id=text_id)

    related_transation_text = await get_related_translation_texts(text_id=root_text_id)

    await generate_original_and_translation_payloads(related_transation_text=related_transation_text, root_text_id=root_text_id)

if __name__ == "__main__":
    asyncio.run(generate_translation_payload())

