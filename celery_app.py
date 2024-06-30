from app import create_app, create_celery

# Create an app instance for Celery to use
app = create_app()

# Create Celery instance
celery = create_celery(app)
