# Credit Approval System (Backend)

Django + DRF backend that evaluates loan eligibility and manages customer loans using historical Excel data.

---

## Run (Docker)

```bash
docker compose up --build
```

This will:

- Start PostgreSQL
- Apply migrations
- Ingest Excel datasets
- Start the API server

Base URL:

```
http://localhost:8000/
```

---

## Endpoints

- **POST** `/api/register/`
- **POST** `/api/check-eligibility/`
- **POST** `/api/create-loan/`
- **GET** `/api/view-loan/<loan_id>/`
- **GET** `/api/view-loans/<customer_id>/`

---

## Key Implementation Notes

- `current_debt` is **not stored statically** and is **calculated dynamically** during `/check-eligibility`.
- Some dataset rows contained **duplicate loan IDs**. Duplicate conflicting entries were ignored to maintain unique loan records.
- Some loans had `emis_paid_on_time > tenure`. The system safely handles this using `min(emis_paid_on_time, tenure)`.
- EMI for new loans is calculated using the **compound interest formula**.
- Data ingestion is **idempotent** (`ignore_conflicts=True`).

---

## Running Tests

```bash
docker compose exec web python manage.py test
```
or Locally:
```bash
python manage.py test
```

---

## Tech Stack

- Django + DRF
- PostgreSQL (Docker)
- Pandas
- Docker Compose
