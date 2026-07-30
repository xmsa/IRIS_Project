from core import cli
from core.logger import app_logger


def main() -> None:
    """Main entry point for the iris project."""
    app_logger.info("Hello from iris-project!")


if __name__ == "__main__":
    main()
    cli()
