# 📅 smart-room <br>  Meeting Room Reservation System API


## Table of Contents
1. [Description](#description)
2. [Features](#features)
    - [Auth](#auth)
    - [📄 Rooms](#rooms)
    - [Reservations](#reservations)
3. [Installation](#installation)
    - [Clone the Repository](#clone-the-repository)
    - [Environment Variables](#environment-variables)
    - [Setup with Docker Compose](#setup-with-docker-compose)
4. [API Documentation](#api-documentation)
5. [Running Tests](#running-tests)
6. [CI/CD with GitHub Actions](#ci-cd-with-github-actions)
7. [Architecture and Database](#architecture-and-database)
    - [Architecture: Monolithic](#architecture-monolithic)
    - [Database: PostgreSQL](#database-postgresql)
8. [Database Migrations with Alembic](#database-migrations-with-alembic)
9. [Extra Features Implemented](#extra-features-implemented)

---

## Description

The **smart-room** is a backend system designed to manage meeting room reservations. This API allows users to:

- Register meeting rooms.
- Check room availability.
- Reserve available rooms.
- Cancel reservations.

It ensures that no conflicts occur when reserving the same room at overlapping times.

---
## Features

### Auth

- **POST /auth/register** - Register a new user.
- **POST /auth/login** - Login an existing user.

---

### Rooms

- **POST /rooms/** - Create a new meeting room.
- **GET /rooms/** - Get a list of all available meeting rooms (📄 supports pagination).
- **GET /rooms/{room_id}/reservations** - Get all reservations for a specific room (📄 supports pagination).
- **GET /rooms/{id}/availability** - Check the availability of a specific room within a time range.

---

### Reservations

- **POST /reservations/** - Make a room reservation at a given time.
- **DELETE /reservations/{reservation_id}** - Cancel a previously created reservation.

---

Let me know if you need any further modifications! 😊


---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/smart-room.git
cd smart-room
```

### 2. Environment Variables:
   To run this project you need to create a .env file and fill the variables
   Copy the .env.exemple file and rename as .env, writing down the variables:

```bash
    POSTGRES_DB=smart_room
    POSTGRES_USER=
    POSTGRES_PASSWORD=
    DB_HOST=db
    DB_PORT=5432
```

You only have to assign the POSTGRES_USER and POSTGRES_PASSWORD to your preference

### 3. Setup with Docker

The project uses **Docker Compose** to run both the application and the database. Follow the steps below to get everything up and running: <br>
**Build and start the containers:**
   From the root of the project, run the following command to start the application and the database:

```bash
docker-compose up --build
```

This command will: </br>
➜ Build the images for the application and the database. </br>
➜ Start the application on http://localhost:8000 and connect it to the database.


## API Documentation
Once the server is running, you can access the Swagger UI documentation at:
```bash
http://localhost:8000/docs
```
Alternatively, Redoc documentation is available at:
```bash
http://localhost:8000/redoc
```

## Running Tests
To run the tests, use the following command:
```bash
docker-compose exec fastapi_app pytest
```

## CI/CD with GitHub Actions

This project is integrated with **GitHub Actions** for continuous integration and deployment. The pipeline executes the following steps:

- Installs dependencies.
- Runs unit tests with 95% coverage.
- Runs **pre-commit hooks** for linters including:
  - `black` (auto-formatting).
  - `isort` (sorting imports).
  - `flake8` (code style checks).

These steps ensure that your code is always correctly formatted, linted, and well-tested before being merged or deployed.


## Architecture and Database

### Architecture: Monolithic

The application follows a **monolithic** architecture, meaning that all components are part of a single codebase. <br> This approach was chosen for simplicity and faster development, as the project doesn't require complex distributed systems or microservices at this stage.

### Database: PostgreSQL

The project uses **PostgreSQL** as the database.  <br>PostgreSQL was selected due to its reliability, powerful features (such as ACID compliance and support for complex queries), and its ability to scale as the application grows.


## Database Migrations with Alembic

To improve database management and ensure smooth transitions between schema changes, we are using **Alembic** as the versioning tool for migrations.

When you run `docker-compose up --build`, Alembic automatically applies the database migrations. This ensures that your database schema is always up to date with the latest changes, without needing any extra steps.


## Extra Features Implemented
**User Authentication & Authorization**: All routes needs to be authenticated to use it.

**Notifications**: Simulated notifications via logs or console output to register user's action.

**Data Validation**: Validation implemented to ensure all creations and reservations occurs logically.
