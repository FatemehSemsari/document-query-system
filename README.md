# Document Query System

A Django-based document question-answering application using Retrieval-Augmented Generation (RAG). Administrators can upload DOCX files, retrieve relevant passages, ask questions in natural language, and view question-answer history. The application supports Persian text and runs locally through Docker Compose.

## Features

- DOCX upload, validation, editing and deletion through Django Admin and REST API.
- Automatic extraction and storage of document body text, including paragraphs and tables.
- Semantic retrieval with multilingual E5 embeddings and persistent ChromaDB storage.
- Two-stage retrieval using a multilingual cross-encoder reranker.
- LangChain prompt and generation pipeline with Groq; answers are instructed to use retrieved document content and cite numbered sources.
- Persistent question-answer history, including user, timestamp and retrieval metadata.
- Django Admin interface for document management and question-answer history, plus a question form if enabled in the admin configuration.

## Architecture

```text
DOCX -> Text extraction -> SQLite (full text)
                         -> Chunking -> E5 embeddings -> ChromaDB
Question -> Semantic search -> Cross-encoder reranking
         -> LangChain prompt + Groq LLM -> Answer + sources
         -> SQLite history -> Django Admin / REST API
```

| Component | Technology |
| --- | --- |
| Backend / UI | Django / Django Admin |
| REST API | Django REST Framework |
| Relational database | SQLite |
| Text extraction | python-docx |
| Pipeline | LangChain |
| Embeddings | intfloat/multilingual-e5-small |
| Vector index | ChromaDB |
| Reranker | cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 |
| Generation | Groq (model configurable via GROQ_MODEL) |
| Runtime | Docker Compose, Python 3.12, CPU PyTorch |

## Run with Docker (recommended)

### Prerequisites

- Docker with Compose v2 (for example, Docker Desktop).
- Internet access to download the base image, dependencies and Hugging Face models, and to call Groq.
- A Groq API key from https://console.groq.com/keys.
- Sufficient disk space and RAM for the local CPU models.

### 1. Configure environment variables

In the directory containing `manage.py` and `docker-compose.yml`, copy `.env.example` to `.env`.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Edit `.env`. Set `GROQ_API_KEY` to your own key, `GROQ_MODEL` to the supported Groq model configured in the project, `DJANGO_SECRET_KEY` to a fresh random secret, and `DJANGO_DEBUG=True` for local development. A secret can be generated with `python -c "import secrets; print(secrets.token_hex(32))"` if Python is installed. Do not commit or distribute `.env`. Keep the model ID configurable; provider availability and quotas can change.

### 2. Build and start

```bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Database migrations are applied automatically on startup. Inspect logs with `docker compose logs -f web` if needed. The first build downloads Python dependencies; the first retrieval also downloads the embedding and reranking models.

### 3. Create an administrator

For a fresh database, run:

```bash
docker compose exec web python manage.py createsuperuser
```

Enter a username and password of your choice. Do not include real credentials in the submission.

### 4. Use the application

1. Open http://127.0.0.1:8000/admin/ and sign in as the administrator.
2. In Documents, upload the DOCX files in `sample_data/`. Enter titles such as `company_rules`, `financial_rules`, and `training_rules`.
3. Open a saved document and confirm that Full text contains the extracted text.
4. Open http://127.0.0.1:8000/api/ask/ in the same signed-in browser, enter a question, and submit POST. If the custom Admin question form is enabled, questions can also be submitted via QA > Questions and Answers > Add.
5. View history in Django Admin or at http://127.0.0.1:8000/api/history/.

A fresh Docker installation intentionally starts with an independent empty database. Sample documents must be uploaded manually; no local database is required or imported.

## Example questions

| Question | Expected answer after uploading sample data |
| --- | --- |
| کارکنان چند روز در سال مرخصی دارند؟ | ۲۶ روز مرخصی استحقاقی |
| ساعات کاری شرکت چگونه است؟ | ۹ صبح تا ۵ عصر |
| سقف وام کارکنان چقدر است؟ | ۵۰ میلیون تومان |
| کارمندان سالانه چند ساعت آموزش می‌بینند؟ | ۴۰ ساعت |
| پایتخت فرانسه کجاست؟ | اطلاعات کافی برای پاسخ به این سؤال در اسناد موجود نیست. |

These are expected answers, not guaranteed exact model output. Source numbers depend on retrieval order.

## API documentation

See [docs/API.md](docs/API.md) for endpoints, authentication, examples, status codes and response formats.

## Data persistence and routine commands

| Storage | Purpose |
| --- | --- |
| `docker_data/db.sqlite3` | Users, documents and question-answer history |
| `docker_data/media/` | Uploaded DOCX files |
| `docker_data/chroma_db/` | Persistent vector index |
| Docker named volume `model_cache` | Hugging Face model and tokenizer cache |

The vector index is synchronized before retrieval; changed or deleted chunks are updated or removed during the next retrieval. `docker compose down` preserves the bind-mounted data and named cache volume.

```bash
docker compose down          # Stop and remove containers
docker compose up -d         # Start again using the existing image
docker compose logs -f web   # Inspect application logs
docker compose up -d --build # Rebuild after source changes
```

Do not use `docker compose down -v` for normal shutdown: it removes the named model cache. Do not delete `docker_data/` unless you intend to remove stored application data.

## Project layout

```text
document_query_system/   Django settings and root URL configuration
documents/               Document model, validation, extraction and retrieval
qa/                      Groq integration, prompts, RAG, history and API
docs/API.md              API documentation
sample_data/             Fictional Persian DOCX fixtures
screenshots/             Actual application screenshots
Dockerfile               Container image definition
docker-compose.yml       Service, environment and storage configuration
requirements.txt         Local Python dependencies
requirements-docker.txt  Docker Python dependencies
.env.example             Example environment configuration
```

## Scope and limitations

This project is configured for local evaluation, not public production deployment. The Django development server and debug media serving should not be used for confidential documents or public internet exposure. Retrieved passages are sent to Groq for generation; use non-confidential data. The system extracts ordinary DOCX body paragraphs and tables, not all possible Word elements (such as text in images, footnotes or text boxes). Retrieval and model-generated answers can be imperfect; source metadata represents retrieved chunks, not verified citations. The first request may take longer while local models load. The vector index is intended for a small, single-process application.
