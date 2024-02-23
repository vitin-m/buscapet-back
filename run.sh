#!/bin/sh
echo "Database startup"
python startup.py
echo "====================="

echo "Database startup"
uvicorn --host "0.0.0.0" --port 8000 main:app
echo "====================="