# Decode Labs Internship Project

This repository contains a rule-based AI chatbot project for Decode Labs. The project is split into two main parts:

- A FastAPI backend that serves chatbot logic and conversation state.
- A React + Vite frontend that provides a modern chat-style user interface.

The chatbot is designed to guide users through Decode Labs information such as the company overview, internship tracks, application information, and contact details.

---

## 1. Project Overview

This project demonstrates how to build a lightweight conversational assistant using:

- Python and FastAPI for the backend API
- React and Vite for the frontend interface
- Tailwind CSS for styling
- Lucide React for icons

The chatbot is rule-based, meaning it does not rely on a Large Language Model (LLM). Instead, it follows a predefined Menu structure and responds based on user selections and keywords.

---

## 2. Features

### Backend features
- FastAPI server with a simple REST API
- In-memory session management for conversation state
- Menu-based navigation with:
  - main menu
  - submenu navigation
  - back functionality
  - restart/menu reset
- Support for final answer responses and error handling

### Frontend features
- Chat-style UI inspired by modern assistants
- Intro animation and typing effect
- Message history display
- Buttons for menu options and navigation
- Connection handling for backend availability
- Restart and back controls

---

## 3. Project Structure

```text
DecodeLabsInternship/
├── Data/
└── Rule-Based AI Chatbot/
    ├── Backend/
    │   ├── main.py
    │   └── requirements.txt
    └── Frontend/
        ├── index.html
        ├── package.json
        ├── vite.config.js
        ├── public/
        └── src/
            ├── App.jsx
            ├── index.css
            ├── main.jsx
            └── assets/
```

### Backend folder
- Contains the FastAPI application logic.
- The main file, [Rule-Based AI Chatbot/Backend/main.py](Rule-Based%20AI%20Chatbot/Backend/main.py), defines the menu tree and API routes.

### Frontend folder
- Contains the React application.
- The chat experience is built in [Rule-Based AI Chatbot/Frontend/src/App.jsx](Rule-Based%20AI%20Chatbot/Frontend/src/App.jsx).

---

## 4. Technologies Used

### Backend
- Python 3
- FastAPI
- Uvicorn
- Pydantic

### Frontend
- React
- Vite
- Tailwind CSS
- Lucide React

---

## 5. Getting Started

### 5.1 Clone the repository

```bash
git clone <repository-url>
cd DecodeLabsInternship
```

---

## 6. Backend Setup

### 6.1 Navigate to the backend folder

```bash
cd "Rule-Based AI Chatbot/Backend"
```

### 6.2 Create and activate a virtual environment (recommended)

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On Bash or Git Bash:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 6.3 Install Python dependencies

```bash
pip install -r requirements.txt
```

### 6.4 Run the FastAPI backend

```bash
uvicorn main:app --reload
```

The backend will usually run at:

```text
http://localhost:8000
```

### 6.5 Backend API endpoints

- GET `/` → health check message
- GET `/menu` → returns the initial chatbot menu structure
- POST `/chatbot` → sends user input and receives the next chatbot response

---

## 7. Frontend Setup

### 7.1 Navigate to the frontend folder

```bash
cd "Rule-Based AI Chatbot/Frontend"
```

### 7.2 Install frontend dependencies

```bash
npm install
```

### 7.3 Start the development server

```bash
npm run dev
```

The frontend will usually run at:

```text
http://localhost:5173
```

---

## 8. Steps When Using React for the Frontend

If you are setting up the React frontend from scratch, this is the usual workflow.

### Step 1: Scaffold the project

This creates the base Vite React files such as package.json, vite.config.js, index.html, src/main.jsx, and src/App.jsx.

```bash
npm create vite@latest frontend -- --template react
cd frontend
```

### Step 2: Install base dependencies

This installs the packages listed in package.json and creates a package-lock.json file.

```bash
npm install
```

### Step 3: Add extra packages your components need

```bash
npm install lucide-react
npm install tailwindcss @tailwindcss/vite
```

### Step 4: Wire up Tailwind

Open vite.config.js and add the Tailwind plugin:

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

Replace the contents of src/index.css with:

```css
@import "tailwindcss";
```

You can also delete src/App.css if it is no longer being used.

### Step 5: Drop in the component

Move your main app UI into src/App.jsx and make sure it is rendered properly by src/main.jsx.

---

## 9. How the Chatbot Works

The chatbot uses a menu-driven conversation tree.

When the user interacts with the app:

1. The frontend sends the message to the backend.
2. The backend checks the current conversation state.
3. It determines whether the input should:
   - move to another submenu,
   - show a final answer,
   - return to the previous screen,
   - or reset the conversation.
4. The frontend renders the returned message and available options.

This makes the chatbot predictable, easy to extend, and suitable for simple informational assistants.

---

## 10. Build Automation with Makefile

A Makefile is included in the project root and can be used to automate common development tasks such as installing dependencies, running the backend, running the frontend, or performing build-related operations.

If you want to use it, run:

```bash
make
```

You can also inspect the Makefile to see the available targets and customize them for your workflow.

---

## 11. Notes for Development

- The backend currently stores session data in memory, so restarting the server clears the chat history.
- For production, you would typically replace the in-memory storage with a database or Redis.
- The frontend expects the backend to be available at localhost:8000.
- If the backend is not running, the UI shows a connection error message.

---

## 12. Useful Commands

### Backend
```bash
cd "Rule-Based AI Chatbot/Backend"
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd "Rule-Based AI Chatbot/Frontend"
npm install
npm run dev
```

---

## 12. Summary

This project is a complete example of a simple rule-based chatbot built with:

- Python + FastAPI for backend logic
- React + Vite + Tailwind for a polished frontend experience

It is ideal for learning how frontend and backend services communicate in a small interactive application.
