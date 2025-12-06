// Map load (pulling up the map)
const map = L.map('map').setView([27.7172, 85.3240], 13);   // initial view (can tweak later)

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    // basic attribution, nothing fancy
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


//User Location (tracking user pos)
let userMarker = null; 
let userLat = 27.7172;   // default fallback coords
let userLng = 85.3240;

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {

        userLat = pos.coords.latitude;
        userLng = pos.coords.longitude;

        map.setView([userLat, userLng], 15);   // move map to user

        userMarker = L.marker([userLat, userLng]).addTo(map)
            .bindPopup('You are here')
            .openPopup();

    }, err => {
        // random console note (happens sometimes)
        console.error("Couldn't get location:", err);
    });
}



//WebSocket 
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'; // protocol stuffs
const wsUrl = `${protocol}//${window.location.host}/ws`;

const socket = new WebSocket(wsUrl);

socket.onopen = () => {
    document.getElementById('connection-status').style.backgroundColor = '#2a9d8f'; // green
    console.log("WebSocket connected");   // simple log
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleRealtimeUpdate(data);   // passing the payload
};

socket.onclose = () => {
    document.getElementById('connection-status').style.backgroundColor = '#e63946'; // red
    console.log("ws closed");
};



// Fetching history on load 
async function fetchAlertHistory() {
    try {
        const res = await fetch('/api/alerts');

        if (res.ok) {
            const alerts = await res.json();

            alerts.forEach(alert => {
                const type = alert.type;
                let data = {};   // will fill this below

                // a bit messy but works fine
                if (type === 'noise_warning') {

                    const level = parseFloat(alert.message.split(':')[1]);
                    data = {
                        title: `${level.toFixed(1)} dB Detected`,
                        message: alert.message,
                        level: level,
                        lat: alert.lat,
                        lng: alert.lng,
                        created_at: alert.created_at
                    };

                    addIoTAlertToFeed(data, false);

                } else if (type === 'pet_missing') {
                    data = {
                        pet_name: "Tommy",   // history doesn't keep full info
                        message: alert.message,
                        lat: alert.lat,
                        lng: alert.lng
                    };

                    addPetAlertToFeed(data);

                } else {
                    data = {
                        title: 'Emergency Alert',
                        message: alert.message,
                        lat: alert.lat,
                        lng: alert.lng
                    };

                    addAlertToFeed(data, type);
                }

                addMarkerToMap(data, type);
            });
        }

    } catch (e) {
        console.error("History load failed:", e);   // happens if backend isn't running
    }
}

// fetchAlertHistory();   // disabled for now


//Handle realtime incoming data 
function handleRealtimeUpdate(payload) {
    const { type, data } = payload;

    // probably should refactor later but it's fine for now
    if (type === 'incident' || type === 'sos') {
        addMarkerToMap(data, type);
        addAlertToFeed(data, type);

        if (type === 'sos') playAlertSound();

    } else if (type === 'noise_warning') {

        addMarkerToMap(data, type);
        addIoTAlertToFeed(data);
        playAlertSound(); // maybe separate sound later

    } else if (type === 'pet_update') {

        updatePetMarker(data);

    } else if (type === 'pet_missing') {

        addPetAlertToFeed(data);
        playAlertSound();
    }
}



// Pet Tracking
let petMarker = null;
let safeCircle = null;

const dogIcon = L.divIcon({
    className: 'custom-div-icon',
    html: "<div style='background-color:#3388ff;width:12px;height:12px;border-radius:50%;border:2px solid white;'></div><div style='font-size:20px;position:absolute;top:-15px;left:-5px;'>🐶</div>",
    iconSize: [30, 42],
    iconAnchor: [15, 42]
});


function updatePetMarker(data) {

    if (!petMarker) {

        petMarker = L.marker([data.lat, data.lng], { icon: dogIcon })
            .addTo(map)
            .bindPopup(`${data.pet_name} (${data.breed})`);

        // draw safe zone circle
        safeCircle = L.circle([data.home_lat, data.home_lng], {
            color: 'green',
            fillColor: '#90EE90',
            fillOpacity: 0.2,
            radius: data.radius
        }).addTo(map);

    } else {
        petMarker.setLatLng([data.lat, data.lng]);  // simple update
    }

    if (!data.is_safe) {
        safeCircle.setStyle({ color: 'red', fillColor: '#f03' }); // red highlight
    }
}



// Marker drawing 
function addMarkerToMap(data, type) {
    const color = (type === 'sos') ? 'red' : 'orange';

    const marker = L.circleMarker([data.lat, data.lng], {
        color,
        fillColor: color,
        fillOpacity: 0.5,
        radius: 10
    }).addTo(map);

    marker.bindPopup(`<b>${type.toUpperCase()}</b><br>${data.title || data.message}`);
}



