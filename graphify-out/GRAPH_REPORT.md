# Graph Report - .  (2026-05-06)

## Corpus Check
- Corpus is ~11,292 words - fits in a single context window. You may not need a graph.

## Summary
- 292 nodes · 324 edges · 58 communities (34 shown, 24 thin omitted)
- Extraction: 64% EXTRACTED · 36% INFERRED · 0% AMBIGUOUS · INFERRED: 116 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Article Management Domain|Article Management Domain]]
- [[_COMMUNITY_Article API Implementation|Article API Implementation]]
- [[_COMMUNITY_Database Models & Setup|Database Models & Setup]]
- [[_COMMUNITY_Subscriber API Routes|Subscriber API Routes]]
- [[_COMMUNITY_Newsletter Delivery Specs|Newsletter Delivery Specs]]
- [[_COMMUNITY_Core App & Authentication|Core App & Authentication]]
- [[_COMMUNITY_Frontend Public Views|Frontend Public Views]]
- [[_COMMUNITY_Frontend Admin Composables|Frontend Admin Composables]]
- [[_COMMUNITY_Frontend Auth State|Frontend Auth State]]
- [[_COMMUNITY_Pydantic Schemas|Pydantic Schemas]]
- [[_COMMUNITY_Content Processing Service|Content Processing Service]]
- [[_COMMUNITY_TipTap HTML Renderer|TipTap HTML Renderer]]
- [[_COMMUNITY_Form Submit Handlers|Form Submit Handlers]]
- [[_COMMUNITY_Application Configuration|Application Configuration]]
- [[_COMMUNITY_Alembic Migrations|Alembic Migrations]]
- [[_COMMUNITY_Docker & Project Meta|Docker & Project Meta]]
- [[_COMMUNITY_TipTap Renderer View|TipTap Renderer View]]
- [[_COMMUNITY_Admin Auth Dependencies|Admin Auth Dependencies]]
- [[_COMMUNITY_TipTap Editor Components|TipTap Editor Components]]
- [[_COMMUNITY_Agent Conventions & TDD|Agent Conventions & TDD]]
- [[_COMMUNITY_Design System Rationale|Design System Rationale]]
- [[_COMMUNITY_Subscriber Confirmation Views|Subscriber Confirmation Views]]
- [[_COMMUNITY_API Composables Core|API Composables Core]]
- [[_COMMUNITY_PostCSS Settings|PostCSS Settings]]
- [[_COMMUNITY_Tailwind Settings|Tailwind Settings]]
- [[_COMMUNITY_Vite Settings|Vite Settings]]
- [[_COMMUNITY_App Module Root|App Module Root]]
- [[_COMMUNITY_Router Index|Router Index]]
- [[_COMMUNITY_Admin Login View|Admin Login View]]
- [[_COMMUNITY_Admin Layout Component|Admin Layout Component]]
- [[_COMMUNITY_TipTap Link Handler|TipTap Link Handler]]
- [[_COMMUNITY_useTipTap Composable|useTipTap Composable]]
- [[_COMMUNITY_Main Module|Main Module]]
- [[_COMMUNITY_Migration Offline Runner|Migration Offline Runner]]
- [[_COMMUNITY_Migration Online Runner|Migration Online Runner]]
- [[_COMMUNITY_Migration Downgrade|Migration Downgrade]]
- [[_COMMUNITY_Invalid Token Test|Invalid Token Test]]
- [[_COMMUNITY_Unsubscribe Invalid Test|Unsubscribe Invalid Test]]
- [[_COMMUNITY_WYSIWYG Editor Rationale|WYSIWYG Editor Rationale]]
- [[_COMMUNITY_Newsletter Capture Rationale|Newsletter Capture Rationale]]
- [[_COMMUNITY_HTML Entry Point|HTML Entry Point]]
- [[_COMMUNITY_External URLs Rationale|External URLs Rationale]]

## God Nodes (most connected - your core abstractions)
1. `create_article()` - 13 edges
2. `create_article service` - 12 edges
3. `create_subscriber()` - 8 edges
4. `send_newsletter_for_article()` - 7 edges
5. `create article endpoint` - 7 edges
6. `update article endpoint` - 7 edges
7. `Blog + Newsletter Platform Proposal` - 7 edges
8. `Article Management Spec` - 7 edges
9. `getAuthHeaders()` - 6 edges
10. `Article model` - 6 edges

