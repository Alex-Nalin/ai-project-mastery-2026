# Pull a quantized version directly
ollama pull qwen3.5:32b-q4_K_M

# Or create a custom quantized variant
ollama run qwen3.5:32b
# Then in another terminal:
ollama create my-qwen-quantized -f Modelfile
