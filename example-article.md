---
title: Building a Blog with FastAPI and Vue 3
description: A deep dive into building a modern blog platform with FastAPI backend, Vue 3 frontend, and PostgreSQL.
tags: fastapi, vue, python, webdev
slug: building-blog-fastapi-vue3
---

# Building a Blog with FastAPI and Vue 3

In this article, we'll explore how to build a modern blog platform from scratch using **FastAPI** for the backend and **Vue 3** for the frontend.

## Why This Stack?

FastAPI provides:
- Automatic OpenAPI documentation
- Async-first architecture
- Type safety with Pydantic

Vue 3 offers:
- Composition API for reusable logic
- Excellent TypeScript support
- Fast virtual DOM

## Project Structure

```
blog-platform/
├── app/
│   ├── main.py
│   ├── routers/
│   └── services/
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   └── components/
│   └── vite.config.ts
└── docker-compose.yml
```

## Getting Started

First, install the dependencies:

```bash
# Backend
pip install fastapi uvicorn sqlmodel

# Frontend
cd frontend && npm install
```

Then run the development servers:

```bash
# Backend (port 8000)
uvicorn app.main:app --reload

# Frontend (port 5173)
npm run dev
```

## Database Models

Here's a simple article model using SQLModel:

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Article(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    content: str
    published_at: datetime = Field(default_factory=datetime.utcnow)
```

## Key Features

| Feature | Backend | Frontend |
|---------|---------|----------|
| CRUD API | FastAPI + SQLModel | Vue Router + Pinia |
| Auth | JWT tokens | Axios interceptors |
| Images | Local storage | TipTap editor |

> **Pro tip:** Always write tests before implementing features. TDD saves time in the long run.

## Conclusion

Building a blog platform is a great way to learn full-stack development. The combination of FastAPI and Vue 3 gives you a *type-safe*, *performant*, and *developer-friendly* stack.

Happy coding!
