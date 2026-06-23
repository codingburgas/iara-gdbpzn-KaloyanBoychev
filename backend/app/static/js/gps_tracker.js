// app/static/js/gps_tracker.js
// Automatically broadcasts the firefighter's GPS position every 15 seconds
// while the mobile dashboard is open. Loaded only on operations/mobile_dashboard.html.

(function () {
    if (!navigator.geolocation) {
        console.warn('[GPS] Geolocation not supported on this device/browser.');
        return;
    }

    function sendPosition() {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const socket = window.gdpSocket || io();
                socket.emit('gps_update', {
                    latitude: pos.coords.latitude,
                    longitude: pos.coords.longitude,
                });
            },
            (err) => console.warn('[GPS] Could not get position:', err.message),
            { enableHighAccuracy: true, timeout: 10000 }
        );
    }

    // Send immediately on load, then every 15 seconds
    sendPosition();
    setInterval(sendPosition, 15000);
})();