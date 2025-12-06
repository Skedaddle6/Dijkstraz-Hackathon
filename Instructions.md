# HamroChimeki - Community Safety Platform

HamroChimeki is a hyperlocal community safety web application featuring real-time alerts, incident reporting, and IoT/Pet safety simulations.

## Prerequisites
*   **Python 3.8+**: Ensure Python is installed and added to your system PATH.

## Installation
1.  **Install Dependencies**:
    Open a terminal in this directory and run:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application
1.  **Start the Server**:
    Double-click `run_server.bat` OR run:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
2.  **Access the App**:
    Open your web browser and go to: `http://localhost:8000`

## Project Structure & Key Files
*   **`main.py`**: The backend FastAPI application (API endpoints, WebSockets).
*   **`database.py`**: Database connection and schema definitions (SQLite).
*   **`iot_simulation.py`**: Script to simulate an IoT noise sensor.
*   **`pet_simulation.py`**: Script to simulate a pet tracker.
*   **`requirements.txt`**: List of Python dependencies.
*   **`run_server.bat`**: Shortcut to start the web server.
*   **`run_simulation.bat`**: Shortcut to run the IoT noise simulation manually.
*   **`static/`**: Folder containing frontend files.
    *   `index.html`: The main user interface.
    *   `styles.css`: Styling for the application (Glassmorphism design).
    *   `app.js`: Frontend logic (Leaflet map, WebSockets, UI interactions).
*   **`hamrochimeki.db`**: SQLite database file (created automatically).

## Features
*   **Real-time Map**: View your location and incidents.
*   **Alerts**: Receive real-time notifications for SOS, Noise, and Missing Pets.
*   **Simulations**:
    *   **Sound**: Simulates loud noises (>50dB) triggering alerts.
    *   **Pet**: Simulates a dog moving outside a safe zone.
*   **SOS Button**: One-tap emergency alert.
