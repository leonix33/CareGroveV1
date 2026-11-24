# CareGrove

Standalone product for families and care providers. It is not part of IntuitPoint.

Families search a free directory, see Suggested matches, save providers, send connection requests, and message. Providers keep a listing, submit evidence, and manage an optional monthly membership on this website. Staff review evidence, reviews, and subscriptions.

The visual base is the 20 November 2026 design package: logo, provider photographs, and all 38 screen images live in `apps/web/public`.

## Run it

API:

```bash
./scripts/dev-api.sh
```

Web, in a second terminal:

```bash
./scripts/dev-web.sh
```

Open http://localhost:3000

Sample password for every demo account: `CareGrove-demo-12`

- Family: `maya.chen@caregrove.demo`
- Provider: `oak@caregrove.demo` (Bright Path Services)
- Staff: `admin@caregrove.demo`

The API uses a local SQLite file until `DATABASE_URL` points at Postgres. `infra/docker-compose.yml` starts Postgres on port 5433.

## Production

`infra/render.yaml` runs one always-on container (the site and the API) plus Postgres. Render gives the site an `onrender.com` address. A custom domain can be added on that service later. Demo sign-in still works. Paid membership checkout stays closed until PayPal and the monthly price are connected.

## Matching rule

Suitable active premium providers fill Suggested matches. Free providers appear there only when no suitable premium provider qualifies. Both stay in All providers. Membership does not change Trust Score or verification.
