# Generate tests for a single file
python test_generator/generator.py app/services/pricing.py

# Specify output location
python test_generator/generator.py app/services/pricing.py --output tests/test_pricing.py

# Generate tests for an entire module
for file in app/services/*.py; do
    python test_generator/generator.py "$file"
done
