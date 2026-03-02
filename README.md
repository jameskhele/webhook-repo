# GitHub Webhook Receiver System

## 🔹 Tech Stack
- Python (Flask)
- MongoDB Atlas
- Render (Deployment)
- GitHub Webhooks

## 🔹 Architecture
GitHub → Webhook → Flask Backend → MongoDB → UI Polling (15s)

## 🔹 Features
- Push Event Detection
- Pull Request Detection
- Merge Event Detection
- Stores events in MongoDB
- UI updates every 15 seconds
- Production deployment using Gunicorn

## 🔹 Live URL
https://webhook-repo-gbye.onrender.com
