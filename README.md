# ARICE Project

## Project Description

(To be filled in)

## Installation

```bash
git clone https://github.com/your-username/ARICE.git
cd ARICE
```

## Docker

This project is fully containerized using Docker. To build and run the application, you'll need to have Docker and Docker Compose installed.

1.  **Build and run the services:**

    ```bash
    docker-compose up --build
    ```

2.  **Access the services:**

    *   **Backend API:** [http://localhost:8000](http://localhost:8000)
    *   **Frontend Web:** [http://localhost:8081](http://localhost:8081)

3.  **To stop the services:**

    ```bash
    docker-compose down
    ```


## Architecture Review (Project File Structure)

The project is a monorepo with a client-server architecture, organized into three main directories:

```
/ARICE
|-- backend/         # FastAPI Python backend
|   |-- app/
|   |   |-- config/    # Pydantic settings management
|   |   |-- models/    # SQLAlchemy ORM models
|   |   |-- routers/   # API endpoint routers
|   |   |-- schemas/   # Pydantic data schemas
|   |   |-- db.py      # Database engine and session setup
|   |   `-- main.py    # FastAPI app instantiation and main entrypoint
|   `-- app.db       # SQLite database file for local development
|
|-- frontend/        # Expo (React Native) frontend
|   |-- app/         # Application screens and navigation (file-based routing)
|   |-- assets/      # Static assets (images, fonts)
|   |-- components/  # Reusable React components
|   |-- constants/   # App-wide constants (e.g., colors, styles)
|   |-- hooks/       # Custom React hooks
|   |-- app.json     # Expo configuration file
|   `-- package.json # NPM dependencies and scripts
|
|-- scripts/         # PowerShell scripts for managing the dev environment
|   |-- dev.ps1      # Starts both backend and frontend servers
|   |-- stop-dev.ps1 # Stops all development processes
|   |-- run-backend.ps1 # Runs only the backend server
|   `-- run-frontend.ps1 # Runs only the frontend server
|
`-- README.md        # This file
```

## Key Features

*   **Architecture Design**: A decoupled monorepo architecture with a Python backend and a React Native (Expo) frontend. Communication occurs via a REST API, allowing the frontend and backend to be developed, tested, and deployed independently.
*   **Frontend Stack**: Built with **Expo** and **React Native**, enabling cross-platform development for web, iOS, and Android from a single codebase. It uses file-based routing for navigation and includes a component-based structure for maintainability.
*   **Database Integration**: The backend uses **SQLAlchemy** as its ORM for database-agnostic data modeling. It is configured to use **SQLite** for local development and can be easily switched to a production database like **PostgreSQL** by changing the `DATABASE_URL` environment variable.

## Git Flow Integration

This project uses a feature-based branching strategy to keep the `develop` branch clean and deployable at all times.


### Branch Structure

*   **`main`**: The primary branch representing the latest stable, production-ready code.
*   **`develop`**: An integration branch where features are merged before being released to `develop`.
*   **`feat/<feature-name>`**: Branches for developing new features. Branched from `feature/<your-branch>` and merged back into `develop` via a pull request.
*   **`fix/<issue-name>`**: Branches for bug fixes. Branched from `develop` and merged back.
*   **`docs/<topic-name>`**: Branches for writing documentation.

### Commit Messages

We follow the **Conventional Commits** specification to create an explicit commit history. Each commit message should be prefixed with a type:

*   **feat**: A new feature.
*   **fix**: A bug fix.
*   **docs**: Documentation only changes.
*   **test**: Adding missing tests or correcting existing tests.
*   **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation.
*   **refactor**: A code change that neither fixes a bug nor adds a feature.

Example: `feat: add user authentication endpoint`

### Pull Request Workflow
When following the pull request workflow, the pull request should be created from the `feature/<your-branch>` branch to the `develop` branch.

**Example Pull Request**
```
## Description 
    This PR includes adding a new feature to frontend 

## Summary of Changes 
 - added new feature to frontend

## Screenshot of changes
 <Picture>

```

## Docs

The backend API documentation is automatically generated and available when the server is running.

*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
