import app.tasks  # noqa
import app.models.all  # noqa
# from app.logging import configure_logging

from .conf import WorkerSettings, task

# configure_logging("worker")

__all__ = ["WorkerSettings", "task"]
