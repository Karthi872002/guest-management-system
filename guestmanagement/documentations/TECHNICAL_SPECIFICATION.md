# Guest Management System - Technical Specification

## Overview

This document provides detailed technical specifications for developers working on the Guest Management System. It covers the system architecture, design patterns, implementation details, and development guidelines.

## System Architecture

### High-Level Architecture

The Guest Management System follows a layered architecture pattern:

```
Presentation Layer (API/Controllers)
        ↓
Application Layer (Services)
        ↓
Domain Layer (Models/Entities)
        ↓
Infrastructure Layer (Repositories/Persistence)
        ↓
Database (PostgreSQL/SQLite)
```

### Components

1. **Presentation Layer**: Django REST Framework ViewSets handling HTTP requests/responses
2. **Application Layer**: Service classes containing business logic
3. **Domain Layer**: Django models representing business entities
4. **Infrastructure Layer**: Repository implementations handling data access
5. **Cross-cutting Concerns**: Authentication, authorization, validation

## Design Patterns Implemented

### 1. Dependency Injection Pattern
- **Location**: `apps/gms/dependencies.py`
- **Implementation**: Services are instantiated once at startup and accessed via `get_service()` function
- **Benefits**: 
  - Loose coupling between components
  - Easy mocking for unit tests
  - Centralized service configuration
  - Lifecycle management

### 2. Repository Pattern
- **Location**: `apps/*/repositories/`
- **Implementation**: 
  - Abstract repository interfaces defining data access contracts
  - Concrete Django ORM implementations
  - Methods return QuerySets or model instances
- **Benefits**:
  - Separation of data access concerns from business logic
  - Ability to swap persistence mechanisms
  - Testability through mock repositories
  - Consistent data access API

### 3. Service Layer Pattern
- **Location**: `apps/*/services/`
- **Implementation**:
  - Business logic encapsulated in service classes
  - Dependencies injected via constructor
  - Transaction script pattern for use cases
  - Validation and business rule enforcement
- **Benefits**:
  - Clear separation of concerns
  - Reusable business logic
  - Easier testing and maintenance
  - Centralized transaction management

### 4. Django REST Framework ViewSet Pattern
- **Location**: `apps/gms/api/`
- **Implementation**:
  - ViewSets handling standard CRUD operations
  - Custom actions via `@action` decorator
  - Serializers for data validation and transformation
  - Permission classes for access control
- **Benefits**:
  - RESTful API design
  - Reduced boilerplate code
  - Consistent endpoint structure
  - Built-in serialization and validation

## Data Model Specifications

### Base Model (`apps/core/models.py`)
```python
class BaseModel(models.Model):
    _id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
```

### Guest Model (`apps/gms/models.py`)
- **Fields**:
  - `name`: CharField(max_length=255)
  - `email`: EmailField(unique=True)
  - `phone_number`: CharField(max_length=255, unique=True)
  - `identification_number`: CharField(max_length=255, unique=True, blank=True, null=True)
  - `identification_type`: CharField(max_length=255, choices=[('AADHAAR', 'Aadhaar'), ('PASSPORT', 'Passport'), ('DRIVING_LICENSE', 'Driving License')], blank=True, null=True)
- **Constraints**: 
  - Unique email and phone number
  - Optional identification with type/number pairing

### Invitation Model (`apps/gms/models.py`)
- **Fields**:
  - `guest`: ForeignKey to Guest (CASCADE)
  - `invited_by`: ForeignKey to User (CASCADE)
  - `purpose`: TextField()
  - `expected_arrival`: DateTimeField()
  - `expected_departure`: DateTimeField(blank=True, null=True)
  - `status`: CharField(max_length=255, choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('CANCELLED', 'Cancelled')], default='PENDING')
  - `invitation_code`: CharField(max_length=255, unique=True, blank=True, null=True)
  - `rejection_reason`: TextField(blank=True, null=True)
  - `created_at`: DateTimeField(auto_now_add=True)
- **Relationships**:
  - Guest: One-to-Many (Guest can have multiple invitations)
  - User: One-to-Many (User can send multiple invitations)
- **Constraints**:
  - Unique invitation_code when set
  - Status controls business logic flow

### Visit Model (`apps/gms/models.py`)
- **Fields**:
  - `invitation`: ForeignKey to Invitation (CASCADE, blank=True, null=True)
  - `check_in_time`: DateTimeField(auto_now_add=True)
  - `check_out_time`: DateTimeField(null=True, blank=True)
  - `status`: CharField(max_length=255, choices=[('CHECKED_IN', 'Checked In'), ('CHECKED_OUT', 'Checked Out')], default='CHECKED_IN')
  - `created_at`: DateTimeField(auto_now_add=True)
- **Relationships**:
  - Invitation: One-to-One (Visit belongs to at most one invitation)
- **Constraints**:
  - Status determines check-in/check-out state

