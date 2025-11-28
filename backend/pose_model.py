import cv2
import mediapipe as mp
import numpy as np
import pickle

# --- Load the MAIN UPLOAD Model ---
try:
    with open('models/yoga_pose_classifier.pkl', 'rb') as f:
        main_model_pipeline = pickle.load(f)
    main_scaler = main_model_pipeline['scaler']
    main_model = main_model_pipeline['model']
    print("Main model loaded successfully (for uploads).")
except FileNotFoundError:
    print("Error: Main model (yoga_pose_classifier.pkl) not found.")
    main_model = None
    main_scaler = None

# --- *** NEW: Load the LIVE WEBCAM Model *** ---
try:
    with open('models/yoga_pose_live_classifier.pkl', 'rb') as f:
        live_model_pipeline = pickle.load(f)
    live_scaler = live_model_pipeline['scaler']
    live_model = live_model_pipeline['model']
    print("Specialist LIVE model loaded successfully (for webcam).")
except FileNotFoundError:
    print("Error: LIVE model (yoga_pose_live_classifier.pkl) not found. Run train_live_model.py")
    live_model = None
    live_scaler = None


mp_pose = mp.solutions.pose
pose_static = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)


# --- Function for Image Uploads (Uses MAIN model) ---
def predict_pose_from_image(image_path):
    if not main_model or not main_scaler:
        return "Main model not loaded", 0.0
    try:
        image = cv2.imread(image_path)
        if image is None: return "Error reading image", 0.0
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose_static.process(image_rgb)
        if not results.pose_landmarks: return "No pose detected", 0.0
        
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
        
        landmarks_array = np.array(landmarks).reshape(1, -1)
        # Use the MAIN scaler and model
        landmarks_scaled = main_scaler.transform(landmarks_array)
        prediction = main_model.predict(landmarks_scaled)
        probability = main_model.predict_proba(landmarks_scaled)
        pose_name = prediction[0]
        confidence = np.max(probability) * 100
        return pose_name, confidence
        
    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        return f"Prediction error: {e}", 0.0

# --- Function for Live Landmarks (Uses LIVE model) ---
def predict_pose_from_landmarks(landmark_list):
    if not live_model or not live_scaler:
        return "Live model not loaded", 0.0
    
    try:
        landmarks_array = np.array(landmark_list).reshape(1, -1)
        # Use the LIVE scaler and model
        landmarks_scaled = live_scaler.transform(landmarks_array)
        prediction = live_model.predict(landmarks_scaled)
        probability = live_model.predict_proba(landmarks_scaled)
        
        pose_name = prediction[0]
        confidence = np.max(probability) * 100
        return pose_name, confidence
        
    except Exception as e:
        print(f"Error in predict_pose_from_landmarks: {e}")
        return f"Prediction error: {e}", 0.0