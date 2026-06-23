
# run.py
import os
from app import create_app, db, socketio

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
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
    # IMPORTANT: use socketio.run(), NOT app.run(), from this point onward.
    # This correctly initializes the WebSocket layer for real-time features.
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)