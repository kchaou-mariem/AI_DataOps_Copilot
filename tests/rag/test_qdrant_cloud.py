import pytest
from dotenv import load_dotenv


@pytest.mark.integration
def test_qdrant_cloud_connection():
	load_dotenv(".env.cloud", override=True)
	from backend.rag.qdrant_utils import get_qdrant_client

	client = get_qdrant_client()
	print(client.get_collections())