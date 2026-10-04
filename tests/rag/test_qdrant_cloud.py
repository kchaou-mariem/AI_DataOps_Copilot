# test_qdrant_cloud.py
import pytest
from dotenv import load_dotenv

pytestmark = pytest.mark.integration

load_dotenv(".env.cloud", override=True)

from backend.rag.qdrant_utils import get_qdrant_client

client = get_qdrant_client()
print(client.get_collections())