//Alerts UI Rendering 
function addAlertToFeed(data, type) {
    const feed = document.getElementById('alerts-feed');
    const empty = feed.querySelector('.empty-state');
    if (empty) empty.remove();

    const card = document.createElement('div');
    card.className = `alert-card ${type}`;

    const time = new Date().toLocaleTimeString();

    card.innerHTML = `
        <div class="alert-header">
            <span class="alert-type">${type.toUpperCase()}</span>
            <span class="alert-time">${time}</span>
        </div>
        <div class="alert-title">${data.title || 'Emergency Alert'}</div>
        <div class="alert-desc">${data.description || data.message}</div>
    `;

    feed.prepend(card);
}



function addIoTAlertToFeed(data) {
    const feed = document.getElementById('iot-feed');
    const empty = feed.querySelector('.empty-state');
    if (empty) empty.remove();

    const card = document.createElement('div');
    card.className = 'alert-card noise-warning';

    const time = new Date().toLocaleTimeString();

    card.innerHTML = `
        <div class="alert-header">
            <span class="alert-type">NOISE ALERT</span>
            <span class="alert-time">${time}</span>
        </div>
        <div class="alert-title">${data.level ? data.level.toFixed(1) : 'High'} dB Detected</div>
        <div class="alert-desc">
            Noise detected! Kindly keep the volume down.
            <br><span style="font-size:0.8em;opacity:0.8">${data.message}</span>
        </div>
        <div class="iot-meta">Source: IoT Sensor</div>
    `;

    feed.prepend(card);
}



function addPetAlertToFeed(data) {
    const feed = document.getElementById('pet-feed');
    const empty = feed.querySelector('.empty-state');
    if (empty) empty.remove();

    const card = document.createElement('div');
    card.className = 'alert-card pet-missing';

    const time = new Date().toLocaleTimeString();

    card.innerHTML = `
        <div class="alert-header">
            <span class="alert-type">PET MISSING</span>
            <span class="alert-time">${time}</span>
        </div>
        <div class="alert-title">Missing: ${data.pet_name}</div>
        <div class="alert-desc">${data.message}</div>
        <div class="iot-meta">Tracker Alert</div>
    `;

    feed.prepend(card);
}



// the sound alertt
function playAlertSound() {
    // simple vibration for now, sound can be added later
    if (navigator.vibrate) {
        navigator.vibrate([500, 200, 500]);
    }
}



// the SOS button
const sosBtn = document.getElementById('sos-btn');

sosBtn.addEventListener('click', () => {
    if (confirm("Send SOS alert?")) sendSOS();
});


async function sendSOS() {
    const payload = {
        message: "SOS! I need help!",
        type: "sos",
        lat: userLat,
        lng: userLng,
        sender_id: 1   // mock for now
    };

    try {
        const res = await fetch('/api/sos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) alert("SOS Sent!");
        else alert("Failed to send SOS");

    } catch (err) {
        console.error("SOS error:", err);
    }
}



//Incident modall
map.on('click', (e) => {
    const { lat, lng } = e.latlng;
    showIncidentModal(lat, lng);
});

const modal = document.getElementById('incident-modal');
const form = document.getElementById('incident-form');
let currentReportCoords = null;

function showIncidentModal(lat, lng) {
    currentReportCoords = { lat, lng };
    modal.classList.remove('hidden');
}

document.getElementById('cancel-report').addEventListener('click', () => {
    modal.classList.add('hidden');
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('incident-title').value;
    const desc  = document.getElementById('incident-desc').value;
    const type  = document.getElementById('incident-type').value;
    const isAnon = document.getElementById('is-anonymous').checked;

    const payload = {
        title,
        description: desc,
        type,
        lat: currentReportCoords.lat,
        lng: currentReportCoords.lng,
        is_anonymous: isAnon,
        reporter_id: 1  // temp
    };

    try {
        const res = await fetch('/api/incidents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            modal.classList.add('hidden');
            form.reset();
        }

    } catch (err) {
        console.error("Incident submit failed:", err);
    }
});



//Tab Switchingg
document.querySelectorAll('.tab-btn').forEach(btn => {

    btn.addEventListener('click', () => {

        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.feed-container').forEach(f => f.classList.add('hidden'));

        btn.classList.add('active');

        const tab = btn.dataset.tab;
        let feedId = null;

        if (tab === 'iot') feedId = 'iot-feed';
        else if (tab === 'pet') feedId = 'pet-feed';
        else if (tab === 'alerts') feedId = 'alerts-feed';

        if (feedId) document.getElementById(feedId).classList.remove('hidden');
    });
});



//Simulation Buttons ko
document.getElementById('sim-sound-btn').addEventListener('click', async () => {
    try {
        await fetch('/api/simulate/sound', { method: 'POST' });
        alert("Sound Simulation Started!");
    } catch (e) {
        console.error(e);
        alert("Couldn't start sound simulation");
    }
});

document.getElementById('sim-pet-btn').addEventListener('click', async () => {
    try {
        await fetch('/api/simulate/pet', { method: 'POST' });
        alert("Pet Simulation Started!");
    } catch (e) {
        console.error(e);
        alert("Couldn't start pet simulation");
    }
});
