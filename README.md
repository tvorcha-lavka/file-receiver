# File Receiver Microservice

This microservice is responsible for receiving image files through WebSocket connections,
performing real-time validation, and saving them to a volume connected to EFS (Elastic File System).  
It ensures minimal resource usage and responsive user feedback during the upload process.

The service validates incoming files by:
- File type: **HEIC**, **HEIF**, **JPEG**, **PNG**, **WEBP**
- File size: up to **5MB** each
- Upload session: up to **10** files
- Uniqueness: no duplicate files within the same browser tab session

Files are saved directly to the mounted volume once validation is passed.

---

## Technology

The microservice utilizes the following technologies:
- **Python 3.11+**
- **FastAPI** — for API and WebSocket handling.
- **Pydantic** — for data validation.
- **Pillow** & **pillow-heif** — to process and validate image files.
- **aiofiles** — for asynchronous file operations.
- **imagehash** — for detecting duplicate files.
- **websockets** — to support real-time file uploads.

---

## Project structure

``` plaintext
file-receiver-py3.11
│
├── .env                  # Environment variables
├── .env.example          # Environment variables example
│
├── Makefile              # Commands for managing
├── pyproject.toml        # Project configuration
│
├── docker                # Configuration for Docker
├── scripts               # Scripts for launching a microservice
│
├── src                   # Source code
│   ├── api               # API layer with WebSocket routes and schemas
│   │   ├── routes        # WebSocket endpoints
│   │   └── schemas       # Request/response models
│   │
│   ├── core              # Application configuration and settings
│   │   └── config        # Configuration modules (logging, image, websocket)
│   │
│   ├── enums             # Enum definitions for file types and WebSocket events
│   ├── handlers          # Image processing logic
│   ├── managers          # Session and upload state management
│   └── validators        # File validators (type, size, duplicates)
│
├── templates             # HTML templates (e.g., for demo/testing)
└── tests                 # Tests
```

---

## Docker

The microservice uses Docker to package all dependencies and run.
The following files are available for working with Docker Compose:

- **docker-compose.yml** — main configuration file.
- **docker-compose.dev.yml** — configuration file for development.
- **docker-compose.test.yml** — configuration file for testing.
- **docker-compose.rabbitmq.yml** — configuration file for RabbitMQ.

---

## Important files
- **entrypoint.sh** — main script for launching the microservice in production mode.
- **entrypoint.py** — main script for launching the microservice in development mode.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/tvorcha-lavka/file-receiver.git
   cd file-receiver
   ```

2. Install Poetry dependencies:

   ```bash
   poetry install --no-root
   ```

3. Create an `.env` file based on the example:

   ```bash
   cp .env.example .env
   ```
   
4. Set environment variables in `.env` if necessary.

---

## Launch
### Local launch

To run the microservice locally, use commands from the Makefile that automate the use of Docker Compose:

- Build an image:

  ```bash
  make build
  ```
  
- Start services:

  ```bash
  make up
  ```

- To stop services:

  ```bash
  make stop
  ```

- Rebuild (if new dependencies are introduced):

  ```bash
  make rebuild
  ```

---

## Testing

1. Make sure that the `ENV_STATE=development` flag is set in the `.env` file.

2. Build an image for testing:

    ```bash
    make build
    ```

3. Use one of the following commands to run the tests:

   - To run all tests:

     ```bash
     make pytest
     ```

   - To run all tests with coverage:

     ```bash
     make pytest-cov
     ```

---

## License

This project is licensed under the [MIT License](./LICENSE).
