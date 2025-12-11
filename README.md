<h1 align="center">Hi there, I'm Neha Nala! 👋</h1>

<h3 align="center">AI \& Machine Learning Student | Python Developer | IoT Enthusiast</h3>



<p align="center">

&nbsp; I am passionate about building intelligent systems that solve real-world problems. My work ranges from Computer Vision and Deep Learning to Embedded Systems and Predictive Analytics.

</p>



<hr>



<h1 align="center">🧘‍♀️ Smart Yoga</h1>

<h3 align="center">AI-Powered Pose Detection \& Recommendation System</h3>



<p>

<b>Smart Yoga</b> is an intelligent web application designed to act as a personal yoga assistant. It solves the problem of performing yoga incorrectly at home by providing real-time AI pose recognition and offers personalized routine recommendations based on health metrics.

</p>



<h3>1. 🧠 AI Pose Recognition (Dual-Model Architecture)</h3>



<ul>

&nbsp; <li><b>Image Upload Analysis:</b> Upload a photo of a yoga pose, and the system identifies it with <b>91%+ accuracy</b>.

&nbsp;   <ul>

&nbsp;     <li><i>Powered by:</i> A Main SVM Model trained on <b>28 classes</b> (27 Yoga Poses + 1 "Other" class for robustness).</li>

&nbsp;   </ul>

&nbsp; </li>



&nbsp; <li><b>Live Webcam Coach:</b> Real-time detection using your webcam with <b>zero lag</b>.

&nbsp;   <ul>

&nbsp;     <li><i>Powered by:</i> A Specialist SVM Model trained on <b>9 key classes</b> for high-speed performance (96% accuracy).</li>

&nbsp;     <li><i>Smart Filtering:</i> Includes logic to detect if the user is just sitting/standing (the "Other" class) or if the full body is not visible, preventing false positives.</li>

&nbsp;   </ul>

&nbsp; </li>

</ul>



<h3>2. 📋 Personalized Recommendation Engine</h3>



<p>A rule-based expert system that generates safe yoga routines based on:</p>



<ul>

&nbsp; <li><b>Health Profile:</b> Age, Sex, Pain Level (Low/Medium/High).</li>

&nbsp; <li><b>Medical Conditions:</b> Filters poses based on disorders (e.g., Back Pain, Stress, Obesity).</li>

&nbsp; <li><b>BMI Analysis:</b> Automatically calculates BMI. If BMI ≥ 25, the system strictly recommends <b>"Joint-Friendly"</b> poses to prevent injury.</li>

</ul>



<h3>3. 🔐 User System</h3>



<ul>

&nbsp; <li>Secure User Registration and Login.</li>

&nbsp; <li>Data stored in a local SQLite database.</li>

</ul>



<hr>



<h2>📊 AI Methodology \& Approach</h2>



<h3>Why MediaPipe + SVM?</h3>



<p>Instead of using a heavy Convolutional Neural Network (CNN) on raw pixels, we utilized a <b>Hybrid AI Approach</b>:</p>



<ol>

&nbsp; <li><b>Feature Extraction:</b> We use Google's <b>MediaPipe Pose</b> to detect 33 body keypoints (skeleton) and convert the image into a lightweight vector of <b>132 numbers</b> (x, y, z, visibility).</li>

&nbsp; <li><b>Classification:</b> We trained a <b>Support Vector Machine (SVM)</b> classifier on this landmark data.</li>

</ol>



<h3>Performance Comparison (The "Bake-Off"):</h3>



<p>We tested 7 different algorithms on our dataset. The <b>SVM (SVC)</b> proved to be superior:</p>



<ul>

&nbsp; <li><b>SVM Accuracy:</b> 91.51% (Winner)</li>

&nbsp; <li><b>Neural Network (MLP):</b> 88.86% (Slower to train)</li>

&nbsp; <li><b>Random Forest:</b> 85.94%</li>

</ul>



<h3>The "Specialist" Strategy</h3>



<p>To ensure the live webcam feature was fast and accurate, we trained a separate <b>Specialist Model</b>. While the main model knows 28 classes, the specialist model focuses only on the 9 specific poses used in the live feature. This reduced confusion and boosted accuracy to <b>96.94%</b>.</p>



