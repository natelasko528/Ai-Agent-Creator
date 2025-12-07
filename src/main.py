"""Main entry point for the AI Digital Assistant."""
import os
import uvicorn
from dotenv import load_dotenv

from .api.server import create_api


def main():
    """Run the AI Digital Assistant server."""
    load_dotenv()

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    app = create_api()

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
