# Diabetes Risk Assessment Web App

A modern web application that provides personalized diabetes risk assessments, generates insights, and offers actionable recommendations using AI/ML capabilities.

## 🎯 Project Goals

- Provide personalized diabetes risk assessment based on health data.
- Generate natural language health recommendations and preventive measures.
- Offer a clear dashboard to visualize individual assessment results.
- Enable a straightforward user journey for new and returning users.

## 🛠 Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React, Material-UI
- **Database**: PostgreSQL
- **Notifications**: Slack (backend integration)
- **AI/ML**: `scikit-learn` for risk assessment, Hugging Face API for LLM recommendations

## 📋 Prerequisites

- Docker and Docker Compose
- Git

## 🚀 Setup Instructions

### Using Docker Compose (Recommended)

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd capsLock\ Project # Navigate to your project directory
    ```

2.  **Create a `.env` file:**

    In the root of your project directory (where `docker-compose.yml` is located), create a file named `.env` and add your database credentials:

    ```dotenv
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_NAME=diabetes_analysis
    # Add any other environment variables required by your backend services here
    # Example: HUGGING_FACE_API_KEY=your_hugging_face_api_key
    ```

3.  **Build and run the services:**

    This command will build the Docker images, create the necessary containers, run database migrations, and load initial dataset data.

    ```bash
    docker compose up --build
    ```

    - The `init_db` service will ensure migrations are applied and the dataset is loaded before the backend starts.
    - The `backend` service will run on `http://localhost:8000`.
    - The `frontend` service will be accessible on `http://localhost:80`.

## 📚 API Documentation

Once the backend server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔄 Development Workflow

1.  Create a new branch for your feature.
2.  Make your changes.
3.  Write/update tests.
4.  Submit a pull request.

## 📝 Project Structure

```
.
├── backend/           # FastAPI backend
├── frontend/         # React frontend
├── docs/            # Project documentation
├── .gitignore
├── README.md
└── docker-compose.yml
```

## 🤝 Contributing

1.  Fork the repository.
2.  Create your feature branch.
3.  Commit your changes.
4.  Push to the branch.
5.  Create a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Project Plan](PLAN.md)
- [Requirements](REQUIREMENTS.md)
