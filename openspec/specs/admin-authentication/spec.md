## ADDED Requirements

### Requirement: Bearer token authentication for admin routes
The system SHALL protect all admin API routes with a bearer token authentication mechanism.

#### Scenario: Authenticated request
- **WHEN** a request includes a valid `Authorization: Bearer <token>` header matching the configured admin token
- **THEN** the system processes the request normally

#### Scenario: Missing authentication
- **WHEN** a request to an admin endpoint does not include an authorization header
- **THEN** the system returns a 401 Unauthorized response

#### Scenario: Invalid token
- **WHEN** a request includes an authorization header with an invalid token
- **THEN** the system returns a 403 Forbidden response

### Requirement: Seeded default admin user
The system SHALL create a default admin user on first startup if no users exist.

#### Scenario: Seed admin on empty database
- **WHEN** the application starts and the `User` table contains no records
- **THEN** the system creates a default admin user with email from `ADMIN_EMAIL` environment variable

#### Scenario: Skip seed when users exist
- **WHEN** the application starts and the `User` table already contains records
- **THEN** the system does not create or modify any user records

### Requirement: User schema from day one
The system SHALL define a `User` table with fields supporting future authentication expansion.

#### Scenario: User model structure
- **WHEN** the database schema is created
- **THEN** the `users` table exists with `id` (UUID), `email`, `hashed_password`, `is_admin`, `created_at`, and `updated_at` columns
