# ARICE Project

## Project Description

This is ARICE

## 1. Installation

### Python Version

- [Python 3.13.5](https://www.python.org/downloads/release/python-3135/)

### IDE (Integrated Development Environment)

- [Visual Studio Code](https://code.visualstudio.com/download)

### Docker

- [Docker](https://www.docker.com/)

### Cloning Project

```bash
    git clone https://github.com/Markrodriguez1105/wonderpets.git
    cd wonderpets
```

---

## 2. Run Project

### Docker

This project is fully containerized using Docker. To build and run the application, you'll need to have [Docker](https://www.docker.com/) and Docker Compose installed.

1.  **Build and run the services:**

    ```bash
    docker compose up --build -d
    ```

    - Run specific services

    ```bash
    docker compose up --build -d "frontend" #Run React Native
    ```

    ```bash
    docker compose up --build -d "backend" #Run FastAPI
    ```

    ```bash
    docker compose up --build -d "postgre" #Run PostgreSQL
    ```

2.  **Access the services:**

    - **Backend API:** [http://localhost:8000](http://localhost:8000)
    - **Frontend Web:** [http://localhost:8081](http://localhost:8081)

3.  **To stop the services:**

    ```bash
    docker compose down
    ```

4.  **Configure Postgre Database**
    [PostgreSQL CLI Commands Cheat Sheet](postgres_cli_commands.md)

### Local Execution

For development mode

1. **Run `PostgreSQL` using Docker**
   ```bash
   docker compose up --build -d "postgre"
   ```
2. **Run `FastAPI` (Backend)**
   1. Move to backend directory
      ```bash
      cd backend
      ```
   2. Initialize Virtual Environment
      ```bash
      python -m venv .venv
      ```
   3. Activate Virtual Environment
      ```bash
      .venv\Scripts\Activate
      ```
   4. Install required dependencies
      ```bash
      pip install -r app/requirements.txt
      ```
   5. Run migration using alembic
      ```bash
      alembic upgrade head
      ```
   6. Run FastAPI Service using uvicorn
      ```bash
      uvicorn app.main:app --reload
      ```
3. **Run `React Native` (Frontend)**
   1. Move to frontend directory
      ```bash
      cd frontend
      ```
   2. Install dependencies
      ```bash
      npm install
      ```
   3. Run and Build frontend service
      ```bash
      npx expo start
      ```

[//]: # "### Running Scripts "
[//]: #
[//]: # "**Running both frontend and backend environments**"
[//]: #
[//]: # "    ``` bash"
[//]: # "    ./scripts/dev.ps1"
[//]: # "    ```"
[//]: # "**Running both frontend environments using scripts**"
[//]: #
[//]: # "    ``` bash"
[//]: # "    ./scripts/run-frontend.ps1"
[//]: # "    ```"
[//]: # "**Running both backend environments using scripts**"
[//]: #
[//]: # "    ``` bash"
[//]: # "    ./scripts/run-backend.ps1"
[//]: # "    ```"
[//]: # "**Stoping both backend environments using scripts**"
[//]: #
[//]: # "    ``` bash"
[//]: # "    ./scripts/stop-dev.ps1"
[//]: # "    ```"

## Architecture Review (Project File Structure)

The project is a monorepo with a client-server architecture, organized into three main directories:

```
/ARICE
|-- backend/         # FastAPI Python backend
|   |-- app/
|       |-- alembic/   # Migration versioning tool
|       |-- config/    # Pydantic settings management
|       |-- models/    # SQLAlchemy ORM models
|       |-- routers/   # API endpoint routers
|       |-- schemas/   # Pydantic data schemas
|       |-- db.py      # Database engine and session setup
|       |-- dependencies.py     #Export the db to perform query
|       |-- main.py    # FastAPI app instantiation and main entrypoint
|       `-- requirements.txt    #Lists of dependencies for this projects
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
    |-- dev.ps1      # Starts both backend and frontend servers
    |-- stop-dev.ps1 # Stops all development processes
    |-- run-backend.ps1 # Runs only the backend server
    `-- run-frontend.ps1 # Runs only the frontend server


```

## Key Features

- **Architecture Design**: A decoupled monorepo architecture with a Python backend and a React Native (Expo) frontend. Communication occurs via a REST API, allowing the frontend and backend to be developed, tested, and deployed independently.
- **Frontend Stack**: Built with **Expo** and **React Native**, enabling cross-platform development for web, iOS, and Android from a single codebase. It uses file-based routing for navigation and includes a component-based structure for maintainability.
- **Database Integration**: The backend uses **SQLAlchemy** as its ORM for database-agnostic data modeling. It is configured to use **Alembic** for local development and can be easily switched to a production database like **PostgreSQL** by changing the `DATABASE_URL` environment variable.

## Git Flow Integration

This project uses a feature-based branching strategy to keep the `develop` branch clean and deployable at all times.

### Branch Structure

- **`main`**: The primary branch representing the latest stable, production-ready code.
- **`develop`**: An integration branch where features are merged before being released to `develop`.
- **`feat/<feature-name>`**: Branches for developing new features. Branched from `feature/<your-branch>` and merged back into `develop` via a pull request.
- **`fix/<issue-name>`**: Branches for bug fixes. Branched from `develop` and merged back.
- **`docs/<topic-name>`**: Branches for writing documentation.

### Commit Messages

We follow the **Conventional Commits** specification to create an explicit commit history. Each commit message should be prefixed with a type:

- **feat**: A new feature.
- **fix**: A bug fix.
- **docs**: Documentation only changes.
- **test**: Adding missing tests or correcting existing tests.
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation.
- **refactor**: A code change that neither fixes a bug nor adds a feature.

Example: `feat: add user authentication endpoint`

### Pull Request Workflow

When following the pull request workflow, the pull request should be created from the `feature/<your-branch>` branch to the `develop` branch.

**Example Pull Request**

```
## Description
    This PR includes adding a new feature to the frontend

## Summary of Changes
 - added new feature to frontend

## Screenshot of changes
 - <Picture>

```

## Docs

The backend API documentation is automatically generated and available when the server is running.

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
