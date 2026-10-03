from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image
import pickle
import json
import threading
from datetime import datetime
from ultralytics import YOLO

# Import our custom modules
from models_db import ModelsDatabase
from violations_db import ViolationsDatabase
from violation_detector import ViolationDetector
from users_db import UsersDatabase
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MODELS_FOLDER = 'models'
VIOLATIONS_FOLDER = 'violations'
IMAGE_SIZE = 96
DEMO_MODE = False  # Will be True if models not found

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIOLATIONS_FOLDER, exist_ok=True)

# Global variables to store models and databases
model = None
encoder = None
detection_model = None
models_db = ModelsDatabase()
violations_db = ViolationsDatabase()
violation_detector = ViolationDetector()
users_db = UsersDatabase()

# Camera variables for live streaming
camera = None
camera_lock = threading.Lock()
camera_streaming = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_active_model():
    """Load the currently active model from database"""
    global model, encoder, DEMO_MODE, detection_model

    active_model = models_db.get_active_model()

    if not active_model:
        print("\n⚠️  No active model found. Starting in DEMO MODE")
        print("   (Predictions will be simulated)\n")
        DEMO_MODE = True
        model = None
        detection_model = None

        # Create a mock encoder
        from sklearn.preprocessing import LabelEncoder
        encoder = LabelEncoder()
        encoder.fit(['ambulance', 'fire_truck', 'police', 'car', 'bus', 'truck', 'bicycle', 'motorcycle'])
        print(f"✅ Demo encoder created with classes: {list(encoder.classes_)}")
        return

    model_path = active_model[2]  # path
    encoder_path = active_model[3]  # encoder_path
    model_type = active_model[4]  # type

    # Get the base directory (where app.py is located)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Convert to absolute path if relative
    if model_path and not os.path.isabs(model_path):
        model_path = os.path.join(base_dir, model_path)
    if encoder_path and not os.path.isabs(encoder_path):
        encoder_path = os.path.join(base_dir, encoder_path)

    print(f"Loading model from: {model_path}")
    print(f"Loading encoder from: {encoder_path}")

    try:
        if model_type == 'classification':
            # Load classification model
            import tensorflow as tf

            print("📦 Loading classification model with compatibility mode...")

            # Try direct load first
            try:
                model = tf.keras.models.load_model(model_path)
                print(f"✅ Model loaded successfully from {model_path}")
            except Exception as e1:
                print(f"⚠️  Direct load failed: {str(e1)[:100]}...")
                print("🔧 Attempting compatibility mode...")

                # Try loading as H5 if it's actually an h5 file
                try:
                    model = tf.keras.models.load_model(model_path, compile=False)
                    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
                    print(f"✅ Model loaded in compatibility mode")
                except:
                    raise FileNotFoundError(f"Could not load model even with compatibility mode: {e1}")

            # Load label encoder if exists
            if encoder_path and os.path.exists(encoder_path):
                with open(encoder_path, 'rb') as f:
                    encoder = pickle.load(f)
                print(f"✅ Label encoder loaded from {encoder_path}")
                print(f"✅ Classes: {list(encoder.classes_)}")
            else:
                # Create default encoder
                encoder = LabelEncoder()
                encoder.fit(['ambulance', 'fire_truck', 'police', 'car', 'bus', 'truck', 'bicycle', 'motorcycle'])

        elif model_type == 'detection':
            # Load detection model (YOLO)
            model = None
            encoder = None
            detection_model = YOLO(model_path)
            print(f"✅ Detection model loaded from {model_path}")

        DEMO_MODE = False

    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("   Starting in DEMO MODE with simulated predictions\n")
        DEMO_MODE = True

        # Create mock encoder as fallback
        from sklearn.preprocessing import LabelEncoder
        encoder = LabelEncoder()
        encoder.fit(['ambulance', 'fire_truck', 'police', 'car', 'bus', 'truck', 'bicycle', 'motorcycle'])
        print(f"✅ Demo encoder created with classes: {list(encoder.classes_)}")

def get_priority(vehicle):
    """Return priority level for vehicle type"""
    priority_map = {
        "ambulance": "🚑 HIGH PRIORITY",
        "fire_truck": "🚒 HIGH PRIORITY",
        "police": "🚓 MEDIUM PRIORITY",
        "car": "🚗 NORMAL",
        "bus": "🚌 NORMAL",
        "truck": "🚚 NORMAL",
        "bicycle": "🚲 LOW",
        "motorcycle": "🏍️ NORMAL"
    }
    return priority_map.get(vehicle.lower(), "UNKNOWN")

