import os
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import login
from llmlingua import PromptCompressor

app = FastAPI(
    title="LLMLingua API",
    description="API do kompresji promptów (LLMLingua-2)",
    version="1.0.0",
)

# ---- HF token (z env) + cache w /tmp, bo root FS Cloud Run jest read-only
HF_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")
if HF_TOKEN:
    try:
        login(HF_TOKEN)
        print("✅ Hugging Face login successful")
    except Exception as e:
        print(f"⚠️ Hugging Face login failed: {e}")
else:
    print("⚠️ No HUGGINGFACE_HUB_TOKEN provided (jeśli model wymaga akceptacji/priv, to będzie 401).")

# ---- Lazy init kompresora + prosta ochrona przed równoległą inicjalizacją
_compressor = None
_init_lock = threading.Lock()

def _ensure_compressor():
    global _compressor
    if _compressor is None:
        with _init_lock:
            if _compressor is None:
                print("⏳ Loading LLMLingua-2 model...")
                # Jeśli masz lokalną kopię modelu w obrazie, podaj model_dir="...".
                _compressor = PromptCompressor(model_name="microsoft/llmlingua-2")
                print("✅ LLMLingua model loaded.")

class CompressRequest(BaseModel):
    text: str
    target_tokens: int = 200

@app.get("/")
def root():
    return {"status": "ok", "model_loaded": _compressor is not None}

@app.post("/warmup")
def warmup():
    try:
        _ensure_compressor()
        return {"ok": True, "model_loaded": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Warmup failed: {e}")

@app.post("/compress")
def compress(req: CompressRequest):
    try:
        _ensure_compressor()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model init failed: {e}")

    # API LLMLingua różni się między wersjami; obsłużmy obie:
    try:
        # najpierw spróbuj nowego
        result = _compressor.compress_prompt(req.text, target_token=req.target_tokens)
        # bywa, że zwraca string; bywa, że dict — znormalizujmy:
        if isinstance(result, dict) and "compressed_prompt" in result:
            return {"compressed": result["compressed_prompt"]}
        return {"compressed": result}
    except AttributeError:
        # starsze API
        result = _compressor.compress(req.text, target_token=req.target_tokens)
        return {"compressed": result.get("compressed_prompt", result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compress failed: {e}")
