document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const emailInput = document.getElementById('emailInput');
    const resultContainer = document.getElementById('resultContainer');
    const verdictBadge = document.getElementById('verdictBadge');
    const confidenceVal = document.getElementById('confidenceVal');
    const riskBar = document.getElementById('riskBar');
    const accuracyVal = document.getElementById('accuracyVal');
    
    let cmChartInstance = null;

    // Fetch and display model baseline metrics on dashboard startup
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            accuracyVal.textContent = `${(data.accuracy * 100).toFixed(2)}%`;
            renderConfusionMatrix(data.confusion_matrix);
        })
        .catch(err => console.error("Error loading analytical metrics:", err));

    // Analyze Click handler
    analyzeBtn.addEventListener('click', () => {
        const text = emailInput.value.trim();
        if (!text) return alert("Please input email text to classify.");

        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analyzing Pipeline...";

        fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email_text: text })
        })
        .then(res => res.json())
        .then(data => {
            verdictBadge.className = 'badge ' + data.prediction.toLowerCase();
            verdictBadge.textContent = data.prediction;
            confidenceVal.textContent = `${(data.confidence * 100).toFixed(1)}%`;
            
            // Render risk percentage
            const riskPct = (data.risk_score * 100).toFixed(0);
            riskBar.style.width = `${riskPct}%`;
            riskBar.style.backgroundColor = data.prediction === 'Phishing' ? '#ef4444' : '#22c55e';
            
            resultContainer.classList.remove('hidden');
        })
        .catch(err => alert("Prediction server error."))
        .finally(() => {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "Run Detection Analysis";
        });
    });

    // Render Matrix breakdown via Chart.js
    function renderConfusionMatrix(matrix) {
        const ctx = document.getElementById('cmChart').getContext('2d');
        // Flattened matrix metrics: [[TN, FP], [FN, TP]]
        const flatData = [matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1]];

        cmChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['True Safe (TN)', 'False Phishing (FP)', 'False Safe (FN)', 'True Phishing (TP)'],
                datasets: [{
                    label: 'Classified Sample Counts',
                    data: flatData,
                    backgroundColor: ['#22c55e', '#f59e0b', '#f43f5e', '#3b82f6'],
                    borderWidth: 0,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#334155' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }
});