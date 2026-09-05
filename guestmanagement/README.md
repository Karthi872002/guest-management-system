# Guest Management System Documentation

This directory contains comprehensive documentation for the Guest Management System (GMS).

## Documentation Files

### [USER_GUIDE.md](USER_GUIDE.md)
**Target Audience**: End-users, receptionists, administrative staff
**Purpose**: Guide for daily operation of the system
**Contents**:
- Overview of the system and user roles
- Step-by-step instructions for managing guests, invitations, and visits
- Common workflows and best practices
- Glossary of terms
- Getting help and support

### [API_SPECIFICATION.md](API_SPECIFICATION.md)
**Target Audience**: API consumers, frontend developers, integrators
**Purpose**: Technical reference for all API endpoints
**Contents**:
- Authentication mechanisms (JWT token acquisition and refresh)
- Detailed endpoint specifications for Guests, Invitations, and Visits
- Request/response formats and examples
- Query parameters and filtering capabilities
- Error response formats and HTTP status codes
- Data models and schemas
- Rate limiting and versioning information

### [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md)
**Target Audience**: Developers, contributors, system architects
**Purpose**: In-depth technical architecture and implementation details
**Contents**:
- System architecture and layered design
- Design patterns implemented (Dependency Injection, Repository, Service Layer)
- Detailed specifications for each layer:
  - Data models and relationships
  - Service layer business logic
  - Repository layer data access
  - API layer ViewSets and serializers
- Authentication and authorization mechanisms
- Security considerations and best practices
- Performance considerations and optimization
- Development guidelines and coding standards
- Deployment considerations and extensibility points

## How to Use This Documentation

### For End-Users
Start with the [USER_GUIDE.md](USER_GUIDE.md) to learn how to perform daily tasks in the system.

### For Developers Integrating with the API
Refer to the [API_SPECIFICATION.md](API_SPECIFICATION.md) for complete details on available endpoints, authentication requirements, and data formats.

### For Developers Working on the Codebase
Consult the [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) for understanding the architecture, design patterns, and implementation details.

### For All Users
The [CLAUDE.md](../CLAUDE.md) file in the project root provides guidance specifically for Claude Code AI assistant when working with this repository.

## Documentation Version
All documents are version 1.0, last updated September 2026.

## Relationship Between Documents
```
User Guide  ←→  API Specification  ←→  Technical Specification
    ↑              ↑                     ↑
End-users    API Consumers       Developers/Contributors
```

Each document builds upon the information in the others, providing appropriate depth for different audiences while maintaining consistency across the documentation set.