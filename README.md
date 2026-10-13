# Orders synchronizer

A small stateless FastAPI service for `https://test.ooobs.ru/api/orders`.

- Fetches the source JSON on each incoming request.
- Normalizes Russian mobile phone numbers to `+7XXXXXXXXXX`, converting `8XXXXXXXXXX` and `9XXXXXXXXX` appropriately. Invalid numbers are discarded.
- Keeps the maximum `amount` per normalized phone. For ties, keeps the newest `created_at`.
- Produces deterministic order by normalized phone. No persistent storage is used, so repeated calls are idempotent.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

`GET /` and `GET /api/orders` return the exact `clients` and `stats` JSON shape.

## Deploy to Vercel

From this directory, run `npx vercel --prod`, or push to GitHub and import the repository into Vercel. Vercel automatically detects the FastAPI `app` in root `app.py`.

## Configuration / secrets

No secrets are needed for the public input endpoint. Override the source with `ORDERS_URL` via a deployment environment variable if required; never commit actual credentials or `.env` files.

## Self-test

```bash
python -m unittest discover -s tests -v
```
