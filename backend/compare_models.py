import pandas as pd
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# --- Import all 7 models we want to compare ---
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB

def run_model_comparison(dataset_csv_path):
    """
    Loads data, trains 7 different models, and prints a comparison
    of their accuracy and training time.
    """
    
    # --- 1. Load and Prepare Data ---
    print(f"Loading dataset: {dataset_csv_path}")
    df = pd.read_csv(dataset_csv_path)

    X = df.drop('class', axis=1)
    y = df['class']

    # Use the same data split for a fair comparison
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Scale the data (using .values to avoid feature name warnings)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train.values)
    X_test_scaled = scaler.transform(X_test.values)

    print(f"Data prepared: {len(X_train)} training samples, {len(X_test)} testing samples.")

    # --- 2. Define All Models ---
    models = {
        "SVM (SVC)": SVC(kernel='rbf', C=10, gamma='scale', probability=True, random_state=42),
        
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        
        "Neural Network (MLP)": MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, alpha=0.001,
                                              solver='adam', random_state=42, tol=0.00001),
        
        "K-Nearest Neighbors (KNN)": KNeighborsClassifier(n_neighbors=5),
        
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        
        "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
        
        "Gaussian Naive Bayes": GaussianNB()
    }

    # --- 3. Train, Time, and Test Each Model ---
    results = []
    print("\n--- Starting Model Bake-Off ---")
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        start_time = time.time()
        model.fit(X_train_scaled, y_train)
        end_time = time.time()
        
        training_time = end_time - start_time
        
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"  > Accuracy: {accuracy * 100:.2f}%")
        print(f"  > Training Time: {training_time:.4f} seconds")
        
        results.append({
            "name": name,
            "accuracy": accuracy,
            "time": training_time
        })

    # --- 4. Print Final Report ---
    print("\n\n--- Final Model Comparison Report ---")
    
    # Sort by accuracy (highest first)
    sorted_results = sorted(results, key=lambda x: x['accuracy'], reverse=True)
    
    print("Rank | Model                 | Accuracy  | Training Time")
    print("----------------------------------------------------------")
    for i, res in enumerate(sorted_results):
        print(f" {i+1:<4} | {res['name']:<23} | {res['accuracy'] * 100:>8.2f}% | {res['time']:>13.4f} s")
    
    print("----------------------------------------------------------")
    print(f"\n*** Winner (by Accuracy): {sorted_results[0]['name']} ***")


if __name__ == '__main__':
    # We will test this on your MAIN dataset
    run_model_comparison('yoga_poses_landmarks.csv')