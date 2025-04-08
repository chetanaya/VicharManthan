#!/usr/bin/env python3

import importlib.util
import os
import platform
import shutil
import subprocess
import sys
import time

# Check if psycopg2 is available without importing it
PSYCOPG2_AVAILABLE = importlib.util.find_spec("psycopg2") is not None


def find_executable(cmd):
    """Find the full path to an executable to avoid partial path issues."""
    return shutil.which(cmd)


def is_docker_installed():
    """Check if Docker is installed on the system."""
    try:
        docker_path = find_executable("docker")
        if not docker_path:
            return False
        subprocess.run(
            [docker_path, "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def is_docker_running():
    """Check if Docker is running."""
    try:
        docker_path = find_executable("docker")
        if not docker_path:
            return False
        result = subprocess.run(
            [docker_path, "info"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return True
    except subprocess.SubprocessError:
        return False


def start_docker_desktop():
    """Start Docker Desktop on macOS."""
    system = platform.system().lower()
    if system == "darwin":  # macOS
        try:
            print("Starting Docker Desktop on macOS...")
            open_path = find_executable("open")
            if not open_path:
                print("Could not find 'open' command.")
                return False

            docker_app_path = "/Applications/Docker.app"
            if not os.path.exists(docker_app_path):
                print(f"Docker Desktop not found at {docker_app_path}")
                return False

            subprocess.run(
                [open_path, docker_app_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for Docker to start (with timeout)
            max_attempts = 15  # 15 * 2 seconds = 30 seconds timeout
            attempts = 0
            while attempts < max_attempts:
                if is_docker_running():
                    print("Docker Desktop started successfully.")
                    return True
                print("Waiting for Docker to start...")
                time.sleep(2)
                attempts += 1

            print("Docker Desktop failed to start within the timeout period.")
            return False
        except subprocess.SubprocessError as e:
            print(f"Failed to start Docker Desktop: {e}")
            return False
    elif system == "windows":
        print("Please start Docker Desktop manually on Windows.")
        return False
    elif system == "linux":
        try:
            print("Starting Docker service on Linux...")
            systemctl_path = find_executable("systemctl")
            if not systemctl_path:
                print("Could not find 'systemctl' command.")
                return False

            # Use sudo only if not running as root
            if os.geteuid() != 0:
                sudo_path = find_executable("sudo")
                if not sudo_path:
                    print("Could not find 'sudo' command and not running as root.")
                    return False
                cmd = [sudo_path, systemctl_path, "start", "docker"]
            else:
                cmd = [systemctl_path, "start", "docker"]

            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print("Docker service started successfully.")
            return True
        except subprocess.SubprocessError as e:
            print(f"Failed to start Docker service: {e}")
            return False
    else:
        print(f"Unsupported operating system: {system}")
        return False


def install_docker():
    """Install Docker based on the operating system."""
    system = platform.system().lower()

    if system == "linux":
        print("Installing Docker on Linux...")
        print("For security reasons, automatic installation is disabled.")
        print("Please install Docker following the official documentation:")
        print("https://docs.docker.com/engine/install/")
        return False
    elif system == "darwin":  # macOS
        print("Installing Docker on macOS...")
        print(
            "Please download and install Docker Desktop from https://www.docker.com/products/docker-desktop"
        )
        print("After installing, please run this script again.")
        return False
    elif system == "windows":
        print("Installing Docker on Windows...")
        print(
            "Please download and install Docker Desktop from https://www.docker.com/products/docker-desktop"
        )
        print("After installing, please run this script again.")
        return False
    else:
        print(f"Unsupported operating system: {system}")
        return False


def is_image_pulled(image_name):
    """Check if a Docker image is already pulled."""
    docker_path = find_executable("docker")
    if not docker_path:
        return False
    result = subprocess.run(
        [docker_path, "images", "-q", image_name],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return bool(result.stdout.strip())


def pull_docker_image(image_name):
    """Pull a Docker image."""
    try:
        docker_path = find_executable("docker")
        if not docker_path:
            print("Docker command not found.")
            return False

        print(f"Pulling Docker image: {image_name}...")
        subprocess.run([docker_path, "pull", image_name], check=True)
        print(f"Successfully pulled {image_name}")
        return True
    except subprocess.SubprocessError as e:
        print(f"Failed to pull Docker image: {e}")
        return False


def is_container_running(container_name):
    """Check if a container is already running."""
    docker_path = find_executable("docker")
    if not docker_path:
        return False
    result = subprocess.run(
        [docker_path, "ps", "-q", "-f", f"name={container_name}"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return bool(result.stdout.strip())


def run_pgvector_container(container_name, db_user, db_password, db_name, port):
    """Run PostgreSQL with pgvector container."""
    try:
        docker_path = find_executable("docker")
        if not docker_path:
            return False, "Docker command not found."

        if is_container_running(container_name):
            print(f"Container {container_name} is already running.")
            return True, None

        # Check if container exists but is not running
        result = subprocess.run(
            [docker_path, "ps", "-a", "-q", "-f", f"name={container_name}"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        if result.stdout.strip():
            print(f"Starting existing container {container_name}...")
            subprocess.run([docker_path, "start", container_name], check=True)
            return True, None

        print(f"Creating and running new container: {container_name}...")
        cmd = [
            docker_path,
            "run",
            "-e",
            f"POSTGRES_USER={db_user}",
            "-e",
            f"POSTGRES_PASSWORD={db_password}",
            "-e",
            f"POSTGRES_DB={db_name}",
            "-e",
            "PGDATA=/var/lib/postgresql/data/pgdata",
            "-v",
            "pgvolume:/var/lib/postgresql/data",
            "--name",
            container_name,
            "-p",
            f"{port}:5432",
            "-d",
            "agnohq/pgvector:16",
        ]
        process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Container {container_name} is now running.")

        # Wait a moment for the container to fully initialize
        print("Waiting for PostgreSQL to start...")
        time.sleep(5)
        return True, None
    except subprocess.SubprocessError as e:
        error_log = f"Failed to run container: {e}\n"
        if hasattr(e, "stderr") and e.stderr:
            error_log += f"Error details: {e.stderr}"
        print(error_log)
        return False, error_log


def test_connection(
    db_name, db_user, db_password, host="localhost", port=5432, max_attempts=5
):
    """Test the connection to the PostgreSQL database."""
    if not PSYCOPG2_AVAILABLE:
        return False, "psycopg2 module is not available"

    attempt = 0
    error_logs = []
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(
                dbname=db_name, user=db_user, password=db_password, host=host, port=port
            )
            conn.close()
            print("Successfully connected to the database.")
            return True, None
        except psycopg2.OperationalError as e:
            attempt += 1
            error_msg = f"Connection attempt {attempt} failed: {e}"
            error_logs.append(error_msg)
            print(error_msg)
            if attempt < max_attempts:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                final_error = (
                    "Max connection attempts reached. Database might not be ready."
                )
                print(final_error)
                error_logs.append(final_error)
                return False, "\n".join(error_logs)


def enable_pgvector(db_name, db_user, db_password, host="localhost", port=5432):
    """Enable the pgvector extension in the PostgreSQL database."""
    if not PSYCOPG2_AVAILABLE:
        return False, "psycopg2 module is not available"

    try:
        conn = psycopg2.connect(
            dbname=db_name, user=db_user, password=db_password, host=host, port=port
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Verify installation
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            if cur.fetchone():
                print("pgvector extension is successfully installed and enabled.")
                conn.close()
                return True, None
            else:
                error_msg = "Failed to verify pgvector extension installation."
                print(error_msg)
                conn.close()
                return False, error_msg
    except psycopg2.Error as e:
        error_msg = f"Database error: {e}"
        print(error_msg)
        return False, error_msg


def setup_pgvector(
    db_user="ai",
    db_password="ai",
    db_name="ai",
    container_name="pgvector",
    port=5532,
):
    """
    Main function to set up PostgreSQL with pgvector in Docker.

    Args:
        db_user (str): PostgreSQL user name
        db_password (str): PostgreSQL password
        db_name (str): PostgreSQL database name
        container_name (str): Name for the Docker container
        port (int): Port to expose PostgreSQL on the host

    Returns:
        tuple: (bool, str) - (Success status, Error logs if any)
    """
    error_logs = []
    global PSYCOPG2_AVAILABLE

    # Check for psycopg2 installation
    if not PSYCOPG2_AVAILABLE:
        print("Installing psycopg2-binary...")
        try:
            pip_path = sys.executable
            subprocess.run(
                [pip_path, "-m", "pip", "install", "psycopg2-binary"],
                check=True,
                capture_output=True,
                text=True,
            )
            # Check availability again after installation
            PSYCOPG2_AVAILABLE = importlib.util.find_spec("psycopg2") is not None
            if PSYCOPG2_AVAILABLE:
                print("Successfully installed psycopg2-binary")
            else:
                error_msg = "Failed to find psycopg2 module after installation"
                print(error_msg)
                error_logs.append(error_msg)
                return False, "\n".join(error_logs)
        except subprocess.SubprocessError as e:
            error_msg = f"Failed to install psycopg2-binary: {e}"
            print(error_msg)
            error_logs.append(error_msg)
            return False, "\n".join(error_logs)

    # Check if Docker is installed
    if not is_docker_installed():
        print("Docker is not installed.")
        if not install_docker():
            error_msg = "Failed to install Docker. Please install Docker manually."
            error_logs.append(error_msg)
            return False, "\n".join(error_logs)
    else:
        print("Docker is already installed.")

    # Check if Docker is running, and start it if not
    if not is_docker_running():
        print("Docker is installed but not running.")
        if not start_docker_desktop():
            error_msg = "Docker is installed but not running. Please start Docker Desktop manually."
            error_logs.append(error_msg)
            return False, "\n".join(error_logs)

    # Pull pgvector image if needed
    image_name = "agnohq/pgvector:16"
    if not is_image_pulled(image_name):
        if not pull_docker_image(image_name):
            error_msg = f"Failed to pull Docker image {image_name}."
            error_logs.append(error_msg)
            return False, "\n".join(error_logs)
    else:
        print(f"Docker image {image_name} is already pulled.")

    # Run container
    success, error = run_pgvector_container(
        container_name, db_user, db_password, db_name, port
    )
    if not success:
        error_logs.append(error if error else "Failed to run PGVector container.")
        return False, "\n".join(error_logs)

    # Test connection
    success, error = test_connection(db_name, db_user, db_password, port=port)
    if not success:
        error_logs.append(error if error else "Failed to connect to the database.")
        return False, "\n".join(error_logs)

    # Enable pgvector extension
    success, error = enable_pgvector(db_name, db_user, db_password, port=port)
    if not success:
        error_logs.append(error if error else "Failed to enable pgvector extension.")
        return False, "\n".join(error_logs)

    success_msg = f"""
Setup completed successfully!

Connection details:
- Host: localhost
- Port: {port}
- Database: {db_name}
- Username: {db_user}
- Password: {db_password}

You can connect to the database using:
psql -h localhost -U {db_user} -d {db_name} -p {port}

Or from Python:
import psycopg2
conn = psycopg2.connect(
    dbname="{db_name}",
    user="{db_user}",
    password="{db_password}",
    host="localhost",
    port={port}
)
"""
    print(success_msg)
    return True, success_msg


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Set up PostgreSQL with pgvector in Docker"
    )
    parser.add_argument("--user", default="ai", help="PostgreSQL username")
    parser.add_argument("--password", default="ai", help="PostgreSQL password")
    parser.add_argument("--db", default="ai", help="PostgreSQL database name")
    parser.add_argument("--container", default="pgvector", help="Docker container name")
    parser.add_argument(
        "--port", type=int, default=5532, help="Port to expose PostgreSQL"
    )

    args = parser.parse_args()

    success, message = setup_pgvector(
        db_user=args.user,
        db_password=args.password,
        db_name=args.db,
        container_name=args.container,
        port=args.port,
    )

    if not success:
        print("\nSetup failed. Error details:")
        print(message)
        sys.exit(1)
