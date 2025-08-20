import httpx
import asyncio
from constant import get_constant
from zip_file_utils import is_zip_present
from pathlib import Path
import aiofiles

OPF_DOWNLOAD_URL = get_constant("OPF_DOWNLOAD_URL")

async def download_opf(pecha_id: str, dir_name: str):
    print("Downloading OPF for pecha id: ", pecha_id)
    async with httpx.AsyncClient(follow_redirects=True, timeout=None) as client:
        async with client.stream("GET", f"{OPF_DOWNLOAD_URL}/{pecha_id}") as r:
            r.raise_for_status()
            Path(dir_name).mkdir(parents=True, exist_ok=True)
            out_path = f"pipeline/{dir_name}/{pecha_id}.zip"
            async with aiofiles.open(out_path, "wb") as f:
                async for chunk in r.aiter_bytes():
                    if chunk:
                        await f.write(chunk)
    if (is_zip_present(pecha_id, dir_name)):
        print(f"Pecha, {pecha_id} already downloaded")
        return True
    else:
        print(f"Pecha, {pecha_id} not downloaded")
        return False


if __name__ == "__main__":
    asyncio.run(download_opf("I182E4445"))