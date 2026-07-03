# Smart Online X

A redesigned storefront for **smart.online.x**, split into two parts:

- **`frontend/`** — static HTML/CSS/JS storefront (works on GitHub Pages, same as before)
- **`backend/`** — a real Flask + SQLAlchemy REST API: accounts, product catalog, cart, checkout, and order history

## Why two parts?

GitHub Pages only serves static files — it can't run Python. So the backend needs
to be hosted somewhere that runs a server (Render, Railway, Fly.io, PythonAnywhere
all have free tiers), and the static frontend on GitHub Pages talks to it over the
network.

## 1. Run the backend locally

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit SECRET_KEY / JWT_SECRET_KEY
python seed.py                  # creates the database + sample products
python app.py                   # runs on http://localhost:5000
```

Visit `http://localhost:5000/api/health` — you should see `{"status": "ok"}`.

## 2. Point the frontend at your backend

Open `frontend/js/api.js` and edit the first line:

```js
const API_BASE_URL = window.SMART_X_API_BASE || "http://localhost:5000";
```

For local testing this already works. For production, change the fallback to your
deployed backend URL, e.g. `"https://smart-online-x-api.onrender.com"`.

Then open `frontend/index.html` directly in a browser, or serve the folder:

```bash
cd frontend
python -m http.server 8080
```

## 3. Deploy the backend (example: Render)

1. Push this repo to GitHub (or push `backend/` as its own repo).
2. On [Render](https://render.com), create a **new Web Service** pointing at the repo,
   root directory `backend`.
3. Build command: `pip install -r requirements.txt`
   Start command: `gunicorn app:app` (add `gunicorn` to `requirements.txt` first)
4. Add environment variables from `.env.example` (`SECRET_KEY`, `JWT_SECRET_KEY`,
   `CORS_ORIGINS` — set this to your GitHub Pages URL, e.g.
   `https://diabmostafa231.github.io`).
5. After the first deploy, open a shell on Render (or run once locally against the
   production `DATABASE_URL`) and run `python seed.py` to populate products.

## 4. Deploy the frontend (GitHub Pages)

1. Copy everything in `frontend/` into your `smart.online.x` repo (this can replace
   the existing static files).
2. Update `API_BASE_URL` in `frontend/js/api.js` to your deployed backend URL.
3. Commit and push — GitHub Pages will serve it as before at
   `https://diabmostafa231.github.io/smart.online.x/`.

## What changed vs. the original site

**Frontend**
- Full redesign: dark "spec sheet" tech aesthetic, consistent nav/search/cart across
  every page, responsive down to mobile, product grid with filtering and search.
- New pages: product detail, cart, checkout, order history — all wired to the API
  instead of being static/non-functional.

**Backend (new)**
- `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me` — JWT-based auth,
  passwords hashed with bcrypt.
- `GET /api/products`, `GET /api/products/<id>` — catalog with category/search filters.
- `GET|POST /api/cart`, `PUT|DELETE /api/cart/<id>` — persistent, per-user cart.
- `POST /api/checkout` — turns the cart into an `Order`, decrements stock.
- `GET /api/orders`, `GET /api/orders/<id>` — order history.

## Notes / next steps

- Payments aren't wired to a real processor — `checkout` currently just records the
  order. Plug in Stripe Checkout or a similar provider before taking real payments.
- The feedback form on `feedback.html` is local-only; add a
  `POST /api/feedback` endpoint (a two-line addition to `app.py`) if you want it
  to actually store submissions.
- Swap SQLite for Postgres in production by setting `DATABASE_URL` — no code changes
  needed, since it's all through SQLAlchemy.
