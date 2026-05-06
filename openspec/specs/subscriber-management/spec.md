## ADDED Requirements

### Requirement: Subscribe to newsletter
The system SHALL allow visitors to subscribe to the newsletter with their email address.

#### Scenario: Successful subscription request
- **WHEN** a visitor submits their email via the subscription form
- **THEN** the system creates a subscriber record with status `pending` and sends a confirmation email

#### Scenario: Duplicate email subscription
- **WHEN** a visitor submits an email that already exists with status `active` or `pending`
- **THEN** the system returns a success response without creating a duplicate or sending another confirmation

### Requirement: Double opt-in confirmation
The system SHALL require subscribers to confirm their email via a unique confirmation link.

#### Scenario: Confirm subscription
- **WHEN** a subscriber clicks the confirmation link in their email
- **THEN** the system updates their status to `active` and they begin receiving newsletters

#### Scenario: Invalid confirmation token
- **WHEN** a subscriber clicks a confirmation link with an invalid or expired token
- **THEN** the system returns an error indicating the link is invalid

### Requirement: One-click unsubscribe
The system SHALL allow subscribers to unsubscribe via a link in every newsletter email.

#### Scenario: Unsubscribe via email link
- **WHEN** a subscriber clicks the unsubscribe link in a newsletter email
- **THEN** the system updates their status to `unsubscribed` and they no longer receive emails

#### Scenario: Unsubscribe already unsubscribed user
- **WHEN** a subscriber with status `unsubscribed` clicks the unsubscribe link
- **THEN** the system returns a message indicating they are already unsubscribed

### Requirement: Subscriber status states
The system SHALL maintain subscribers in one of three states: `pending`, `active`, or `unsubscribed`.

#### Scenario: Pending subscriber does not receive newsletters
- **WHEN** a newsletter is sent
- **THEN** the system excludes subscribers with status `pending` or `unsubscribed` from the recipient list

#### Scenario: Active subscriber receives newsletters
- **WHEN** a newsletter is sent and a subscriber has status `active`
- **THEN** the system includes the subscriber in the recipient list
