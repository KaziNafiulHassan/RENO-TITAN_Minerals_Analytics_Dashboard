#!/bin/bash
# Start the Streamlit app

cd /home/kazi-nafiul-hassan/Hochschule\ Magdeburg-Stendal/RENO_TITAN_Project/code/reno-titan-intelligence-platform

echo "🚀 Starting RENO-TITAN Intelligence Platform..."
echo ""
echo "📍 The app will be available at: http://localhost:8501"
echo ""

source venv/bin/activate
streamlit run app/app.py --logger.level=info
