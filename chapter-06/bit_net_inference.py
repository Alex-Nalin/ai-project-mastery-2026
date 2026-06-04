import torch
import numpy as np
from typing import Optional, List, Dict
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class BitNetInference:
    """Run BitNet b1.58 inference on CPU."""
    
    def __init__(self, model_path: str, max_seq_len: int = 2048):
        self.model_path = model_path
        self.max_seq_len = max_seq_len
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load the BitNet model and tokenizer."""
        # In production, use the actual BitNet loading code
        # This is a simplified example
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float32,  # CPU inference
            device_map="cpu"
        )
        
        # Enable memory-efficient inference
        self.model.eval()
        print(f"Model loaded. Parameters: {self._count_parameters():,}")
        print(f"Peak memory: {self._get_memory_usage():.2f} GB")
    
    def _count_parameters(self) -> int:
        """Count total parameters."""
        return sum(p.numel() for p in self.model.parameters())
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in GB."""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / (1024 ** 3)
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50
    ) -> str:
        """Generate text using the BitNet model."""
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode output
        generated_text = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )
        
        return generated_text
    
    def stream_generate(self, prompt: str, **kwargs):
        """Stream generated tokens one by one."""
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            for output in self.model.generate(
                inputs.input_ids,
                max_new_tokens=kwargs.get('max_new_tokens', 256),
                temperature=kwargs.get('temperature', 0.7),
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                output_scores=True,
                return_dict_in_generate=True
            ):
                token = self.tokenizer.decode(output[0][-1:], skip_special_tokens=True)
                if token:
                    yield token

# FastAPI server
app = FastAPI(title="BitNet Edge Server")
model = None

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7

class GenerateResponse(BaseModel):
    text: str
    tokens_generated: int
    memory_usage_gb: float

@app.on_event("startup")
async def startup():
    global model
    model = BitNetInference("./models/bitnet-b1.58-7b")

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    if model is None:
        raise HTTPException(503, "Model not loaded")
    
    text = model.generate(
        request.prompt,
        max_new_tokens=request.max_tokens,
        temperature=request.temperature
    )
    
    return GenerateResponse(
        text=text,
        tokens_generated=len(text.split()),
        memory_usage_gb=model._get_memory_usage()
    )

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "memory_usage_gb": model._get_memory_usage() if model else 0
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
