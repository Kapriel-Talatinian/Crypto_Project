const CONFIG = {
    chartOptions: {
        responsive: true,
        displayModeBar: false,
    }
 };
 
 const state = {
    isDarkMode: true,
    selectedTimeRange: '24h',
    isLive: true,
    refreshInterval: 5000,
    refreshTimer: null,
    previousValues: {
        eth_gas: null,
        bnb_gas: null, 
        sol_tps: null
    }
 };
 
 class CryptoFeeAnalytics {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.startDataRefresh();
    }
 
    init() {
        this.updateAllCharts();
        this.setupTheme();
    }
 
    setupTheme() {
        if (state.isDarkMode) {
            document.documentElement.classList.add('dark');
        }
    }
 
    setupEventListeners() {
        document.querySelectorAll('[data-timerange]').forEach(button => {
            button.addEventListener('click', (e) => {
                document.querySelectorAll('[data-timerange]').forEach(btn => {
                    btn.classList.remove('bg-indigo-600');
                    btn.classList.add('bg-gray-700');
                });
                e.target.classList.remove('bg-gray-700');
                e.target.classList.add('bg-indigo-600');
                
                state.selectedTimeRange = e.target.dataset.timerange;
                this.updateAllCharts();
            });
        });
 
        const refreshSelect = document.getElementById('refreshRate');
        if (refreshSelect) {
            refreshSelect.addEventListener('change', (e) => {
                state.refreshInterval = parseInt(e.target.value);
                this.restartDataRefresh();
                
                const liveIndicator = document.getElementById('liveIndicator');
                if (liveIndicator) {
                    if (state.refreshInterval === 5000) {
                        liveIndicator.classList.add('live-pulse');
                        liveIndicator.textContent = 'Live';
                    } else {
                        liveIndicator.classList.remove('live-pulse');
                        liveIndicator.textContent = state.refreshInterval === 900000 ? '15min' : '1h';
                    }
                }
            });
        }
 
        document.querySelector('#darkModeToggle')?.addEventListener('click', () => {
            this.toggleDarkMode();
        });
    }
 
    async fetchData() {
        try {
            const response = await fetch(`/get_data?timeRange=${state.selectedTimeRange}`);
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
 
            const dashboardData = JSON.parse(data.dashboard);
            return {
                dashboardData,
                stats: data.stats,
                predictions: data.predictions
            };
        } catch (error) {
            console.error('Error fetching data:', error);
            this.showError(error.message);
            return null;
        }
    }
 
    async updateAllCharts() {
        const data = await this.fetchData();
        if (!data) return;
 
        const { dashboardData } = data;
        
        const commonLayout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#fff' },
            xaxis: {
                gridcolor: 'rgba(255,255,255,0.1)',
                zerolinecolor: 'rgba(255,255,255,0.1)'
            },
            yaxis: {
                gridcolor: 'rgba(255,255,255,0.1)',
                zerolinecolor: 'rgba(255,255,255,0.1)'
            },
            showlegend: true,
            legend: { 
                orientation: 'h', 
                font: { color: '#fff' },
                y: 1.1
            },
            margin: { t: 50, r: 10, b: 50, l: 50 }
        };
 
        const chartConfigs = [
            { id: 'mainChart', data: dashboardData.data.slice(0, 3), title: 'Frais en Temps Réel' },
            { id: 'volumeChart', data: dashboardData.data.slice(3, 6), title: 'Volume des Transactions' },
            { id: 'hourlyChart', data: dashboardData.data.slice(9, 12), title: 'Analyse Horaire' },
            { id: 'trendChart', data: dashboardData.data.slice(12, 15), title: 'Tendances des Prix' },
            { id: 'correlationChart', data: dashboardData.data.slice(15, 18), title: 'Corrélation Volume/Prix' }
        ];
 
        chartConfigs.forEach(config => {
            const element = document.getElementById(config.id);
            if (element && config.data) {
                const layout = {
                    ...commonLayout,
                    height: 300,
                    title: {
                        text: config.title,
                        font: { color: '#fff', size: 16 },
                        y: 0.98
                    }
                };
                
                Plotly.newPlot(config.id, config.data, layout, { displayModeBar: false });
            }
        });
 
        this.updateStats(data.stats);
        this.updatePredictions(data.predictions);
        this.updateBestOption(data.predictions);
    }
 
    updateStats(stats) {
        const statsMapping = {
            'eth_gas': { value: stats.eth_gas, max: 200, min: 0 },
            'bnb_gas': { value: stats.bnb_price, max: 100, min: 0 },
            'sol_tps': { value: stats.sol_tps, max: 5000, min: 0 }
        };
    
        Object.entries(statsMapping).forEach(([key, data]) => {
            const valueElement = document.querySelector(`[data-stat="${key}"]`);
            if (valueElement && !isNaN(data.value)) {
                // Mise à jour de la valeur principale
                valueElement.textContent = data.value.toFixed(2);
                valueElement.classList.add('update-flash');
                setTimeout(() => valueElement.classList.remove('update-flash'), 500);
    
                // Calcul du pourcentage de variation
                const trendElement = document.querySelector(`[data-stat="${key}Trend"]`);
                if (trendElement) {
                    if (state.previousValues[key] !== null) {
                        const variation = ((data.value - state.previousValues[key]) / state.previousValues[key]) * 100;
                        const trend = Math.round(variation);
                        trendElement.textContent = `${trend > 0 ? '↑' : '↓'} ${Math.abs(trend)}%`;
                        trendElement.className = `text-${trend > 0 ? 'green' : 'red'}-400`;
                    } else {
                        trendElement.textContent = '0%';
                        trendElement.className = 'text-gray-400';
                    }
                }
    
                // Mise à jour de la valeur précédente
                state.previousValues[key] = data.value;
    
                // Mise à jour de la barre de progression
                const progressBar = valueElement?.parentElement?.parentElement?.nextElementSibling?.querySelector('.bg-indigo-500, .bg-yellow-500, .bg-purple-500');
                if (progressBar) {
                    const percentage = Math.min(Math.max(((data.value - data.min) / (data.max - data.min)) * 100, 0), 100);
                    progressBar.style.width = `${percentage}%`;
                }
            }
        });
    }
 
    updatePredictions(predictions) {
        const predictionContainer = document.getElementById('predictions');
        if (!predictionContainer) return;
 
        const predictionHTML = Object.entries(predictions.predictions).map(([network, pred]) => {
            const currentFee = pred.average_fee;
            const predictedFee = pred.lowest_fee;
            const savingsPercent = Math.round(((currentFee - predictedFee) / currentFee) * 100);
 
            return `
                <div class="glass-card p-4">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-medium">${network}</span>
                        <span class="text-${savingsPercent > 0 ? 'green' : 'red'}-400">
                            ${savingsPercent}% économie potentielle
                        </span>
                    </div>
                    <div class="text-sm text-gray-400 space-y-1">
                        <div>Prix actuel: ${currentFee.toFixed(6)} USD</div>
                        <div>Prix prédit: ${predictedFee.toFixed(6)} USD</div>
                        <div>Meilleur jour: ${pred.best_day_name}</div>
                        <div>Meilleures heures: ${pred.best_hours.join('h, ')}h</div>
                    </div>
                </div>
            `;
        }).join('');
 
        predictionContainer.innerHTML = predictionHTML;
    }
 
    updateBestOption(predictions) {
        const bestOptionContainer = document.getElementById('bestOption');
        if (!bestOptionContainer) return;
 
        if (predictions.blockchain_comparison) {
            const { cheapest_chain, comparisons } = predictions.blockchain_comparison;
            const bestChainData = predictions.predictions[cheapest_chain];
 
            const bestOptionHTML = `
                <div class="p-4">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-green-400 font-bold">${cheapest_chain}</span>
                        <span class="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-sm">Recommandé</span>
                    </div>
                    <div class="space-y-2 text-sm text-gray-400">
                        <div>Prix moyen: ${bestChainData.average_fee.toFixed(6)} USD</div>
                        <div>Rapidité: ${bestChainData.transaction_speed || 'N/A'} TPS</div>
                        <div>Économie vs autres: jusqu'à ${Math.round(bestChainData.potential_savings)}%</div>
                        <div class="mt-4 text-green-400">
                            Meilleur moment: ${bestChainData.best_day_name} à ${bestChainData.best_hours[0]}h
                        </div>
                    </div>
                </div>
            `;
 
            bestOptionContainer.innerHTML = bestOptionHTML;
        }
    }
 
    startDataRefresh() {
        this.stopDataRefresh();
        state.refreshTimer = setInterval(() => {
            this.updateAllCharts();
        }, state.refreshInterval);
    }
 
    stopDataRefresh() {
        if (state.refreshTimer) {
            clearInterval(state.refreshTimer);
            state.refreshTimer = null;
        }
    }
 
    restartDataRefresh() {
        this.stopDataRefresh();
        this.startDataRefresh();
    }
 
    toggleDarkMode() {
        state.isDarkMode = !state.isDarkMode;
        document.documentElement.classList.toggle('dark');
        this.updateAllCharts();
    }
 
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 
            'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        setTimeout(() => {
            errorDiv.classList.add('animate-fade-out');
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }
 }
 
 document.addEventListener('DOMContentLoaded', () => {
    new CryptoFeeAnalytics();
 });
 const connectWalletButton = document.getElementById('connectWallet');