## Service Layer Specifications

### Guest Service (`apps/gms/services/guest.py`)
**Responsibilities**: Guest-related business operations
**Methods**:
- `create_guest(data)`: Create new guest with validation
- `get_guest_by_id(_id)`: Retrieve guest by UUID
- `get_guests(filters=None)`: List guests with optional filtering
- `update_guest(_id, data)`: Update guest with validation
- `delete_guest(_id)`: Delete guest (with business rule checks)
- **Dependencies**: GuestRepository

### Invitation Service (`apps/gms/services/invitation.py`)
**Responsibilities**: Invitation-related business operations including authorization logic
**Methods**:
- `create_invitation(data)`: Create invitation with duplicate prevention
- `approve_invitation(invitation_id, user)`: Approve invitation (staff-only, not creator)
- `reject_invitation(invitation_id, reason, user)`: Reject invitation (staff-only, not creator, requires reason)
- `cancel_invitation(invitation_id)`: Cancel invitation (creator-only for PENDING/APPROVED)
- `update_invitation(invitation_id, data)`: Update invitation (only when PENDING)
- `list_invitations(filters=None)`: List invitations with filtering
- `get_invitations_by_guest(guest_id)`: Get invitations for specific guest
- `delete_invitation(_id)`: Delete invitation
- **Private Methods**:
  - `_check_approval_permission(user, invitation)`: Enforces authorization rules
  - `check_invitation_for_guest(guest_id, expected_arrival)`: Prevents date conflicts
- **Dependencies**: InvitationRepository

### Visit Service (`apps/gms/services/visit.py`)
**Responsibilities**: Visit-related business operations
**Methods**:
- `create_visit(data)`: Create visit (check-in) with invitation validation
- `get_visit_by_id(_id)`: Retrieve visit by UUID
- `list_visits(filters=None)`: List visits with optional filtering
- `update_visit(_id, data)`: Update visit
- `delete_visit(_id)`: Delete visit
- `check_out(_id)`: Check-out visit (sets check_out_time and status)
- **Dependencies**: VisitRepository

## Repository Layer Specifications

### Guest Repository (`apps/gms/repositories/guest_repository.py`)
**Interface Methods**:
- `create_guest(data)`: Create guest instance
- `get_guest_by_id(_id)`: Retrieve guest by UUID
- `get_guests(filters=None)`: Query guests with filters
- `update_guest(_id, data)`: Update guest instance
- `delete_guest(_id)`: Delete guest instance
- **Returns**: Model instances or QuerySets

### Invitation Repository (`apps/gms/repositories/invitation_repository.py`)
**Interface Methods**:
- `create_invitation(data)`: Create invitation instance
- `get_invitation_by_id(_id)`: Retrieve invitation by UUID
- `list_invitations(filters=None)`: Query invitations with filters
- `get_invitations_by_guest(guest_id)`: Get invitations for specific guest
- `update_invitation(_id, data)`: Update invitation instance
- `delete_invitation(_id)`: Delete invitation instance
- `set_status(_id, status)`: Update invitation status
- `reject_invitation(_id, reason)`: Set rejection reason and status
- `get_guest_invitation_by_date(guest_id, expected_arrival)`: Check for date conflicts
- **Returns**: Model instances or QuerySets

### Visit Repository (`apps/gms/repositories/visit_repository.py`)
**Interface Methods**:
- `create_visit(data)`: Create visit instance
- `get_visit_by_id(_id)`: Retrieve visit by UUID
- `list_visits(filters=None)`: Query visits with filters
- `update_visit(_id, data)`: Update visit instance
- `delete_visit(_id)`: Delete visit instance
- **Returns**: Model instances or QuerySets

## API Layer Specifications

### ViewSets (`apps/gms/api/views.py`)
**Common Features**:
- All ViewSets inherit from `viewsets.ViewSet`
- JWT authentication via `IsAuthenticated` permission classes
- Manual service retrieval via `get_service()` in `__init__`
- Standard CRUD operations mapped to HTTP methods
- Custom actions via `@action` decorator
- Consistent error handling with try/catch blocks
- Proper HTTP status code responses

### Serializers (`apps/gms/api/serializers.py`)
**GuestSerializer**:
- Fields: `_id`, `name`, `email`, `phone_number`, `identification_number`, `identification_type`
- Read-only: `_id`

**InvitationSerializer**:
- Fields: `__all__` (all model fields)
- Read-only: `created_at`, `status`, `invitation_code`

**VisitSerializer**:
- Fields: `__all__` (all model fields)
- Read-only: `created_at`, `check_in_time`, `check_out_time`, `status`

## Authentication and Authorization

### JWT Authentication
- **Implementation**: `rest_framework_simplejwt`
- **Configuration**: `guestmanagement/guestmanagement/settings/base.py`
- **Endpoints**:
  - `POST /api/token/`: Obtain access/refresh tokens
  - `POST /api/token/refresh/`: Refresh access token
