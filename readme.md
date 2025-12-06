# 🏠 HAMRO CHIMEKI

## A Smart Community Safety & Monitoring System

---

## 🎯 Our Main Motive

The primary objective of **Hamro Chimeki** is to foster a safer, more connected, and responsive neighborhood. We believe that community safety relies on **fast communication** and **automated awareness**.

This project bridges the gap between manual community reporting and automated hardware monitoring. By integrating IoT sensors with a web platform, we aim to:
1.  **Democratize Safety:** Allow any resident to report incidents instantly.
2.  **Automate Alerts:** Use hardware to detect environmental hazards (gas, pollution) and noise anomalies without human intervention.
3.  **Protect Pets:** Create a safety net for community animals through GPS tracking.

---

## 🌟 Key Features

### 1. 📢 Community Incident Reporting
* **User Reporting:** Residents can log in and report accidents, suspicious activities, or civic issues directly on the platform.
* **Live Feed:** A real-time dashboard allows neighbors to see what is happening around them instantly.

### 2. 🔊 Smart Noise Monitoring (IoT)
* **Hardware:** Integrated Microphone Sensors.
* **The Logic:** The system listens for sound anomalies. If the noise level exceeds a safety threshold (e.g., **85-90 dB**, indicative of screaming, explosions, or crashing), the system triggers an alert.
* **Action:** Notifications are sent immediately via App or SMS to relevant users or authorities.

### 3. 🐕 Pet Safety & Tracking
* **Hardware:** GPS-enabled collars.
* **Geofencing:** Owners can set a "safe zone" range for their pets.
* **"On The Loose" Alert:** If a pet goes beyond the specific range:
    * The owner receives an immediate notification.
    * The website updates the map to show the pet is **"On the Loose,"** allowing neighbors to help locate and rescue the animal.

### 4. 🌫️ Environmental Safety (Pollution & Gas)
* **Pollution Meter:** Hardware sensors detect the local Air Quality Index (AQI) and provide live updates on the community map.
* **Gas Leak Detection:** Sensors monitor for hazardous gases (LPG, Smoke). If a leak is detected, the website flashes a warning to nearby residents to ensure immediate evacuation or caution.

---

## 🛠️ Tech Stack & File Structure

**Software:**
* **Frontend:** HTML5, CSS3, JavaScript
* **Backend:** Python
* **Database:** Custom Python implementation

**Project Structure:**
```text
Hamro-Chimeki/
│
├── main.py          # Server entry point & Logic
├── database.py      # Database management
├── index.html       # User Interface
├── styles.css       # Styling
├── app.js           # Frontend scripts & Map logic
└── readme.txt       # Notes
