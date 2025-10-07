from app import create_app

app = create_app()

if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))

    logger.info(f"🚀 Serveur Flask lancé sur http://127.0.0.1:{port}")
    app.run(debug=True, port=port)
