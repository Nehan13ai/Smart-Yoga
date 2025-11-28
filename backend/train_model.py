import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import pickle

def train_classifier(dataset_csv_path, model_output_path):
    """Trains an SVM classifier and saves the model."""
    df = pd.read_csv(dataset_csv_path)
    
    X = df.drop('class', axis=1)
    y = df['class']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    
    # Use .values to train the scaler on nameless data
    X_train_scaled = scaler.fit_transform(X_train.values) 
    X_test_scaled = scaler.transform(X_test.values)
    
    print("Training SVM (SVC) model...")
    svm_model = SVC(kernel='rbf', C=10, gamma='scale', probability=True, random_state=42)
    
    svm_model.fit(X_train_scaled, y_train)
    
    y_pred = svm_model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    
    model_pipeline = {
        'scaler': scaler,
        'model': svm_model
    }
    
    with open(model_output_path, 'wb') as f:
        pickle.dump(model_pipeline, f)
    print(f"Model and scaler saved to {model_output_path}")

if __name__ == '__main__':
    DATASET_CSV = 'yoga_poses_landmarks.csv'
    MODEL_PATH = 'models/yoga_pose_classifier.pkl'
    train_classifier(DATASET_CSV, MODEL_PATH)