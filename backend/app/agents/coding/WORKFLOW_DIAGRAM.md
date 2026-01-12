# Complete Workflow with API Integration

## Visual Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│  - GitHub Frontend URL                                           │
│  - Backend Stack Choice                                          │
│  - Optional: PRD/Impact Analysis                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    1. PLANNER AGENT                              │
│  - Analyzes requirements                                         │
│  - Creates project specification                                 │
│  - Defines API endpoints                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 2. GITHUB CLONER AGENT                           │
│  - Clones frontend from GitHub                                   │
│  - Extracts file structure                                       │
│  - Returns frontend code                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. BACKEND GENERATOR AGENT                          │
│  - Generates complete backend code                               │
│  - Creates API routes, models, auth                              │
│  - Returns backend files                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  4. INTEGRATOR AGENT                             │
│  - Writes frontend files to disk                                 │
│  - Writes backend files to disk                                  │
│  - Creates root-level files (README, .gitignore)                 │
│  - Calls FrontendIntegratorAgent ──────────┐                     │
└────────────────────────┬───────────────────┘                     │
                         │                                         │
                         │                    ┌────────────────────▼──────┐
                         │                    │ 5. FRONTEND INTEGRATOR    │
                         │                    │    AGENT (NEW!)           │
                         │                    │                           │
                         │                    │ a) Detect Framework       │
                         │                    │    - React/Vue/Next.js    │
                         │                    │                           │
                         │                    │ b) Add Axios              │
                         │                    │    - Update package.json  │
                         │                    │                           │
                         │                    │ c) Create API Service     │
                         │                    │    - src/services/api.js  │
                         │                    │    - All endpoints        │
                         │                    │    - Auth interceptors    │
                         │                    │                           │
                         │                    │ d) Modify Components      │
                         │                    │    - Find components      │
                         │                    │    - Inject API calls     │
                         │                    │    - Replace mock data    │
                         │                    │                           │
                         │                    │ e) Create .env            │
                         │                    │    - VITE_API_URL         │
                         │                    └───────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    6. PACKAGER AGENT                             │
│  - Creates ZIP file                                              │
│  - Proper folder structure                                       │
│  - Ready for download                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              7. GITHUB PUBLISHER AGENT (Optional)                │
│  - Creates new GitHub repository                                 │
│  - Pushes all files                                              │
│  - Returns repository URL                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT                                      │
│  ✅ Fully integrated project                                     │
│  ✅ Frontend with API calls                                      │
│  ✅ Backend with routes/models                                   │
│  ✅ Ready to run                                                 │
│  ✅ Optional: GitHub repository                                  │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure Output

```
project-name/
│
├── frontend/                          ← From GitHub
│   ├── src/
│   │   ├── components/
│   │   │   ├── ItemList.jsx          ← MODIFIED (API calls added)
│   │   │   ├── Login.jsx             ← MODIFIED (API calls added)
│   │   │   └── Dashboard.jsx         ← MODIFIED (API calls added)
│   │   │
│   │   ├── services/                 ← CREATED
│   │   │   └── api.js                ← NEW (API service)
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── .env                          ← CREATED (VITE_API_URL)
│   ├── package.json                  ← MODIFIED (axios added)
│   ├── vite.config.js
│   └── index.html
│
├── backend/                           ← Generated by AI
│   ├── main.py                       ← FastAPI app
│   ├── models.py                     ← Database models
│   ├── schemas.py                    ← Pydantic schemas
│   ├── database.py                   ← DB connection
│   ├── auth.py                       ← JWT auth
│   ├── settings.py                   ← Configuration
│   ├── requirements.txt              ← Dependencies
│   ├── .env.example                  ← Config template
│   └── README.md                     ← Setup instructions
│
├── README.md                          ← Project documentation
├── .gitignore                         ← Git ignore rules
└── docker-compose.yml                 ← Docker config (optional)
```

## API Integration Details

### What Gets Created

```
src/services/api.js
├── Axios Instance
│   ├── Base URL: http://localhost:8000
│   └── Headers: Content-Type: application/json
│
├── Request Interceptor
│   └── Adds Authorization: Bearer <token>
│
├── Response Interceptor
│   └── Handles 401 (auto-logout)
│
├── Authentication Functions
│   ├── login(email, password)
│   ├── register(email, username, password)
│   └── logout()
│
└── API Endpoint Functions
    ├── getItems(params)
    ├── createItem(data)
    ├── updateItem(id, data)
    └── deleteItem(id)
```

