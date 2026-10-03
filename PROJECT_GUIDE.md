# 🚗 Traffic Monitoring & Violation Alert System

A comprehensive deep learning-powered traffic monitoring system with vehicle classification, detection, and violation alerting capabilities.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Installation Steps](#installation-steps)
6. [Running the Application](#running-the-application)
7. [Features Guide](#features-guide)
8. [API Documentation](#api-documentation)
9. [Model Information](#model-information)
10. [Troubleshooting](#troubleshooting)

---

## 🔰 Project Overview

This is a **Traffic Monitoring & Violation Alert System** that provides:

- **Vehicle Classification** - Identify 21 types of vehicles from images
- **Live Camera Detection** - Real-time vehicle detection from webcam
- **Traffic Violation Detection** - Detect and record violations (speeding, red light, wrong lane)
- **Video Analysis** - Analyze video files for traffic monitoring
- **Model Management** - Add, switch, and manage different AI models

---

## 💻 Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Flask** | Web framework for REST API |
| **TensorFlow/Keras** | Vehicle classification model |
| **Ultralytics YOLO** | Object detection |
| **OpenCV** | Image/video processing |
| **SQLite** | Database for models and violations |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React** | User interface |
| **Axios** | API requests |
| **CSS3** | Premium dark theme styling |

---

## 📁 Project Structure

```
Work_10_03/
├── backend/                    # Flask API Server
│   ├── app.py                # Main application (current)
│   ├── app_v2.py            # Enhanced version with video analysis
│   ├── models_db.py         # Model database management
│   ├── violations_db.py     # Violations database
│   ├── violation_detector.py # Violation detection logic
│   ├── models/              # Trained model files
│   │   ├── traffic_model.keras
│   │   └── label_encoder.pkl
│   ├── uploads/             # Uploaded images/videos
│   ├── violations/           # Violation evidence images
│   ├── requirements.txt     # Python dependencies
│   └── setup_model.py       # Model registration script
│
├── frontend/                  # React Web Application
│   ├── src/
│   │   ├── components/      # UI Components
│   │   │   ├── ImageUploader.js
│   │   │   ├── PredictionResult.js
│   │   │   ├── ClassesList.js
│   │   │   ├── ModelSelector.js
│   │   │   ├── CameraStream.js
│   │   │   └── ViolationsList.js
│   │   ├── App.js          # Main app component
│   │   └── App.css         # Premium dark theme
│   ├── package.json
│   └── README.md
│
├── YOLOv8_Vehicle_Detection.ipynb  # YOLO training notebook
├── ModelTraining.ipynb              # Keras training notebook
└── README.md                       # Project overview
```

---

## ✅ Prerequisites

### Required Software

1. **Python 3.8 - 3.12** (Python 3.13 has compatibility issues with TensorFlow)
2. **Node.js 14+** (for frontend)
3. **pip** (Python package manager)

### Optional (for GPU acceleration)
- CUDA Toolkit 11.x+
- cuDNN 8.x+

---

## 🔧 Installation Steps

### Step 1: Clone/Extract Project

Extract the project to your desired location.

### Step 2: Set Up Python Virtual Environment

```bash
# Navigate to project directory
cd Work_10_03

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On Linux/Mac:
source .venv/bin/activate
```

### Step 3: Install Backend Dependencies

```bash
# Navigate to backend
cd backend

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

> **Note:** If you have Python 3.13, you may need to use compatible package versions:
> ```bash
> pip install Flask>=3.0.0 Flask-CORS>=4.0.0
> pip install "tensorflow>=2.15.0"
> pip install opencv-python numpy scikit-learn Pillow Werkzeug requests ultralytics
> ```

### Step 4: Set Up Model Database

```bash
# The model is automatically registered when you run setup_model.py
python setup_model.py
```

This registers the pre-trained model in the database.

### Step 5: Install Frontend Dependencies

```bash
# Navigate to frontend
cd ../frontend

# Install Node.js dependencies
npm install
```

---

## 🚀 Running the Application

### Step 1: Start the Backend Server

**Option A - Using the script (Windows):**
```bash
cd backend
run.bat
```

**Option B - Manual Start:**
```bash
cd backend
python app.py
```

Expected output:
```
Loading model...
✅ Model loaded successfully from models/traffic_model.keras
✅ Label encoder loaded from models/label_encoder.pkl

🚀 Starting Flask server...
 * Running on http://0.0.0.0:5000
```

### Step 2: Start the Frontend Server

**Option A - Using the script (Windows):**
```bash
cd frontend
run.bat
```

**Option B - Manual Start:**
```bash
cd frontend
npm start
```

If port 3000 is in use, specify a different port:
```bash
set PORT=3001
npm start
```

### Step 3: Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3001 (or 3000)
- **API**: http://localhost:5000

---

## 📖 Features Guide

### 1. Vehicle Classification (Upload Tab)

1. Click **"Upload & Predict"** tab
2. Choose input method:
   - **Upload File**: Drag & drop or click to select an image
   - **From URL**: Paste an image URL
3. Click **"Analyze"** to process
4. View results:
   - Predicted vehicle type
   - Confidence score
   - Priority level (HIGH/MEDIUM/NORMAL/LOW)
   - All class probabilities

### 2. Live Camera Detection (Camera Tab)

1. Click **"Live Camera"** tab
2. Click **"Start Camera"** to begin streaming
3. The video feed shows real-time vehicle detection
4. Use **"Capture & Analyze"** to get detailed detection results
5. Click **"Stop Camera"** when finished

### 3. Traffic Violations (Violations Tab)

1. Click **"Violations"** tab
2. View all recorded violations
3. Filter by type:
   - Speeding violations
   - Red light violations
   - Wrong lane violations
   - Emergency vehicle violations

### 4. Model Management (Models Tab)

1. Click **"Models"** tab
2. View available models
3. **Activate** a different model
4. **Add** new models with custom paths
5. **Delete** unused models

---

## 🔌 API Documentation

### Base URL: `http://localhost:5000/api`

#### Health Check
```
GET /api/health
```
Returns system status and loaded model info.

#### Vehicle Classification
```
POST /api/predict
Content-Type: multipart/form-data
```
- Input: Image file (JPG, PNG, GIF)
- Returns: Vehicle type, confidence, priority

#### URL Prediction
```
POST /api/predict-url
Content-Type: application/json
```
```json
{"url": "https://example.com/car.jpg"}
```

#### Vehicle Detection
```
POST /api/detect
Content-Type: multipart/form-data
```
- Input: Image file
- Returns: Array of detected objects with bounding boxes

#### Video Analysis
```
POST /api/video/analyze
Content-Type: multipart/form-data
```
- Input: Video file (MP4, AVI, MOV)
- Returns: All detections, violations, statistics

#### Camera Control
```
POST /api/camera/start
POST /api/camera/stop
GET  /api/camera/stream     # Video streaming endpoint
POST /api/camera/capture    # Capture and analyze frame
```

#### Violations
```
GET  /api/violations
GET  /api/violations/<type>
POST /api/violations
```

#### Models
```
GET    /api/models
POST   /api/models
POST   /api/models/<id>/activate
DELETE /api/models/<id>
```

---

## 🤖 Model Information

### Pre-trained Classification Model

- **File**: `models/traffic_model.keras`
- **Input Size**: 96x96 RGB
- **Classes**: 21 vehicle types
  - ambulance, army vehicle, auto rickshaw, bicycle, bus, car, garbagevan, human hauler, minibus, minivan, motorbike, pickup, policecar, rickshaw, scooter, suv, taxi, three wheelers (CNG), truck, van, wheelbarrow

### Pre-trained Detection Model (YOLO)

The system also supports YOLO models:
- YOLOv8 Nano (fastest)
- YOLOv8 Small (balanced)
- YOLOv8 Medium (most accurate)

---

## ⚠️ Troubleshooting

### Issue: "Module not found" errors

**Solution:** Ensure virtual environment is activated:
```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### Issue: TensorFlow not loading model

**Solution:** Use absolute paths in model registration or downgrade to Python 3.11/3.12

### Issue: Port already in use

**Backend:**
```bash
# Change port in app.py or use:
python app.py --port 5001
```

**Frontend:**
```bash
set PORT=3001
npm start
```

### Issue: Camera not working

- Check if camera is connected
- Grant browser camera permissions
- Some browsers require HTTPS for camera access

### Issue: Model prediction fails

1. Check model file exists: `backend/models/traffic_model.keras`
2. Verify model is registered in database
3. Try activating the model through the UI

---

## 📝 Additional Notes

### GPU Acceleration

For faster inference, install TensorFlow with GPU support:
```bash
pip install tensorflow-gpu
```

### Production Deployment

For production, use production WSGI servers:
```bash
# Backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Frontend
npm run build
```

### Training Custom Models

Use the Jupyter notebooks provided:
- `ModelTraining.ipynb` - Keras CNN training
- `YOLOv8_Vehicle_Detection.ipynb` - YOLO training

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 👤 Author

Created for traffic monitoring and vehicle classification demonstrations.

**Happy Monitoring! 🚗🚓🚒**

