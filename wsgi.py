"""Used by unicorn to start dash app."""

from app import server as application

if __name__ == "__main__":
    application.run()