### Component Modification Flow

```
Original Component (from GitHub)
├── Has useState
├── Has useEffect
├── Uses mock data
└── Has TODO comments

        ↓ FrontendIntegratorAgent

Modified Component
├── Import API service added
├── useEffect modified with API call
├── Mock data replaced with real data
├── Error handling added
└── Loading states preserved
```

## Data Flow

### Authentication Flow
```
User Login
    ↓
Frontend: login(email, password)
    ↓
API Service: POST /auth/login
    ↓
Backend: Verify credentials
    ↓
Backend: Generate JWT token
    ↓
API Service: Store token in localStorage
    ↓
All subsequent requests include token
```

### Data Fetching Flow
```
Component Mount
    ↓
useEffect triggered
    ↓
API Service: getItems()
    ↓
Request Interceptor: Add auth token
    ↓
Backend: GET /api/items
    ↓
Backend: Verify token
    ↓
Backend: Query database
    ↓
Backend: Return data
    ↓
Response Interceptor: Check status
    ↓
Component: Update state with data
    ↓
UI: Render data
```

### Error Handling Flow
```
API Call
    ↓
Error occurs (401, 500, etc.)
    ↓
Response Interceptor catches error
    ↓
If 401: Remove token, redirect to /login
    ↓
If other: Pass error to component
    ↓
Component: Display error message
```

## Technology Stack

### Frontend
- Framework: React/Vue/Next.js/Svelte (detected)
- HTTP Client: Axios (added automatically)
- State: useState/useEffect
- Auth: localStorage + JWT

### Backend
- Framework: FastAPI/Django/Express (user choice)
- Database: SQLite/PostgreSQL
- Auth: JWT tokens
- ORM: SQLAlchemy/Prisma

### Integration
- API Service: Centralized axios instance
- Interceptors: Request/Response
- Environment: .env files
- CORS: Enabled for local development

## Key Features

### 🔐 Authentication
- JWT token management
- Auto-attach to requests
- Auto-logout on 401
- Secure token storage

### 🔄 Data Fetching
- Async/await pattern
- Error handling
- Loading states
- Real-time updates

### 🛠️ Configuration
- Environment variables
- Easy backend URL change
- Development/production modes

### 📦 Dependencies
- Axios auto-installed
- Version compatibility
- Minimal dependencies

## Benefits Summary

### Before (Manual Integration)
❌ Clone frontend manually
❌ Generate backend separately
❌ Install axios manually
❌ Create API service manually
❌ Modify each component manually
❌ Add auth handling manually
❌ Configure environment manually
⏱️ Time: 2-4 hours

### After (Automatic Integration)
✅ Everything done automatically
✅ Frontend + Backend connected
✅ API calls injected
✅ Auth handling included
✅ Environment configured
✅ Production ready
⏱️ Time: 2-4 minutes

## Usage Example

### Step 1: Generate Project
```bash
# In CODE AGENT UI
1. Enter GitHub URL: https://github.com/user/frontend-repo
2. Select Backend: FastAPI + SQLAlchemy
3. Click "Generate Full Project"
4. Wait 2-4 minutes
5. Download ZIP
```

### Step 2: Run Project
```bash
# Extract ZIP
unzip project-name.zip
cd project-name

# Start Backend
cd backend
pip install -r requirements.txt
python main.py
# Running on http://localhost:8000

# Start Frontend (new terminal)
cd frontend
npm install  # Installs axios automatically
npm run dev
# Running on http://localhost:3000
```

### Step 3: Test Integration
```bash
# Open browser to http://localhost:3000
# Components automatically fetch data from backend
# Login works with JWT tokens
# All CRUD operations connected
```

## Success Metrics

✅ **Zero Manual Work** - Everything automated
✅ **Production Ready** - Best practices included
✅ **Type Safe** - Consistent API calls
✅ **Secure** - Proper auth handling
✅ **Maintainable** - Centralized service
✅ **Fast** - 2-4 minutes generation
✅ **Complete** - Frontend + Backend integrated

---

**The complete workflow from GitHub URL to fully integrated, production-ready application!**
