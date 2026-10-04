from dotenv import load_dotenv
load_dotenv(".env.cloud", override=True)

from backend.data_pipeline.loader import get_engine, create_tables, seed_sample_data

engine = get_engine()
create_tables(engine)
counts = seed_sample_data(engine)
print("Données insérées dans Supabase :", counts)