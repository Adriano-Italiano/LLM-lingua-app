import os
from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import login
from llmlingua import PromptCompressor

app = FastAPI(
    title="LLMLingua API",
    description="API do kompresji promptów z LLMlingua",
    version="1.0.0"
)

# logowanie do Hugging Face (token z Cloud Run env)
hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN")
if hf_token:
    try:
        login(hf_token)
        print("✅ Hugging Face login successful")
    except Exception as e:
        print(f"⚠️ Hugging Face login failed: {e}")
else:
    print("⚠️ No Hugging Face token provided")

# inicjalizacja modelu (w try/except)
compressor = None
try:
    compressor = PromptCompressor(model_name="microsoft/llmlingua-2")
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Model loading failed: {e}")


class CompressRequest(BaseModel):
    text: str
    target_tokens: int


@app.get("/")
def root():
    return {"status": "ok", "model_loaded": compressor is not None}


@app.post("/compress")
def compress_text(req: CompressRequest):
    if not compressor:
        return {"error": "Compressor not initialized"}
    try:
        result = compressor.compress_prompt(
            req.text,
            target_token=req.target_tokens
        )
        return {"compressed": result}
    except Exception as e:
        return {"error": str(e)}
