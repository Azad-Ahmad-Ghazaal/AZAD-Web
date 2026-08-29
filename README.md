# AZAD Web

Public web frontend for **AZAD**, connected to the `AZAD-AI` backend.

## Architecture

`AZAD-Web` is the public frontend. The intelligence, memory, agents, bots, voice and API remain in `AZAD-AI`.

- Frontend: `ghazaalbaloch1-cloud/AZAD-Web`
- Backend: `ghazaalbaloch1-cloud/AZAD-AI`
- API health: `/api/v1/health`
- Chat: `/api/v1/chat`
- Bots: `/api/v1/bots`
- Automatic bot routing: `/api/v1/bots/auto`
- Bot creation: `/api/v1/bots/create`

## Deployment

Deploy this repository with Vercel (or another static host). The frontend no longer asks users for an access token and does not store authentication credentials in browser storage.

Set the production backend URL in `index.html` via the `AZAD_BACKEND_URL` constant when the backend endpoint changes. Do not commit API keys, access tokens, model credentials, private URLs, or user data.

The backend must be configured separately. Public deployment should retain server-side rate limiting and authorization controls even though the frontend has no token UI.
