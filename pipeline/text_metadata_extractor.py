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
    print(response)
    for item in response:
        if "translation_of" in item or "commentary_of" in item:
            continue
        else:
            return item['id']
    print("ROOT TEXT ID NOT FOUND")
    return None

async def get_related_translation_texts(text_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OPEN_PECHA_BACKEND_URL}/metadata/{text_id}/related?traversal=full_tree&relationships=translation")
        response = response.json()
        return response

async def get_text_metadata(text_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OPEN_PECHA_BACKEND_URL}/metadata/{text_id}")
        response = response.json()
        return response
    
async def _get_pecha_annotation_(pecha_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OPEN_PECHA_BACKEND_URL}/annotation/{pecha_id}")
        response = response.json()
        return response

async def get_annotation_details(pecha_id: str):
    pecha_annotation = await _get_pecha_annotation_(pecha_id=pecha_id)
    pecha_annotataion_id = list(pecha_annotation.keys())[0]
    pecha_annotataion = pecha_annotation[pecha_annotataion_id]
    annotation = {
        "id": pecha_annotataion_id,
        "type": pecha_annotataion['type'],
        "aligned_to": pecha_annotataion['aligned_to']['alignment_id']
    }
    return annotation