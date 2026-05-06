## ADDED Requirements

### Requirement: Article CRUD operations
The system SHALL provide create, read, update, and delete operations for articles.

#### Scenario: Create draft article
- **WHEN** an authenticated admin sends a POST request to `/api/articles` with title, slug, and content
- **THEN** the system creates an article with status `draft` and returns the created article

#### Scenario: Read article by slug
- **WHEN** a visitor sends a GET request to `/api/articles/{slug}`
- **THEN** the system returns the published article with rendered HTML content

#### Scenario: Update article
- **WHEN** an authenticated admin sends a PUT request to `/api/articles/{id}` with updated fields
- **THEN** the system updates the article and returns the updated article

#### Scenario: Delete article
- **WHEN** an authenticated admin sends a DELETE request to `/api/articles/{id}`
- **THEN** the system deletes the article and returns a 204 response

### Requirement: Article content stored as TipTap JSON
The system SHALL store article content as TipTap JSON document and render HTML on demand.

#### Scenario: Store TipTap JSON
- **WHEN** an admin creates or updates an article with content
- **THEN** the system stores the raw TipTap JSON document in the database

#### Scenario: Render HTML for public view
- **WHEN** a visitor requests a published article
- **THEN** the system renders the TipTap JSON to sanitized HTML for the response

### Requirement: Unique human-readable slugs
The system SHALL generate unique URL slugs from article titles with collision handling.

#### Scenario: Generate slug from title
- **WHEN** an article is created with title "Procedural Generation Mechanics"
- **THEN** the system generates the slug `procedural-generation-mechanics`

#### Scenario: Handle duplicate slug
- **WHEN** an article is created with a title that produces an existing slug
- **THEN** the system appends `-2`, `-3`, etc. until the slug is unique

### Requirement: Draft and published lifecycle
The system SHALL support a one-way `draft` to `published` status transition.

#### Scenario: Publish article
- **WHEN** an authenticated admin updates an article from `draft` to `published`
- **THEN** the system sets `published_at` to the current timestamp and the article becomes publicly visible

#### Scenario: Prevent unpublish
- **WHEN** an authenticated admin attempts to change a `published` article back to `draft`
- **THEN** the system rejects the request with a 400 error

### Requirement: Auto-generated meta description
The system SHALL auto-generate a meta description from article content with optional override.

#### Scenario: Auto-generate description
- **WHEN** an article is created without an explicit description
- **THEN** the system generates a description from the first 160 characters of plain text content

#### Scenario: Override description
- **WHEN** an article is created with an explicit description field
- **THEN** the system stores the provided description instead of auto-generating one

### Requirement: Public article list
The system SHALL expose a public endpoint listing published articles in reverse chronological order.

#### Scenario: List published articles
- **WHEN** a visitor sends a GET request to `/api/articles`
- **THEN** the system returns only articles with status `published`, ordered by `published_at` descending
