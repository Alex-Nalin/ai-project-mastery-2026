# Clone and install
git clone https://github.com/open-webui/open-webui.git
cd open-webui

# Backend
cd backend
pip install -r requirements.txt
python main.py &

# Frontend
cd ../frontend
npm install
npm run dev
