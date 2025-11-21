# auvik-report-demo
This is a demo code of the production code that I wrote during my Internship at Sebastian Corp. Working to add mock data to replace API calls for full functionality.

## 📌 Fronted Overview
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
```

## Backend Overview
Flask-based backend for the internal Auvik reporting tool.  
Provides authentication, session management, API endpoints, and report generation.

- **Framework**: Flask (Python)
- **Database**: SQLite
- **Sessions**: Redis
- **Reports**: PDF generation using `pdfkit` and `wkhtmltopdf`
- **Deployment**: Runs on Windows Server using Waitress + NSSM

---

## Requirements
- Python 3.10+
- Redis (Docker Desktop or Memurai)
- wkhtmltopdf
- NSSM (for service auto-start on Windows Server)

---

## ⚙️ Environment Variables
| Variable             | Description                                     | Example                                            |
|----------------------|-------------------------------------------------|----------------------------------------------------|
| `AUVIK_USERNAME`     | Username for Auvik API authentication           | `myuser@example.com`                               |
| `AUVIK_API_KEY`      | API key for Auvik API authentication            | `xxxxxxxxxxxxxxxx`                                 |
| `BASE_URL`           | Base URL for Auvik API calls                    | `https://auvikapi.us1.my.auvik.com`                |
| `MAIN_DOMAIN_PREFIX` | Prefix for your Auvik tenant domain             | `mainauvikdomain`                                  |
| `SECRET_KEY`         | Flask secret key                                | `supersecretkey`                                   |
| `REDIS_URL`          | Redis connection string                         | `redis://localhost:6379/0`                         |
| `FLASK_ENV`          | Flask environment mode                          | `production` (or `development`)                    |
| `DEBUG`              | Enable/disable debug mode                       | `False`                                            |
| `WKHTMLTOPDF_PATH`   | Path to wkhtmltopdf binary (Windows)            | `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe` |
| `REGISTRATION_SECRET`| Secret required for user registration           | `someregistrationsecret`                           |

* Place .env file at the root of the backend directory

---

## Example .env file
```markdown
AUVIK_USERNAME=myauvikusername
AUVIK_API_KEY=secretapikey
BASE_URL=https://auvikapi.us2.my.auvik.com
...
```

---


## Running Locally
```powershell
python -m venv venv
venv\Scripts\Activate #Windows
venv/bin/activate #mac/linux
pip install -r requirements.txt
waitress-serve --listen=127.0.0.1:5555 app:app
```

## 📦 Deployment (Windows Server)

### 1. Clone Repo
```powershell
git clone https://github.com/your-org/backend.git C:\yourapp
cd C:\yourapp
```

### 2. Download Python Requirements
```powershell
pip install -r requirements.txt
```

### 3. Configure wkhtmltopdf
* Install into C:\Program Files\wkhtmltopdf\bin
* Add to PATH
* Set enviornment variable

### 4. Run with Waitress
```powershell
waitress-serve --listen=127.0.0.1:5555 app:app
```

### 5. Install as Service (NSSM)
```powershell
nssm install FlaskApp "C:\yourapp\venv\Scripts\python.exe" "-m waitress --listen=127.0.0.1:5555 app:app"
nssm start FlaskApp
sc config FlaskApp start= auto
```

---

## 🔄 Updating
```powershell
cd C:\yourapp
git pull
venv\Scripts\activate
pip install -r requirements.txt
nssm restart FlaskApp
```

---

## ✅ Verification Checklist

After deployment or updates, confirm the following:

- [ ] Visit `http://<vm-ip>/` → React frontend loads correctly  
- [ ] API calls to `/api/...` return expected responses from Flask  
- [ ] User login and registration flow works end-to-end  
- [ ] Reports generate successfully (PDF output created via wkhtmltopdf)  
- [ ] Redis is running and responding (`redis-cli ping` returns `PONG`)  
- [ ] NSSM service for backend is installed, running, and set to auto-start  
- [ ] Reboot VM → Flask backend auto-starts automatically  
- [ ] (Optional) HTTPS works if certificates are configured in IIS or Nginx  
