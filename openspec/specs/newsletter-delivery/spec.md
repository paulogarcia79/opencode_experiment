## ADDED Requirements

### Requirement: Newsletter auto-send on publish
The system SHALL automatically send a newsletter to all active subscribers when an article is first published.

#### Scenario: Send newsletter on first publish
- **WHEN** an article transitions from `draft` to `published` and the `send_newsletter` flag is true
- **THEN** the system sends the article HTML as an email to all subscribers with status `active`

#### Scenario: Skip newsletter for opted-out article
- **WHEN** an article transitions from `draft` to `published` and the `send_newsletter` flag is false
- **THEN** the system publishes the article without sending a newsletter

#### Scenario: Do not re-send on subsequent updates
- **WHEN** a published article is updated
- **THEN** the system does not send another newsletter

### Requirement: Newsletter email content
The system SHALL render article content as email-safe HTML for newsletter delivery.

#### Scenario: Render full article HTML for email
- **WHEN** a newsletter is triggered for an article
- **THEN** the system converts the TipTap JSON content to inline-styled HTML suitable for email clients

#### Scenario: Include unsubscribe link
- **WHEN** a newsletter email is sent
- **THEN** the email body includes a one-click unsubscribe link unique to each recipient

### Requirement: Email delivery via Resend
The system SHALL use the Resend API for all transactional and newsletter emails.

#### Scenario: Send confirmation email
- **WHEN** a new subscriber is created with status `pending`
- **THEN** the system sends a confirmation email via Resend with a unique confirmation link

#### Scenario: Send newsletter batch
- **WHEN** a newsletter is triggered
- **THEN** the system sends individual emails via Resend to each active subscriber

### Requirement: Track newsletter sends
The system SHALL record when a newsletter was sent to each subscriber.

#### Scenario: Log sent newsletter
- **WHEN** a newsletter email is successfully sent to a subscriber
- **THEN** the system creates a `newsletter_send` record with article_id, subscriber_id, and sent_at timestamp

#### Scenario: Prevent duplicate sends
- **WHEN** a newsletter has already been sent to a subscriber for a given article
- **THEN** the system does not send another email for that article-subscriber pair
