# app/blueprints/chat/__init__.py
"""
Chat blueprint — incident-scoped messaging with text, templates,
and image attachments. Real-time delivery happens via SocketIO
(see app/socket_events.py); this blueprint handles the HTTP side:
image upload and the initial message history load.
"""

import os
import uuid
from flask import Blueprint, jsonify, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db, socketio
from app.models.incident import Incident
from app.models.message import Message, MessageType
from app import csrf
chat_bp = Blueprint('chat', __name__)


def _allowed_file(filename: str) -> bool:
    """Check the file extension against the configured allow-list."""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_IMAGE_EXTENSIONS']


@chat_bp.route('/incident/<int:incident_id>/messages')
@login_required
def message_history(incident_id):
    """
    Returns the full chat history for an incident as JSON.
    Called once when the chat panel first loads; SocketIO handles
    everything sent after that point.
    """
    incident = db.session.get(Incident, incident_id)
    if incident is None:
        abort(404)

    messages = Message.query.filter_by(incident_id=incident_id) \
                             .order_by(Message.sent_at.asc()).all()

    return jsonify([
        {
            'id': m.id,
            'content': m.content,
            'message_type': m.message_type.value,
            'image_path': m.image_path,
            'sender_id': m.sender_id,
            'sender_name': m.sender.full_name if m.sender else 'System',
            'sent_at': m.sent_at.isoformat(),
        }
        for m in messages
    ])


@chat_bp.route('/incident/<int:incident_id>/upload-image', methods=['POST'])
@csrf.exempt
@login_required


def upload_image(incident_id):
    """
    Handles an image attachment upload via standard HTTP POST
    (multipart/form-data) — SocketIO doesn't carry binary files well,
    so images go through this regular endpoint, then we broadcast
    the resulting message over SocketIO afterward.
    """
    incident = db.session.get(Incident, incident_id)
    if incident is None:
        abort(404)

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not _allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Generate a unique filename to avoid collisions between users
    ext = file.filename.rsplit('.', 1)[-1].lower()
    unique_name = f"inc{incident_id}_{uuid.uuid4().hex[:10]}.{ext}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)

    file.save(filepath)

    # Store the relative path (relative to static/) for use in templates
    relative_path = f"uploads/{unique_name}"

    message = Message(
        message_type=MessageType.IMAGE,
        image_path=relative_path,
        sender_id=current_user.id,
        incident_id=incident_id,
    )
    db.session.add(message)
    db.session.commit()

    # Broadcast to everyone currently viewing this incident
    socketio.emit('new_chat_message', {
        'id': message.id,
        'content': None,
        'message_type': 'image',
        'image_path': relative_path,
        'sender_id': current_user.id,
        'sender_name': current_user.full_name,
        'sent_at': message.sent_at.isoformat(),
    }, room=f'incident_{incident_id}')

    return jsonify({'success': True, 'image_path': relative_path})