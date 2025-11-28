import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- 1. Define the 7 specialist classes ---
# These must match the 'id' names in your database and folder names
LIVE_CLASSES = [
    'Ardha Matsyendrasana', 'Balasana', 'Bhujangasana', 'Shavasana',
    'tadasana', 'Vajrasana', 'Other'
]
live_classes_normalized = [c.lower().replace(' ', '').replace('_', '') for c in LIVE_CLASSES]

print("Loading main dataset: yoga_poses_landmarks.csv")

# Check if the dataset file exists
if not os.path.exists('yoga_poses_landmarks.csv'):
    print("Error: 'yoga_poses_landmarks.csv' not found.")
    print("Please make sure you are in the 'backend' directory.")
    exit()
    
df = pd.read_csv('yoga_poses_landmarks.csv')

# --- 2. Filter for the 7 specialist classes ---
df['class_normalized'] = df['class'].str.lower().str.replace(' ', '').replace('_', '')
live_df = df[df['class_normalized'].isin(live_classes_normalized)].copy()

if live_df.empty:
    print("Error: Could not find any of the specified live classes in the dataset.")
    print("Please check the LIVE_CLASSES list and your dataset folder names.")
    exit()
    
print(f"Filtered to {len(live_df)} samples for the 7 live classes.")
print(f"Classes found: {live_df['class'].unique()}")

X = live_df.drop(['class', 'class_normalized'], axis=1)
y = live_df['class']

# --- 3. Re-create the exact same test data split ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train.values)
X_test_scaled = scaler.transform(X_test.values)

# --- 4. Load the specialist model ---
model_path = 'models/yoga_pose_live_classifier.pkl'
if not os.path.exists(model_path):
    print(f"Error: Model file not found at {model_path}")
    print("Please make sure you have run train_live_model.py")
    exit()

print(f"Loading specialist live model from {model_path}...")
with open(model_path, 'rb') as f:
    model_pipeline = pickle.load(f)
model = model_pipeline['model']

# --- 5. Make predictions ---
print("Generating predictions on the test set...")
y_pred = model.predict(X_test_scaled)

# --- 6. Generate and plot the Confusion Matrix ---
class_names = sorted(y.unique())
cm = confusion_matrix(y_test, y_pred, labels=class_names)

print("Plotting heatmap...")
plt.figure(figsize=(10, 8))
# --- CHANGE THIS LINE ---
sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu', # <-- This is the new, elegant one
            xticklabels=class_names, yticklabels=class_names, annot_kws={"size": 16})

# Use your actual specialist model accuracy here if it's different
plt.title('Confusion Matrix for Specialist Live Model (96.94% Accuracy)', fontsize=16) 
plt.ylabel('Actual Pose (True Label)', fontsize=12)
plt.xlabel('Predicted Pose (Model Guess)', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(rotation=0, fontsize=10)
plt.tight_layout()

# --- 7. Save the figure ---
output_filename = 'specialist_model_confusion_matrix.png'
plt.savefig(output_filename)
print(f"\nSuccess! Heatmap saved to your backend folder as: {output_filename}")