def preprocess_image(image_array):
    """Preprocess image for model prediction"""
    # Convert RGB to BGR since the model was trained on BGR images (cv2.imread)
    img_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
    # Resize to model's expected size
    img = cv2.resize(img_bgr, (IMAGE_SIZE, IMAGE_SIZE))
    # Normalize
    img = img.astype("float32") / 255.0
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    return img

def get_demo_prediction(image_array):
    """Generate demo predictions based on image analysis"""
    # Analyze image brightness/features for deterministic demo
    img_small = cv2.resize(image_array, (32, 32))
    brightness = np.mean(img_small)
    color_variance = np.std(img_small)
    
    # Use image features to generate consistent but varied predictions
    seed = int(brightness * 100) % len(encoder.classes_)
    np.random.seed(seed)
    
    # Generate random predictions
    predictions = np.random.dirichlet(np.ones(len(encoder.classes_)) * 2)
    predictions = predictions / predictions.sum()
    
    return predictions

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None or detection_model is not None,
        'encoder_loaded': encoder is not None or detection_model is not None,
        'demo_mode': DEMO_MODE,
        'message': 'Running in DEMO MODE - using simulated predictions' if DEMO_MODE else 'Using real trained model'
    })

@app.route('/api/classes', methods=['GET'])
def get_classes():
    """Get list of vehicle classes"""
    if encoder is not None:
        classes = list(encoder.classes_)
    elif detection_model is not None:
        classes = list(detection_model.names.values())
    elif DEMO_MODE:
        classes = ['ambulance', 'fire_truck', 'police', 'car', 'bus', 'truck', 'bicycle', 'motorcycle']
    else:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({'classes': classes})

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict vehicle type from uploaded image"""
    if model is None and detection_model is None and not DEMO_MODE:
        return jsonify({'error': 'Model not loaded'}), 500
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400
    
    try:
        # Read image
        img_data = Image.open(file.stream).convert('RGB')
        img_array = np.array(img_data)
        
        # Check if image is valid
        if img_array.shape[2] != 3 and len(img_array.shape) < 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        
        # Preprocess
        img_preprocessed = preprocess_image(img_array)
        
        # Predict
        if DEMO_MODE:
            predictions = np.array([get_demo_prediction(img_array)])
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            predicted_class = encoder.inverse_transform([predicted_class_idx])[0]
            all_preds = {
                encoder.inverse_transform([i])[0]: round(float(predictions[0][i]) * 100, 2)
                for i in range(len(predictions[0]))
            }
        elif model is not None:
            predictions = model.predict(img_preprocessed, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            predicted_class = encoder.inverse_transform([predicted_class_idx])[0]
            all_preds = {
                encoder.inverse_transform([i])[0]: round(float(predictions[0][i]) * 100, 2)
                for i in range(len(predictions[0]))
            }
        elif detection_model is not None:
            results = detection_model(img_array)
            best_conf = 0.0
            best_class = "Unknown"
            for r in results:
                for box in r.boxes:
                    conf = float(box.conf)
                    if conf > best_conf:
                        best_conf = conf
                        best_class = r.names[int(box.cls)]
            
            predicted_class = best_class
            confidence = best_conf
            all_preds = {predicted_class: round(confidence * 100, 2)}
        
        # Get priority
        priority = get_priority(predicted_class)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        img_data.save(file_path)
        
        return jsonify({
            'success': True,
            'predicted_vehicle': predicted_class,
            'confidence': round(confidence * 100, 2),
            'priority': priority,
            'demo_mode': DEMO_MODE,
            'all_predictions': all_preds
        })
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/api/predict-url', methods=['POST'])
def predict_from_url():
    """Predict from image URL"""
    if model is None and detection_model is None and not DEMO_MODE:
        return jsonify({'error': 'Model not loaded'}), 500
    
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        import requests
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        img_data = Image.open(BytesIO(response.content)).convert('RGB')
        img_array = np.array(img_data)
        
        # Preprocess and predict
        img_preprocessed = preprocess_image(img_array)
        
        if DEMO_MODE:
            predictions = np.array([get_demo_prediction(img_array)])
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            predicted_class = encoder.inverse_transform([predicted_class_idx])[0]
            all_preds = {
                encoder.inverse_transform([i])[0]: round(float(predictions[0][i]) * 100, 2)
                for i in range(len(predictions[0]))
            }
        elif model is not None:
            predictions = model.predict(img_preprocessed, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            predicted_class = encoder.inverse_transform([predicted_class_idx])[0]
            all_preds = {
                encoder.inverse_transform([i])[0]: round(float(predictions[0][i]) * 100, 2)
                for i in range(len(predictions[0]))
            }
        elif detection_model is not None:
            results = detection_model(img_array)
            best_conf = 0.0
            best_class = "Unknown"
            for r in results:
                for box in r.boxes:
                    conf = float(box.conf)
                    if conf > best_conf:
                        best_conf = conf
                        best_class = r.names[int(box.cls)]
            
            predicted_class = best_class
            confidence = best_conf
            all_preds = {predicted_class: round(confidence * 100, 2)}
            
        priority = get_priority(predicted_class)
        
        return jsonify({
            'success': True,
            'predicted_vehicle': predicted_class,
            'confidence': round(confidence * 100, 2),
            'priority': priority,
            'demo_mode': DEMO_MODE,
            'all_predictions': all_preds
        })
        
    except Exception as e:
        return jsonify({'error': f'URL fetch error: {str(e)}'}), 500

# ============= AUTHENTICATION ENDPOINTS =============

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Basic email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'error': 'Invalid email address'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400

    hashed_pw = generate_password_hash(password)
    success, msg = users_db.create_user(email, hashed_pw)

    if success:
        # Get user to create session token
        user = users_db.get_user_by_email(email)
        token = users_db.update_user_token(user[0])
        return jsonify({'success': True, 'token': token, 'email': email})
    else:
        return jsonify({'error': msg}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = users_db.get_user_by_email(email)
    
    if user and check_password_hash(user[2], password):
        token = users_db.update_user_token(user[0])
        return jsonify({'success': True, 'token': token, 'email': email})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/verify-token', methods=['POST'])
def verify_token():
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'No token provided'}), 400
        
    user = users_db.verify_token(token)
    if user:
        return jsonify({'success': True, 'email': user[1]})
    else:
        return jsonify({'error': 'Invalid or expired token'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    data = request.get_json()
    token = data.get('token')
    if token:
        users_db.logout_user(token)
    return jsonify({'success': True})

# ============= MODEL MANAGEMENT ENDPOINTS =============

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get list of available models"""
    models = models_db.get_models()
    return jsonify({
        'models': [{
            'id': m[0],
            'name': m[1],
            'type': m[4],
            'classes': json.loads(m[5]) if m[5] else None,
            'active': bool(m[7]),
            'created_at': m[6]
        } for m in models]
    })

