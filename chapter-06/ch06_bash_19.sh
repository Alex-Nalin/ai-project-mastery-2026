# Install BitNet dependencies
pip install torch numpy transformers

# Clone and install BitNet
git clone https://github.com/microsoft/BitNet.git
cd BitNet
pip install -e .

# Download the 7B model (1.4GB)
python scripts/download_model.py --model bitnet-b1.58-7b --output ./models