connectWalletButton.addEventListener('click', async () => {
    if (typeof window.ethereum !== 'undefined') {
        try {
            // Demande de connexion au compte MetaMask
            const accounts = await window.ethereum.request({ 
                method: 'eth_requestAccounts' 
            });
            
            const account = accounts[0];
            console.log('Compte connecté:', account);
            
            // Vous pouvez modifier le texte du bouton pour montrer que l'utilisateur est connecté
            connectWalletButton.textContent = `Connected: ${account.slice(0, 6)}...${account.slice(-4)}`;
            
        } catch (error) {
            console.error('Erreur de connexion:', error);
        }
    } else {
        // MetaMask n'est pas installé
        alert('Veuillez installer MetaMask !');
        window.open('https://metamask.io', '_blank');
    }
});
let currentAccount = null;

async function connectWallet() {
    try {
        if (typeof window.ethereum !== 'undefined') {
            const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
            currentAccount = accounts[0];
            
            // Afficher l'adresse raccourcie
            const shortAddress = `${currentAccount.slice(0, 6)}...${currentAccount.slice(-4)}`;
            
            // Cacher le bouton connect et montrer le bouton disconnect
            document.getElementById('connectWallet').classList.add('hidden');
            document.getElementById('disconnectWallet').classList.remove('hidden');
            
            // Mettre à jour le statut de connexion
            updateConnectionStatus(true);
            
            return true;
        } else {
            alert('Veuillez installer MetaMask!');
            return false;
        }
    } catch (error) {
        console.error(error);
        return false;
    }
}

