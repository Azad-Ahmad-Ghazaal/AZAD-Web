# AZAD Web

Public web frontend for **AZAD**, connected to the private `AZAD-AI` backend.

## Architecture

`AZAD-Web` is the static GitHub Pages frontend. The intelligence, memory, agents, bots, voice and API remain in the private `AZAD-AI` repository.

- Frontend: `ghazaalbaloch1-cloud/AZAD-Web`
- Backend: `ghazaalbaloch1-cloud/AZAD-AI`
- API health: `/api/v1/health`
- Chat: `/api/v1/chat`
- Bots: `/api/v1/bots`
- Automatic bot routing: `/api/v1/bots/auto`
- Bot creation: `/api/v1/bots/create`

## Deployment

Publish the `main` branch with GitHub Pages. The frontend asks for the backend URL and access token in the browser, so secrets are not committed to this public repository.

The backend should run with `AZAD_ENV=production` and a strong `AZAD_MOBILE_TOKEN`. For the GitHub Pages frontend, allow the origin `https://ghazaalbaloch1-cloud.github.io` through `AZAD_ALLOWED_ORIGINS` (the AZAD backend now includes this origin by default).

## Important

Do not commit API keys, access tokens, model credentials, private URLs, or user data to this repository.
