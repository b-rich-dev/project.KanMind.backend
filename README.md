# KanMind - Kanban Board Backend API

A Django REST Framework-based backend API for managing Kanban boards, tasks, and team collaboration.

## Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Permissions & Access Control](#permissions--access-control)
- [Special Features & Business Logic](#special-features--business-logic)
- [Project Structure](#project-structure)

## Features

- **User Authentication**: Token-based authentication with registration and login
- **Kanban Boards**: Create and manage multiple Kanban boards
- **Task Management**: Create, update, delete tasks with status tracking
- **Team Collaboration**: Board ownership and member management
- **Task Assignment**: Assign tasks to team members with assignee and reviewer roles
- **Comments**: Add and manage comments on tasks
- **Email Validation**: Check if user emails are registered
- **Filtered Views**: Get tasks assigned to you or tasks you're reviewing

## Technology Stack

- **Framework**: Django 6.0.1
- **API**: Django REST Framework 3.16.1
- **Database**: SQLite (development)
- **Authentication**: Token-based authentication
- **CORS**: django-cors-headers 4.9.0
- **Python**: 3.x

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment tool (venv)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/b-rich-dev/project.KanMind.backend
cd project.KanMind.backend
```

### 2. Create Virtual Environment

```bash
python -m venv env
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\env\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
.\env\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source env/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Configuration

### CORS Settings

The application is configured to accept requests from:
- `http://127.0.0.1:5500`
- `http://localhost:5500`

To modify CORS settings, edit `core/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]
```

### Database

The project uses SQLite by default. The database file `db.sqlite3` is created automatically after running migrations.

## Running the Application

### Start Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

### Access Admin Panel

Navigate to: `http://127.0.0.1:8000/admin/`

Login with your superuser credentials.

## API Documentation

### Base URL
```
http://127.0.0.1:8000/api/
```

### Authentication Endpoints

#### Register User
- **POST** `/auth/register/`
- **Body**:
```json
{
  "fullname": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "repeated_password": "securepassword"
}
```
- **Response**: Token, user data

#### Login
- **POST** `/auth/login/`
- **Body**:
```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```
- **Response**: Token, user data

#### Logout
- **POST** `/auth/logout/`
- **Headers**: `Authorization: Token <your-token>`
- **Response**: Success message

### Board Endpoints

#### List/Create Boards
- **GET** `/boards/` - List all boards accessible to user
- **POST** `/boards/` - Create new board
- **Headers**: `Authorization: Token <your-token>`
- **POST Body**:
```json
{
  "title": "My Project Board",
  "members": [2, 3, 5]
}
```

#### Board Details
- **GET** `/boards/<id>/` - Get board details with tasks
- **PATCH** `/boards/<id>/` - Update board
- **DELETE** `/boards/<id>/` - Delete board (owner only)
- **Headers**: `Authorization: Token <your-token>`
- **PATCH Body**:
```json
{
  "title": "Updated Title",
  "members": [2, 3, 5, 8]
}
```

### Task Endpoints

#### List/Create Tasks
- **GET** `/tasks/` - List all tasks
- **POST** `/tasks/` - Create new task
- **Headers**: `Authorization: Token <your-token>`
- **POST Body**:
```json
{
  "board": 1,
  "title": "Implement feature",
  "description": "Detailed description",
  "status": "to_do",
  "priority": "high",
  "assignee_id": 3,
  "reviewer_id": 5,
  "due_date": "2026-02-15"
}
```

#### Task Details
- **GET** `/tasks/<id>/` - Get task details
- **PATCH** `/tasks/<id>/` - Update task
- **DELETE** `/tasks/<id>/` - Delete task
- **Headers**: `Authorization: Token <your-token>`

#### Assigned Tasks
- **GET** `/tasks/assigned-to-me/` - Get tasks assigned to current user

#### Reviewing Tasks
- **GET** `/tasks/reviewing/` - Get tasks where current user is reviewer

### Comment Endpoints

#### List/Create Comments
- **GET** `/tasks/<task_id>/comments/` - List task comments
- **POST** `/tasks/<task_id>/comments/` - Create comment
- **Headers**: `Authorization: Token <your-token>`
- **POST Body**:
```json
{
  "content": "This is a comment"
}
```

#### Comment Details
- **GET** `/tasks/<task_id>/comments/<comment_id>/` - Get comment
- **PATCH** `/tasks/<task_id>/comments/<comment_id>/` - Update comment
- **DELETE** `/tasks/<task_id>/comments/<comment_id>/` - Delete comment (author only)

### Utility Endpoints

#### Email Check
- **GET** `/email-check/?email=user@example.com`
- **Headers**: `Authorization: Token <your-token>`
- **Response**: User data if exists, 404 if not found

## Authentication

The API uses **Token-based authentication**. After registration or login, you'll receive a token that must be included in the `Authorization` header for all protected endpoints:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Permissions & Access Control

### Board Access
- **Owner**: Full access (read, update, delete)
- **Members**: Can read and update board, cannot delete
- **Non-members**: No access

### Task Access
- **Create**: Only board members can create tasks
- **Read/Update**: Only board members
- **Delete**: Only task creator or board owner

### Comment Access
- **Create**: Only board members
- **Read**: Only board members
- **Delete**: Only comment author

## Special Features & Business Logic

### 1. Board Visibility
Users can see boards where they are:
- Owner
- Member
- Assignee of at least one task

### 2. Task Assignment Validation
- **Assignee** and **Reviewer** must be board members
- If not specified, fields remain empty (allowed)
- Attempting to assign non-members returns **400 Bad Request**

### 3. Board Field Protection
- The `board` field in tasks is **read-only** during updates
- Tasks cannot be moved between boards

### 4. Task Creator Tracking
- Each task stores its creator in the `created_by` field
- Only creator or board owner can delete tasks

### 5. Comment Chronology
- Comments are automatically sorted by creation date (oldest first)
- Creation timestamp is automatically set

### 6. Email Uniqueness
- Email addresses must be unique during registration
- Duplicate emails return **400 Bad Request**

### 7. Board Deletion Restrictions
- Only board owners can delete boards
- Members can only view/update

### 8. 404 vs 403 Handling
- **404 Not Found**: Resource doesn't exist
- **403 Forbidden**: Resource exists but access denied
- **401 Unauthorized**: Authentication required

### 9. Automatic Owner Assignment
- User creating a board automatically becomes the owner
- User creating a task is set as `created_by`
- User creating a comment is set as `author`

### 10. Task Status & Priority
**Status Options**: `to_do`, `in_progress`, `review`, `done`  
**Priority Options**: `low`, `medium`, `high`

## Project Structure

```
project.KanMind.backend/
├── auth_app/              # User authentication
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── models.py
├── kanban_app/            # Kanban board functionality
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── models.py
├── core/                  # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3            # Database file
├── manage.py
├── requirements.txt
└── README.md
```

## Models Overview

### KanbanBoard
- `title`: Board name
- `owner`: Board creator (ForeignKey to User)
- `members`: Board members (ManyToMany to User)
- Timestamps: `created_at`, `updated_at`

### Task
- `board`: Associated board (ForeignKey)
- `title`, `description`
- `status`: to_do, in_progress, review, done
- `priority`: low, medium, high
- `assignee`, `reviewer_id`: Assigned users
- `created_by`: Task creator
- `due_date`: Optional deadline
- Timestamps: `created_at`, `updated_at`

### Comment
- `task`: Associated task (ForeignKey)
- `author`: Comment creator (ForeignKey to User)
- `content`: Comment text (max 1000 chars)
- Timestamp: `created_at`

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **204 No Content**: Successful deletion (no response body)
- **400 Bad Request**: Invalid data or validation error
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource doesn't exist

## Development Notes

1. **Default Status**: New tasks default to `to_do` status
2. **Default Priority**: New tasks default to `medium` priority
3. **Partial Updates**: PATCH requests support partial updates (omit unchanged fields)
4. **Cascading Deletes**: Deleting a board deletes all associated tasks and comments
5. **Soft Deletes**: Not implemented - all deletes are permanent

## Support & Contact

For issues, questions, or contributions, please contact the development team.

## License

[Specify your license here]

---

**Last Updated**: January 2026
