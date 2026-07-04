"""
run.py — Module 5 Flask entry point
Development server runner. Use gunicorn for production.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5005,
        debug=True,
    )
