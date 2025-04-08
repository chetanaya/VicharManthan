import shutil
import subprocess

import psycopg2


def find_executable(cmd):
    """Find the full path to an executable to avoid partial path issues."""
    return shutil.which(cmd)


def check_docker_container_status(config):
    """
    Check if the Docker container is running.

    Args:
        config (dict): Configuration with container_name

    Returns:
        dict: Status information
    """
    status = {"docker_running": False}

    try:
        docker_path = find_executable("docker")
        if not docker_path:
            return status

        container_name = config.get("container_name", "pgvector")
        # Validate container name to prevent command injection
        if not container_name.isalnum() and not all(
            c in "-_" for c in container_name if not c.isalnum()
        ):
            status["error"] = "Invalid container name"
            return status

        result = subprocess.run(
            [docker_path, "ps", "-q", "-f", f"name={container_name}"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
            stderr=subprocess.PIPE,
        )
        status["docker_running"] = bool(result.stdout.strip())

    except (subprocess.SubprocessError, FileNotFoundError) as e:
        status["error"] = str(e)

    return status


def connect_to_database(config):
    """
    Connect to PostgreSQL database.

    Args:
        config (dict): Database configuration

    Returns:
        tuple: (connection, error_message)
    """
    try:
        conn = psycopg2.connect(
            dbname=config.get("db_name", "ai"),
            user=config.get("db_user", "ai"),
            password=config.get("db_password", "ai"),
            host=config.get("host", "localhost"),
            port=config.get("port", 5532),
        )
        return conn, None
    except psycopg2.Error as e:
        return None, str(e)


def execute_query(conn, query, params=None):
    """
    Execute a query safely with parameters.

    Args:
        conn: PostgreSQL connection
        query (str): SQL query with parameter placeholders
        params (tuple, optional): Query parameters

    Returns:
        tuple: (results, error_message)
    """
    try:
        with conn.cursor() as cur:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)

            # Only fetch if it's a SELECT query
            if query.strip().upper().startswith("SELECT"):
                results = cur.fetchall()
                return results, None
            else:
                conn.commit()
                return None, None
    except psycopg2.Error as e:
        conn.rollback()
        return None, str(e)


def start_container(config):
    """
    Start the PostgreSQL container if it exists but is not running.

    Args:
        config (dict): Configuration with container_name

    Returns:
        tuple: (success, error_message)
    """
    try:
        docker_path = find_executable("docker")
        if not docker_path:
            return False, "Docker command not found"

        container_name = config.get("container_name", "pgvector")
        # Validate container name to prevent command injection
        if not container_name.isalnum() and not all(
            c in "-_" for c in container_name if not c.isalnum()
        ):
            return False, "Invalid container name"

        # Check if container exists but is not running
        result = subprocess.run(
            [docker_path, "ps", "-a", "-q", "-f", f"name={container_name}"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )

        if result.stdout.strip():
            subprocess.run([docker_path, "start", container_name], check=True)
            return True, None
        else:
            return False, "Container not found"

    except subprocess.SubprocessError as e:
        return False, str(e)


def check_pgvector_extension(conn):
    """
    Check if pgvector extension is installed.

    Args:
        conn: PostgreSQL connection

    Returns:
        tuple: (is_installed, error_message)
    """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            return bool(cur.fetchone()), None
    except psycopg2.Error as e:
        return False, str(e)


def create_vector_table(conn, table_name, dim=1536):
    """
    Create a table with vector support.

    Args:
        conn: PostgreSQL connection
        table_name (str): Name of the table to create
        dim (int): Vector dimension

    Returns:
        tuple: (success, error_message)
    """
    # Validate table name to prevent SQL injection
    if not table_name.isalnum() and not all(
        c in "_" for c in table_name if not c.isalnum()
    ):
        return False, "Invalid table name"

    try:
        with conn.cursor() as cur:
            # Create extension if not exists
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # Create table with vector column
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding VECTOR({dim}) NOT NULL
            );
            """
            cur.execute(query)

            # Create index for vector similarity search
            query = f"""
            CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx
            ON {table_name} USING ivfflat (embedding vector_cosine_ops);
            """
            cur.execute(query)

            conn.commit()
            return True, None
    except psycopg2.Error as e:
        conn.rollback()
        return False, str(e)
