import requests
import json
import time

def test_search():
    url = "http://localhost:8000/api/v1/research-search"
    payload = {"query": "Ashwagandha"}
    
    # Wait for backend to be fully up
    for _ in range(5):
        try:
            r = requests.get("http://localhost:8000/docs")
            if r.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)
            
    print("Testing API...")
    try:
        response = requests.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        print(f"Success! Found {len(data.get('records', []))} records.")
        print(f"Query Analyzed: {data.get('query_analyzed')}")
        
        sources = set()
        fields_found = set()
        for rec in data.get('records', []):
            sources.add(rec.get('source'))
            if rec.get('title'): fields_found.add('title')
            if rec.get('authors'): fields_found.add('authors')
            if rec.get('year'): fields_found.add('year')
            if rec.get('journal'): fields_found.add('journal')
            if rec.get('abstract'): fields_found.add('abstract')
            if rec.get('doi'): fields_found.add('doi')
            if rec.get('url'): fields_found.add('url')
            
        print(f"Sources returned: {sources}")
        print(f"Fields found across results: {fields_found}")
        
    except Exception as e:
        print(f"Error testing API: {e}")
        
if __name__ == "__main__":
    test_search()
