import os
import json
import hashlib

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
corpus_dir = os.path.join(project_dir, "data", "legal_corpus")

def sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

f1 = os.path.join(corpus_dir, "DMROA.pdf")
f2 = os.path.join(corpus_dir, "Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954.pdf")

print("DMROA.pdf exists:", os.path.exists(f1))
if os.path.exists(f1):
    print("  hash DMROA:", sha256(f1), "size:", os.path.getsize(f1))

print("Drugs and Magic Remedies... exists:", os.path.exists(f2))
if os.path.exists(f2):
    print("  hash Drugs & Magic:", sha256(f2), "size:", os.path.getsize(f2))
