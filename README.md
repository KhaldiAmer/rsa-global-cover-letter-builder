# RSA Global Cover Letter Builder

A comprehensive job application tracking system built with Temporal Cloud workflows, Gemini AI, React, and FastAPI. Features automated cover letter generation, deadline management, and intelligent reminder systems.

## 🚀 Features

- **Automated Workflow Management**: Temporal Cloud workflows handle application lifecycles
- **AI-Powered Cover Letters**: Gemini AI generates personalized cover letters
- **Deadline Tracking**: Automatic reminders when deadlines approach
- **Status Management**: Track application progress from submission to offer
- **Real-time Updates**: Live status updates through Temporal signals
- **Production Ready**: Deployed with full CI/CD pipeline

## 🏗️ Architecture

### Technology Stack

- **Frontend**: React 18 with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python 3.11
- **Workflows**: Temporal Cloud for reliable workflow orchestration
- **AI**: Google Gemini 1.5 Flash for cover letter generation
- **Database**: PostgreSQL for persistent storage
- **Deployment**: Docker with Terraform Infrastructure as Code
- **CI/CD**: GitHub Actions for automated deployment

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │    │  Temporal Cloud │
│   (Frontend)    │────│   (Backend)     │────│   (Workflows)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   Gemini AI     │
                       │   (Database)    │    │   (LLM API)     │
                       └─────────────────┘    └─────────────────┘
```

## 🔧 Prerequisites

Before running this project, ensure you have:

1. **API Keys**:

   - Google Gemini API key ([Get here](https://makersuite.google.com/app/apikey))
   - Temporal Cloud account ([Sign up](https://temporal.io/cloud))

2. **Development Tools**:
   - Docker and Docker Compose
   - Node.js 18+
   - Python 3.11+
   - Git

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/KhaldiAmer/rsa-global-cover-letter-builder.git
cd rsa-global-cover-letter-builder
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
TEMPORAL_API_KEY=your_temporal_cloud_api_key_here
TEMPORAL_ADDRESS=your-namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=your-namespace
```

### 3. Run with Docker Compose

```bash
# Start database and backend services
docker-compose up --build backend worker

# In a separate terminal, start frontend
docker-compose up --build frontend
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 📱 Usage

### Creating a Job Application

1. Navigate to http://localhost:3000
2. Click "Add New Application"
3. Fill in:
   - Company name
   - Role title
   - Job description
   - Your resume content
   - Email for notifications
   - Deadline (weeks from now)
4. Click "Start Application Workflow"

### Tracking Application Status

1. View all applications on the dashboard with real-time status
2. Click "View Details" for any application
3. See current status, AI-generated cover letter, and reminders
4. Update status when you hear back from companies
5. Get automatic reminders when deadlines approach

### Workflow Features

- **Automatic Cover Letter**: Generated within minutes using Gemini AI
- **Smart Deadline Tracking**: Monitors application progress automatically
- **Status Updates**: Real-time updates through Temporal Cloud signals
- **Intelligent Reminders**: Notifications when deadlines approach
- **Auto-archiving**: Applications archived after grace period with no updates

## 🛠️ Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Testing the API

```bash
# Health check
curl http://localhost:8000/api/health/

# Create application
curl -X POST "http://localhost:8000/api/applications/" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Example Corp",
    "role": "Software Engineer",
    "job_description": "Looking for talented developers...",
    "resume": "Experienced developer with...",
    "user_email": "test@example.com",
    "deadline_weeks": 2
  }'

# List applications
curl http://localhost:8000/api/applications/
```

## 🌐 Production Deployment

### Prerequisites

1. **Terraform Cloud Account**: For infrastructure management
2. **GitHub Repository**: For CI/CD pipeline
3. **Cloud Provider Account**: For hosting services

### GitHub Secrets Configuration

Add these secrets to your GitHub repository:

```
GEMINI_API_KEY
TEMPORAL_API_KEY
TEMPORAL_ADDRESS
TEMPORAL_NAMESPACE
```

### Deployment Steps

1. **Create GitHub Repository**:

   ```bash
   gh repo create job-tracker --private
   git remote add origin https://github.com/YOUR_USERNAME/job-tracker.git
   ```

2. **Configure Infrastructure**:

   - Update Terraform configurations in `terraform/` directory
   - Set up cloud provider credentials
   - Configure environment variables

3. **Deploy**:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push origin main
   ```

## 📊 Monitoring & Health

### Application Health

- **Backend Health**: `GET /api/health`
- **Database Connection**: Automatic health checks
- **Temporal Connection**: Verified on startup

### Workflow Management

- **Status Tracking**: Real-time workflow state monitoring
- **Error Handling**: Comprehensive error recovery
- **Retry Policies**: Configurable retry mechanisms for activities

## 🔒 Security

- **API Key Management**: Secure environment variable handling
- **Database Security**: Parameterized queries prevent SQL injection
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: Built-in FastAPI rate limiting
- **CORS Configuration**: Proper cross-origin resource sharing setup

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Data models
│   │   ├── workflows/      # Temporal workflows
│   │   ├── activities/     # Temporal activities
│   │   └── main.py         # Application entry point
│   ├── Dockerfile          # Backend container
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── screens/        # Page components
│   │   └── services/       # API services
│   ├── Dockerfile.dev      # Frontend container
│   └── package.json        # Node dependencies
├── terraform/              # Infrastructure as Code
├── .github/               # CI/CD workflows
├── docker-compose.remote.yml # Docker setup for remote Temporal
└── README.md              # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Backend not starting:**

- Check that PostgreSQL is running: `docker-compose ps`
- Verify environment variables in `.env` file
- Check logs: `docker-compose logs backend`

**Frontend build failures:**

- Clear node_modules: `rm -rf frontend/node_modules && cd frontend && npm install`
- Check memory allocation for Docker
- Verify React build process: `cd frontend && npm run build`

**Temporal connection issues:**

- Verify TEMPORAL_API_KEY is valid and not expired
- Check TEMPORAL_ADDRESS format: `namespace.region.gcp.api.temporal.io:7233`
- Ensure network connectivity to Temporal Cloud

**Workflow not starting:**

- Check Temporal worker is running: `docker-compose logs worker`
- Verify workflow registration in worker logs
- Check activity function availability

### Getting Help

- Check existing issues in the repository
- Review Temporal Cloud documentation
- Check FastAPI and React documentation for framework-specific issues

---

**Status**: ✅ Production Ready with enhanced UI/UX, robust error handling, and comprehensive workflow management.
