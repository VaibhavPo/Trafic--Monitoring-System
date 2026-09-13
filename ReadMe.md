# 🚦 Traffic Monitoring System for Chardham Route  
**Enhancing Pilgrimage Safety & Vehicle Flow using AI**

![Project Overview](https://github.com/VaibhavPo/Trafic--Monitoring-System/blob/main/ProjectPoster.png)

---

## 🎯 Objective

To **strengthen the management of people and vehicles** on pilgrimage routes, particularly along the **Chardham Yatra corridor in Uttarakhand**, using computer vision and real-time monitoring.

---

## 🛠️ Tech Stack

- **YOLOv8 (Ultralytics)** – Vehicle detection  
- **OpenCV** – Frame preprocessing and filtering  
- **SORT** – Vehicle tracking  
- **Tesseract OCR** – License plate recognition  
- **Firebase Realtime Database** – Data logging and live updates  
- **Python** – Core scripting and logic

---

## 🔄 System Workflow

1. 🎥 Read live video frames  
2. 🧹 Apply filters using OpenCV  
3. 🚗 Detect vehicles with YOLOv8  
4. 📍 Track vehicles using SORT  
5. 📏 Check if the vehicle crosses a virtual monitoring line  
6. 🔎 Detect & crop number plates  
7. 🔤 Segment characters and apply OCR (Tesseract)  
8. 🧠 Parse and validate the number  
9. ☁️ Send data to Firebase for real-time use

> View the complete flowchart in the repo for visual understanding.

---

## 📌 Use Case & Deployment Region

- 📍 **Chardham Route, Uttarakhand**  
- 🧘 Pilgrimage-focused use: managing inflow/outflow of vehicles  
- 🧭 Helps reduce **delays**, improves **monitoring**, and enhances **safety**

---

## 🏛️ Government Support

This project was initiated under the **guidance of CO Tehri**, officially **allotted by the DM of Tehri** district.

---

## 🧪 Status

- ✅ Initial development completed  
- 📦 Firebase integration tested  
- 🛣️ Ready for pilot testing on selected road checkpoints

---

## 📂 Repository

🔗 [Visit the GitHub Repo](https://github.com/VaibhavPo/Trafic--Monitoring-System)

---

## 🤝 Contributions & Contact

We welcome collaboration, especially on:
- Improving OCR accuracy
- Integrating alert systems
- Deploying on embedded hardware (e.g. Raspberry Pi, Jetson Nano)

📬 **Connect with me** on [LinkedIn](https://www.linkedin.com/in/vaibhav-pokhriyal-237b86259/) or raise an issue to contribute.

---


## How to run
1. Clone the repository:
   ```bash
   git clone https://github.com/VaibhavPo/Trafic--Monitoring-System.git
   ```
2. Install dependencies:
--- use python 3.11 in virtual enviroment
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main script:
   ```bash
   python gui.py
   ```
4. Add Firebase Admin SDK JSON file:
   - Download the JSON file from Firebase Console.
   - Place it in the project directory.
   - Update in `Setfirebase.py` with the filename.
   - Also add realtime db url at databaseURL.

5. Install pytessaract and add the installed location at enviromental variable 
   -also update it at readPlateImg2.py

> “Smart roads lead to smoother journeys – not just physically, but spiritually.”

## Known Limitations

Plate reads are validated against the standard Indian number-plate format
(state code + district code + series + number, e.g. `UK12...`). When a raw
OCR read doesn't match that pattern, the system falls back to running OCR
on the full plate crop directly — which is where most read errors come from.

Two failure modes show up in the detection logs:
- **Inconsistent reads across frames** — the same vehicle can log two
  different plate strings a few frames apart (e.g. `DL7CD507` vs `DL7C507`),
  since OCR isn't deterministic frame-to-frame.
- **Partial/failed reads** — plates flagged with "unable to read a valid
  license plate correctly," usually from motion blur, angle, or plate
  condition.

This was the actual bottleneck in the system — not detection (which
validated at 80%+ on sample footage) but OCR reliability. The logical next
step would be multi-frame voting (take the majority read across several
frames per vehicle instead of trusting a single frame) rather than trying
to improve single-frame OCR accuracy directly.
