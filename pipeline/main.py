import asyncio
import json
from OPF_downloader import download_opf




def write_json_file(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



async def generate_translation_payload():

    pecha_id = input("Enter the pecha id: ")

    if (not await download_opf(pecha_id=pecha_id)):
        return

    


if __name__ == "__main__":
    asyncio.run(generate_translation_payload())