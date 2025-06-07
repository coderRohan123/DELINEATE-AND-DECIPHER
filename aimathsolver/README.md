# AI Math Solver

A full-stack application that allows users to draw mathematical expressions, which are then recognized and solved using AI. The solution is displayed in LaTeX format. The project consists of a React + Vite frontend and a FastAPI backend, with deployment-ready configurations for Vercel.

---

## Features
- Draw math expressions on a canvas
- AI-powered recognition and solution of handwritten math
- LaTeX rendering of results
- Variable assignment and memory
- Modern UI with Mantine and TailwindCSS

---

## Tech Stack
- **Frontend:** React, TypeScript, Vite, Mantine, TailwindCSS, MathJax
- **Backend:** FastAPI, Python, Google Gemini API, Pillow, Pydantic
- **Deployment:** Vercel (serverless)

---

## Folder Structure
```
DELINEATE-AND-DECIPHER/aimathsolver/
├── aicalcfrontend/   # React frontend
└── aicalcbackend/    # FastAPI backend
```

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repo-url>
cd DELINEATE-AND-DECIPHER/aimathsolver
```

### 2. Backend Setup

#### a. Create a virtual environment (recommended)
```bash
cd aicalcbackend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### b. Install dependencies
```bash
pip install -r requirements.txt
```

#### c. Set up environment variables
Create a `.env` file in `aicalcbackend/` with your Google Gemini API key:
```
GEMINI_API_KEY=your_google_gemini_api_key
```

#### d. Run the backend server
```bash
uvicorn main:app --host 0.0.0.0 --port 8900 --reload
```

The backend will be available at `http://localhost:8900/`.

---

### 3. Frontend Setup

#### a. Install dependencies
```bash
cd ../aicalcfrontend
npm install
```

#### b. Configure API URL
Create a `.env` file in `aicalcfrontend/`:
```
VITE_API_URL=http://localhost:8900
```

#### c. Run the frontend
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173/` (default Vite port).

---

## Usage
1. Open the frontend in your browser.
2. Draw a math expression on the canvas.
3. Click the solve button to send the image to the backend.
4. The recognized expression and its solution will be displayed in LaTeX format.

---

## API Reference

### POST `/calculate`
- **Request Body:**
  ```json
  {
    "image": "data:image/png;base64,...",
    "dict_of_vars": {}
  }
  ```
- **Response:**
  ```json
  {
    "message": "Image processed",
    "data": [
      { "expr": "x+2", "result": "5", "assign": false }
    ],
    "status": "success"
  }
  ```

---

## Deployment (Vercel)
Both frontend and backend have `vercel.json` for serverless deployment. Push to your Vercel-connected repo and set the required environment variables in the Vercel dashboard.

---

## License
[MIT](LICENSE)

---

## Acknowledgements
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vite](https://vitejs.dev/)
- [Mantine](https://mantine.dev/)
- [MathJax](https://www.mathjax.org/)
- [Google Gemini API](https://ai.google.dev/)