## Surprising Connections (you probably didn't know these)
- `get_article_by_slug service` --implements--> `Article Management Spec`  [INFERRED]
  app/services/article_service.py → openspec/specs/article-management/spec.md
- `list_published_articles service` --implements--> `Article Management Spec`  [INFERRED]
  app/services/article_service.py → openspec/specs/article-management/spec.md
- `unsubscribe_subscriber service` --implements--> `Subscriber Management Spec`  [INFERRED]
  app/services/subscriber_service.py → openspec/specs/subscriber-management/spec.md
- `send_confirmation_email` --implements--> `Newsletter Delivery Spec`  [INFERRED]
  app/services/email_service.py → openspec/specs/newsletter-delivery/spec.md
- `send_newsletter_email` --implements--> `Newsletter Delivery Spec`  [INFERRED]
  app/services/email_service.py → openspec/specs/newsletter-delivery/spec.md

## Hyperedges (group relationships)
- **Authentication System** — adminloginview, admin_useadminstore, index_beforeeach, adminlayout, useadminapi [INFERRED 0.75]
- **TipTap Content Pipeline** — tiptapeditor, adminarticleeditview, tiptaprenderer, usetiptap_rendertiptapjson [INFERRED 0.75]
- **Triple-Coded State UI Pattern** — newsletterform, adminarticleeditview, newsletterform_handlesubmit, adminarticleeditview_handlesubmit [INFERRED 0.85]
- **Application startup initialization** — main_on_startup, database_create_db_and_tables, seed_service_seed_default_admin [EXTRACTED 1.00]
- **Core domain models** — user_user, article_article, subscriber_subscriber, newsletter_send_newslettersend [EXTRACTED 1.00]
- **Test database isolation pattern** — conftest_session_fixture, conftest_client_fixture, database_get_session [INFERRED 0.85]
- **TipTap Content Processing Pipeline** — content_service_extract_plain_text_from_tiptap, content_service_auto_generate_description, tiptap_renderer_render_tiptap_node_to_html, tiptap_renderer_render_tiptap_to_email_html [INFERRED 0.85]
- **Newsletter Delivery Flow** — newsletter_service_send_newsletter_for_article, subscriber_service_list_active_subscribers, email_service_send_newsletter_email, tiptap_renderer_render_tiptap_to_email_html [INFERRED 0.85]
- **Subscriber Lifecycle State Machine** — subscriber_service_create_subscriber, subscriber_service_confirm_subscriber, subscriber_service_unsubscribe_subscriber, subscriber_service_list_active_subscribers [INFERRED 0.85]

## Communities (58 total, 24 thin omitted)

### Community 0 - "Article Management Domain"
Cohesion: 0.07
Nodes (38): Article Management Spec (Archive), Article model, create_article service, delete_article service, generate_slug, get_article_by_slug service, list_all_articles service, list_published_articles service (+30 more)

### Community 1 - "Article API Implementation"
Cohesion: 0.11
Nodes (21): create_article_endpoint(), delete_article_endpoint(), get_article_endpoint(), list_admin_articles_endpoint(), list_articles_endpoint(), create_article(), delete_article(), generate_slug() (+13 more)

### Community 2 - "Database Models & Setup"
Cohesion: 0.1
Nodes (14): Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online(), create_db_and_tables(), get_session(), on_startup(), Article (+6 more)

### Community 3 - "Subscriber API Routes"
Cohesion: 0.11
Nodes (16): update_article_endpoint(), confirm_endpoint(), subscribe_endpoint(), unsubscribe_endpoint(), send_confirmation_email(), send_newsletter_email(), Send newsletter to all active subscribers who haven't received it yet., send_newsletter_for_article() (+8 more)

### Community 4 - "Newsletter Delivery Specs"
Cohesion: 0.12
Nodes (22): Newsletter Delivery Spec (Archive), Subscriber Management Spec (Archive), auto_generate_description, extract_plain_text_from_tiptap, Double Opt-in and Soft Unsubscribe, Resend Synchronous Email Delivery, send_confirmation_email, send_newsletter_email (+14 more)

