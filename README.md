# Train Management Backend

A Flask REST API for managing users, trains, stations, schedules, bookings,
payments, and user favourites. Authentication uses a server-side session cookie.

## API base URL

All application endpoints are prefixed with `/api`. After deployment, replace
`<service-url>` below with the Render service URL.

| Endpoint | Purpose | Authentication |
| --- | --- | --- |
| `GET /` | Service information | Public |
| `GET /health` | Health check for Render | Public |
| `POST /api/register` | Create an account | Public |
| `POST /api/login` | Start a session | Public |
| `DELETE /api/logout` | End the current session | Required |
| `GET /api/check-session` | Get the signed-in user | Required |
| `/api/users` | User resources | Required |
| `/api/trains` | Train resources | Required |
| `/api/stations` | Station resources | Required |
| `/api/schedules` | Schedule resources | Required |
| `/api/bookings` | Booking resources | Required |
| `/api/payments` | Payment resources | Required |
| `/api/favourites` | Favourite resources | Required |

Individual resources use an ID, for example `/api/trains/1`. Consult the
resource handlers in `resources/` for the methods and request fields supported
by each endpoint.

## Local setup

1. Create and activate a virtual environment.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:

   ```env
   DATABASE_URI=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
   SECRET_KEY=replace-with-a-long-random-secret
   ALLOWED_ORIGINS=http://localhost:5173
   SESSION_COOKIE_SAMESITE=Lax
   SESSION_COOKIE_SECURE=False
   ```

4. Apply the database migrations and start the API:

   ```bash
   flask --app app db upgrade
   flask --app app run --debug
   ```

The application is then available at `http://127.0.0.1:5000`. Check it with:

```bash
curl http://127.0.0.1:5000/health
```

## Deploying to Render

The included `render.yaml` creates a Python web service. Render installs from
`requirements.txt`, starts Gunicorn with `app:app`, and checks `GET /health`.

1. Push this project to a Git repository and create a **Blueprint** in Render,
   selecting that repository. Alternatively create a Python Web Service and use:

   ```text
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
   ```

2. Create a Render PostgreSQL database and set the service environment
   variables:

   ```text
   DATABASE_URI=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
   SECRET_KEY=<long random value>
   ALLOWED_ORIGINS=https://your-frontend.example
   SESSION_COOKIE_SAMESITE=None
   SESSION_COOKIE_SECURE=True
   ```

   Use the connection values supplied by Render for `DATABASE_URI`; do not
   commit credentials to `.env` or the repository.

3. Run `flask --app app db upgrade` once against the Render database (for
   example from the Render Shell) before using the API.

4. Redeploy. Opening the service URL now returns JSON rather than a 404; use
   `<service-url>/health` to confirm the service is ready.

For a browser frontend on another domain, keep `supports_credentials` in mind:
requests must send credentials and `ALLOWED_ORIGINS` must contain the exact
frontend origin (not `*`).

## Example

```bash
curl -X POST http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"password"}' \
  -c cookies.txt
```

Use `-b cookies.txt` on later requests to include the session cookie.
