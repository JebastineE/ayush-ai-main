import os
from dotenv import load_dotenv

load_dotenv()

key_set = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

print(f"API_KEY_PRESENT: {key_set}")

try:
    import google.genai as genai
    import importlib.metadata
    try:
        ver = importlib.metadata.version("google-genai")
    except Exception:
        ver = "installed"
    print(f"SDK_VERSION: google-genai {ver}")
except Exception as e:
    print(f"SDK_ERROR: {e}")

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
model_name = "gemini-3.5-flash-lite"
print(f"CONFIGURED_MODEL: {model_name}")

if api_key:
    try:
        client = genai.Client(api_key=api_key, vertexai=False)
        resp = client.models.generate_content(
            model=model_name,
            contents="Reply with exactly: GEMINI_API_TEST_OK"
        )
        print(f"TEST_RESULT: SUCCESS")
        print(f"TEST_RESPONSE: {resp.text.strip()}")
    except Exception as e:
        print(f"TEST_RESULT: FAILED")
        print(f"ERROR_TYPE: {type(e).__name__}")
        print(f"ERROR_MSG: {str(e)}")
else:
    print("TEST_RESULT: FAILED")
    print("ERROR_TYPE: MissingKey")
    print("ERROR_MSG: No API key found in environment")
