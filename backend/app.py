from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from pose_model import predict_pose_from_image, predict_pose_from_landmarks 

app = Flask(__name__)
app.secret_key = 'a_very_secret_key_that_you_should_change'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- YOGA POSES DATABASE (Unchanged) ---
YOGA_POSES_DATABASE = [
    {"id": "Shavasana", "name": "Savasana (Corpse Pose)", "img_url": "/static/poses/shavasana.png", "description": "A foundational resting pose to calm the mind and relax the body.", "tags": ['bp', 'stress', 'jp', 'age_15_70', 'intensity_low', 'intensity_medium', 'intensity_high', 'joint_friendly']},
    {"id": "Pawanmuktasana", "name": "Pawanmuktasana / Apanasana (Wind-Relieving Pose)", "img_url": "/static/poses/pawanmuktasana.jpg", "description": "Massages abdominal organs, aids digestion, and relieves lower back pain.", "tags": ['bp', 'jp', 'obesity', 'stress', 'st', 'age_15_70', 'intensity_low', 'intensity_medium', 'intensity_high', 'joint_friendly']},
    {"id": "Marjariasana bitilasana", "name": "Marjariasana-Bitilasana (Cat-Cow)", "img_url": "/static/poses/marjariasana_bitilasana.jpeg", "description": "A dynamic flow that warms the spine and improves flexibility.", "tags": ['stress', 'jp', 'bp', 'age_15_70', 'intensity_low', 'intensity_medium', 'gender_female', 'joint_friendly']},
    {"id": "Setu Bandhasana", "name": "Setu Bandhasana (Bridge Pose)", "img_url": "/static/poses/setu-bandhasana.jpg", "description": "Strengthens the back, glutes, and legs while opening the chest.", "tags": ['stress', 'obesity', 'bp', 'jp', 'age_15_50', 'intensity_low', 'intensity_medium']},
    {"id": "Bhujangasana", "name": "Bhujangasana (Cobra Pose)", "img_url": "/static/poses/Bhujangasana.jpg", "description": "A backbend that increases spinal flexibility and strengthens back muscles.", "tags": ['stress', 'obesity', 'bp', 'st', 'age_15_50', 'intensity_low', 'intensity_medium', 'joint_friendly']},
    {"id": "Salabhasana", "name": "Shalabhasana (Locust Pose)", "img_url": "/static/poses/Salabhasana.png", "description": "Strengthens the entire back of the body and improves posture.", "tags": ['bp', 'obesity', 'st', 'age_15_50', 'intensity_low']},
    {"id": "Vajrasana", "name": "Vajrasana (Thunderbolt Pose)", "img_url": "/static/poses/vajrasana.jpeg", "description": "A simple sitting pose that aids digestion and strengthens pelvic muscles.", "tags": ['stress', 'bp', 'st', 'age_15_70', 'intensity_low', 'intensity_medium', 'joint_friendly']},
    {"id": "Balasana", "name": "Balasana (Child's Pose)", "img_url": "/static/poses/balasana.jpeg", "description": "A restorative pose that gently stretches the back, hips, and ankles.", "tags": ['stress', 'st', 'bp', 'age_15_50', 'intensity_low', 'intensity_medium', 'intensity_high', 'joint_friendly']},
    {"id": "Ardha Matsyendrasana", "name": "Ardha Matsyendrasana (Half Lord of the Fishes)", "img_url": "/static/poses/Ardha_Matsyendrasana.jpeg", "description": "A seated twist that energizes the spine and stimulates digestive organs.", "tags": ['obesity', 'stress', 'st', 'age_15_50', 'intensity_low', 'joint_friendly']},
    {"id": "Malasana", "name": "Malasana (Garland Pose)", "img_url": "/static/poses/malasana1.jpeg", "description": "A deep squat that stretches the hips, groin, and lower back.", "tags": ['obesity', 'st', 'age_15_50', 'intensity_low', 'intensity_medium', 'gender_female']},
    {"id": "Viparita karani", "name": "Viparita Karani (Legs-Up-the-Wall Pose)", "img_url": "/static/poses/viparita_karani.jpeg", "description": "A restorative pose that helps relieve tired legs and can reduce stress.", "tags": ['stress', 'jp', 'bp', 'st', 'age_15_70', 'intensity_low', 'intensity_medium', 'intensity_high', 'gender_female', 'joint_friendly']},
    {"id": "paschimottanasana", "name": "Paschimottanasana (Seated Forward Bend)", "img_url": "/static/poses/Paschimottanasana.jpeg", "description": "An intense forward stretch that calms the brain and relieves stress.", "tags": ['st', 'obesity', 'stress', 'age_15_30', 'intensity_low', 'intensity_medium']},
    {"id": "Nadi Shodhana Pranayama", "name": "Nadi Shodhana Pranayama (Alternate Nostril Breathing)", "img_url": "/static/poses/nadi_shoshana_pranayama.jpeg", "description": "A breathing technique to calm the nervous system and reduce anxiety.", "tags": ['stress', 'obesity', 'bp', 'age_15_70', 'intensity_low', 'intensity_medium', 'intensity_high', 'joint_friendly']},
    {"id": "tadasana", "name": "Tadasana (Mountain Pose)", "img_url": "/static/poses/tadasan.png", "description": "The foundational standing pose that improves posture and body awareness.", "tags": ['stress', 'obesity', 'jp', 'bp', 'age_15_70', 'intensity_low', 'intensity_medium', 'intensity_high', 'gender_female', 'joint_friendly']},
    {"id": "Surya Namaskar", "name": "Surya Namaskar (Sun Salutation)", "img_url": "/static/poses/surya_namaskar.jpg", "description": "A sequence of poses that warms up the entire body, improves strength and flexibility.", "tags": ['stress', 'obesity', 'st', 'jp', 'bp', 'age_15_70', 'intensity_low', 'intensity_medium']},
    {"id": "virabhadrasana", "name": "Virabhadrasana (Warrior Pose)", "img_url": "/static/poses/virabhadrasana.jpg", "description": "Builds strength and stamina in the legs and core, improving balance.", "tags": ['jp', 'stress', 'obesity', 'bp', 'age_15_50', 'intensity_low', 'intensity_medium']},
    {"id": "utkatasana", "name": "Utkatasana (Chair Pose)", "img_url": "/static/poses/utkasana.jpg", "description": "A powerful pose that strengthens the legs, core, and arms.", "tags": ['stress', 'obesity', 'bp', 'age_15_50', 'intensity_low', 'intensity_medium']},
    {"id": "sirsasana", "name": "Sirsasana (Headstand)", "img_url": "/static/poses/Sirsasana.jpg", "description": "An advanced inversion that calms the brain and strengthens the upper body.", "tags": ['stress', 'age_15_30', 'intensity_low']},
    {"id": "bakasana", "name": "Bakasana (Crow Pose)", "img_url": "/static/poses/bakasana5.jpg", "description": "An arm balance that strengthens the arms and wrists, and improves core strength.", "tags": ['stress', 'obesity', 'age_15_30', 'intensity_low']},
    {"id": "vasisthasana", "name": "Vasisthasana (Side Plank Pose)", "img_url": "/static/poses/vasisthasana.png", "description": "Strengthens the arms, wrists, core, and legs. Improves balance.", "tags": ['stress', 'obesity', 'age_15_30', 'intensity_low']},
    {"id": "purvottanasana", "name": "Purvottanasana (Upward Plank Pose)", "img_url": "/static/poses/Purvottanasana.png", "description": "A powerful pose that strengthens the back, arms, and legs.", "tags": ['bp', 'stress', 'age_15_30', 'intensity_low']},
    {"id": "mayurasana", "name": "Mayurasana (Peacock Pose)", "img_url": "/static/poses/Mayurasana.png", "description": "An advanced arm balance that detoxifies the body and strengthens digestion.", "tags": ['bp', 'st', 'age_15_30', 'intensity_low']},
    {"id": "Vrikshasana", "name": "Vrksasana (Tree Pose)", "img_url": "/static/poses/vrikshasana.jpg", "description": "A balancing pose that improves focus and concentration.", "tags": ['jp', 'stress', 'bp', 'age_15_50', 'intensity_low', 'intensity_medium']},
    {"id": "Sarvangasana_", "name": "Sarvangasana (Shoulder Stand)", "img_url": "/static/poses/Sarvangasana.jpg", "description": "A calming inversion that can help regulate metabolism.", "tags": ['stress', 'obesity', 'bp', 'age_15_30', 'intensity_low']},
    {"id": "Kati chakrasana", "name": "Katichakrasana (Standing Spinal Twist)", "img_url": "/static/poses/Kati_chakrasana.jpg", "description": "A simple standing twist that improves spinal flexibility.", "tags": ['stress', 'obesity', 'st', 'age_15_70', 'intensity_low', 'intensity_medium', 'intensity_high', 'joint_friendly']},
    {"id": "Ardhakati chakrasana", "name": "Ardha Katichakrasana (Half Spinal Twist)", "img_url": "/static/poses/Ardhakati_chakrasana.jpg", "description": "A standing side-bending pose that stretches the sides of the body.", "tags": ['stress', 'obesity', 'st', 'jp', 'bp', 'age_15_70', 'intensity_low', 'intensity_medium', 'joint_friendly']},
    {"id": "uttanasana", "name": "Uttanasana (Standing Forward Bend)", "img_url": "/static/poses/Uttanasana.png", "description": "A calming pose that stretches the hamstrings and back.", "tags": ['bp', 'stress', 'age_15_30', 'intensity_low', 'intensity_medium']},
]

