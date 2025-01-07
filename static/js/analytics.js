// static/js/analytics.js

document.addEventListener('DOMContentLoaded', function() {
    // Configuration de base pour tous les graphiques
    const baseChartConfig = {
        responsive: true,
        displayModeBar: false,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#fff' },
        margin: { t: 30, r: 20, l: 40, b: 40 },
        xaxis: {
            gridcolor: 'rgba(255,255,255,0.1)',
            linecolor: 'rgba(255,255,255,0.2)'
        },
        yaxis: {
            gridcolor: 'rgba(255,255,255,0.1)',
            linecolor: 'rgba(255,255,255,0.2)'
        }
    };
 
    // Gas Price Analysis Chart
    function initGasPriceChart() {
        const trace1 = {
            x: generateTimeData(24),
            y: generateRandomData(24, 30, 100),
            type: 'scatter',
            mode: 'lines',
            name: 'ETH Gas',
            line: {
                color: '#627EEA',
                width: 2
            }
        };
 
        const trace2 = {
            x: generateTimeData(24),
            y: generateRandomData(24, 5, 15),
            type: 'scatter',
            mode: 'lines',
            name: 'BNB Gas',
            line: {
                color: '#F3BA2F',
                width: 2
            }
        };
 
        Plotly.newPlot('gasPriceChart', [trace1, trace2], {
            ...baseChartConfig,
            title: { text: 'Prix du Gas en temps réel', font: { color: '#fff' } }
        });
    }
 
    // Transaction Volume Chart
    function initVolumeChart() {
        const trace = {
            x: generateTimeData(24),
            y: generateRandomData(24, 1000, 5000),
            type: 'bar',
            marker: {
                color: '#8B5CF6',
                opacity: 0.6
            },
            name: 'Volume'
        };
 
        Plotly.newPlot('volumeChart', [trace], {
            ...baseChartConfig,
            title: { text: 'Volume des Transactions', font: { color: '#fff' } },
            barmode: 'group'
        });
    }
 
    // Gas Usage Patterns Chart
    function initGasPatternChart() {
        const hours = Array.from({length: 24}, (_, i) => i);
        const trace = {
            x: hours,
            y: generateRandomData(24, 20, 100),
            type: 'scatter',
            mode: 'lines+markers',
            line: {
                color: '#EC4899',
                shape: 'spline'
            },
            marker: {
                size: 6,
                color: '#EC4899'
            }
        };
 
        Plotly.newPlot('gasPatternChart', [trace], {
            ...baseChartConfig,
            title: { text: 'Patterns d\'utilisation du Gas', font: { color: '#fff' } }
        });
    }
 
    // Fonctions utilitaires
    function generateTimeData(hours) {
        const data = [];
        const now = new Date();
        for (let i = 0; i < hours; i++) {
            const date = new Date(now);
            date.setHours(now.getHours() - i);
            data.unshift(date);
        }
        return data;
    }
 
    function generateRandomData(count, min, max) {
        return Array.from({length: count}, () => 
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    }
 
    // Gestionnaires d'événements pour les filtres
    function setupEventListeners() {
        // Période
        document.querySelectorAll('[data-timerange]').forEach(button => {
            button.addEventListener('click', (e) => {
                // Retirer la classe active de tous les boutons
                document.querySelectorAll('[data-timerange]').forEach(btn => 
                    btn.classList.remove('bg-purple-500/20', 'text-purple-300'));
                
                // Ajouter la classe active au bouton cliqué
                e.target.classList.add('bg-purple-500/20', 'text-purple-300');
                
                // Mettre à jour les graphiques avec la nouvelle période
                updateChartsData(e.target.dataset.timerange);
            });
        });
 
        // Blockchain
        document.querySelectorAll('[data-blockchain]').forEach(button => {
            button.addEventListener('click', (e) => {
                // Toggle de la sélection
                e.target.classList.toggle('bg-purple-500/20');
                
                // Mettre à jour les graphiques avec les blockchains sélectionnées
                updateChartsByBlockchain();
            });
        });
    }
 
    function updateChartsData(timeRange) {
        // Logique de mise à jour selon la période sélectionnée
        const hours = timeRange === '24h' ? 24 : 
                     timeRange === '7d' ? 168 : 
                     timeRange === '30d' ? 720 : 8760;
 
        // Mettre à jour chaque graphique
        updateGasPriceChart(hours);
        updateVolumeChart(hours);
        updateGasPatternChart(hours);
    }
 
    function updateChartsByBlockchain() {
        // Mettre à jour les graphiques selon les blockchains sélectionnées
        const selectedBlockchains = Array.from(document.querySelectorAll('[data-blockchain].bg-purple-500\\/20'))
            .map(btn => btn.dataset.blockchain);
 
        // Mettre à jour les graphiques avec les données filtrées
        updateChartsWithBlockchains(selectedBlockchains);
    }
 
    // Initialisation
    function init() {
        initGasPriceChart();
        initVolumeChart();
        initGasPatternChart();
        setupEventListeners();
    }
 
    init();
 });