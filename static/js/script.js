// Configuration
const CONFIG = {
    refreshInterval: 30000,
    plotlyConfig: {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
    },
    colors: {
        eth: '#627EEA',
        bnb: '#F3BA2F',
        sol: '#00FFA3'
    }
};

// Gestionnaire principal du dashboard
class BlockchainDashboard {
    constructor() {
        this.initializeEventListeners();
        this.startAutoRefresh();
    }

    initializeEventListeners() {
        document.querySelectorAll('.time-range-selector button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleTimeRangeChange(e);
            });
        });

        document.querySelectorAll('.parameter-toggle').forEach(toggle => {
            toggle.addEventListener('change', () => {
                this.updateVisibility(toggle.id, toggle.checked);
                this.updateDashboard();
            });
        });

        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.updateCardData(card.dataset.crypto);
            });
        });
    }

    updateVisibility(toggleId, isVisible) {
        const elements = {
            'priceToggle': '.price-data',
            'volumeToggle': '.volume-data',
            'tpsToggle': '.tps-data'
        };

        if (elements[toggleId]) {
            document.querySelectorAll(elements[toggleId]).forEach(el => {
                el.style.display = isVisible ? 'block' : 'none';
            });
        }
    }

    handleTimeRangeChange(event) {
        document.querySelector('.time-range-selector button.active').classList.remove('active');
        event.target.classList.add('active');
        this.updateDashboard();
    }

    async updateDashboard() {
        try {
            const timeRange = document.querySelector('.time-range-selector button.active').dataset.range;
            const response = await fetch(`/get_data?timeRange=${timeRange}`);
            const data = await response.json();

            this.updateCharts(data);
            this.updateStats(data.stats);
            this.updateCards(data.stats);
        } catch (error) {
            console.error('Erreur lors de la mise à jour du dashboard:', error);
            this.showError('Erreur de mise à jour des données');
        }
    }

    updateCharts(data) {
        try {
            Plotly.newPlot('comparison-chart', 
                JSON.parse(data.comparison).data, 
                JSON.parse(data.comparison).layout,
                CONFIG.plotlyConfig
            );

            Plotly.newPlot('eth-chart', 
                JSON.parse(data.eth_specific).data, 
                JSON.parse(data.eth_specific).layout,
                CONFIG.plotlyConfig
            );

            if (data.correlations) {
                this.updateCorrelationDisplay(data.correlations);
            }
        } catch (error) {
            console.error('Erreur lors de la mise à jour des graphiques:', error);
        }
    }

    updateStats(stats) {
        const updates = {
            'eth-gas': `${stats.eth_gas} Gwei`,
            'bnb-fee': `${stats.bnb_price} BNB`,
            'sol-tps': `${stats.sol_tps} TPS`,
            'total-tps': `${stats.total_tps} TPS`
        };

        Object.entries(updates).forEach(([id, value]) => {
            const element = document.querySelector(`#${id} .value`);
            if (element) {
                element.textContent = value;
                this.animateValue(element);
            }
        });
    }

    updateCards(stats) {
        const cardUpdates = {
            'eth-price': `${stats.eth_gas} Gwei`,
            'bnb-price': `${stats.bnb_price} BNB`,
            'sol-price': `${stats.sol_tps} TPS`
        };

        Object.entries(cardUpdates).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    updateCorrelationDisplay(correlations) {
        if (document.getElementById('correlation-display')) {
            const correlationText = `
                ETH Volume Correlation: ${(correlations.eth_volume_correlation * 100).toFixed(2)}%
                BNB Volume Correlation: ${(correlations.bnb_volume_correlation * 100).toFixed(2)}%
                SOL Volume Correlation: ${(correlations.sol_volume_correlation * 100).toFixed(2)}%
            `;
            document.getElementById('correlation-display').textContent = correlationText;
        }
    }

    animateValue(element) {
        element.style.animation = 'none';
        element.offsetHeight; // Trigger reflow
        element.style.animation = 'fadeIn 0.5s ease-out';
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 3000);
    }

    startAutoRefresh() {
        this.updateDashboard();
        setInterval(() => this.updateDashboard(), CONFIG.refreshInterval);
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    new BlockchainDashboard();
});