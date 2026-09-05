# Guest Management System - API Specification

## Overview

This document provides a detailed technical specification of the Guest Management System's RESTful API. The API is built using Django REST Framework and secured with JWT authentication. All endpoints require valid authentication tokens unless otherwise noted.

## Base URL

```
http://{host}:{port}/
```

All API endpoints are prefixed with `/gms/api/` as defined in the URL configuration.

## Authentication

### JWT Token Acquisition

**Endpoint**: `POST /api/token/`
**Description**: Obtain JWT access and refresh tokens
**Request Body**:
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```
**Success Response**:
- Code: 200 OK
- Content:
```json
{
  "access": "string (JWT access token)",
  "refresh": "string (JWT refresh token)"
}
```
**Error Responses**:
- 400 Bad Request: Invalid credentials or missing fields
- 401 Unauthorized: Invalid email/password combination

### Token Refresh

**Endpoint**: `POST /api/token/refresh/`
**Description**: Obtain a new access token using a valid refresh token
**Request Body**:
```json
{
  "refresh": "string (required)"
}
```
**Success Response**:
- Code: 200 OK
- Content:
```json
{
  "access": "string (new JWT access token)"
}
```
**Error Responses**:
- 400 Bad Request: Invalid or expired refresh token
- 401 Unauthorized: Invalid token

### Authenticated Requests

All API endpoints (except token endpoints) require the following header:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### Guests

#### List Guests
- **Endpoint**: `GET /gms/api/guests`
- **Description**: Retrieve a paginated list of guests with optional filtering
- **Query Parameters**:
  - `name`: Filter by guest name (partial match)
  - `email`: Filter by email address (exact match)
  - `phone_number`: Filter by phone number (exact match)
  - `identification_type`: Filter by ID type
  - `identification_number`: Filter by ID number (partial match)
- **Success Response**:
  - Code: 200 OK
  - Content: Array of guest objects
- **Error Responses**:
  - 401 Unauthorized: Missing or invalid authentication

#### Create Guest
- **Endpoint**: `POST /gms/api/guests`
- **Description**: Create a new guest record
- **Request Body**:
```json
{
  "name": "string (required, max 255 chars)",
  "email": "string (required, valid email format)",
  "phone_number": "string (required, max 255 chars)",
  "identification_number": "string (optional, max 255 chars)",
  "identification_type": "string (optional, one of: AADHAAR, PASSPORT, DRIVING_LICENSE)"
}
```
- **Success Response**:
  - Code: 201 Created
  - Content: Created guest object including `_id` (UUID)
- **Error Responses**:
  - 400 Bad Request: Validation errors (duplicate email/phone, missing required fields)
  - 401 Unauthorized: Missing or invalid authentication

#### Retrieve Guest
- **Endpoint**: `GET /gms/api/guests/{_id}`
- **Description**: Get details of a specific guest
- **URL Parameters**: `_id` (UUID of the guest)
- **Success Response**:
  - Code: 200 OK
  - Content: Guest object
- **Error Responses**:
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Guest with specified ID not found

#### Update Guest
- **Endpoint**: `PUT /gms/api/guests/{_id}`
- **Description**: Update an existing guest record
- **URL Parameters**: `_id` (UUID of the guest)
- **Request Body**: Same as create guest (all fields optional except those requiring uniqueness)
- **Success Response**:
  - Code: 200 OK
  - Content: Updated guest object
- **Error Responses**:
  - 400 Bad Request: Validation errors
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Guest with specified ID not found

#### Delete Guest
- **Endpoint**: `DELETE /gms/api/guests/{_id}`
- **Description**: Delete a guest record
- **URL Parameters**: `_id` (UUID of the guest)
- **Success Response**:
  - Code: 204 No Content
- **Error Responses**:
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Guest with specified ID not found
  - 400 Bad Request: Cannot delete guest with active invitations (business rule)

### Invitations

#### List Invitations
- **Endpoint**: `GET /gms/api/invitations`
- **Description**: Retrieve a paginated list of invitations with optional filtering
- **Query Parameters**:
  - `guest`: Filter by guest ID (UUID)
  - `invited_by`: Filter by inviting user ID (UUID)
  - `status`: Filter by invitation status (PENDING, APPROVED, REJECTED, CANCELLED)
  - `purpose`: Filter by purpose (partial match)
  - `expected_arrival_after`: Filter invitations arriving after this datetime (ISO format)
  - `expected_arrival_before`: Filter invitations arriving before this datetime (ISO format)
- **Success Response**:
  - Code: 200 OK
  - Content: Array of invitation objects
- **Error Responses**:
  - 401 Unauthorized: Missing or invalid authentication

#### Create Invitation
- **Endpoint**: `POST /gms/api/invitations`
- **Description**: Create a new invitation
- **Request Body**:
```json
{
  "guest": "string (UUID, required, must exist)",
  "invited_by": "string (UUID, required, must exist)",
  "purpose": "string (required, detailed description)",
  "expected_arrival": "string (ISO datetime, required)",
  "expected_departure": "string (ISO datetime, optional)"
}
```
- **Success Response**:
  - Code: 201 Created
  - Content: Created invitation object including `_id` (UUID) and auto-generated `invitation_code`
- **Error Responses**:
  - 400 Bad Request: Validation errors (missing fields, invalid UUIDs, date conflicts, duplicate active invitation for same guest)
  - 401 Unauthorized: Missing or invalid authentication
  - 403 Forbidden: Non-staff user attempting to create invitation for another user (business rule varies by implementation)

#### Retrieve Invitation
- **Endpoint**: `GET /gms/api/invitations/{_id}`
- **Description**: Get details of a specific invitation
- **URL Parameters**: `_id` (UUID of the invitation)
- **Success Response**:
  - Code: 200 OK
  - Content: Invitation object
- **Error Responses**:
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Invitation with specified ID not found

#### Update Invitation
- **Endpoint**: `PUT /gms/api/invitations/{_id}`
- **Description**: Update an existing invitation (only when in PENDING status)
- **URL Parameters**: `_id` (UUID of the invitation)
- **Request Body**: Same as create invitation (status field cannot be updated via this endpoint)
- **Success Response**:
  - Code: 200 OK
  - Content: Updated invitation object
- **Error Responses**:
  - 400 Bad Request: Validation errors, invitation not in PENDING status, attempting to update status directly
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Invitation with specified ID not found

#### Delete Invitation
- **Endpoint**: `DELETE /gms/api/invitations/{_id}`
- **Description**: Delete an invitation record
- **URL Parameters**: `_id` (UUID of the invitation)
- **Success Response**:
  - Code: 204 No Content
- **Error Responses**:
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Invitation with specified ID not found
  - 400 Bad Request: Cannot delete invitation with associated visits (business rule)

#### Approve Invitation
- **Endpoint**: `POST /gms/api/invitations/{_id}/approve`
- **Description**: Approve a pending invitation (staff only, not the creator)
- **URL Parameters**: `_id` (UUID of the invitation)
- **Request Body**: None
- **Success Response**:
  - Code: 200 OK
  - Content: Updated invitation object with status set to APPROVED
- **Error Responses**:
  - 400 Bad Request: Invitation not in PENDING status, user is the creator, user is not staff
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Invitation with specified ID not found

#### Reject Invitation
- **Endpoint**: `POST /gms/api/invitations/{_id}/reject`
- **Description**: Reject a pending invitation (staff only, not the creator)
- **URL Parameters**: `_id` (UUID of the invitation)
- **Request Body**:
```json
{
  "reason": "string (required, explanation for rejection)"
}
```
- **Success Response**:
  - Code: 200 OK
  - Content: Updated invitation object with status set to REJECTED and rejection_reason populated
- **Error Responses**:
  - 400 Bad Request: Invitation not in PENDING status, user is the creator, user is not staff, missing or empty reason
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Invitation with specified ID not found

#### Cancel Invitation
- **Endpoint**: `POST /gms/api/invitations/{_id}/cancel`
- **Description**: Cancel an invitation (creator can cancel PENDING/APPROVED invitations)
- **URL Parameters**: `_id` (UUID of the invitation)
- **Request Body**: None
- **Success Response**:
  - Code: 200 OK
  - Content: Updated invitation object with status set to CANCELLED
- **Error Responses**:
  - 400 Bad Request: Invitation not in PENDING or APPROVED status
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Invitation with specified ID not found

### Visits

#### List Visits
- **Endpoint**: `GET /gms/api/visits`
- **Description**: Retrieve a paginated list of visits with optional filtering
- **Query Parameters**:
  - `invitation`: Filter by invitation ID (UUID)
  - `status`: Filter by visit status (CHECKED_IN, CHECKED_OUT)
  - `check_in_time_after`: Filter visits checking in after this datetime (ISO format)
  - `check_in_time_before`: Filter visits checking in before this datetime (ISO format)
  - `check_out_time_after`: Filter visits checking out after this datetime (ISO format)
  - `check_out_time_before`: Filter visits checking out before this datetime (ISO format)
- **Success Response**:
  - Code: 200 OK
  - Content: Array of visit objects
- **Error Responses**:
  - 401 Unauthorized: Missing or invalid authentication

#### Create Visit
- **Endpoint**: `POST /gms/api/visits`
- **Description**: Create a new visit (check-in a guest)
- **Request Body**:
```json
{
  "invitation": "string (UUID, required, must exist and be APPROVED)"
}
```
- **Success Response**:
  - Code: 201 Created
  - Content: Created visit object including `_id` (UUID), auto-generated `check_in_time`, and default status CHECKED_IN
- **Error Responses**:
  - 400 Bad Request: Validation errors, invitation not APPROVED, invitation already has an active visit
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Invitation with specified ID not found

#### Retrieve Visit
- **Endpoint**: `GET /gms/api/visits/{_id}`
- **Description**: Get details of a specific visit
- **URL Parameters**: `_id` (UUID of the visit)
- **Success Response**:
  - Code: 200 OK
  - Content: Visit object
- **Error Responses**:
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Visit with specified ID not found

#### Update Visit
- **Endpoint**: `PUT /gms/api/visits/{_id}`
- **Description**: Update an existing visit
- **URL Parameters**: `_id` (UUID of the visit)
- **Request Body**: Same as create visit (invitation field optional)
- **Success Response**:
  - Code: 200 OK
  - Content: Updated visit object
- **Error Responses**:
  - 400 Bad Request: Validation errors
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Visit with specified ID not found

#### Delete Visit
- **Endpoint**: `DELETE /gms/api/visits/{_id}`
- **Description**: Delete a visit record
- **URL Parameters**: `_id` (UUID of the visit)
- **Success Response**:
  - Code: 204 No Content
- **Error Responses**:
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Visit with specified ID not found

#### Check Out Visit
- **Endpoint**: `POST /gms/api/visits/{_id}/check_out`
- **Description**: Check out a guest (end their visit)
- **URL Parameters**: `_id` (UUID of the visit)
- **Request Body**: None
- **Success Response**:
  - Code: 200 OK
  - Content: Updated visit object with `check_out_time` populated and status set to CHECKED_OUT
- **Error Responses**:
  - 400 Bad Request: Visit not in CHECKED_IN status
  - 401 Unauthorized: Missing or invalid authentication
  - 404 Not Found: Visit with specified ID not found

## Data Models

### Guest Object
```json
{
  "_id": "string (UUID)",
  "name": "string",
  "email": "string",
  "phone_number": "string",
  "identification_number": "string (nullable)",
  "identification_type": "string (nullable, one of: AADHAAR, PASSPORT, DRIVING_LICENSE)"
}
```

### Invitation Object
```json
{
  "_id": "string (UUID)",
  "guest": "string (UUID reference to Guest)",
  "invited_by": "string (UUID reference to User)",
  "purpose": "string",
  "expected_arrival": "string (ISO datetime)",
  "expected_departure": "string (ISO datetime, nullable)",
  "status": "string (one of: PENDING, APPROVED, REJECTED, CANCELLED)",
  "invitation_code": "string (unique, auto-generated)",
  "rejection_reason": "string (nullable)",
  "created_at": "string (ISO datetime, auto-generated)"
}
```

### Visit Object
```json
{
  "_id": "string (UUID)",
  "invitation": "string (UUID reference to Invitation)",
  "check_in_time": "string (ISO datetime, auto-generated)",
  "check_out_time": "string (ISO datetime, nullable)",
  "status": "string (one of: CHECKED_IN, CHECKED_OUT)",
  "created_at": "string (ISO datetime, auto-generated)"
}
```

## Error Response Format

All error responses follow this format:
```json
{
  "error": "string (human-readable error message)"
}
```

Validation errors may include field-specific messages:
```json
{
  "email": ["string (error message)"],
  "phone_number": ["string (error message)"]
}
```

## HTTP Status Codes

- **200 OK**: Successful GET, PUT, or POST that returns data
- **201 Created**: Successful POST that creates a resource
- **204 No Content**: Successful DELETE or POST that doesn't return data
- **400 Bad Request**: Client error (validation, missing parameters, business rule violations)
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Authenticated user lacks permission for the action
- **404 Not Found**: Requested resource does not exist
- **500 Internal Server Error**: Unexpected server error

## Rate Limiting

The API implements rate limiting to prevent abuse:
- Anonymous requests: 100/hour
- Authenticated requests: 1000/hour
- Exceeding limits returns 429 Too Many Requests

## Versioning

This documentation applies to API version 1.0. Future versions will maintain backward compatibility where possible, with breaking changes documented in release notes.

---

*Document version: 1.0*
*Last updated: September 2026*