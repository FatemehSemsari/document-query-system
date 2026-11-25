# REST API Reference

Base URL: `http://127.0.0.1:8000`

The API uses Django REST Framework. All routes below require an authenticated staff user (`is_staff=True`). Use HTTP Basic Authentication with Django credentials in Postman, or sign in to Django Admin and use the DRF browsable API in the same browser. Session-authenticated unsafe requests require a CSRF token. Basic Authentication should only be used over HTTPS outside localhost. The Groq API key is server-side and must not be sent by API clients.

## Endpoint overview

| Method | Route | Purpose | Success |
| --- | --- | --- | --- |
| GET | `/api/documents/` | List documents | 200 |
| POST | `/api/documents/` | Create a DOCX document | 201 |
| GET | `/api/documents/{id}/` | Retrieve one document | 200 |
| PUT | `/api/documents/{id}/` | Full document update | 200 |
| PATCH | `/api/documents/{id}/` | Partial update | 200 |
| DELETE | `/api/documents/{id}/` | Delete a document | 204 |
| POST | `/api/search/` | Retrieve and rerank relevant chunks | 200 |
| POST | `/api/ask/` | Generate an answer and save history | 200 |
| GET | `/api/history/` | List paginated history | 200 |
| GET | `/api/history/{id}/` | Retrieve one history entry | 200 |

All routes have a trailing slash. Replace `{id}` with an existing integer record ID. JSON responses and scores below are illustrative, not recorded results. Use actual IDs from your application.

## Documents

### List and retrieve

`GET /api/documents/` returns an array of document objects; `GET /api/documents/1/` returns one object. No request body is required.

Example document:

```json
{
  "id": 1,
  "title": "company_rules",
  "file": "http://127.0.0.1:8000/media/documents/company_rules.docx",
  "full_text": "قوانین شرکت\nکارکنان در سال ۲۶ روز مرخصی استحقاقی دارند.",
  "created_at": "2026-11-25T09:00:00Z",
  "updated_at": "2026-11-25T09:00:00Z"
}
```

### Create

`POST /api/documents/` with `multipart/form-data`:

| Field | Type | Required | Example |
| --- | --- | --- | --- |
| `title` | Text | Yes | `company_rules` |
| `file` | File | Yes | `company_rules.docx` |

In Postman select Body > form-data, set `file` to File, and select the sample document. Do not manually set a multipart boundary. The API extracts text automatically and returns the saved document (201). The file must be a readable, non-empty DOCX, at most 10 MiB (10 × 1024 × 1024 bytes); title is limited to 255 characters. The ID, extracted text and timestamps are read-only.

### Update

`PATCH /api/documents/1/` with `application/json`:

```json
{"title": "updated_company_rules"}
```

To replace a file, use multipart/form-data with the `file` field. For `PUT`, provide the complete writable data (`title` and `file`) as multipart/form-data. Replacing the file re-extracts its text; updating only the title preserves the existing text. Returns the updated document (200).

### Delete

`DELETE /api/documents/1/` requires no request body. Returns 204 with an empty body. The associated file is cleaned up and stale index chunks are removed on the next retrieval. A missing ID returns 404. Existing question-answer history may retain source metadata for the deleted document.

## Advanced search

`POST /api/search/` with `Content-Type: application/json`:

```json
{"question": "شرایط دریافت وام چیست؟"}
```

`question` is required, nonblank and at most 1000 characters. This endpoint performs semantic search and cross-encoder reranking without calling Groq or saving question-answer history.

Example response (200):

```json
{
  "question": "شرایط دریافت وام چیست؟",
  "count": 1,
  "results": [
    {
      "document_id": 1,
      "title": "company_rules",
      "chunk_index": 0,
      "text": "حداقل سابقه لازم برای دریافت وام شرکت ۲ سال است.",
      "distance": 0.32,
      "rerank_score": 7.85
    }
  ]
}
```

The returned text is the retrieved chunk, not necessarily a single sentence. Lower distance means closer embeddings; higher reranker score means higher rank. Neither is an accuracy percentage. With no documents, the results array is empty and count is zero.

## Question answering

`POST /api/ask/` with `Content-Type: application/json`:

```json
{"question": "کارکنان چند روز در سال مرخصی دارند؟"}
```

The same question validation applies. The system retrieves and reranks chunks, constructs a LangChain prompt, calls Groq when context exists, and saves a successful result in history.

Example response (200):

```json
{
  "id": 1,
  "user": 1,
  "username": "admin",
  "question": "کارکنان چند روز در سال مرخصی دارند؟",
  "answer": "کارکنان در سال ۲۶ روز مرخصی استحقاقی دارند. [1]",
  "sources": [
    {
      "source_number": 1,
      "document_id": 1,
      "title": "company_rules",
      "chunk_index": 0,
      "distance": 0.2301,
      "rerank_score": 8.42
    }
  ],
  "created_at": "2026-11-25T09:05:00Z"
}
```

`id` identifies the history entry; `user` is the Django user ID. `sources` lists retrieved chunks passed to the model, not necessarily all chunks actually cited. The source numbering matches the prompt's numbered context. For an unsupported question, the intended answer is `اطلاعات کافی برای پاسخ به این سؤال در اسناد موجود نیست.` With an empty index, sources is `[]`. With nonempty retrieval, sources may still contain candidates even when the answer reports insufficient information. Such a successful no-answer response is saved in history; upstream errors are not.

## History

`GET /api/history/` returns history ordered newest first, 20 entries per page. `GET /api/history/1/` returns one history object in the same format as the Ask response. No request body is required.

Optional parameters on the list:

| Parameter | Example | Purpose |
| --- | --- | --- |
| `page` | `?page=2` | Select page |
| `search` | `?search=مرخصی` | Search question, answer or username |

Example empty response (200):

```json
{"count": 0, "next": null, "previous": null, "results": []}
```

For populated history, `results` contains the full history objects, and `next` / `previous` contain pagination URLs where applicable. The API is read-only for history; staff can see all entries under the current access policy. If a user is deleted, the user association can become null.

## Error handling

| Code | Meaning |
| --- | --- |
| 400 | Invalid input, missing/blank question, invalid DOCX |
| 401 | Missing or invalid authentication credentials |
| 403 | Insufficient permission or failed session CSRF validation |
| 404 | Record not found |
| 405 | Unsupported method (e.g. GET on `/api/ask/`) |
| 415 | Unsupported media type |
| 500 | Unexpected internal or retrieval error |
| 502 | Groq API error |
| 503 | Groq rate limit, connection failure, or missing configuration |
| 504 | Groq request timeout |

Validation example (400):

```json
{"question": ["This field may not be blank."]}
```

Service error example (503):

```json
{"error": "LLM service rate limit exceeded."}
```

Exact validation text can depend on Django language settings and library versions.
