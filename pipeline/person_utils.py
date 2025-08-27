import httpx
import asyncio
from constant import (
    get_constant
)
from class_model import (
    CreatePersonPayload
)
from typing import Optional

NEW_OPEN_PECHA_BACKEND_URL = get_constant("GABOR_NEW_ENDPOINT")

class PersonUtils:

    @staticmethod
    async def get_all_persons():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{NEW_OPEN_PECHA_BACKEND_URL}/persons", timeout=None)
            response.raise_for_status()
            return response.json()
        
    @staticmethod
    async def create_person(person_name: str, language: str) -> dict:
        payload = CreatePersonPayload(
            name={
                language: person_name
            }
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{NEW_OPEN_PECHA_BACKEND_URL}/persons", json=payload.model_dump(), timeout=None)
            response.raise_for_status()
            response = response.json()
            print("Person created successfully, ", response)
            return response
        
    @staticmethod
    def search_person_by_name(person_name: str, language: str, all_persons_data: dict) -> Optional[bool]:
        for person in all_persons_data:
            if person['name'] is not None:
                if (language in person['name'] and person['name'][language] == person_name):
                    return person['id']
            if person['alt_names'] is not None:
                if (language in person['alt_names'] and person['alt_names'][language] == person_name):
                    return person['id']
        return None


if __name__ == "__main__":
    person_name = "Tenzin 1"
    language = "en"
    result = asyncio.run(PersonUtils.create_person(person_name=person_name, language=language))
    print("Search result:", result)
    print("Search result:", result['_id'])

'''
jKxZYPqsPrF6f3wD
RPfFQ67F85phX-BY
aVRZ_mewidp7lVEN
'''
