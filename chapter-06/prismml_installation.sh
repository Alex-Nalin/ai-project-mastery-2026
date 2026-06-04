# PrismML installation
pip install prismml

# Load and run a model
from prismml import BitModel

model = BitModel.from_pretrained("prismml/bitnet-7b-chat")
response = model.generate("What are the benefits of local AI?")
print(response)
