from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from loguru import logger

# Configure logging
logger.add("access.log", rotation="1 week", retention="1 month", level="INFO")

app = FastAPI(
    title="LinkRedirect",
    description="A simple service to manage permanent links.",
    version="0.1.0",
    docs_url=None,  # Disable Swagger UI for security obscuration
    redoc_url=None,
)

CONFIG_FILE = Path("config.yaml")


class ConfigLoader:
    """
    Helper class to load configuration with caching based on file modification time.
    """

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._cache: dict | None = None
        self._last_mtime: float = 0
        self._routes: dict[str, str] = {}
        self._access_key: str | None = None

    def get_config(self) -> tuple[dict[str, str], str | None]:
        """
        Returns the current routes mapping and access key.
        Reloads the config if the file has been modified.
        """
        try:
            current_mtime = self.config_path.stat().st_mtime
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            return {}, None

        if current_mtime > self._last_mtime:
            self._load_config(current_mtime)

        return self._routes, self._access_key

    def _load_config(self, mtime: float):
        """Loads and parses the YAML configuration file."""
        try:
            logger.info("Reloading configuration...")
            with open(self.config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if not config:
                logger.warning("Config file is empty.")
                self._routes = {}
                self._access_key = None
            else:
                self._routes = config.get("routes", {})
                self._access_key = config.get("security", {}).get("access_key")
                logger.info(f"Loaded {len(self._routes)} routes.")

            self._last_mtime = mtime
            self._cache = config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")


# Initialize ConfigLoader
config_loader = ConfigLoader(CONFIG_FILE)


@app.get("/")
async def root():
    """Root endpoint. Returns 404 to avoid leaking information."""
    raise HTTPException(status_code=404, detail="Not Found")


@app.get("/{path_key}")
async def redirect_to_url(path_key: str, key: str = Query(None)):
    """
    Redirects to the target URL associated with the given path_key.
    Requires a valid access key.
    """
    routes, valid_access_key = config_loader.get_config()

    # 1. Check Access Key
    if not valid_access_key:
        logger.error("No access key configured in config.yaml!")
        raise HTTPException(status_code=500, detail="Server Configuration Error")

    if key != valid_access_key:
        logger.warning(f"Unauthorized access attempt for '{path_key}' with key='{key}'")
        raise HTTPException(status_code=403, detail="Forbidden")

    # 2. Check Route
    target_url = routes.get(path_key)

    if target_url:
        logger.info(f"Redirecting key '{path_key}' to '{target_url}'")
        return RedirectResponse(url=target_url, status_code=307)

    logger.warning(f"Key not found: '{path_key}'")
    raise HTTPException(status_code=404, detail="Not Found")
