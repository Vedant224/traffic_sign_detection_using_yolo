Traffic Sign & Object Detection Assignment

Here is how to set up and run the project on Windows.

1. Setup Virtual Environment

Open PowerShell inside this folder and run these commands one by one:

# 1. Create the virtual environment
python -m venv venv

# 2. Activate the environment
.\venv\Scripts\Activate.ps1


Note: If you get a red error saying "running scripts is disabled", run this command first, then try activating again:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

2. Install Dependencies

Make sure your terminal shows (venv) at the start, then install the required libraries:

pip install fastapi uvicorn python-multipart ultralytics pillow requests


3. How to Run

You need two terminal windows open.

Terminal 1: Start the Server

Run this to start the detection API (keep this window open):

.\venv\Scripts\Activate.ps1
python main.py


Wait until you see: Uvicorn running on http://0.0.0.0:8000

Terminal 2: Run the Test

Open a new terminal and run this to process the images:

.\venv\Scripts\Activate.ps1
python batch_client.py


4. Results

Input: Put your test images in the test_images folder.

Output: Check the results folder to see the images with detected bounding boxes (Traffic Signs = Red, Objects = Blue).