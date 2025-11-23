# Agent Master Console

This directory contains the primary files for the Agent Master Console. See individual subdirectories for details and usage.

## Setup

Server and test utilities live in the `server/` and `client/` folders respectively. Install the Python backend dependencies before starting the mock server or running the tests:

```
python -m pip install -r server/requirements.txt
```

## Testing

The end-to-end suite uses Playwright to launch the FastAPI mock server and the Vite client together. From the `client/` directory:

1) Install the Node dependencies:

```
npm install
```

2) On the first run, download the Playwright browser and system dependencies:

```
npm run setup:e2e
```

3) Execute the test suite:

```
npm run test:e2e
```

Live API integration tests reside in `server/tests`. They are skipped automatically unless `OPENAI_API_KEY` is set in the environment.