@app.route('/api/models', methods=['POST'])
def add_model():
    """Add a new model to the database"""
    data = request.get_json()
    name = data.get('name')
    model_path = data.get('model_path')
    encoder_path = data.get('encoder_path')
    model_type = data.get('type', 'classification')
    classes = data.get('classes')

    if not name or not model_path:
        return jsonify({'error': 'Name and model_path required'}), 400

    try:
        models_db.add_model(name, model_path, encoder_path, model_type, classes)
        return jsonify({'success': True, 'message': f'Model {name} added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/activate', methods=['POST'])
def activate_model(model_id):
    """Activate a specific model"""
    try:
        models_db.set_active_model(model_id)
        load_active_model()  # Reload the active model
        return jsonify({'success': True, 'message': 'Model activated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete a model"""
    try:
        models_db.delete_model(model_id)
        return jsonify({'success': True, 'message': 'Model deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= DETECTION ENDPOINTS =============

@app.route('/api/detect', methods=['POST'])
def detect_vehicles():
    """Detect vehicles in an uploaded image"""
    if not detection_model:
        return jsonify({'error': 'Detection model not loaded'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    try:
        img_data = Image.open(file.stream).convert('RGB')
        img_array = np.array(img_data)

        # Run detection
        results = detection_model(img_array)

        # Process results
        detections = []
        for result in results:
            for box in result.boxes:
                detection = {
                    'class': result.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': [float(x) for x in box.xyxy[0].tolist()]
                }
                detections.append(detection)

        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= VIOLATION DETECTION ENDPOINTS =============

@app.route('/api/violations', methods=['GET'])
def get_violations():
    """Get all recorded violations"""
    violations = violations_db.get_violations()
    return jsonify({
        'violations': [{
            'id': v[0],
            'type': v[1],
            'vehicle_type': v[2],
            'details': json.loads(v[3]) if v[3] else {},
            'image_path': v[4],
            'timestamp': v[5]
        } for v in violations]
    })

@app.route('/api/violations/<violation_type>', methods=['GET'])
def get_violations_by_type(violation_type):
    """Get violations of a specific type"""
    violations = violations_db.get_violations_by_type(violation_type)
    return jsonify({
        'type': violation_type,
        'violations': [{
            'id': v[0],
            'vehicle_type': v[2],
            'details': json.loads(v[3]) if v[3] else {},
            'image_path': v[4],
            'timestamp': v[5]
        } for v in violations]
    })

@app.route('/api/violations', methods=['POST'])
def add_violation():
    """Record a new traffic violation"""
    data = request.get_json()
    violation_type = data.get('type')
    vehicle_type = data.get('vehicle_type')
    details = data.get('details', {})
    image_base64 = data.get('image')

    if not violation_type or not vehicle_type:
        return jsonify({'error': 'type and vehicle_type required'}), 400

    try:
        image_path = None
        
        # Save image if provided
        if image_base64:
            import base64
            try:
                # Remove data URL prefix if present
                if ',' in image_base64:
                    image_data = base64.b64decode(image_base64.split(',')[1])
                else:
                    image_data = base64.b64decode(image_base64)
                
                filename = f"violation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                image_path = os.path.join(VIOLATIONS_FOLDER, filename)
                with open(image_path, 'wb') as f:
                    f.write(image_data)
            except Exception as e:
                print(f"Warning: Could not save image: {e}")

        violations_db.add_violation(violation_type, vehicle_type, details, image_path)
        return jsonify({'success': True, 'message': 'Violation recorded'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-violations', methods=['POST'])
def check_violations():
    """Check detections for traffic violations"""
    data = request.get_json()
    detections = data.get('detections', [])
    speed_data = data.get('speed_data', {})

    violations = []

    for detection in detections:
        vehicle_type = detection.get('class', '').lower()
        confidence = detection.get('confidence', 0)
        bbox = detection.get('bbox', [])

        if confidence < 0.5:  # Skip low confidence detections
            continue

        # Check speeding
        if vehicle_type in speed_data:
            speed = speed_data[vehicle_type]
            is_speeding, limit = violation_detector.detect_speeding(vehicle_type, speed)

            if is_speeding:
                violations.append({
                    'type': 'speeding',
                    'vehicle': vehicle_type,
                    'speed': speed,
                    'limit': limit,
                    'bbox': bbox,
                    'timestamp': datetime.now().isoformat()
                })

        # Check blocking emergency vehicles
        emergency_violations = violation_detector.detect_emergency_vehicle_precedence(detections)
        violations.extend(emergency_violations)

    return jsonify({
        'violations': violations,
        'count': len(violations)
    })

# ============= CAMERA STREAMING ENDPOINTS =============

def gen_frames():
    """Generate frames for video streaming"""
    global camera
    while camera_streaming:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    """Start camera stream"""
    global camera, camera_streaming
    
    try:
        with camera_lock:
            if camera is None or not camera.isOpened():
                camera = cv2.VideoCapture(0)
                if not camera.isOpened():
                    return jsonify({'error': 'Could not open camera'}), 500
            camera_streaming = True
        return jsonify({'success': True, 'message': 'Camera started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    """Stop camera stream"""
    global camera, camera_streaming
    
    with camera_lock:
        camera_streaming = False
        if camera:
            camera.release()
            camera = None
    
    return jsonify({'success': True, 'message': 'Camera stopped'})

@app.route('/api/camera/stream')
def camera_stream():
    """Stream video from camera"""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera/capture', methods=['POST'])
def capture_frame():
    """Capture current camera frame and run prediction"""
    global camera
    
    try:
        with camera_lock:
            if camera is None or not camera.isOpened():
                return jsonify({'error': 'Camera not available'}), 400
            
            success, frame = camera.read()
            if not success:
                return jsonify({'error': 'Failed to capture frame'}), 500
        
        # Convert to PIL format
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img_array = np.array(pil_image)
        
        # Run prediction
        if model is None and detection_model is None and not DEMO_MODE:
            return jsonify({'error': 'Model not loaded'}), 500
        
        img_preprocessed = preprocess_image(img_array)
        
        if DEMO_MODE:
            predictions = np.array([get_demo_prediction(img_array)])
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            predicted_class = encoder.inverse_transform([predicted_class_idx])[0]
        elif model is not None:
            predictions = model.predict(img_preprocessed, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            predicted_class = encoder.inverse_transform([predicted_class_idx])[0]
        elif detection_model is not None:
            results = detection_model(img_array)
            best_conf = 0.0
            best_class = "Unknown"
            for r in results:
                for box in r.boxes:
                    conf = float(box.conf)
                    if conf > best_conf:
                        best_conf = conf
                        best_class = r.names[int(box.cls)]
            
            predicted_class = best_class
            confidence = best_conf
        
        priority = get_priority(predicted_class)
        
        return jsonify({
            'success': True,
            'predicted_vehicle': predicted_class,
            'confidence': round(confidence * 100, 2),
            'priority': priority,
            'demo_mode': DEMO_MODE
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print("Loading model...")
    load_active_model()
    print("\n🚀 Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
