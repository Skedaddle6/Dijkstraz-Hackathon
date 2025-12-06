@echo off
echo Starting HamroChimeki Server on Port 9000...
echo Open your browser to: http://localhost:9000
echo Press Ctrl+C to stop.
uvicorn main:app --reload --port 9000
pause
