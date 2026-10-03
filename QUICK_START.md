## 🚀 QUICK START GUIDE

This file will get you up and running in 5 minutes!

---

## ✅ What Was Created

Your Traffic Vehicle Classifier consists of:

```
Work_10_03/
├── backend/         ← Flask REST API server
├── frontend/        ← React web application
├── README.md        ← Full documentation
└── ModelTraining.ipynb ← Your trained model source
```

---

## 📋 Prerequisites

**Windows, macOS, or Linux with:**
- Python 3.8+ → https://www.python.org/downloads/
- Node.js 14+ → https://nodejs.org/ (includes npm)
- Trained model files (from Google Drive)

---

## ⚡ Super Quick Start (Windows)

### Terminal 1 - Start Backend:
```bash
cd backend
run.bat
```

### Terminal 2 - Start Frontend:
```bash
cd frontend
run.bat
```

Then open http://localhost:3000 in your browser!

---

## ⚡ Super Quick Start (Mac/Linux)

### Terminal 1 - Start Backend:
```bash
cd backend
bash run.sh
```

### Terminal 2 - Start Frontend:
```bash
cd frontend
bash run.sh
```

Then open http://localhost:3000 in your browser!

---

## 📥 Important: Get Your Model Files!

Before running, you need to download 2 files from Google Drive:

1. `traffic_model.keras` → Place in `backend/models/`
2. `label_encoder.pkl` → Place in `backend/models/`

Create the folder if needed:
```bash
mkdir backend/models
```

---

## 🎯 Step-by-Step Setup

### Step 1️⃣: Prepare Backend

```bash
cd backend

# Create models folder
mkdir models

# Download model files from Google Drive and place them in:
# backend/models/traffic_model.keras
# backend/models/label_encoder.pkl

# Install Python packages
pip install -r requirements.txt
```

### Step 2️⃣: Prepare Frontend

```bash
cd frontend

# Install Node packages
npm install
```

### Step 3️⃣: Run Backend

```bash
cd backend
python app.py
```

Wait for:
```
✅ Model loaded from models/traffic_model.keras
✅ Label encoder loaded from models/label_encoder.pkl
🚀 Starting Flask server...
 * Running on http://0.0.0.0:5000
```

### Step 4️⃣: Run Frontend (in NEW terminal)

```bash
cd frontend
npm start
```

Browser should open to http://localhost:3000

### Step 5️⃣: Test It!

1. You should see "API Ready" (green light)
2. Upload a vehicle image or paste image URL
3. See instant predictions!

---

## 🆘 Troubleshooting

### "Model not found" error
```bash
# 1. Create models folder
mkdir backend/models

# 2. Download from Google Drive:
#    - traffic_model.keras
#    - label_encoder.pkl

# 3. Place both files in backend/models/
```

### "API Offline" in browser
```bash
# Make sure backend is running
# Terminal 1 should show:
#  * Running on http://0.0.0.0:5000
```

### Port already in use
```bash
# Use different port in app.py or:

# Windows: Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :5000
kill -9 <PID>
```

### Slow to install?
This is normal on first install. TensorFlow is large (~500MB).

---

## 📁 Project Structure

```
backend/
├── app.py              ← Main Flask application
├── requirements.txt    ← Python dependencies
├── models/             ← Your trained models (create & populate)
│   ├── traffic_model.keras
│   └── label_encoder.pkl
├── uploads/            ← Uploaded images storage
└── README.md           ← Detailed backend docs

frontend/
├── src/                ← React source code
│   ├── components/     ← React components
│   ├── App.js
│   └── index.js
├── public/
│   └── index.html
├── package.json        ← Node dependencies
└── README.md           ← Detailed frontend docs
```

---

## 🔗 API Endpoints

**Base URL:** `http://localhost:5000/api`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check API status |
| GET | `/classes` | Get vehicle classes |
| POST | `/predict` | Upload & classify image |
| POST | `/predict-url` | Classify from URL |

---

## 🎮 How to Use

1. **Upload File:** Drag/drop or click upload area
2. **Use URL:** Switch tab and paste image URL
3. **Get Results:** Instant vehicle prediction with confidence
4. **View Priority:** See if it's emergency vehicle (🚑 🚒 🚓)

Supported formats: JPG, PNG, GIF

---

## ✨ Features

✅ Deep learning vehicle classification
✅ Real-time predictions
✅ Emergency vehicle detection
✅ Confidence scores for all classes
✅ Responsive web interface
✅ GPU/CPU support
✅ Simple REST API

---

## 📖 Full Documentation

- `../README.md` - Complete project overview
- `backend/README.md` - Backend API details
- `frontend/README.md` - Frontend setup & features

---

## 🎓 Next Steps

1. ✅ Get model files from Google Drive
2. ✅ Place in `backend/models/`
3. ✅ Run `bash run.sh` (or `run.bat` on Windows) in both folders
4. ✅ Visit http://localhost:3000
5. ✅ Start classifying! 🚗

---

## 💡 Pro Tips

- **First prediction is slower** (model loading) - subsequent faster
- **Better images = Better predictions** - clear, well-lit photos work best
- **Check console** (F12) if anything goes wrong
- **GPU mode** - Install tensorflow-gpu for 2-3x faster inference
- **Multiple terminals** - Always run backend & frontend in separate terminals

---

## 🆙 Production Deployment

When ready to deploy:

```bash
# Backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Frontend
npm run build  # Creates optimized build/
serve -s build
```

---

**Questions?** Check the detailed README files in each folder!

**Ready? Let's go! 🚀**
