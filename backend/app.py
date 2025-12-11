from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from pose_model import predict_pose_from_image, predict_pose_from_landmarks 

app = Flask(__name__)
app.secret_key = 'smart_yoga_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- YOGA POSES DATABASE (STRICT TAGS + DETAILED INFO) ---
YOGA_POSES_DATABASE = [
    # --- 1. STRESS SPECIALISTS ---
    {
        "id": "NadiShodhana", 
        "name": "Nadi Shodhana (Alternate Breathing)", 
        "img_url": "/static/poses/nadi_shoshana_pranayama.jpeg", 
        "tags": ['stress', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "A breathing technique to calm the nervous system and reduce anxiety.",
        "steps": ["Sit comfortably.", "Close right nostril, inhale left.", "Close left, exhale right.", "Inhale right, exhale left. Repeat."],
        "benefits": ["Lowers heart rate.", "Reduces stress and anxiety.", "Purifies energy channels."]
    },
    {
        "id": "Shavasana", 
        "name": "Savasana (Corpse Pose)", 
        "img_url": "/static/poses/shavasana.png", 
        "tags": ['stress', 'bp', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "A foundational resting pose to calm the mind and relax the body.",
        "steps": ["Lie flat on your back.", "Arms at sides, palms up.", "Close eyes and breathe deeply.", "Relax your entire body."],
        "benefits": ["Calms the brain.", "Relieves stress and depression.", "Lowers blood pressure."]
    },
    {
        "id": "Balasana", 
        "name": "Balasana (Child's Pose)", 
        "img_url": "/static/poses/balasana.jpeg", 
        "tags": ['stress', 'bp', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "A restorative pose that gently stretches the back and hips.",
        "steps": ["Kneel on floor, toes touching.", "Sit back on heels, separate knees.", "Lay torso down between thighs.", "Extend arms forward."],
        "benefits": ["Relieves back and neck pain.", "Calms the brain.", "Gently stretches hips and ankles."]
    },
    {
        "id": "ViparitaKarani", 
        "name": "Viparita Karani (Legs-Up-the-Wall)", 
        "img_url": "/static/poses/viparita_karani.jpeg", 
        "tags": ['stress', 'jp', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "A restorative pose that helps relieve tired legs and can reduce stress.",
        "steps": ["Sit sideways next to a wall.", "Swing legs up the wall as you lie back.", "Rest arms by sides.", "Relax for 5-15 mins."],
        "benefits": ["Relieves tired legs and feet.", "Calms the mind.", "Gently stretches back of neck."]
    },

    # --- 2. BACK PAIN SPECIALISTS ---
    {
        "id": "Marjariasana", 
        "name": "Marjariasana-Bitilasana (Cat-Cow)", 
        "img_url": "/static/poses/marjariasana_bitilasana.jpeg", 
        "tags": ['bp', 'stress', 'age_15_70', 'intensity_low', 'joint_friendly'],
        "description": "A dynamic flow that warms the spine and improves flexibility.",
        "steps": ["Start on hands and knees (tabletop).", "Inhale, drop belly, lift head (Cow).", "Exhale, round spine, tuck chin (Cat).", "Repeat 5-10 times."],
        "benefits": ["Improves posture.", "Strengthens spine and neck.", "Massages abdominal organs."]
    },
    {
        "id": "SetuBandhasana", 
        "name": "Setu Bandhasana (Bridge Pose)", 
        "img_url": "/static/poses/setu-bandhasana.jpg", 
        "tags": ['bp', 'age_15_70', 'intensity_low', 'intensity_medium'], 
        "description": "Strengthens the back, glutes, and legs while opening the chest.",
        "steps": ["Lie on back, knees bent, feet flat.", "Lift hips high toward ceiling.", "Interlace fingers under back.", "Hold for 30 seconds."],
        "benefits": ["Stretches chest and neck.", "Calms brain.", "Stimulates thyroid and lungs."]
    },
    {
        "id": "Bhujangasana", 
        "name": "Bhujangasana (Cobra Pose)", 
        "img_url": "/static/poses/Bhujangasana.jpg", 
        "tags": ['bp', 'age_15_70', 'intensity_low', 'intensity_medium'], 
        "description": "A backbend that increases spinal flexibility and strengthens back muscles.",
        "steps": ["Lie on stomach.", "Place hands under shoulders.", "Inhale, lift chest off floor.", "Keep shoulders down away from ears."],
        "benefits": ["Strengthens spine.", "Stretches chest and lungs.", "Soothes sciatica and asthma."]
    },
    {
        "id": "Salabhasana", 
        "name": "Shalabhasana (Locust Pose)", 
        "img_url": "/static/poses/Salabhasana.png", 
        "tags": ['bp', 'age_15_70', 'intensity_low'], 
        "description": "Strengthens the entire back of the body and improves posture.",
        "steps": ["Lie on belly, arms at sides.", "Inhale, lift head, chest, arms, and legs.", "Look forward.", "Hold for 30 seconds."],
        "benefits": ["Strengthens spine and buttocks.", "Stretches chest and shoulders.", "Improves posture."]
    },

    # --- 3. STOMACH PAIN SPECIALISTS ---
    {
        "id": "Pawanmuktasana", 
        "name": "Pawanmuktasana (Wind-Relieving Pose)", 
        "img_url": "/static/poses/pawanmuktasana.jpg", 
        "tags": ['st', 'bp', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "Massages abdominal organs, aids digestion, and relieves lower back pain.",
        "steps": ["Lie on back.", "Bring knees to chest.", "Clasp hands around legs.", "Rock gently side to side."],
        "benefits": ["Strengthens back.", "Massages intestines.", "Relieves gas and digestion issues."]
    },
    {
        "id": "Vajrasana", 
        "name": "Vajrasana (Thunderbolt Pose)", 
        "img_url": "/static/poses/vajrasana.jpeg", 
        "tags": ['st', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "A simple sitting pose that aids digestion and strengthens pelvic muscles.",
        "steps": ["Kneel on floor.", "Sit back on heels.", "Keep spine straight.", "Rest hands on knees. Hold for 5 mins."],
        "benefits": ["Aids digestion and acidity.", "Strengthens pelvic muscles.", "Calms the mind."]
    },
    {
        "id": "ArdhaMatsyendrasana", 
        "name": "Ardha Matsyendrasana (Half Fish Pose)", 
        "img_url": "/static/poses/Ardha_Matsyendrasana.jpeg", 
        "tags": ['st', 'obesity', 'age_15_70', 'intensity_low', 'joint_friendly'],
        "description": "A seated twist that energizes the spine and stimulates digestive organs.",
        "steps": ["Sit with legs straight.", "Bend right knee, place foot outside left thigh.", "Twist torso to the right.", "Look over shoulder. Repeat."],
        "benefits": ["Stimulates liver and kidneys.", "Energizes the spine.", "Relieves backache."]
    },
    
    # --- 4. JOINT PAIN & OBESITY SPECIALISTS ---
    {
        "id": "Tadasana", 
        "name": "Tadasana (Mountain Pose)", 
        "img_url": "/static/poses/tadasan.png", 
        "tags": ['jp', 'bp', 'obesity', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "The foundational standing pose that improves posture and body awareness.",
        "steps": ["Stand tall with feet together.", "Engage thigh muscles.", "Lengthen spine upward.", "Relax shoulders down."],
        "benefits": ["Improves posture.", "Strengthens thighs, knees, and ankles.", "Firms abdomen."]
    },
    {
        "id": "Vrikshasana", 
        "name": "Vrksasana (Tree Pose)", 
        "img_url": "/static/poses/vrikshasana.jpg", 
        "tags": ['jp', 'stress', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "A balancing pose for focus.",
        "steps": ["Stand tall.", "Place foot on inner thigh.", "Hands in prayer.", "Find focal point."],
        "benefits": ["Strengthens legs and spine.", "Improves balance.", "Stretches groins."]
    },
    {
        "id": "Virabhadrasana", 
        "name": "Virabhadrasana (Warrior Pose)", 
        "img_url": "/static/poses/virabhadrasana.jpg", 
        "tags": ['obesity', 'jp', 'age_15_70', 'intensity_medium'], 
        "description": "Builds strength and stamina in the legs and core, improving balance.",
        "steps": ["Step feet wide.", "Turn right foot out.", "Bend right knee.", "Raise arms parallel to floor.", "Gaze over hand."],
        "benefits": ["Strengthens legs and ankles.", "Stretches chest and lungs.", "Increases stamina."]
    },
    {
        "id": "Utkatasana", 
        "name": "Utkatasana (Chair Pose)", 
        "img_url": "/static/poses/utkasana.jpg", 
        "tags": ['obesity', 'jp', 'age_15_70', 'intensity_medium'], 
        "description": "A powerful pose that strengthens the legs, core, and arms.",
        "steps": ["Stand in Tadasana.", "Inhale arms up.", "Exhale, sit back as if in a chair.", "Hold, keeping back long."],
        "benefits": ["Strengthens ankles and thighs.", "Stretches shoulders.", "Stimulates heart and diaphragm."]
    },
    {
        "id": "SuryaNamaskar", 
        "name": "Surya Namaskar (Sun Salutation)", 
        "img_url": "/static/poses/surya_namaskar.jpg", 
        "tags": ['obesity', 'age_15_70', 'intensity_high'], 
        "description": "A sequence of poses that warms up the entire body, improves strength and flexibility.",
        "steps": ["Prayer pose.", "Raised arms.", "Forward fold.", "Lunge.", "Plank.", "Cobra.", "Downward Dog.", "Return to standing."],
        "benefits": ["Improves blood circulation.", "Tones muscles and weight loss.", "Calms mind and focus."]
    },
    
    # --- 5. FLEXIBILITY / GENERAL ---
    {
        "id": "Paschimottanasana", 
        "name": "Paschimottanasana (Seated Forward Bend)", 
        "img_url": "/static/poses/Paschimottanasana.jpeg", 
        "tags": ['stress', 'st', 'age_15_70', 'intensity_medium'], 
        "description": "An intense forward stretch that calms the brain and relieves stress.",
        "steps": ["Sit with legs straight.", "Inhale arms up.", "Exhale, fold forward from hips.", "Hold feet or shins."],
        "benefits": ["Calms the brain.", "Stretches spine and hamstrings.", "Stimulates liver and kidneys."]
    },
    {
        "id": "Katichakrasana", 
        "name": "Katichakrasana (Standing Twist)", 
        "img_url": "/static/poses/Kati_chakrasana.jpg", 
        "tags": ['bp', 'st', 'obesity', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "A simple standing twist that improves spinal flexibility.",
        "steps": ["Stand feet shoulder-width.", "Inhale, arms to sides.", "Exhale, twist waist right, hand to shoulder.", "Repeat left."],
        "benefits": ["Relieves constipation.", "Strengthens spine.", "Good for back stiffness."]
    },
    {
        "id": "ArdhaKatichakrasana", 
        "name": "Ardha Katichakrasana (Half Spinal Twist)", 
        "img_url": "/static/poses/Ardhakati_chakrasana.jpg", 
        "tags": ['bp', 'obesity', 'st', 'age_15_70', 'intensity_low', 'joint_friendly'], 
        "description": "A standing side-bending pose that stretches the sides of the body.",
        "steps": ["Stand straight.", "Raise right arm overhead.", "Bend torso to the left.", "Slide left hand down leg. Repeat."],
        "benefits": ["Reduces waist fat.", "Improves liver function.", "Relieves back pain."]
    },
    {
        "id": "Uttanasana", 
        "name": "Uttanasana (Standing Forward Bend)", 
        "img_url": "/static/poses/Uttanasana.png", 
        "tags": ['bp', 'stress', 'age_15_70', 'intensity_medium'],
        "description": "A calming pose that stretches the hamstrings and back.",
        "steps": ["Stand tall in Tadasana.", "Exhale, fold forward from hips.", "Place hands on floor or hold elbows.", "Relax head down."],
        "benefits": ["Calms brain.", "Stretches hamstrings and calves.", "Stimulates liver and kidneys."]
    },

  # --- 6. YOUNGER / HIGH INTENSITY ONLY (Fully Detailed) ---
    {
        "id": "Sirsasana", 
        "name": "Sirsasana (Headstand)", 
        "img_url": "/static/poses/Sirsasana.jpg", 
        "tags": ['stress', 'age_15_30', 'intensity_high'], 
        "description": "Known as the king of asanas, this advanced inversion calms the brain and strengthens the body.", 
        "steps": [
            "Kneel on the floor and interlace your fingers to form a cup.",
            "Place the crown of your head on the floor, cradled by your hands.",
            "Lift your hips and walk your feet towards your face.",
            "Engage your core and slowly lift your legs up towards the ceiling."
        ], 
        "benefits": [
            "Calms the brain and relieves stress and mild depression.",
            "Strengthens the arms, legs, and spine.",
            "Stimulates the pituitary and pineal glands.",
            "Improves digestion."
        ]
    },
    {
        "id": "Bakasana", 
        "name": "Bakasana (Crow Pose)", 
        "img_url": "/static/poses/bakasana5.jpg", 
        "tags": ['stress', 'obesity', 'age_15_30', 'intensity_high'], 
        "description": "An arm balance that builds strength in the arms and wrists while improving focus.", 
        "steps": [
            "Squat down with feet together and knees wide apart.",
            "Place hands on the floor shoulder-width apart.",
            "Place your knees on the backs of your upper arms (triceps).",
            "Lean forward, shifting weight onto your hands, and lift your feet off the floor."
        ], 
        "benefits": [
            "Strengthens arms and wrists.",
            "Stretches the upper back.",
            "Strengthens the abdominal muscles.",
            "Opens the groins."
        ]
    },
    {
        "id": "Vasisthasana", 
        "name": "Vasisthasana (Side Plank Pose)", 
        "img_url": "/static/poses/vasisthasana.png", 
        "tags": ['stress', 'obesity', 'age_15_30', 'intensity_high'], 
        "description": "A powerful balancing pose that strengthens the arms, wrists, and core.", 
        "steps": [
            "Start in a standard plank pose.",
            "Shift weight onto your right hand and roll onto the outer edge of your right foot.",
            "Stack your left foot on top of your right.",
            "Lift your left arm toward the ceiling and look up."
        ], 
        "benefits": [
            "Strengthens the arms, belly, and legs.",
            "Stretches and strengthens the wrists.",
            "Stretches the backs of the legs.",
            "Improves sense of balance."
        ]
    },
    {
        "id": "Purvottanasana", 
        "name": "Purvottanasana (Upward Plank Pose)", 
        "img_url": "/static/poses/Purvottanasana.png", 
        "tags": ['bp', 'stress', 'age_15_30', 'intensity_high'], 
        "description": "An intense stretch for the front body that strengthens the back, arms, and wrists.", 
        "steps": [
            "Sit with legs extended in front of you.",
            "Place hands behind your hips, fingers pointing forward.",
            "Press into your hands and feet to lift your hips high.",
            "Gently drop your head back if comfortable."
        ], 
        "benefits": [
            "Strengthens the arms, wrists, and legs.",
            "Stretches the shoulders, chest, and front ankles.",
            "Frees the mind and helps relieve fatigue."
        ]
    },
    {
        "id": "Mayurasana", 
        "name": "Mayurasana (Peacock Pose)", 
        "img_url": "/static/poses/Mayurasana.png", 
        "tags": ['bp', 'st', 'age_15_30', 'intensity_high'], 
        "description": "An advanced arm balance that strongly detoxifies the body and improves digestion.", 
        "steps": [
            "Kneel on the floor, knees wide.",
            "Place hands on the floor with fingers pointing backwards towards your feet.",
            "Bend elbows and press them into your belly button.",
            "Lean forward and lift legs off the ground, balancing on your hands."
        ], 
        "benefits": [
            "Detoxifies the body.",
            "Strengthens digestive organs and aids digestion.",
            "Strengthens wrists and forearms.",
            "Tones the abdomen."
        ]
    },
    {
        "id": "Sarvangasana", 
        "name": "Sarvangasana (Shoulder Stand)", 
        "img_url": "/static/poses/Sarvangasana.jpg", 
        "tags": ['stress', 'obesity', 'bp', 'age_15_30', 'intensity_medium'], 
        "description": "The 'Queen of Asanas', this inversion helps regulate metabolism and calms the nerves.", 
        "steps": [
            "Lie on your back with arms by your sides.",
            "Lift your legs, buttocks, and back off the floor.",
            "Support your lower back with your hands.",
            "Straighten your legs and spine upwards. Rest weight on shoulders, not neck."
        ], 
        "benefits": [
            "Calms the brain and helps relieve stress and mild depression.",
            "Stimulates the thyroid and prostate glands.",
            "Stretches the shoulders and neck.",
            "Tones the legs and buttocks."
        ]
    },
    {
        "id": "Malasana", 
        "name": "Malasana (Garland Pose)", 
        "img_url": "/static/poses/malasana1.jpeg", 
        "tags": ['obesity', 'st', 'age_15_50', 'intensity_medium', 'gender_female'], 
        "description": "A deep squat that opens the hips and is excellent for pelvic health.", 
        "steps": [
            "Squat with your feet as close together as possible. Keep heels on floor if possible.",
            "Separate your thighs slightly wider than your torso.",
            "Lean your torso forward and fit it snugly between your thighs.",
            "Bring palms together in prayer position and press elbows against inner knees."
        ], 
        "benefits": [
            "Stretches the ankles, groins, and back torso.",
            "Tones the belly.",
            "Improves function of the colon.",
            "Relieves back pain."
        ]
    }
]

# --- USER DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES ---
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('main_dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
            conn.commit()
            return jsonify({'success': True, 'message': 'Account created! Redirecting to login...'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Email already exists!'})
        finally:
            conn.close()
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return jsonify({'success': True, 'redirect_url': url_for('main_dashboard')})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'})
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/main')
def main_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('main.html', user_name=session['user_name'])

# --- 1. PREDICT FROM IMAGE UPLOAD (Unrestricted) ---
@app.route('/predict', methods=['POST'])
def predict():
    if 'mediaUpload' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['mediaUpload']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    predicted_pose_name, confidence = predict_pose_from_image(filepath)
    
    # NO CONFIDENCE RESTRICTION HERE - Always returns result
    
    pose_details = None
    normalized_pred = predicted_pose_name.lower().replace(" ", "").replace("_", "")
    
    for pose in YOGA_POSES_DATABASE:
        normalized_id = pose['id'].lower().replace(" ", "").replace("_", "")
        if normalized_id == normalized_pred:
            pose_details = pose
            break
    
    if pose_details:
        response_data = {
            'name': pose_details['name'],
            'description': pose_details['description'],
            'img_url': pose_details['img_url'],
            'steps': pose_details.get('steps', []),
            'benefits': pose_details.get('benefits', [])
        }
    else:
        response_data = {
            'name': predicted_pose_name,
            'description': "Pose detected.",
            'img_url': "",
            'steps': [],
            'benefits': []
        }

    return jsonify({
        'success': True,
        'pose_data': response_data,
        'confidence': f"{confidence:.2f}%"
    })

# --- 2. LIVE PREDICTION API ---
@app.route('/predict_live', methods=['POST'])
def predict_live():
    data = request.get_json()
    landmarks = data['landmarks']
    
    predicted_pose_name, confidence = predict_pose_from_landmarks(landmarks)
    
    if predicted_pose_name.lower() == 'other':
        return jsonify({'success': True, 'pose_name': 'No Pose Detected', 'confidence': confidence})
    
    if confidence < 50.0:
        return jsonify({'success': True, 'pose_name': 'No Pose Detected', 'confidence': confidence})
    
    normalized_prediction = predicted_pose_name.lower().replace(" ", "").replace("_", "")
    pose_name_for_display = predicted_pose_name 
    
    for pose in YOGA_POSES_DATABASE:
        normalized_id = pose['id'].lower().replace(" ", "").replace("_", "")
        if normalized_id == normalized_prediction: # FIXED: Changed normalized_pred to normalized_prediction
            pose_name_for_display = pose['name'].split('(')[0].strip()
            break
            
    return jsonify({'success': True, 'pose_name': pose_name_for_display, 'confidence': confidence})

# --- 3. RECOMMENDATION ENGINE ---
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_disorders = data.get('disorders', [])
    age_group = data.get('age')
    pain_level = data.get('painLevel')
    bmi = float(data.get('bmi', 0))

    recommended_poses = []
    
    # Filter 1: Disorders
    for pose in YOGA_POSES_DATABASE:
        for disorder in user_disorders:
            tag = ''
            if disorder == 'Back Pain': tag = 'bp'
            elif disorder == 'Stress': tag = 'stress'
            elif disorder == 'Obesity': tag = 'obesity'
            elif disorder == 'Joint Pain': tag = 'jp'
            elif disorder == 'Stomach Pain': tag = 'st'
            
            if tag in pose['tags']:
                if pose not in recommended_poses:
                    recommended_poses.append(pose)
                break 
    
    # Filter 2: Age & Pain Level
    filtered_poses = []
    for pose in recommended_poses:
        if age_group == '31-50' and 'age_15_30' in pose['tags']:
            continue
        elif age_group == '51-70' and 'age_15_70' not in pose['tags']:
            continue

        if pain_level == 'High':
            if 'intensity_medium' in pose['tags'] or 'intensity_high' in pose['tags']:
                continue
        elif pain_level == 'Moderate':
            if 'intensity_high' in pose['tags']:
                continue
            
        filtered_poses.append(pose)
        
    # Filter 3: BMI Check
    final_poses = []
    if bmi >= 25:
        for pose in filtered_poses:
            if 'joint_friendly' in pose['tags']:
                final_poses.append(pose)
    else:
        final_poses = filtered_poses

    return jsonify({'success': True, 'recommendations': final_poses})

if __name__ == '__main__':
    app.run(debug=True)