- **Usage**: `Authorization: Bearer <access-token>` header required for all API endpoints

### Authorization Rules (Invitation Service)
1. **Creator Restriction**: User who created invitation cannot approve or reject it
2. **Staff Requirement**: Only users with `is_staff=True` can approve/reject invitations
3. **Status Requirements**: 
   - Only PENDING invitations can be approved/rejected/updated
   - Only PENDING/APPROVED invitations can be cancelled
4. **Rejection Requirement**: Rejection must include a reason
5. **Creator Privilege**: Invitation creator can cancel their own invitations

## Security Considerations

### Data Protection
- UUID primary keys prevent ID enumeration attacks
- Unique constraints on email, phone_number, and identification_number prevent duplicates
- Input validation through Django REST Framework serializers

### Authentication Security
- JWT tokens signed with SECRET_KEY
- Access tokens have short expiration (typically 5 minutes)
- Refresh tokens allow obtaining new access tokens without re-authentication
- Token blacklisting not implemented (would require additional infrastructure)

### Authorization Security
- Server-side validation of all authorization rules
- No client-side trust for permissions
- Clear error messages without leaking sensitive information

### Input Validation
- Field-level validation in serializers (required fields, formats, uniqueness)
- Business rule validation in service layer (date conflicts, status transitions)
- SQL injection protection through Django ORM
- XSS protection through Django's automatic escaping

## Performance Considerations

### Database Optimization
- Proper use of ForeignKey relationships with indexes
- Query optimization in repository methods (select_related/prefetch_related where appropriate)
- Pagination for list endpoints to prevent large result sets
- Filtering capabilities to reduce unnecessary data transfer

### Caching Opportunities
- Frequently accessed reference data (identification types, status choices)
- User permissions and roles
- API response caching for read-heavy endpoints (with proper invalidation)

### Scalability
- Stateless API design suitable for horizontal scaling
- Separation of concerns allows independent scaling of layers
- Database connection pooling through Django's database backend

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Keep functions focused on single responsibility
- Write clear docstrings for public methods
- Use type hints where beneficial

### Testing Guidelines
- Unit tests for service layer business logic
- Integration tests for API endpoints
- Test both positive and negative cases
- Mock external dependencies (repositories, services)
- Test authorization rules with different user types
- Aim for high test coverage on critical business logic

### Adding New Features
1. **Update Models**: Modify `apps/*/models.py` as needed
2. **Create Migration**: `python manage.py makemigrations`
3. **Apply Migration**: `python manage.py migrate`
4. **Update Repository**: Modify interface and implementation
5. **Implement Service Logic**: Add methods to service class
6. **Update Serializers**: Modify `apps/*/api/serializers.py` if needed
7. **Update Views**: Add/ViewSet methods in `apps/*/api/views.py`
8. **Write Tests**: Create/update test cases
9. **Document Changes**: Update API documentation if public interface changed

### Error Handling
- Use try/catch blocks at appropriate levels
- Return meaningful error messages to clients
- Log unexpected errors for debugging
- Use appropriate HTTP status codes:
  - 2xx: Success
  - 4xx: Client errors (validation, authentication, authorization)
  - 5xx: Server errors (unexpected exceptions)

## Deployment Considerations

### Environment Variables
- `SECRET_KEY`: Django secret key (must be kept secret)
- `DEBUG`: Boolean for development vs production
- `ALLOWED_HOSTS`: List of allowed domain/IP addresses
- Database configuration (if not using default SQLite)

### Production Settings
- Set `DEBUG = False`
- Configure proper ALLOWED_HOSTS
- Use strong SECRET_KEY
- Configure secure database (PostgreSQL recommended)
- Set up proper logging
- Consider using gunicorn/uWSGI with Nginx
- Implement HTTPS termination at reverse proxy

### Monitoring and Logging
- Configure Django logging appropriately
- Monitor API response times and error rates
- Track authentication failures and authorization denials
- Log business rule violations for audit purposes

## Extensibility Points

### Adding New Model Types
1. Create model inheriting from BaseModel
2. Create repository interface and implementation
3. Create service class with business logic
4. Create serializer for API
5. Create ViewSet for API endpoints
6. Update dependencies.py to register new service
7. Write tests

### Adding New API Endpoints
1. Determine appropriate ViewSet or create new one
2. Add method with proper HTTP verb mapping
3. Implement business logic delegation to service
4. Add serializer if needed for request/response
5. Apply appropriate permission classes
6. Test thoroughly

### Modifying Business Rules
1. Identify which layer contains the rule (service vs repository)
2. Update the relevant method
3. Update corresponding tests
4. Verify API behavior through integration tests
5. Update documentation if user-facing behavior changed

---

*Document version: 1.0*
*Last updated: September 2026*