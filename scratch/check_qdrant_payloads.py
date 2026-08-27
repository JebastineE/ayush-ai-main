import os
from qdrant_client import QdrantClient

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
qdrant_path = os.path.join(project_dir, "data", "qdrant_store")

client = QdrantClient(path=qdrant_path)
res = client.scroll("legal_docs", limit=5)

points = res[0]
print(f"Retrieved {len(points)} points from legal_docs:")
for p in points:
    print(f"Point ID: {p.id}")
    print("  Payload keys:", list(p.payload.keys()))
    print("  Jurisdiction in payload:", p.payload.get("jurisdiction"))
    print("  Source file:", p.payload.get("source_file"))
