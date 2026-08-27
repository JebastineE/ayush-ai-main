import os
from qdrant_client import QdrantClient

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
qdrant_path = os.path.join(project_dir, "data", "qdrant_store")

print("=== QDRANT DATABASE AUDIT ===")
if os.path.exists(qdrant_path):
    try:
        client = QdrantClient(path=qdrant_path)
        collections = client.get_collections().collections
        print(f"Collections found ({len(collections)}):")
        for col in collections:
            col_name = col.name
            info = client.get_collection(col_name)
            count = client.count(col_name).count
            print(f"  - Collection: '{col_name}'")
            print(f"    Vector count: {count}")
            print(f"    Vector size: {info.config.params.vectors.size}")
            print(f"    Distance metric: {info.config.params.vectors.distance}")
            
            # Retrieve sample point
            res = client.scroll(col_name, limit=1)
            if res[0]:
                sample_point = res[0][0]
                print(f"    Sample point ID: {sample_point.id}")
                print(f"    Sample payload keys: {list(sample_point.payload.keys())}")
                if "source_file" in sample_point.payload:
                    print(f"    Sample source_file: {sample_point.payload['source_file']}")
    except Exception as e:
        print(f"Error querying Qdrant: {e}")
else:
    print(f"Qdrant path not found: {qdrant_path}")
