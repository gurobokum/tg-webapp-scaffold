# Telegram WebApp Scaffold

This repo contains scaffold for Telegram WebApp, for fast starting of Telegram WebApp.

It contains:

- Authentication
- Linters, formatters
- WebApp and tgbot i18n
- Logging, Logfire integration
- Credits system with stars
- Invites system
- LLM Langchain integration

## Tech stack

### Backend

- FastAPI
- Arq
- MinIO (S3)
- PostgreSQL
- Redis
- python-telegram-bot
- SQLAlchemy
- Pydantic

### Frontend

- NextJS
- Tailwind CSS
- daisyui
- zod
- tanstack
- i18next
- framer-motion
- react-hook-form
- hey-api

## Installation

1. Install [pnpm](https://pnpm.io/installation#using-npm)
2. Install [poetry](https://python-poetry.org/docs/#installation)
3. Install dependencies
   ```bash
   pnpm install
   ```
4. Generate OpenAPI SDK
   ```bash
   pnpm generate_openapi
   ```

## Setup telegram

1. Create telegram bot with [@BotFather](https://t.me/botfather)
2. Set TGBOT_TOKEN in `.env` file
