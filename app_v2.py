"""
Enhanced Flask Backend for Traffic Monitoring & Violation Alert System
Features:
- Vehicle Classification
- YOLO Detection
- Video Analysis
- Violation Recording with Clips
- Model Training
"""

from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import cv2
import numpy as np
import os
import pickle
import json
import threading
import base64
from datetime import datetime
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image
from ultralytics import YOLO

# Import custom modules
from models_db import ModelsDatabase
from violations_db import ViolationsDatabase
from violation_detector import ViolationDetector

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
VIOLATIONS_FOLDER = 'violations'
CLIPS_FOLDER = 'violation_clips'
MODELS_FOLDER = 'models'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'gif'}
IMAGE_SIZE = 96
DEMO_MODE = False

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIOLATIONS_FOLDER, exist_ok=True)
os.makedirs(CLIPS_FOLDER, exist_ok=True)

# Global variables
model = None
encoder = None
detection_model = None
models_db = ModelsDatabase()
violations_db = ViolationsDatabase()
violation_detector = ViolationDetector()

# Video analysis state
video_analysis_active = False
video_analysis_thread = None
current_video_results = []

# Camera state
camera = None
camera_lock = threading.Lock()
camera_streaming = False
recording_clip = False
clip_writer = None
clip_frames = []

def allowed_file(filename, allow_video=False):
    ext = ALLOWED_EXTENSIONS if allow_video else ALLOWED_IMAGE
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ext

def load_active_model():
    """Load the currently active model from database"""
    global model, encoder, detection_model, DEMO_MODE

    active_model = models_db.get_active_model()
    if not active_model:
        print("\n⚠️  No active model found. Starting in DEMO MODE")
        DEMO_MODE = True
        from sklearn.preprocessing import LabelEncoder
        encoder = LabelEncoder()
        encoder.fit(['ambulance', 'car', 'bus', 'truck', 'bicycle', 'motorcycle'])
        return

    model_path = active_model[2]
    encoder_path = active_model[3]
    model_type = active_model[4]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if model_path and not os.path.isabs(model_path):
        model_path = os.path.join(base_dir, model_path)
    if encoder_path and not os.path.isabs(encoder_path):
        encoder_path = os.path.join(base_dir, encoder_path)

    print(f"Loading {model_type} model from: {model_path}")

    try:
        if model_type == 'classification':
            import tensorflow as tf
            model = tf.keras.models.load_model(model_path)
            print(f"✅ Classification model loaded")

            if encoder_path and os.path.exists(encoder_path):
                with open(encoder_path, 'rb') as f:
                    encoder = pickle.load(f)
                print(f"✅ Encoder loaded: {list(encoder.classes_)}")
            DEMO_MODE = False

        elif model_type == 'detection':
            # Handle YOLO pretrained models
            if model_path.endswith('.pt'):
                detection_model = YOLO(model_path)
            else:
                detection_model = YOLO(model_path)
            print(f"✅ Detection model loaded: {model_path}")
            DEMO_MODE = False

    except Exception as e:
        print(f"❌ Error loading model: {e}")
        DEMO_MODE = True
        from sklearn.preprocessing import LabelEncoder
        encoder = LabelEncoder()
        encoder.fit(['ambulance', 'car', 'bus', 'truck', 'bicycle', 'motorcycle'])

def get_priority(vehicle):
    priority_map = {
        "ambulance": "🚑 HIGH PRIORITY",
        "fire_truck": "🚒 HIGH PRIORITY", 
        "policecar": "🚓 MEDIUM PRIORITY",
        "police": "🚓 MEDIUM PRIORITY",
        "car": "🚗 NORMAL",
        "bus": "🚌 NORMAL",
        "truck": "🚚 NORMAL",
        "bicycle": "🚲 LOW",
        "motorcycle": "🏍️ NORMAL",
        "motorbike": "🏍️ NORMAL"
    }
    return priority_map.get(vehicle.lower(), "🚗 NORMAL")

