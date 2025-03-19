# Serverless Python REST API (lambda)

A portfolio project demonstrating a serverless Python REST API with AWS Lambda, API Gateway, and PostgreSQL.

## Architecture

This project implements a RESTful API using:

- **Serverless Framework** for Infrastructure as Code (IaC)
- **AWS Lambda** for serverless function execution
- **API Gateway** for HTTP endpoint management
- **PostgreSQL** for data persistence
- **Dependency Injection** for decoupling components
- **Domain-Driven Design** principles for code organization

## Project Structure

```
serverless-python-api/
├── serverless.yml                # Serverless Framework configuration
├── src/                          # Application source code
│   ├── api/                      # API handlers and schemas
│   ├── core/                     # Core components (DI, DB, etc.)
│   ├── domain/                   # Domain models and services
│   ├── repositories/             # Data access layer
│   └── config/                   # Configuration
├── tests/                        # Test suite
├── migrations/                   # Database migrations
└── requirements.txt              # Python dependencies
```

## API Endpoints

| HTTP Method | Endpoint         | Description            |
|-------------|------------------|------------------------|
| GET         | /health          | Health check           |
| POST        | /users           | Create a new user      |
| GET         | /users           | List users             |
| GET         | /users/{userId}  | Get user by ID         |
| PUT         | /users/{userId}  | Update user            |
| DELETE      | /users/{userId}  | Delete user            |

## Features

- **RESTful API endpoints** for CRUD operations
- **Dependency Injection** for better testability and flexibility
- **PostgreSQL Connection Pooling** for efficient database access
- **Error Handling Middleware** for consistent API responses
- **Request Validation** using data classes
- **Separation of Concerns** with repository and service layers
- **Environment-based Configuration** for different deployment stages
- **AWS Parameter Store Integration** for secure credential management

## Prerequisites

- Python 3.9+
- Node.js 14+ (Serverless Framework)
- PostgreSQL database

## Project Best Practices

This project follows these best practices:

1. **Dependency Injection**: Services and repositories are decoupled and injected where needed using the DI container
2. **Repository Pattern**: Data access is abstracted behind repository interfaces
3. **Service Layer**: Business logic is contained in service classes
4. **Error Handling**: Centralized error handling with consistent responses
5. **Validation**: Request data is validated using data classes
6. **Environment Configuration**: Different settings per environment (dev, test, prod)
7. **Connection Pooling**: Database connections are pooled for efficiency
8. **Secure Credential Storage**: Sensitive data is stored in AWS Parameter Store

## Future Improvements

- Add authentication and authorization (JWT, Cognito)
- Implement database migrations with Alembic
- Add API documentation with Swagger/OpenAPI
- Set up CI/CD pipeline
- Add monitoring and logging (CloudWatch)
- Implement caching layer (Redis)
# python-serverless-rest-api
