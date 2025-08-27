import httpx
import asyncio
from constant import (
    get_constant
)
from class_model import (
    CreatePersonPayload
)

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
            return response.json()


if __name__ == "__main__":
    persons = asyncio.run(PersonUtils.get_all_persons())
    print(persons)