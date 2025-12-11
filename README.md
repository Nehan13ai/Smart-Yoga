\# Hi there, I'm Neha Nala! 👋

\### AI \& Machine Learning Student | Python Developer | IoT Enthusiast



I am passionate about building intelligent systems that solve real-world problems. My work ranges from Computer Vision and Deep Learning to Embedded Systems and Predictive Analytics.



---



\# 🧘‍♀️ Smart Yoga  

\### AI-Powered Pose Detection \& Recommendation System



\*\*Smart Yoga\*\* is an intelligent web application designed to act as a personal yoga assistant. It solves the problem of performing yoga incorrectly at home by providing real-time AI pose recognition and offers personalized routine recommendations based on health metrics.



---



\## 1. 🧠 AI Pose Recognition (Dual-Model Architecture)



\### • Image Upload Analysis  

Upload a photo of a yoga pose, and the system identifies it with \*\*91%+ accuracy\*\*.  

\- \*Powered by:\* A Main SVM Model trained on \*\*28 classes\*\* (27 Yoga Poses + 1 "Other" class for robustness).



\### • Live Webcam Coach  

Real-time detection using your webcam with \*\*zero lag\*\*.  

\- \*Powered by:\* A Specialist SVM Model trained on \*\*9 key classes\*\* for high-speed performance (96% accuracy).  

\- \*Smart Filtering:\* Includes logic to detect if the user is just sitting/standing (the "Other" class) or if the full body is not visible, preventing false positives.



---



\## 2. 📋 Personalized Recommendation Engine



A rule-based expert system that generates safe yoga routines based on:



\- \*\*Health Profile:\*\* Age, Sex, Pain Level (Low/Medium/High).  

\- \*\*Medical Conditions:\*\* Filters poses based on disorders (e.g., Back Pain, Stress, Obesity).  

\- \*\*BMI Analysis:\*\* Automatically calculates BMI. If BMI ≥ 25, the system strictly recommends \*\*"Joint-Friendly"\*\* poses to prevent injury.



---



\## 3. 🔐 User System



\- Secure User Registration and Login  

\- Data stored in a local SQLite database  



---



\# 📊 AI Methodology \& Approach



\## Why MediaPipe + SVM?



Instead of using a heavy Convolutional Neural Network (CNN) on raw pixels, we utilized a \*\*Hybrid AI Approach\*\*:



1\. \*\*Feature Extraction:\*\*  

&nbsp;  We use Google's \*\*MediaPipe Pose\*\* to detect 33 body keypoints (skeleton) and convert the image into a lightweight vector of \*\*132 numbers\*\* (x, y, z, visibility).



2\. \*\*Classification:\*\*  

&nbsp;  We trained a \*\*Support Vector Machine (SVM)\*\* classifier on this landmark data.



---



\## Performance Comparison (The "Bake-Off")



We tested 7 different algorithms on our dataset. The \*\*SVM (SVC)\*\* proved to be superior:



\- \*\*SVM Accuracy:\*\* 91.51% (Winner)  

\- \*\*Neural Network (MLP):\*\* 88.86% (Slower to train)  

\- \*\*Random Forest:\*\* 85.94%



---



\## The "Specialist" Strategy



To ensure the live webcam feature was fast and accurate, we trained a separate \*\*Specialist Model\*\*.  

While the main model knows 28 classes, the specialist model focuses only on the 9 specific poses used in the live feature.  

This reduced confusion and boosted accuracy to \*\*96.94%\*\*.



