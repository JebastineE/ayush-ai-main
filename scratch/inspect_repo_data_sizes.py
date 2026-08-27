import os

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
data_dir = os.path.join(project_dir, "data")

def get_dir_info(dir_path):
    if not os.path.exists(dir_path):
        return 0, 0, []
    total_size = 0
    total_files = 0
    files_list = []
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                total_size += sz
                total_files += 1
                rel = os.path.relpath(fp, project_dir)
                files_list.append((rel, sz))
            except Exception:
                pass
    return total_size, total_files, files_list

subdirs = [
    "data/legal_corpus",
    "data/processed",
    "data/qdrant_store",
    "data/tkdl_public",
    "data/traditional_knowledge",
    "data/evaluation",
    "data/legal_corpus_backup_task1",
    "data/processed_backup_task6",
    "data/qdrant_store_backup_task6"
]

print("=== DATA DIRECTORY INSPECTION ===")
for sd in subdirs:
    full_p = os.path.join(project_dir, sd)
    sz, cnt, flist = get_dir_info(full_p)
    print(f"\n[{sd}]")
    print(f"  Total Files: {cnt} | Total Size: {sz / (1024*1024):.2f} MB")
    flist_sorted = sorted(flist, key=lambda x: x[1], reverse=True)
    for rel, fsz in flist_sorted[:5]:
        print(f"    - {rel} ({fsz / 1024:.1f} KB)")

