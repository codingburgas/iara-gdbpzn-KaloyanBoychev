// app/static/js/main.js
// Global real-time listener — loaded on every authenticated page via base.html

document.addEventListener('DOMContentLoaded', function () {
    if (typeof io === 'undefined') return;


    window.gdpSocket = window.gdpSocket || io();
    const socket = window.gdpSocket;

    socket.on('connect', () => {
        console.log('[SocketIO] Connected');
    });

    // ... rest of the existing listeners stay exactly the same

    // ── New incident assigned to this user's crew ────────────────────────────
    socket.on('new_incident_assigned', (data) => {
        showToast(
            `New Incident: ${data.incident_type.replace('_', ' ').toUpperCase()}`,
            `${data.address}, ${data.city} — Priority: ${data.priority.toUpperCase()}`,
            'danger'
        );
        playNotificationSound();
    });

    // ── SOS alert (only meaningful for ops/admin, but harmless elsewhere) ────
    socket.on('sos_alert_received', (data) => {
        showToast(
            `🆘 SOS ALERT — ${data.firefighter_name}`,
            data.notes || 'Immediate response required.',
            'danger'
        );
        playNotificationSound();
    });

    socket.on('sos_response_confirmed', (data) => {
        showToast(
            'Help is on the way',
            `${data.acknowledged_by} acknowledged your SOS.`,
            'success'
        );
    });
});


/**
 * Displays a Bootstrap-styled toast notification in the top-right corner.
 */
function showToast(title, body, variant) {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = 1080;
        document.body.appendChild(container);
    }

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-bg-${variant} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong><br>${body}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast"></button>
        </div>
    `;
    container.appendChild(toastEl);

    const toast = new bootstrap.Toast(toastEl, { delay: 8000 });
    toast.show();

    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}


/**
 * Plays a short notification beep using the Web Audio API.
 * No external sound file needed.
 */
function playNotificationSound() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = ctx.createOscillator();
        const gain = ctx.createGain();
        oscillator.connect(gain);
        gain.connect(ctx.destination);
        oscillator.frequency.value = 880;
        gain.gain.value = 0.15;
        oscillator.start();
        oscillator.stop(ctx.currentTime + 0.2);
    } catch (e) {
        console.warn('Audio notification unavailable:', e);
    }
}