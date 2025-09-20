# Assembly Parts Backend

## Project Overview
This project implements a backend service for managing an inventory of assembly parts, categorized as `RAW` or `ASSEMBLED`. It supports complex nested assemblies, enforces roles and permissions using JWT authentication, and follows clean-code and SOLID principles for a robust and maintainable design.

## Tech Stack
*   **Language**: Python
*   **Framework**: FastAPI
*   **Database**: PostgreSQL (using SQLAlchemy as ORM)
*   **Authentication**: JWT (JSON Web Tokens)
*   **Dependency Management**: `pip` with `requirements.txt`
*   **Environment Variables**: `python-dotenv`

## Architecture
The project follows an **MVC (Model-View-Controller) Pattern**, adapted for a RESTful API:
*   **Models**: Defined using SQLAlchemy for database interaction (`app/models/models.py`).
*   **Views (API Endpoints)**: Handled by FastAPI routers (`app/api/routes.py`).
*   **Controllers (Services)**: Contains the core business logic and interacts with repositories (`app/services/`).
*   **Repositories**: Abstracts database operations for models (`app/repositories/`).
*   **Schemas**: Pydantic models for request validation and response serialization (`app/schemas/`).

## Key Principles & Practices
*   **SOLID Principles**: Emphasis on Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion to ensure an extensible and loosely coupled design.
*   **Clean Code**: Prioritizes clarity, structure, and maintainability through meaningful names, small functions, and adherence to the DRY (Don't Repeat Yourself) principle.
*   **Request Validation**: All incoming requests are validated using Pydantic schemas.
*   **AI Tooling**: Encouraged use of AI tools (e.g., GitHub Copilot, ChatGPT) to enhance productivity and code quality.

## Core Requirements Implemented

### 1. Authentication (JWT)
*   All API calls that modify system state (create parts, add inventory, etc.) require an `Authorization` header with a valid JWT token.
*   Ensures only authenticated users can perform sensitive inventory operations.
*   User ID from JWT claims is recorded for auditing purposes on each action.

### 2. Roles & Permissions
The system supports two distinct roles:

*   **`Creator`**
    *   Can create new parts (`RAW` or `ASSEMBLED`).
    *   Can add parts to the inventory.
    *   Can view all parts and assemblies.
*   **`Viewer`**
    *   Can only view parts and assemblies.
    *   Cannot create, modify, or update inventory.

### 3. Part Types and Properties
The system handles two types of parts:

*   **`Raw Parts`**
    *   Purchased from external suppliers (e.g., "Bolts").
    *   Properties: `unique identifier (string)`, `name`, `type: RAW`, `quantity in stock`.
*   **`Assembled Parts`**
    *   Built by combining raw and/or other assembled parts (e.g., "Gearbox").
    *   Properties: `unique identifier (string)`, `name`, `type: ASSEMBLED`, `quantity in stock`.
    *   Additionally store: A list of required constituent parts with their respective quantities.

## Problem Statement: REST APIs

### 1. Create Part Entry
API to register raw and assembled parts.

*   **Endpoint**: `POST /api/part`
*   **Authentication**: Required (Creator role)

**Request to register a raw part:**
```json
{
    "name": "Bolt",
    "type": "RAW"
}
```
**Response (example):**
```json
{
    "id": "bolt-1",
    "name": "Bolt",
    "type": "RAW",
    "quantity_in_stock": 0
}
```

**Request to register an assembled part:**
```json
{
    "name": "Gearbox",
    "type": "ASSEMBLED",
    "parts": [
        {"id": "bolt-1", "quantity": 4},
        {"id": "shaft-1", "quantity": 2}
    ]
}
```
**Response (example):**
```json
{
    "id": "gearbox-1",
    "name": "Gearbox",
    "type": "ASSEMBLED",
    "quantity_in_stock": 0,
    "parts": [
        {"id": "bolt-1", "quantity": 4},
        {"id": "shaft-1", "quantity": 2}
    ]
}
```

### 2. Add Parts to Inventory
API to add parts to inventory.

*   **Endpoint**: `POST /api/part/<partId>`
*   **Authentication**: Required (Creator role)

**Add Raw Part:** Adds raw parts directly to inventory.
**Add Assembled Part:** Automatically deducts the required quantities of constituent parts from inventory. If any constituent part has insufficient quantity, the operation fails gracefully (no partial updates).

**Request:**
```json
{
    "quantity": 4
}
```
**Response (Success):**
```json
{
    "status": "SUCCESS"
}
```
**Response (Failed - Example):**
```json
{
    "status": "FAILED",
    "message": "Insufficient quantity - shaft-01"
}
```

## System Requirements
*   **Nested Assemblies**: Supports any level of nested assemblies (sub-assemblies of sub-assemblies, etc.).
*   **Circular Dependency Prevention**: Logic to prevent circular dependencies (e.g., `A → B → A`).
*   **Atomic Operations**: Uses database transactions to ensure data consistency (no partial updates).
*   **Code Quality**: Designed with clean, robust, and maintainable code practices.
*   **Performance**: Optimized for performance.

## Setup and Running the Project

### Prerequisites
*   Python 3.11+
*   Docker (for local PostgreSQL database)

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd assembly-parts-backend
```

### 2. Set up a Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL Database with Docker
```bash
docker run --name assembly-parts-postgres -e POSTGRES_DB=assembly_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```
*(If port 5432 is already in use, stop the conflicting process or change the `-p` mapping, e.g., `-p 5433:5432`)*

### 5. Create `.env` file
Create a file named `.env` in the `assembly-parts-backend/` directory with your JWT secret and database URL:
```
JWT_SECRET="your_generated_jwt_secret_key"
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/assembly_db"
```
*(Replace `your_generated_jwt_secret_key` with a key generated using `python3 scripts/generate_jwt_secret.py`)*

### 6. Create Initial Users
```bash
PYTHONPATH=. python3 scripts/create_initial_users.py
```

### 7. Run the Application
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```
*(If port 8001 is already in use, try changing it to `8002` or another available port.)*

### 8. Test Authentication
Once the application is running, you can test the authentication:
```bash
curl -X POST "http://127.0.0.1:8001/api/auth/token" \
-H "Content-Type: application/json" \
-d '{"username":"creator","password":"creatorpass"}'
```
This should return a JWT token.

## API Documentation
Once the application is running, you can access the interactive API documentation at:
*   **Swagger UI**: `http://127.0.0.1:8001/docs`
*   **ReDoc**: `http://127.0.0.1:8001/redoc`
