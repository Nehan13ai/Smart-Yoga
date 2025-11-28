import cv2
import mediapipe as mp
import numpy as np
import os
import pandas as pd
import random 

# --- SETTINGS ---
DATASET_DIR = 'dataset'
OUTPUT_CSV = 'yoga_poses_landmarks.csv'
# Set to 60 as per your excellent recommendation
MAX_SAMPLES_PER_NEGATIVE_CLASS = 60


def extract_landmarks(image_path):
    """Extracts pose landmarks from a single image with error handling."""
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        try:
            image = cv2.imread(image_path)
            if image is None:
                print(f"Warning: Could not read image {image_path}. Skipping.")
                return None
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            if not results.pose_landmarks:
                return None
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
            return landmarks
        except RuntimeError as e:
            print(f"!!! FAILED to process {image_path}. Error: {e}. Skipping file.")
            return None
        except Exception as e:
            print(f"!!! An unexpected error occurred with {image_path}. Error: {e}. Skipping file.")
            return None

def create_pose_dataset(dataset_path, output_csv_path):
    """Processes all images in the dataset path and saves landmarks to a CSV."""
    
    pose_classes = sorted([d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))])
    all_landmarks = []
    
    print(f"Found {len(pose_classes)} pose classes: {pose_classes}")

    for pose_name in pose_classes:
        class_path = os.path.join(dataset_path, pose_name)
        image_files = [f for f in os.listdir(class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        is_negative_class = (pose_name.lower() == 'other')
        if is_negative_class and len(image_files) > MAX_SAMPLES_PER_NEGATIVE_CLASS:
            print(f"\nLimiting '{pose_name}' class: found {len(image_files)} images, will use {MAX_SAMPLES_PER_NEGATIVE_CLASS}.")
            random.shuffle(image_files)
            image_files_to_process = image_files[:MAX_SAMPLES_PER_NEGATIVE_CLASS]
        else:
            image_files_to_process = image_files

        print(f"\nProcessing {len(image_files_to_process)} images for class '{pose_name}'...")
        
        successful_landmarks = 0
        for image_name in image_files_to_process:
            image_path = os.path.join(class_path, image_name)
            landmarks = extract_landmarks(image_path)
            
            if landmarks:
                row = [pose_name] + landmarks
                all_landmarks.append(row)
                successful_landmarks += 1

        print(f"Successfully processed {successful_landmarks} / {len(image_files_to_process)} images for {pose_name}.")

    if not all_landmarks:
        print("\nWarning: No landmarks were extracted from any images. The CSV will be empty.")
        return

    num_landmark_values = len(all_landmarks[0]) - 1 
    columns = ['class'] + [f'landmark_{i}' for i in range(num_landmark_values)]
    
    df = pd.DataFrame(all_landmarks, columns=columns)
    df.to_csv(output_csv_path, index=False)
    print(f"\nDataset successfully created at {output_csv_path} with {len(df)} total samples.")
    print("Dataset is now balanced.")


if __name__ == '__main__':
    create_pose_dataset(DATASET_DIR, OUTPUT_CSV)