import pymupdf4llm
from pathlib import Path

files = list(Path('data/legal_corpus').glob('*.pdf'))
print(f'Found {len(files)} PDFs: {[f.name for f in files[:3]]}')

if not files:
    print("No PDFs found!")
    exit(1)

p = files[0]
print(f"\nInspecting: {p.name}")
pages = pymupdf4llm.to_markdown(str(p), page_chunks=True)
print(f"Total pages returned: {len(pages)}")

for i, pg in enumerate(pages[:5]):
    keys = list(pg.keys())
    non_text = {k: v for k, v in pg.items() if k != 'text'}
    print(f"\nPage chunk [{i}] keys: {keys}")
    print(f"Page chunk [{i}] non-text fields: {non_text}")
