import httpx
from constant import get_constant

OPEN_PECHA_BACKEND_URL = get_constant("OPEN_PECHA_BACKEND_URL")

async def get_root_text_id(text_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OPEN_PECHA_BACKEND_URL}/metadata/{text_id}/related?traversal=full_tree&relationships=version")
        response = response.json()
        root_text_id = _get_root_text_id_from_response_(response=response)
        if not root_text_id:
            return None
        return root_text_id

def _get_root_text_id_from_response_(response: dict) -> str | None:
    for item in response:
        if "translation_of" in item or "commentary_of" in item:
            continue
        else:
            return item['id']
    print("ROOT TEXT ID NOT FOUND")
    return None

async def get_related_translations_text(text_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OPEN_PECHA_BACKEND_URL}/metadata/{text_id}/related?traversal=full_tree&relationships=translation")
        response = response.json()
        return response

async def get_text_metadata(text_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OPEN_PECHA_BACKEND_URL}/metadata/{text_id}")
        response = response.json()
        return response