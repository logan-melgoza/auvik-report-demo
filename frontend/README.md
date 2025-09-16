# Internal Reporting Tool - Frontend

## 📌 Overview
This is the **React (Vite)** frontend for the Internal Reporting Tool.  
It provides the user interface and communicates with the Flask backend via API requests.

- **Framework**: React (Vite)
- **Deployment**: Built static files served by IIS or Nginx on Windows Server
- **Backend**: Flask API proxied at `/api/...`

---

## 🛠️ Tech Stack

This frontend is built with the following libraries:

- **react** / **react-dom** → Core React framework and DOM rendering  
- **vite** → Build tool & dev server (hot reload, optimized production build)  
- **bootstrap** → Styling framework for responsive layouts and UI components  
- **react-router-dom** → Client-side routing (e.g., `/login`, `/reports`)    

### Development Tools
- **@vitejs/plugin-react** → Adds React/JSX support to Vite  
- **eslint** + plugins → Enforces coding standards and React hook rules  
- **@types/react** / **@types/react-dom** → TypeScript typings (helpful for IDEs)  

---

## 🖥️ Requirements
- Node.js 18+
- NPM 9+
- Backend API (Flask) running on the same VM or proxied from another server

---

## ⚙️ Environment Variables
Frontend `.env` variables are prefixed with `VITE_` so they can be exposed to the build.  

| Variable        | Description                                | Example                        |
|-----------------|--------------------------------------------|--------------------------------|
| `VITE_API_URL`  | URL of backend API                         | `http://127.0.0.1:5555`        |

* Include a .env.development file and a .env.production file to root directory
* React will handle which file to use based on the method ran

⚠️ Sensitive variables like `AUVIK_API_KEY`, `SECRET_KEY`, and `REDIS_URL` **must never be included in frontend `.env` files**. They belong in the backend only.

---

## 🚀 Running Locally
```powershell
npm install
npm run dev

