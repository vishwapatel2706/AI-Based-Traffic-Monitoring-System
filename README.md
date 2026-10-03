## Backend API - Flask Server

This is the backend API for the Traffic Vehicle Classifier system.

### Prerequisites

- Python 3.8+
- pip package manager

### Setup Instructions

1. **Create a models folder:**
   ```bash
   mkdir models
   ```

2. **Copy trained model files:**
   - Download `traffic_model.keras` from Google Drive and place it in the `models/` folder
   - Download `label_encoder.pkl` from Google Drive and place it in the `models/` folder

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** TensorFlow is included in requirements.txt. If you have GPU support, you can optionally install:
   > ```bash
   > pip install tensorflow-gpu
   > ```

### Running the Server

Start the Flask development server:

```bash
python app.py
```

The server will run on `http://localhost:5000`

You should see output like:
```
Loading model...
✅ Model loaded from models/traffic_model.keras
✅ Label encoder loaded from models/label_encoder.pkl

🚀 Starting Flask server...
 * Running on http://0.0.0.0:5000
```

### API Endpoints

#### 1. Health Check
```
GET /api/health
```
Returns server and model status.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "encoder_loaded": true
}
```

#### 2. Get Available Classes
```
GET /api/classes
```
Returns list of vehicle classes the model can recognize.

**Response:**
```json
{
  "classes": ["ambulance", "fire_truck", "police", "car", "bus"]
}
```

#### 3. Predict from Image Upload
```
POST /api/predict
Content-Type: multipart/form-data
```
Analyzes an uploaded image and returns vehicle prediction.

**Request:**
- `file`: Image file (JPG, PNG, GIF)

**Response:**
```json
{
  "success": true,
  "predicted_vehicle": "ambulance",
  "confidence": 95.32,
  "priority": "🚑 HIGH PRIORITY",
  "all_predictions": {
    "ambulance": 95.32,
    "fire_truck": 3.21,
    "police": 1.47,
    "car": 0.00,
    "bus": 0.00
  }
}
```

#### 4. Predict from Image URL
```
POST /api/predict-url
Content-Type: application/json
```
Analyzes an image from a URL.

**Request:**
```json
{
  "url": "https://example.com/image.jpg"
}
```

**Response:** Same as `/api/predict`

### Troubleshooting

1. **"Model not found" error:**
   - Make sure you've created the `models/` folder
   - Verify `traffic_model.keras` and `label_encoder.pkl` are in the `models/` folder

2. **Port 5000 already in use:**
   ```bash
   # Change port in app.py or use:
   python app.py --port 5001
   ```

3. **CORS errors in frontend:**
   - The backend already has CORS enabled
   - Check that the frontend is using `http://localhost:5000/api` as the API URL

4. **TensorFlow import error:**
   ```bash
   pip install --upgrade tensorflow
   ```

### Configuration

Edit these variables in `app.py` to customize:

```python
UPLOAD_FOLDER = 'uploads'      # Where uploaded files are saved
ALLOWED_EXTENSIONS = {...}    # Allowed file types
IMAGE_SIZE = 96                # Must match model training size
```

### Development Notes

- The model expects 96x96 RGB images
- All images are automatically normalized to [0, 1] range
- Predictions include confidence scores for all classes
- Emergency vehicles (ambulance, fire_truck) are marked as HIGH PRIORITY