# --- Database Helper Functions (Unchanged) ---
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- User Auth Routes (Unchanged) ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main_app'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return jsonify({'success': True, 'redirect_url': url_for('main_app')})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password.'})

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (name, email, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Signup successful! Please login.'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email address already registered.'})

@app.route('/main')
def main_app():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('main.html', user_name=session.get('user_name'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))

# --- Image Upload Prediction Route (Unchanged) ---
@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    if 'mediaUpload' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['mediaUpload']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        predicted_pose_name, confidence = predict_pose_from_image(filepath)
        os.remove(filepath) 
        
        if predicted_pose_name.lower() == 'other':
            return jsonify({
                'success': False,
                'error': f'No yoga pose was detected in the image. (Confidence: {confidence:.2f}%)'
            })
        
        CONFIDENCE_THRESHOLD = 50.0 # This remains 50% for high-quality uploads
        if confidence < CONFIDENCE_THRESHOLD:
            return jsonify({'success': False, 'error': f'Could not identify pose with high confidence. (Confidence: {confidence:.2f}%)'})
        
        pose_details = None
        normalized_prediction = predicted_pose_name.lower().replace(" ", "").replace("_", "")
        for pose in YOGA_POSES_DATABASE:
            normalized_id = pose['id'].lower().replace(" ", "").replace("_", "")
            if normalized_id == normalized_prediction:
                pose_details = pose
                break
        
        if pose_details:
            return jsonify({'success': True, 'pose_data': pose_details, 'confidence': f"{confidence:.2f}%"})
        else:
            return jsonify({'success': False, 'error': f"Pose '{predicted_pose_name}' recognized but not found in the information database."})

