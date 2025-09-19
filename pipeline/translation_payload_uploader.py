import os
import requests
import asyncio
from pathlib import Path

from constant import (
    get_constant
)

OPEN_PECHA_BACKEND_URL = get_constant("GABOR_NEW_ENDPOINT")

async def post_translation_payloads(original_manifestation_id: str, folder_path="post_payloads"):
    """
    For each file in the post_payloads folder, POST its content to the translation endpoint.
    """
    endpoint = f"{OPEN_PECHA_BACKEND_URL}/text/{original_manifestation_id}/translation"
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return

    for filename in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and not filename.startswith('.'):
            try:
                content = await asyncio.to_thread(Path(file_path).read_text, encoding="utf-8")

                print(content)
                response = await asyncio.to_thread(
                    requests.post,
                    endpoint,
                    data=content,
                    headers={"Content-Type": "application/json"}
                )
                print(f"Posted {filename}: Status {response.status_code}")
                if not response.ok:
                    print(f"Response: {response.text}")
            except Exception as e:
                print(f"Error posting {filename}: {e}")

if __name__ == "__main__":
    original_manifestation_id = input("Enter the original manifestation id: ")
    asyncio.run(post_translation_payloads(original_manifestation_id=original_manifestation_id))
