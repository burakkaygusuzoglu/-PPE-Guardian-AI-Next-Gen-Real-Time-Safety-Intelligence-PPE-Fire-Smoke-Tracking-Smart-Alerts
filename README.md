Real-Time Multi-Hazard & PPE Compliance Detection with Computer Vision

AI-powered real-time Occupational Health & Safety (OHS) monitoring system built using custom-trained Ultralytics YOLO and ID-based tracking logic.

🚀 Project Overview

This project is a real-time industrial safety monitoring system designed to detect:

👷 PPE compliance (Helmet, Vest, Gloves, Goggles)

🔥 Fire

🌫 Smoke

🚜 Forklift presence

🧍 Person tracking (ID-based)

The system runs live on camera input and performs:

Object detection

Person ID tracking (IoU-based tracker)

PPE compliance verification

Violation duration tracking (3-second rule)

Intelligent alarm triggering

Video recording

Alert image capture

CSV logging

It is designed as a production-ready AI pipeline, not just a demo model.

🧠 What Makes This Project Advanced?
1️⃣ Custom YOLO Training

Multi-class custom dataset

Helmet, Vest, Fire, Smoke, Gloves, Forklift, Goggles

Trained with Ultralytics YOLO

mAP ≈ 0.88

Confidence tuning & false positive reduction

2️⃣ Real-Time ID Tracking System

Instead of triggering alerts per frame, the system:

Assigns unique IDs to each detected person

Tracks individuals across frames

Applies time-based violation logic per ID

This prevents:

Instant false alarms

Frame-based noise triggering

Flickering detection issues

3️⃣ PPE Violation Duration Logic (3-Second Rule)

A violation is only triggered if:

NO_HELMET or NO_VEST persists ≥ 3 seconds

This introduces:

Temporal reasoning

Real-world compliance simulation

False-positive suppression

4️⃣ Intelligent Alarm System

Alarm hierarchy:

Condition	Level
Fire detected	CRITICAL
Smoke detected	CRITICAL
PPE violation	WARNING

Includes:

Cooldown logic (anti-spam)

Alert image saving

CSV logging with object counts

Visual alarm banner overlay

5️⃣ Modular Architecture

The system is structured for scalability:

MASTER_MERGED/
│
├── run_camera.py
├── core/
│   ├── __init__.py
│   └── ppe_timer.py
├── alerts/
├── recordings/

Core components:

IoU-based tracker

ID-based violation state manager

Detection pipeline

Logging & recording module

Designed for future:

ESP32 hardware integration

Web dashboard

Mobile notification system

Pre/Post event video buffering

🛠 Tech Stack

Python 3.10

Ultralytics YOLO

PyTorch (CUDA)

OpenCV

Custom IoU tracker

CSV logging

Real-time video pipeline

🏗 Engineering Challenges Solved

✔ Real-time processing with stable FPS
✔ False positive reduction via spatial + temporal filtering
✔ ID-based event logic instead of frame-based logic
✔ Modular structure for production extension
✔ Alert cooldown & persistence logic

📈 What I Learned

Through this project, I developed hands-on experience in:

Real-time computer vision systems

Model training & hyperparameter tuning

Detection post-processing logic

Temporal event reasoning

State machine design

Tracker implementation (without external libraries)

Performance optimization for live camera systems

Engineering production-style pipelines

Logging, alert handling & structured output

This project moved beyond "just training a model" and into building a complete AI-powered safety system.

🎯 Future Development Roadmap

Intelligent fire/smoke evidence accumulation

Pre-event + post-event video clip saving

ESP32 hardware alarm integration

Web dashboard (Flask / FastAPI)

Mobile push notification system

ByteTrack / DeepSORT upgrade

📌 Why This Project Matters

Industrial safety monitoring is critical in:

Construction sites

Manufacturing plants

Warehouses

Smart factories

This system demonstrates how AI can be integrated into real-world safety environments to:

Reduce risk

Automate monitoring

Improve compliance

Enable smart industrial infrastructure

👨‍💻 Author

Burak Kaygusuzoğlu
Computer Engineering Student
AI & Real-Time Systems Enthusiast

GitHub: github.com/burakkaygusuzoglu
LinkedIn: linkedin.com/in/burak-kaygusuzoglu-173559334
