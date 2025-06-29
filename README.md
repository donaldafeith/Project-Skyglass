# Project Skyglass: A Citizen-Led Weather Intelligence System

## Skyglass Operational Console v4.0
## 1. Mission Statement
The Skyglass Operational Console is a professional-grade, standalone environmental intelligence platform. It is designed to run entirely on a local machine (laptop or desktop) for offline-first operation. Its mission is to provide any individual with the power to independently collect, analyze, and visualize critical data from a redundant network of global satellites and sensors, especially in scenarios where primary data sources are unavailable.

This is not a website. It is a self-contained application built for resilience, designed to function as a personal "storm center" when external infrastructure is unreliable.

## 2. System Prerequisites
Before you begin, you must have the following software installed on your system. The setup will fail without them.

Git: For downloading the project files. (Download Git)

Python: Version 3.9, 3.10, or 3.11. (Download Python)

Crucial for Windows Users: During installation, you MUST check the box that says "Add Python to PATH".

Node.js: Version 18.x. This includes npm (Node Package Manager). (Download Node.js)

Verification Command: Open a terminal (Command Prompt, PowerShell, or Terminal) and run each of these commands. You should see a version number for each, not an error.
```
git --version
python --version  # or python3 --version on macOS/Linux
node --version
npm --version
```
## 3. Foolproof Setup Instructions
Follow these five steps exactly. Do not skip any.

## Step 1: Get the Project Files
Open your terminal.

Navigate to a folder where you want to keep the project (e.g., your Documents folder).
```
cd Documents
```
Clone the project repository from its source (replace <repository_url_here> with the actual Git URL).
```
git clone <repository_url_here> skyglass-console

Enter the newly created project directory. This is your project root.

cd skyglass-console
```
## Step 2: Configure API Keys
The console is immensely more powerful with API keys. While it will run without them, key data layers will show an error. Getting keys is free.

Inside the skyglass-console folder, find and enter the backend sub-folder.

You will see a file named .env. Open this file in a simple text editor (Notepad, VSCode, TextEdit, etc.).

Paste your keys between the quotation marks.
```
Service

URL to Get Free Key

Purpose

.env Variable

NASA FIRMS

earthdata.nasa.gov/firms/api-key

Real-time Global Wildfires

FIRMS_API_KEY

RainViewer

rainviewer.com/api.html

Global Weather Radar

RAINVIEWER_API_KEY

OpenAQ

openaq.org/developers/request-key

Global Air Quality Data

OPENAQ_API_KEY
```
Save the .env file. Your keys are stored securely on your local machine and are never transmitted anywhere except to the respective API provider.

## Step 3: Install All Software Packages
This is a one-time setup command that installs all necessary components.

In your terminal, ensure you are in the main skyglass-console project root directory.

Run the main installation command:
```
npm install
```
This command will take several minutes. Be patient. It installs packages for the Electron application, the Python backend, and the React frontend all at once.

Step 4: Initialize the Local Database
The console uses a local file-based database (app.db) to store collected data for offline access. You must initialize it once.

In your terminal, navigate into the backend directory:
```
cd backend
```
Activate the Python virtual environment. This isolates the project's dependencies.

### On macOS/Linux: source venv/bin/activate

### On Windows: .\venv\Scripts\activate

You will know it worked if you see (venv) at the beginning of your terminal prompt.

Run the database setup commands, one by one:
```
flask db init
flask db migrate -m "Initial database schema"
flask db upgrade
```
Note: It is normal to see an error on flask db init if the migrations folder already exists. You can safely ignore this specific error and proceed.

Deactivate the virtual environment to return your terminal to normal:
```
deactivate
```
Navigate back to the project root directory:
```
cd ..
```
You have successfully set up the console. You are ready for operations.

## 5. Running the Skyglass Console
To launch the application:

Make sure you are in the root skyglass-console directory in your terminal.

Run the single start command:
```
npm start
```
Two things will happen:

Your terminal will fill with log output from the local Python data service. You will see the scheduler start up and begin fetching data.

After a moment, the Skyglass Operational Console desktop application window will appear.

To stop the application, close the desktop application window, then go to your terminal and press Ctrl+C.

## 6. Advanced Commands
Run these from the root skyglass-console directory.

Run Backend Tests: To verify the integrity of the backend code.
```
npm run test-backend
```
Create a Backup: To create a timestamped backup of your local database to your user's home folder.
```
npm run backup
```
## 7. Creating a Standalone Executable (Optional)
To create a single, clickable application file (like a .exe or .dmg) that you can run without the terminal:

Make sure you are in the root skyglass-console directory.

Run the package command:
```
npm run package
```
This process is slow and will take several minutes. Once complete, a dist directory will be created. Inside, you will find the standalone application for your operating system.
