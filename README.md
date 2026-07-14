# LinkRedirect

A simple, secure, and permanent link redirection service, that supports dynamic URL generation.

## Usage

1.  **Install Dependencies**:

    ```bash
    uv sync
    ```

2.  **Configuration**:
    Edit `config.yaml`:

    ```yaml
    security:
        access_key: "your-secret-key"

    routes:
        example: "https://example.com/actual-url"
        dynamic_example: "fn://my_custom_function"
    ```

3.  **Dynamic Functions**:
    Define your custom logic in `custom.py`:

    ```python
    def my_custom_function(routes):
        return "https://dynamically-generated-url.com"
    ```

    A dynamic function may also return a FastAPI `Response`. This is useful when
    LinkRedirect should fetch an internal-only service and return its content
    without exposing that service or redirecting the client to it. Synchronous
    functions run in a worker thread so a slow internal request does not block
    the server event loop.

4.  **Run Server**:

    ```bash
    uv run uvicorn main:app --host 0.0.0.0 --port 8000
    ```

5.  **Access Links**:
    ```
    http://<server-ip>:8000/<key>?key=<access_key>
    ```
    Example: `http://localhost:8000/dynamic_example?key=your-secret-key`

## Logs

Access logs are saved to `access.log`.
