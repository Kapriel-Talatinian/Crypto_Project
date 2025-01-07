// static/js/portfolio.js

document.addEventListener('DOMContentLoaded', function() {
    // Configuration initiale des charts
    const chartConfig = {
        responsive: true,
        displayModeBar: false,
        showlegend: true,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            color: '#fff'
        },
        xaxis: {
            gridcolor: 'rgba(255,255,255,0.1)',
            zerolinecolor: 'rgba(255,255,255,0.1)'
        },
        yaxis: {
            gridcolor: 'rgba(255,255,255,0.1)', 
            zerolinecolor: 'rgba(255,255,255,0.1)'
        }
    };
 
    // Distribution par Blockchain
    const distributionData = {
        values: [45, 35, 20],
        labels: ['ETH', 'BNB', 'SOL'],
        type: 'pie',
        marker: {
            colors: ['#627EEA', '#F3BA2F', '#00FFA3']
        },
        textinfo: 'percent',
        hoverinfo: 'label+percent'
    };
 
    Plotly.newPlot('blockchainDistribution', [distributionData], {
        ...chartConfig,
        title: {
            text: 'Distribution par Blockchain',
            font: { color: '#fff' }
        }
    });
 
    // Gas Usage Trends
    const gasUsageData = {
        x: generateDates(30),
        y: generateRandomData(30, 50, 150),
        type: 'scatter',
        mode: 'lines',
        name: 'Gas Usage',
        line: {
            color: '#8B5CF6',
            width: 2
        },
        fill: 'tozeroy',
        fillcolor: 'rgba(139, 92, 246, 0.1)'
    };
 
    Plotly.newPlot('gasUsageTrend', [gasUsageData], {
        ...chartConfig,
        title: {
            text: 'Tendance d\'utilisation du Gas',
            font: { color: '#fff' }
        },
        xaxis: {
            title: 'Date',
            showgrid: true,
            gridcolor: 'rgba(255,255,255,0.1)'
        },
        yaxis: {
            title: 'Gas (Gwei)',
            showgrid: true,
            gridcolor: 'rgba(255,255,255,0.1)'
        }
    });
 
    // Simuler les données de l'historique des transactions
    populateTransactionHistory();
    updatePortfolioStats();
 });
 
 // Fonctions utilitaires
 function generateDates(count) {
    const dates = [];
    const today = new Date();
    for (let i = 0; i < count; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        dates.unshift(date.toISOString().split('T')[0]);
    }
    return dates;
 }
 
 function generateRandomData(count, min, max) {
    return Array.from({length: count}, () => 
        Math.floor(Math.random() * (max - min + 1)) + min
    );
 }
 
 function populateTransactionHistory() {
    const tbody = document.getElementById('transactionHistory');
    const transactions = generateMockTransactions(10);
    
    transactions.forEach(tx => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="py-3">${tx.date}</td>
            <td class="py-3">
                <div class="flex items-center space-x-2">
                    <img src="${getBlockchainIcon(tx.blockchain)}" class="w-4 h-4">
                    <span>${tx.blockchain}</span>
                </div>
            </td>
            <td class="py-3 font-mono text-sm">${tx.address}</td>
            <td class="py-3">${tx.amount}</td>
            <td class="py-3">${tx.gas}</td>
            <td class="py-3">
                <span class="px-2 py-1 rounded-full ${getStatusClass(tx.status)}">
                    ${tx.status}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
 }
 
 function getBlockchainIcon(blockchain) {
    const icons = {
        ETH: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiI+PHBhdGggZmlsbD0iIzYyN0VFQSIgZD0iTTE2IDMyQzcuMTYzIDMyIDAgMjQuODM3IDAgMTZTNy4xNjMgMCAxNiAwczE2IDcuMTYzIDE2IDE2LTcuMTYzIDE2LTE2IDE2em03Ljk5NC0xNS43NDNMMTYuNDk4IDRsLTcuNDggMTIuMjU3TDE2LjQ5OCAxOS41bDcuNDk2LTMuMjQzem0tNy45OSA0LjM2M0w3Ljk5NiAxNi4yNTdsMy4zNDggNS41IDQuNjYtMS45Mzd6Ii8+PC9zdmc+',
        BNB: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiI+PHBhdGggZmlsbD0iI0YzQkEyRiIgZD0iTTE2IDMyQzcuMTYzIDMyIDAgMjQuODM3IDAgMTZTNy4xNjMgMCAxNiAwczE2IDcuMTYzIDE2IDE2LTcuMTYzIDE2LTE2IDE2em0tLjY1NC03LjQyTDkuOSAxOS4xMzZsMS4zNDctMS4zNDcgNC4xIDQuMDk4IDQuMDk4LTQuMDk4IDEuMzQ3IDEuMzQ3LTUuNDQ2IDUuNDQ0em0wLTcuMzY0TDkuOSAxMS43NzJsMS4zNDctMS4zNDcgNC4xIDQuMDk4IDQuMDk4LTQuMDk4IDEuMzQ3IDEuMzQ3LTUuNDQ2IDUuNDQ0eiIvPjwvc3ZnPg==',
        SOL: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiI+PHBhdGggZmlsbD0iIzAwRkZBMyIgZD0iTTE2IDMyQzcuMTYzIDMyIDAgMjQuODM3IDAgMTZTNy4xNjMgMCAxNiAwczE2IDcuMTYzIDE2IDE2LTcuMTYzIDE2LTE2IDE2em0yLjUwNC0xNi4yMzhsLTQuNzEgNC43MUw4LjIzOCAxNC45MmwxLjU3LTEuNTcgNC43MSA0LjcxIDQuNzEtNC43MSAxLjU3IDEuNTctNi4yOCA2LjI4LTEuNTctMS41Ny00LjcxLTQuNzEgMS41Ny0xLjU3IDQuNzEgNC43MSA0LjcxLTQuNzEgMS41NyAxLjU3eiIvPjwvc3ZnPg=='
    };
    return icons[blockchain] || '';
 }
 
 function getStatusClass(status) {
    const classes = {
        'Succès': 'bg-green-500/20 text-green-500',
        'En cours': 'bg-yellow-500/20 text-yellow-500',
        'Échec': 'bg-red-500/20 text-red-500'
    };
    return classes[status] || '';
 }
 
 function generateMockTransactions(count) {
    const statuses = ['Succès', 'En cours', 'Échec'];
    const blockchains = ['ETH', 'BNB', 'SOL'];
    
    return Array.from({length: count}, (_, i) => ({
        date: new Date(Date.now() - i * 86400000).toLocaleDateString(),
        blockchain: blockchains[Math.floor(Math.random() * blockchains.length)],
        address: `0x${Math.random().toString(16).substr(2, 40)}`,
        amount: `${(Math.random() * 10).toFixed(4)} ${blockchains[Math.floor(Math.random() * blockchains.length)]}`,
        gas: `${(Math.random() * 100).toFixed(2)} Gwei`,
        status: statuses[Math.floor(Math.random() * statuses.length)]
    }));
 }
 
 function updatePortfolioStats() {
    document.getElementById('totalTx').textContent = '156';
    document.getElementById('totalGas').textContent = '2.45 ETH';
    document.getElementById('totalSavings').textContent = '$1,234.56';
    document.getElementById('optimizationScore').textContent = '85%';
 }