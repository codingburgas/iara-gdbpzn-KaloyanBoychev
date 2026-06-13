
import os
from app import create_app, db

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Imports available automatically in 'flask shell'."""
    from app.models.user import User
    from app.models.crew import Crew, Shift
    from app.models.vehicle import Vehicle
    from app.models.incident import Incident
    from app.models.task import Task
    from app.models.message import Message, SOSAlert
    return {
        'db': db,
        'User': User,
        'Crew': Crew,
        'Shift': Shift,
        'Vehicle': Vehicle,
        'Incident': Incident,
        'Task': Task,
        'Message': Message,
        'SOSAlert': SOSAlert,
    }


if __name__ == '__main__':
    app.run()