function disconnectWallet() {
    currentAccount = null;
    
    // Cacher le bouton disconnect et montrer le bouton connect
    document.getElementById('disconnectWallet').classList.add('hidden');
    document.getElementById('connectWallet').classList.remove('hidden');
    
    // Mettre à jour le statut de connexion
    updateConnectionStatus(false);
}

function updateConnectionStatus(isConnected) {
    // Mise à jour de l'interface selon l'état de connexion
    if (isConnected) {
        // Actions quand connecté
    } else {
        // Actions quand déconnecté
    }
}

// Event listeners
document.getElementById('connectWallet').addEventListener('click', connectWallet);
document.getElementById('disconnectWallet').addEventListener('click', disconnectWallet);

// Écouter les changements de compte MetaMask
if (window.ethereum) {
    window.ethereum.on('accountsChanged', function (accounts) {
        if (accounts.length === 0) {
            // L'utilisateur s'est déconnecté de MetaMask
            disconnectWallet();
        } else {
            // Le compte a changé
            currentAccount = accounts[0];
            updateConnectionStatus(true);
        }
    });
}
// Gestion du menu mobile
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobileMenuButton');
    const mobileMenu = document.getElementById('mobileMenu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            const isHidden = mobileMenu.classList.contains('hidden');
            
            // Toggle du menu
            if (isHidden) {
                mobileMenu.classList.remove('hidden');
                // Animation d'ouverture
                mobileMenu.style.opacity = '0';
                mobileMenu.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    mobileMenu.style.opacity = '1';
                    mobileMenu.style.transform = 'translateY(0)';
                }, 50);
            } else {
                // Animation de fermeture
                mobileMenu.style.opacity = '0';
                mobileMenu.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    mobileMenu.classList.add('hidden');
                }, 300);
            }
        });

        // Fermer le menu si on clique en dehors
        document.addEventListener('click', function(event) {
            if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }

    // Ajout de la classe active sur le lien courant
    const currentPath = window.location.pathname;
    document.querySelectorAll('nav a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('bg-purple-500/20', 'text-purple-300');
        }
    });
});