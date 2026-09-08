from google import genai
from pydantic import BaseModel, Field
import os 
from dotenv import load_dotenv
load_dotenv()

class Transliteration(BaseModel):
    transliterated_texts : list = Field(description="transliterated_texts")

class GeminiAPI:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

    def transliterate(self, texts: list, language: str) -> list:
        interaction = self.client.interactions.create(
            model="gemini-3.5-flash",
            input=f"Transliterate these to {language} : [{", ".join(texts)}]",
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": Transliteration.model_json_schema()
            },
            system_instruction=f"You must provide exactly {len(texts)} items in the response list & preserve order. if any of the item is empty or un-transliterable (for example : ., ..., ---, etc) return the same item ("" in case of "")."

        )

        if interaction.output_text is not None:
            results = Transliteration.model_validate_json(interaction.output_text).transliterated_texts
            return results
        else:
            raise Exception('no response')