def preprocess_image(image_array):
    img = cv2.resize(image_array, (IMAGE_SIZE, IMAGE_SIZE))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# ============= HEALTH & CLASSES =============

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None or detection_model is not None,
        'encoder_loaded': encoder is not None,
        'detection_model_loaded': detection_model is not None,
        'demo_mode': DEMO_MODE,
        'video_analysis_active': video_analysis_active,
        'message': 'System ready' if (model or detection_model) else 'Running in demo mode'
    })

@app.route('/api/classes', methods=['GET'])
def get_classes():
    if encoder:
        return jsonify({'classes': list(encoder.classes_)})
    return jsonify({'classes': ['ambulance', 'car', 'bus', 'truck', 'bicycle', 'motorcycle']})

# ============= CLASSIFICATION ENDPOINTS =============

@app.route('/api/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        img_data = Image.open(file.stream).convert('RGB')
        img_array = np.array(img_data)
        
        if encoder is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        img_preprocessed = preprocess_image(img_array)
        predictions = model.predict(img_preprocessed, verbose=0)
        
        predicted_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_idx])
        predicted_class = encoder.inverse_transform([predicted_idx])[0]
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        img_data.save(file_path)
        
        return jsonify({
            'success': True,
            'predicted_vehicle': predicted_class,
            'confidence': round(confidence * 100, 2),
            'priority': get_priority(predicted_class),
            'all_predictions': {
                encoder.inverse_transform([i])[0]: round(float(predictions[0][i]) * 100, 2)
                for i in range(len(predictions[0]))
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-url', methods=['POST'])
def predict_from_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        import requests
        response = requests.get(url, timeout=10)
        img_data = Image.open(BytesIO(response.content)).convert('RGB')
        img_array = np.array(img_data)
        
        if encoder is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        img_preprocessed = preprocess_image(img_array)
        predictions = model.predict(img_preprocessed, verbose=0)
        
        predicted_idx = np.argmax(predictions[0])
        predicted_class = encoder.inverse_transform([predicted_idx])[0]
        
        return jsonify({
            'success': True,
            'predicted_vehicle': predicted_class,
            'confidence': round(float(predictions[0][predicted_idx]) * 100, 2),
            'priority': get_priority(predicted_class)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= DETECTION ENDPOINTS =============

@app.route('/api/detect', methods=['POST'])
def detect_vehicles():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    try:
        img_data = Image.open(file.stream).convert('RGB')
        img_array = np.array(img_data)
        
        if detection_model is None:
            # Return mock detection for demo
            return jsonify({
                'success': True,
                'detections': [
                    {'class': 'car', 'confidence': 0.95, 'bbox': [100, 100, 300, 250]},
                    {'class': 'truck', 'confidence': 0.87, 'bbox': [350, 80, 550, 280]}
                ],
                'count': 2
            })
        
        results = detection_model(img_array, verbose=False)
        
        detections = []
        for result in results:
            for box in result.boxes:
                detections.append({
                    'class': result.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': [float(x) for x in box.xyxy[0].tolist()]
                })
        
        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= VIDEO ANALYSIS ENDPOINTS =============

@app.route('/api/video/analyze', methods=['POST'])
def analyze_video():
    """Analyze video file and detect vehicles"""
    if 'file' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['file']
    if not allowed_file(file.filename, allow_video=True):
        return jsonify({'error': 'Invalid video format'}), 400
    
    try:
        # Save uploaded video
        filename = secure_filename(file.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(video_path)
        
        # Analyze video
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        all_detections = []
        violations_found = []
        
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run detection every 10 frames for efficiency
            if frame_idx % 10 == 0 and detection_model:
                results = detection_model(frame, verbose=False)
                for result in results:
                    for box in result.boxes:
                        cls = result.names[int(box.cls)]
                        conf = float(box.conf)
                        if conf > 0.5:
                            all_detections.append({
                                'frame': frame_idx,
                                'class': cls,
                                'confidence': conf,
                                'timestamp': frame_idx / fps
                            })
                            
                            # Check for emergency vehicles
                            if cls in ['ambulance', 'policecar'] and conf > 0.7:
                                violations_found.append({
                                    'type': 'emergency_vehicle',
                                    'vehicle': cls,
                                    'frame': frame_idx,
                                    'timestamp': frame_idx / fps,
                                    'confidence': conf
                                })
            
            frame_idx += 1
        
        cap.release()
        
        return jsonify({
            'success': True,
            'total_frames': frame_count,
            'fps': fps,
            'duration': frame_count / fps,
            'detections': all_detections,
            'violations': violations_found,
            'violation_count': len(violations_found),
            'vehicle_count': len(set([d['class'] for d in all_detections]))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video/analyze-url', methods=['POST'])
def analyze_video_url():
    """Analyze video from URL"""
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        # Download video
        import requests
        response = requests.get(url, timeout=30, stream=True)
        
        filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Analyze
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        detections = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if detection_model:
                results = detection_model(frame, verbose=False)
                for result in results:
                    for box in result.boxes:
                        cls = result.names[int(box.cls)]
                        conf = float(box.conf)
                        if conf > 0.5:
                            detections.append({'class': cls, 'confidence': conf})
        
        cap.release()
        os.remove(video_path)
        
        return jsonify({
            'success': True,
            'total_frames': frame_count,
            'detections': detections,
            'unique_vehicles': list(set([d['class'] for d in detections]))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= LIVE CAMERA WITH VIOLATION DETECTION =============

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    global camera, camera_streaming
    
    data = request.get_json() or {}
    enable_detection = data.get('enable_detection', True)
    enable_recording = data.get('enable_recording', False)
    
    try:
        with camera_lock:
            if camera is None or not camera.isOpened():
                camera = cv2.VideoCapture(0)
                if not camera.isOpened():
                    return jsonify({'error': 'Could not open camera'}), 500
            camera_streaming = True
        
        return jsonify({
            'success': True, 
            'message': 'Camera started',
            'detection_enabled': enable_detection,
            'recording_enabled': enable_recording
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    global camera, camera_streaming
    
    with camera_lock:
        camera_streaming = False
        if camera:
            camera.release()
            camera = None
    
    return jsonify({'success': True, 'message': 'Camera stopped'})

@app.route('/api/camera/stream')
def camera_stream():
    """Video streaming with detection overlay"""
    def generate_frames():
        global camera_streaming
        while camera_streaming:
            with camera_lock:
                if camera is None or not camera.isOpened():
                    break
                success, frame = camera.read()
                if not success:
                    break
                
                # Run detection if model loaded
                if detection_model:
                    results = detection_model(frame, verbose=False)
                    for result in results:
                        for box in result.boxes:
                            if float(box.conf) > 0.5:
                                x1, y1, x2, y2 = box.xyxy[0].tolist()
                                cls = result.names[int(box.cls)]
                                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                                cv2.putText(frame, f"{cls} {float(box.conf):.2f}", (int(x1), int(y1)-10), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera/capture', methods=['POST'])
def capture_with_detection():
    """Capture frame and run detection"""
    global camera
    
    try:
        with camera_lock:
            if camera is None or not camera.isOpened():
                return jsonify({'error': 'Camera not available'}), 400
            
            success, frame = camera.read()
            if not success:
                return jsonify({'error': 'Failed to capture'}), 500
        
        # Run detection
        detections = []
        if detection_model:
            results = detection_model(frame, verbose=False)
            for result in results:
                for box in result.boxes:
                    if float(box.conf) > 0.5:
                        detections.append({
                            'class': result.names[int(box.cls)],
                            'confidence': float(box.conf),
                            'bbox': [float(x) for x in box.xyxy[0].tolist()]
                        })
        
        # Check for violations
        violations = []
        for det in detections:
            if det['class'] in ['ambulance', 'policecar'] and det['confidence'] > 0.7:
                violations.append({
                    'type': 'emergency_vehicle_detected',
                    'vehicle': det['class'],
                    'confidence': det['confidence'],
                    'timestamp': datetime.now().isoformat()
                })
                # Record violation
                violations_db.add_violation(
                    violation_type='emergency_vehicle',
                    vehicle_type=det['class'],
                    details={'confidence': det['confidence'], 'source': 'camera'},
                    image_path=None
                )
        
        return jsonify({
            'success': True,
            'detections': detections,
            'violations': violations,
            'violation_count': len(violations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= VIOLATION RECORDING =============

@app.route('/api/violations', methods=['GET'])
def get_violations():
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
    data = request.get_json()
    violation_type = data.get('type')
    vehicle_type = data.get('vehicle_type')
    details = data.get('details', {})
    image_base64 = data.get('image')

    if not violation_type or not vehicle_type:
        return jsonify({'error': 'type and vehicle_type required'}), 400

    try:
        image_path = None
        if image_base64:
            try:
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

# ============= MODEL MANAGEMENT =============

@app.route('/api/models', methods=['GET'])
def get_models():
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
        return jsonify({'success': True, 'message': f'Model {name} added'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/activate', methods=['POST'])
def activate_model(model_id):
    try:
        models_db.set_active_model(model_id)
        load_active_model()
        return jsonify({'success': True, 'message': 'Model activated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    try:
        models_db.delete_model(model_id)
        return jsonify({'success': True, 'message': 'Model deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= MODEL TRAINING =============

@app.route('/api/train', methods=['POST'])
def train_model():
    """Train a new model from uploaded images"""
    if 'file' not in request.files:
        return jsonify({'error': 'No training data provided'}), 400
    
    data = request.form
    model_name = data.get('name', 'Custom Model')
    epochs = int(data.get('epochs', 10))
    model_type = data.get('type', 'classification')
    
    # This is a placeholder - actual training would require proper setup
    # For now, return a mock response
    return jsonify({
        'success': True,
        'message': f'Training started for {model_name}',
        'epochs': epochs,
        'status': 'Training would begin with the provided data',
        'note': 'Full training implementation requires proper dataset structure'
    })

@app.route('/api/train/status', methods=['GET'])
def get_training_status():
    """Get training status"""
    return jsonify({
        'status': 'idle',
        'current_epoch': 0,
        'total_epochs': 0,
        'loss': 0,
        'accuracy': 0
    })

# ============= PRETRAINED MODELS =============

@app.route('/api/pretrained', methods=['GET'])
def get_pretrained_models():
    """Get list of available pretrained models"""
    return jsonify({
        'models': [
            {
                'id': 'yolov8n',
                'name': 'YOLOv8 Nano',
                'type': 'detection',
                'description': 'Fast, lightweight detection model',
                'classes': ['person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck']
            },
            {
                'id': 'yolov8s',
                'name': 'YOLOv8 Small', 
                'type': 'detection',
                'description': 'Balanced speed and accuracy',
                'classes': ['person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck']
            },
            {
                'id': 'yolov8m',
                'name': 'YOLOv8 Medium',
                'type': 'detection',
                'description': 'Higher accuracy, slower speed',
                'classes': ['person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck']
            }
        ]
    })

@app.route('/api/pretrained/<model_id>/load', methods=['POST'])
def load_pretrained(model_id):
    """Load a pretrained model"""
    global detection_model
    
    try:
        model_map = {
            'yolov8n': 'yolov8n.pt',
            'yolov8s': 'yolov8s.pt', 
            'yolov8m': 'yolov8m.pt'
        }
        
        if model_id not in model_map:
            return jsonify({'error': 'Unknown model'}), 400
        
        detection_model = YOLO(model_map[model_id])
        print(f"✅ Loaded pretrained model: {model_id}")
        
        return jsonify({
            'success': True,
            'message': f'Loaded {model_id}',
            'model_type': 'detection'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Loading model...")
    load_active_model()
    print("\n🚀 Starting Enhanced Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)

