import os
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llmlingua import PromptCompressor

app = FastAPI(
    title="LLMLingua API",
    description="API do kompresji promptów (offline, model w obrazie)",
    version="1.0.0",
)

# ---- Konfiguracja
MODEL_DIR = os.getenv("LLM_MODEL_DIR", "/app/model")
USE_LLMLINGUA2 = os.getenv("USE_LLMLINGUA2", "false").lower() == "true"

# Lazy init kompresora
_compressor = None
_init_lock = threading.Lock()


def _ensure_compressor():
    global _compressor
    if _compressor is None:
        with _init_lock:
            if _compressor is None:
                print(f"⏳ Loading LLMLingua model from {MODEL_DIR} ...")
                _compressor = PromptCompressor(
                    model_name=MODEL_DIR,
                    use_llmlingua2=USE_LLMLINGUA2
                )
                print("✅ LLMLingua model loaded.")


# ---- Request schemas
class CompressRequest(BaseModel):
    text: str
    target_tokens: int | None = 200  # używane w LLMLingua-1
    rate: float | None = 0.6        # używane w LLMLingua-2


# ---- API endpoints
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

    # ---- LLMLingua-1 API (target_tokens)
    try:
        if not USE_LLMLINGUA2:
            result = _compressor.compress_prompt(req.text, target_token=req.target_tokens)
            if isinstance(result, dict) and "compressed_prompt" in result:
                return {"compressed": result["compressed_prompt"]}
            return {"compressed": result}

        # ---- LLMLingua-2 API (rate)
        result = _compressor.compress_prompt_llmlingua2(
            req.text,
            rate=req.rate or 0.6,
            force_tokens=["\n", ".", "!", "?", ","],
            chunk_end_tokens=[".", "\n"],
            return_word_label=False,
            drop_consecutive=True,
        )
        if isinstance(result, dict) and "compressed_prompt" in result:
            return {"compressed": result["compressed_prompt"]}
        return {"compressed": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compress failed: {e}")
