# One-liner install
curl -fsSL https://ollama.com/install.sh | sh

# Or for Debian/Ubuntu specifically
sudo apt-get update
sudo apt-get install -y pciutils curl
curl -fsSL https://ollama.com/install.sh | sh

# Start as a system service
systemctl start ollama
