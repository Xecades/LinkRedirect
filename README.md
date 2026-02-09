# LinkRedirect

A simple, secure, and permanent link redirection service.

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
        google: "https://google.com"
    ```

3.  **Run Server**:

    ```bash
    uv run uvicorn main:app --host 0.0.0.0 --port 8000
    ```

4.  **Access Links**:
    ```
    http://<server-ip>:8000/<key>?key=<access_key>
    ```
    Example: `http://localhost:8000/google?key=your-secret-key`

## Logs

Access logs are saved to `access.log`.
