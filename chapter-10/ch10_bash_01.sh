# Install PrismML
pip install prismml

# Download a 1-bit quantized model
prismml download --model qwen3.5-7b-1bit --output ./models

# Run inference
prismml run --model ./models/qwen3.5-7b-1bit.pt \
            --prompt "Explain quantum computing in simple terms" \
            --max_tokens 500 \
            --temperature 0.7
