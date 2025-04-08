import subprocess

import psycopg2

from utils.setup_pgvector import setup_pgvector


def check_pgvector_status(config):
    """
    Check if pgvector is installed and running.

    Args:
        config: The pgvector configuration dict

    Returns:
        dict: Status information with keys 'docker_running', 'db_connectable', 'extension_enabled'
    """
    status = {
        "docker_running": False,
        "db_connectable": False,
        "extension_enabled": False,
    }

    # Check if Docker container is running
    try:
        container_name = config.get("container_name", "pgvector")
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", f"name={container_name}"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
            stderr=subprocess.PIPE,
        )
        status["docker_running"] = bool(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        # Docker might not be installed or accessible
        pass

    # Check if database is connectable
    try:
        conn = psycopg2.connect(
            dbname=config.get("db_name", "ai"),
            user=config.get("db_user", "ai"),
            password=config.get("db_password", "ai"),
            host=config.get("host", "localhost"),
            port=config.get("port", 5532),
            connect_timeout=3,  # Short timeout for quick check
        )
        status["db_connectable"] = True

        # Check if pgvector extension is enabled
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            status["extension_enabled"] = bool(cur.fetchone())

        conn.close()
    except (psycopg2.Error, Exception):
        # Database connection failed
        pass

    return status


def start_pgvector_setup(config):
    """
    Start the pgvector setup process using the configuration.

    Args:
        config: The pgvector configuration dict

    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        return setup_pgvector(
            db_user=config.get("db_user", "ai"),
            db_password=config.get("db_password", "ai"),
            db_name=config.get("db_name", "ai"),
            container_name=config.get("container_name", "pgvector"),
            port=config.get("port", 5532),
        )
    except Exception as e:
        print(f"Error setting up pgvector: {e}")
        return False
