# Clone the BitNet repository
git clone https://github.com/microsoft/BitNet.git
cd BitNet

# Install dependencies
pip install -r requirements.txt

# Download a pre-trained model (7B parameters)
# Models available: 7B, 13B, 70B (yes, 70B runs on CPU)
python download_model.py --model bitnet-b1.58-7b

# Run inference
python run_inference.py --model bitnet-b1.58-7b --prompt "Explain the benefits of 1-bit LLMs"
