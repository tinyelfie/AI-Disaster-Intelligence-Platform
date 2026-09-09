// Initialize Map
const map = L.map('map').setView([20, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap'
}).addTo(map);

// Fetch recent disasters and plot on map
async function fetchDisasters() {
    try {
        const res = await fetch('http://localhost:8000/disasters');
        const data = await res.json();
        
        data.data.forEach(d => {
            if (d.latitude && d.longitude) {
                L.marker([d.latitude, d.longitude]).addTo(map)
                    .bindPopup(`<b>${d.disaster_type}</b><br>${d.country}<br>${d.date}`);
            }
        });
    } catch (err) {
        console.error('Error fetching disasters:', err);
    }
}

fetchDisasters();

async function runPredictions() {
    const resultsDiv = document.getElementById('prediction-results');
    resultsDiv.innerHTML = "<i>Running predictions...</i>";
    
    setTimeout(() => {
        resultsDiv.innerHTML = `
            <p>Satellite: Flood (85%)</p>
            <p>NLP: High Urgency</p>
            <p>Forecast: 0.75 Risk</p>
            <p><strong>Severity: HIGH</strong></p>
        `;
    }, 1000);
}

async function generateReport() {
    const reportDiv = document.getElementById('report-output');
    reportDiv.innerHTML = "<i>Generating report via Gemini API...</i>";
    
    try {
        const res = await fetch('http://localhost:8000/situation-report', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                region: "California",
                severity: "HIGH",
                disaster_type: "Wildfire"
            })
        });
        const data = await res.json();
        reportDiv.innerHTML = data.report;
    } catch (err) {
        reportDiv.innerHTML = `<span style="color:red">Failed to generate report. Make sure backend is running.</span>`;
        console.error(err);
    }
}
