# tests/rag/test_list_groq_models.py
import pytest
from dotenv import load_dotenv


@pytest.mark.integration
def test_list_groq_models():
    load_dotenv(".env.cloud", override=True)
    import os
    from openai import OpenAI

    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )
    models = client.models.list()
    for m in models.data:
        print(m.id)