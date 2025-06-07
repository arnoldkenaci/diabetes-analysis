# Automated Dataset Analysis Web App

A modern web application that automatically analyzes datasets, generates insights, and provides actionable recommendations using AI/ML capabilities.

## 🎯 Project Goals

- Automate dataset analysis and insight generation
- Provide real-time notifications for significant findings
- Create an intuitive dashboard for data visualization
- Generate natural language summaries and recommendations
- Enable scheduled/triggered analysis workflows

## 🛠 Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React
- **Database**: PostgreSQL
- **Notifications**: Slack
- **AI/ML**: Hugging Face API

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Git

## 🚀 Setup Instructions

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

### Database Setup

1. Install PostgreSQL if not already installed
2. Create a new database:
   ```sql
   CREATE DATABASE dataset_analysis;
   ```
3. Run migrations (when available):
   ```bash
   cd backend
   alembic upgrade head
   ```

## 📚 API Documentation

Once the backend server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔄 Development Workflow

1. Create a new branch for your feature
2. Make your changes
3. Write/update tests
4. Submit a pull request

## 📝 Project Structure

```
.
├── backend/           # FastAPI backend
├── frontend/         # React frontend
├── docs/            # Project documentation
├── .gitignore
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Project Plan](PLAN.md)
- [Requirements](REQUIREMENTS.md)