### Community 5 - "Core App & Authentication"
Cohesion: 0.12
Nodes (19): upgrade migration, Admin Authentication Spec (Archive), Settings configuration class, client fixture, session fixture, create_db_and_tables, get_session, require_admin dependency (+11 more)

### Community 6 - "Frontend Public Views"
Cohesion: 0.15
Nodes (13): Admin Article Edit View, Admin Articles View, Handle Article Delete, Load Admin Articles, Article View, Home View, Newsletter Form, Triple-Coded State UI Pattern (+5 more)

### Community 7 - "Frontend Admin Composables"
Cohesion: 0.35
Nodes (8): createArticle(), deleteArticle(), fetchAdminArticle(), fetchAdminArticles(), getAuthHeaders(), updateArticle(), handleDelete(), loadArticles()

### Community 9 - "Frontend Auth State"
Cohesion: 0.31
Nodes (9): Clear Admin Token, Set Admin Token, Admin Token Ref, Admin Pinia Store, Admin Logout Function, Admin Login Function, Router BeforeEach Guard, LocalStorage Token Persistence (+1 more)

### Community 10 - "Pydantic Schemas"
Cohesion: 0.6
Nodes (4): ArticleCreate, ArticleUpdate, SubscribeRequest, BaseModel

### Community 11 - "Content Processing Service"
Cohesion: 0.5
Nodes (4): auto_generate_description(), extract_plain_text_from_tiptap(), Generate a description from the first N characters of article plain text., Recursively extract plain text from TipTap JSON document.

### Community 12 - "TipTap HTML Renderer"
Cohesion: 0.5
Nodes (4): Render a single TipTap node to HTML string., Render TipTap JSON document to email-safe HTML with inline styles., render_tiptap_node_to_html(), render_tiptap_to_email_html()

### Community 13 - "Form Submit Handlers"
Cohesion: 0.5
Nodes (5): Handle Article Submit, Handle Newsletter Submit, Create Article, Update Article, Subscribe to Newsletter

### Community 15 - "Application Configuration"
Cohesion: 0.5
Nodes (3): Config, Settings, BaseSettings

### Community 18 - "Docker & Project Meta"
Cohesion: 0.67
Nodes (4): AGENTS.md Project Documentation, OpenSpec Config, Docker Compose Dev Configuration, Docker Compose Prod Configuration

### Community 21 - "TipTap Editor Components"
Cohesion: 1.0
Nodes (3): TipTap Editor, TipTap Renderer, Render TipTap JSON

### Community 22 - "Agent Conventions & TDD"
Cohesion: 0.67
Nodes (3): SQLModel Single Source of Truth, Test-Driven Development (TDD), Tech Stack Definition

### Community 23 - "Design System Rationale"
Cohesion: 0.67
Nodes (3): Design System & UI Conventions, Laboratory Aesthetic, Triple-Coded Accessibility

## Knowledge Gaps
- **68 isolated node(s):** `Config`, `Verify the request includes the correct admin bearer token.`, `Create a default admin user if no users exist in the database.`, `Recursively extract plain text from TipTap JSON document.`, `Generate a description from the first N characters of article plain text.` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_article()` connect `Article API Implementation` to `Database Models & Setup`, `Content Processing Service`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `create_article service` connect `Article Management Domain` to `Newsletter Delivery Specs`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `upgrade migration` connect `Core App & Authentication` to `Article Management Domain`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `create_article()` (e.g. with `create_article_endpoint()` and `auto_generate_description()`) actually correct?**
  _`create_article()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `create_subscriber()` (e.g. with `subscribe_endpoint()` and `send_confirmation_email()`) actually correct?**
  _`create_subscriber()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `send_newsletter_for_article()` (e.g. with `update_article_endpoint()` and `list_active_subscribers()`) actually correct?**
  _`send_newsletter_for_article()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `Verify the request includes the correct admin bearer token.`, `Create a default admin user if no users exist in the database.` to the rest of the system?**
  _68 weakly-connected nodes found - possible documentation gaps or missing edges._