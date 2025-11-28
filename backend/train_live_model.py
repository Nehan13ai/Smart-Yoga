import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import pickle

# --- SETTINGS FOR THE LIVE MODEL ---
DATASET_CSV = 'yoga_poses_landmarks.csv' 
MODEL_OUTPUT_PATH = 'models/yoga_pose_live_classifier.pkl' 

# --- UPDATED LIST: Now contains 9 classes (7 poses + Other) ---
LIVE_CLASSES = [
    'Ardha Matsyendrasana', 
    'Balasana', 
    'Bhujangasana', 
    'Shavasana',
    'tadasana', 
    'Vajrasana', 
    'paschimottanasana',  # <-- ADDED
    'uttanasana',         # <-- ADDED
    'Other' 
]

def train_live_classifier(dataset_csv_path, model_output_path):
    """Trains a specialist SVM classifier for live poses."""
    
    df = pd.read_csv(dataset_csv_path)
    
    # --- Filter the DataFrame to ONLY include our 9 live classes ---
    # Normalize class names for robust matching (e.g., 'Other' matches 'other')
    live_classes_normalized = [c.lower().replace(' ', '').replace('_','') for c in LIVE_CLASSES]
    df['class_normalized'] = df['class'].str.lower().str.replace(' ', '').str.replace('_', '')
    
    live_df = df[df['class_normalized'].isin(live_classes_normalized)].copy()
    
    if live_df.empty:
        print("Error: Could not find any of the specified live classes in the dataset.")
        print("Please check the LIVE_CLASSES list and your dataset folder names.")
        return

    print(f"Creating specialist model with {len(live_df)} samples from {len(live_df['class'].unique())} classes:")
    print(live_df['class'].unique())

    X = live_df.drop(['class', 'class_normalized'], axis=1)
    y = live_df['class']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train.values) 
    X_test_scaled = scaler.transform(X_test.values)
    
    print("Training Specialist SVM (SVC) model...")
    svm_model = SVC(kernel='rbf', C=10, gamma='scale', probability=True, random_state=42)
    
    svm_model.fit(X_train_scaled, y_train)
    
    y_pred = svm_model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Specialist Model Accuracy: {accuracy * 100:.2f}%")
    
    model_pipeline = {
        'scaler': scaler,
        'model': svm_model
    }
    
    with open(model_output_path, 'wb') as f:
        pickle.dump(model_pipeline, f)
    print(f"Specialist model saved to {model_output_path}")

if __name__ == '__main__':
    train_live_classifier(DATASET_CSV, MODEL_OUTPUT_PATH)