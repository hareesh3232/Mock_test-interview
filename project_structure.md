# AI-Powered Resume-Based Job-Matched Mock Interview System

## Project Structure

```
mock-interview-ai/
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database connection & setup
│   │   ├── models/             # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── job.py
│   │   │   ├── interview.py
│   │   │   └── result.py
│   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── job.py
│   │   │   ├── interview.py
│   │   │   └── result.py
│   │   ├── api/                # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── resume.py
│   │   │   ├── jobs.py
│   │   │   ├── interview.py
│   │   │   └── dashboard.py
│   │   ├── services/           # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── resume_parser.py
│   │   │   ├── job_search.py
│   │   │   ├── ai_service.py
│   │   │   └── evaluation.py
│   │   ├── core/               # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   ├── dependencies.py
│   │   │   └── exceptions.py
│   │   └── utils/              # Utility functions
│   │       ├── __init__.py
│   │       ├── file_utils.py
│   │       └── text_processing.py
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Backend tests
│   ├── requirements.txt
│   ├── .env.example
│   └── alembic.ini
├── frontend/                   # React Frontend
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   │   ├── common/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   ├── Navbar.jsx
│   │   │   │   └── Loading.jsx
│   │   │   ├── forms/
│   │   │   │   ├── ResumeUpload.jsx
│   │   │   │   ├── JobSearch.jsx
│   │   │   │   └── InterviewForm.jsx
│   │   │   └── dashboard/
│   │   │       ├── ScoreCard.jsx
│   │   │       ├── ProgressChart.jsx
│   │   │       └── HistoryTable.jsx
│   │   ├── pages/              # Page components
│   │   │   ├── Home.jsx
│   │   │   ├── Upload.jsx
│   │   │   ├── Jobs.jsx
│   │   │   ├── Interview.jsx
│   │   │   ├── Results.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── services/           # API services
│   │   │   ├── api.js
│   │   │   ├── auth.js
│   │   │   └── storage.js
│   │   ├── hooks/              # Custom React hooks
│   │   │   ├── useAuth.js
│   │   │   ├── useInterview.js
│   │   │   └── useLocalStorage.js
│   │   ├── context/            # React Context
│   │   │   ├── AuthContext.jsx
│   │   │   └── InterviewContext.jsx
│   │   ├── utils/              # Utility functions
│   │   │   ├── constants.js
│   │   │   ├── helpers.js
│   │   │   └── validators.js
│   │   ├── styles/             # CSS and Tailwind
│   │   │   ├── globals.css
│   │   │   └── components.css
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── .env.example
├── docker-compose.yml          # Development environment
├── README.md
├── .gitignore
└── requirements.txt            # Python dependencies
```

## Database Schema (PostgreSQL)

### Users Table
- id (UUID, Primary Key)
- email (String, Unique)
- full_name (String)
- created_at (Timestamp)
- updated_at (Timestamp)

### Resumes Table
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key)
- filename (String)
- file_path (String)
- extracted_text (Text)
- skills (JSON)
- education (JSON)
- experience (JSON)
- created_at (Timestamp)

### Jobs Table
- id (UUID, Primary Key)
- title (String)
- company (String)
- description (Text)
- requirements (JSON)
- skills_required (JSON)
- location (String)
- salary_min (Integer)
- salary_max (Integer)
- job_type (String)
- created_at (Timestamp)

### Interviews Table
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key)
- resume_id (UUID, Foreign Key)
- job_id (UUID, Foreign Key)
- questions (JSON)
- answers (JSON)
- status (String)
- started_at (Timestamp)
- completed_at (Timestamp)

### Results Table
- id (UUID, Primary Key)
- interview_id (UUID, Foreign Key)
- technical_score (Float)
- communication_score (Float)
- job_match_score (Float)
- overall_score (Float)
- strengths (JSON)
- weaknesses (JSON)
- recommendations (JSON)
- created_at (Timestamp)

## API Endpoints

### Authentication
- POST /auth/register
- POST /auth/login
- GET /auth/me

### Resume Management
- POST /api/resume/upload
- GET /api/resume/{resume_id}
- GET /api/resume/parse/{resume_id}

### Job Search
- GET /api/jobs/search
- GET /api/jobs/{job_id}
- POST /api/jobs/mock-search

### Interview System
- POST /api/interview/generate
- POST /api/interview/start
- POST /api/interview/submit-answer
- GET /api/interview/{interview_id}
- POST /api/interview/complete

### Results & Dashboard
- GET /api/results/{interview_id}
- GET /api/dashboard/stats
- GET /api/dashboard/history
- GET /api/dashboard/progress

## Tech Stack Details

### Backend (FastAPI)
- FastAPI for API framework
- SQLAlchemy for ORM
- PostgreSQL for database
- Alembic for migrations
- OpenAI API for LLM integration
- PyMuPDF/docx2txt for resume parsing
- spaCy for NLP processing

### Frontend (React + Tailwind)
- React 18 with hooks
- Tailwind CSS for styling
- Axios for API calls
- React Router for navigation
- Context API for state management
- Chart.js for dashboard visualizations

### AI Integration
- OpenAI GPT for question generation
- OpenAI GPT for answer evaluation
- Custom prompt engineering
- Mock job search API (JSON responses)

