import os
import asyncio
import httpx
import anyio

import logging

# Set up logging
log_file = "upload_log.txt"
logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def upload_payloads(file_path, filename):
    """
    Uploads the given JSON file to the specified endpoint using HTTP POST.
    Sends the file directly as the request body.
    """
    endpoint = "https://api-l25bgmwqoa-uc.a.run.app/v2/text/Zx3byc9l0jVQeT1C/translation"
    headers = {
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        content = await anyio.Path(file_path).read_bytes()
        response = await client.post(endpoint, headers=headers, content=content)
        response.raise_for_status()
        print(f"Uploaded {filename}: Status {response.status_code}")
        return response.json()

if __name__ == "__main__":
    folder_path = "pipeline/post_payloads"

    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
    else:
        count = 0
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith('.json') and not filename.startswith('.'):
                file_path = os.path.join(folder_path, filename)
                try:
                    logging.info(f"Uploading {filename}")
                    print(f"Uploading {filename}:")
                    asyncio.run(upload_payloads(file_path, filename))
                    logging.info(f"Successfully uploaded {filename}")
                except Exception as e:
                    logging.error(f"Error uploading {filename}: {e}")
                    print(f"Error uploading {filename}: {e}")
            count += 1
        print("Upload complete", count)