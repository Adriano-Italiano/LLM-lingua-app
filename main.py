import os
from fastapi import FastAPI
from pydantic import BaseModel
from llmlingua import PromptCompressor
from huggingface_hub import login

# logowanie do Hugging Face przy starcie
hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN")
if hf_token:
    login(hf_token)

# FastAPI app
app = FastAPI(
    title="LLMLingua API",
    description="API do kompresji promptów z LLMLingua",
    version="1.0.0"
)

# inicjalizacja kompresora
compressor = PromptCompressor(model_name="microsoft/llmlingua-2")

# Schemat requestu
class CompressRequest(BaseModel):
    text: str
    target_tokens: int

# Endpoint
@app.post("/compress")
def compress_text(req: CompressRequest):
    result = compressor.compress_prompt(
        req.text,
        target_token=req.target_tokens
    )
    return {"compressed": result}
