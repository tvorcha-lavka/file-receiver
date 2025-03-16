#!/usr/bin/env python
"""
Development entrypoint for `file-receiver` project.

This script runs the FastAPI application using Uvicorn with automatic
reload enabled for development purposes.
"""
import os

import uvicorn


def main() -> None:
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        reload_delay=5.0,
        use_colors=True,
    )


if __name__ == "__main__":
    main()
