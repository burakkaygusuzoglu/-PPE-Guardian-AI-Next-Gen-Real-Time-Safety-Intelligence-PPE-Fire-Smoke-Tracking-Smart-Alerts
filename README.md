Industrial PPE Safety AI
Real-Time Vision System • Edge-Ready • Automation-Oriented
🔎 Project Summary

Industrial PPE Safety AI is a real-time computer vision system designed for industrial environments.

It performs:

• Multi-class hazard detection
• ID-based person tracking
• Duration-based PPE violation analysis
• Structured alarm generation
• Snapshot + CSV logging
• Edge-device integration preparation

This project is engineered as a system architecture — not just a detection demo.

🎯 Detection Capabilities

The model detects:

• Person
• Helmet
• Vest
• Gloves
• Goggles
• Fire
• Smoke
• Forklift

Model details:

• Custom-trained Ultralytics YOLO
• mAP ≈ 0.88
• GPU accelerated (PyTorch CUDA)
• Optimized confidence & IoU thresholds

🧠 System Design Philosophy

This system was redesigned independently with a production-oriented mindset.

Instead of frame-based alerts:

• ID-based temporal logic is applied
• Violations require 3-second persistence
• Cooldown logic prevents alarm spam
• State management ensures stability
• Detection is converted into structured safety events

The focus is reliability, not visual demo output.

⚙️ Architecture Overview
1️⃣ Vision Layer

• Real-time YOLO inference
• Optimized frame loop
• FPS smoothing

2️⃣ Tracking Layer

• Custom IoU-based multi-object tracker
• Persistent person_id assignment
• Track lifecycle management

No external tracker dependency.

3️⃣ Compliance Intelligence Layer

• Person region segmentation (head / torso)
• Spatial object association
• Duration-based violation accumulation
• Temporal state control

4️⃣ Alarm Engine

• WARNING → PPE violations
• CRITICAL → Fire / Smoke
• Alert snapshot capture
• CSV event logging
• Cooldown-based trigger control

5️⃣ Automation-Ready Output

Designed to integrate with:

• ESP32 (HTTP trigger + buzzer + relay)
• Raspberry Pi edge deployment
• On-site automation systems
• Future web dashboard interface

Hardware abstraction is separated from detection logic.

🏗️ Engineering Concepts Applied

• Real-Time System Design
• Multi-Object Tracking
• IoU-Based Association
• Temporal Decision Logic
• State Management
• Event-Driven Architecture
• Structured Logging
• Embedded System Preparation
• Performance Optimization

📚 What I Practiced & Learned
Computer Vision

• Dataset merging & label consistency
• Confidence calibration
• False-positive reduction
• Bounding box region modeling

System Architecture

• Modular folder structure
• Separation of logic layers
• Production-style code organization
• Stable real-time loop handling

Automation Thinking

• Event → trigger pipeline design
• Hardware abstraction planning
• Edge deployment considerations

🌐 Broader Development Direction

In parallel with AI & real-time systems, I am actively improving:

• JavaScript
• HTML
• CSS
• Frontend structure design

Long-term vision:

• Web-based monitoring dashboard
• Live stream interface
• Alert analytics panel
• Remote safety management system

The architecture is intentionally built to evolve into a full-stack industrial monitoring platform.

🖥️ Technical Stack

• Python 3.10
• Ultralytics YOLO 8.x
• PyTorch (CUDA)
• OpenCV
• Custom IoU Tracker
• Structured CSV logging

Planned extensions:

• Raspberry Pi deployment
• ESP32 alarm system
• Web dashboard (JS/HTML/CSS)
• Distributed monitoring nodes

💼 Professional Positioning

This project demonstrates:

• System-level thinking
• Industrial scenario awareness
• Applied AI beyond academic scope
• Embedded-ready architecture
• Real-time optimization capability

It reflects readiness for:

• AI Engineering internships
• Computer Vision roles
• Embedded AI systems
• Industrial automation projects
• Full-stack monitoring solutions

👨‍💻 Author

Burak Kaygusuzoğlu
Computer Engineering Student
