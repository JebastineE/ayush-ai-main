from transformers import AutoModel, AutoTokenizer
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

model_name = "law-ai/InLegalBERT"

logging.info(f"Downloading {model_name} to local cache. This may take 2-5 minutes depending on internet speed...")

# This downloads the model weights and tokenizer directly to your machine
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

logging.info("✅ InLegalBERT successfully downloaded and loaded locally!")