# --- Recommendation Route (Unchanged) ---
@app.route('/recommend', methods=['POST'])
def recommend():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    age_group = data.get('age')
    sex = data.get('sex')
    pain_level = data.get('painLevel')
    disorders = data.get('disorders', [])
    bmi = float(data.get('bmi', 0))

    if not all([age_group, sex, pain_level, disorders]):
        return jsonify({'success': False, 'error': 'Missing required information.'})

    disorder_map = {"Back Pain": "bp", "Joint Pain": "jp", "Stomach Pain": "st", "Stress": "stress", "Obesity": "obesity"}
    required_disorder_tags = {disorder_map[d] for d in disorders}

    valid_age_tags = set()
    if age_group == "15-30":
        valid_age_tags.update(["age_15_30", "age_15_50", "age_15_70"])
    elif age_group == "31-50":
        valid_age_tags.update(["age_15_50", "age_15_70"])
    elif age_group == "51-70":
        valid_age_tags.add("age_15_70")
    
    valid_intensity_tags = set()
    if pain_level == 'High':
        valid_intensity_tags.add('intensity_low')
    elif pain_level == 'Moderate':
        valid_intensity_tags.update(['intensity_low', 'intensity_medium'])
    else: # Low
        valid_intensity_tags.update(['intensity_low', 'intensity_medium', 'intensity_high'])

    candidate_poses = []
    for pose in YOGA_POSES_DATABASE:
        pose_tags = set(pose['tags'])
        if not required_disorder_tags.intersection(pose_tags) and 'all' not in pose_tags:
            continue
        if not valid_age_tags.intersection(pose_tags):
            continue
        if not valid_intensity_tags.intersection(pose_tags):
            continue
        if sex == "Male" and pose.get('gender') == 'Female Only': 
             continue
        candidate_poses.append(pose)

    final_recommendations = []
    if bmi >= 25:
        for pose in candidate_poses:
            if 'joint_friendly' in pose['tags']:
                final_recommendations.append(pose)
    else:
        final_recommendations = candidate_poses
    
    if not final_recommendations and bmi >= 25:
        final_recommendations = [pose for pose in YOGA_POSES_DATABASE if 'joint_friendly' in pose['tags']]

    return jsonify({'success': True, 'recommendations': final_recommendations})


# --- *** LIVE PREDICTION ROUTE (with Threshold changed to 50%) *** ---
@app.route('/predict_live', methods=['POST'])
def predict_live():
    """Receives landmarks from client, returns pose prediction."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data or 'landmarks' not in data:
        return jsonify({'success': False, 'error': 'No landmark data received.'})
    
    landmarks = data['landmarks']
    
    predicted_pose_name, confidence = predict_pose_from_landmarks(landmarks)
    
    # We will keep the print statement for now, it's good for debugging.
    print(f"RAW PREDICTION: {predicted_pose_name}, CONFIDENCE: {confidence:.2f}%")

    # Check for "Other" class first
    if predicted_pose_name.lower() == 'other':
        return jsonify({
            'success': True, 
            'pose_name': 'No Pose Detected',
            'confidence': confidence
        })
    
    # --- THIS IS THE FIX ---
    # We set the threshold back to 50% as you requested.
    CONFIDENCE_THRESHOLD = 50.0 
    if confidence < CONFIDENCE_THRESHOLD:
        return jsonify({
            'success': True, 
            'pose_name': 'No Pose Detected',
            'confidence': confidence
        })
    
    # Check against database to get the proper name
    pose_name_for_display = "Unknown Pose"
    normalized_prediction = predicted_pose_name.lower().replace(" ", "").replace("_", "")
    for pose in YOGA_POSES_DATABASE:
        normalized_id = pose['id'].lower().replace(" ", "").replace("_", "")
        if normalized_id == normalized_prediction:
            pose_name_for_display = pose['name'].split('(')[0].strip()
            break
            
    return jsonify({
        'success': True,
        'pose_name': pose_name_for_display,
        'confidence': confidence
    })

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True)