// static/js/main.js
const COMMON = {
    // Configuration Plotly commune
    chartConfig: {
        responsive: true,
        displayModeBar: false,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#fff' }
    },
    
    // Fonctions utilitaires communes
    generateTimeData: function(hours) {
        const data = [];
        const now = new Date();
        for (let i = 0; i < hours; i++) {
            const date = new Date(now);
            date.setHours(now.getHours() - i);
            data.unshift(date);
        }
        return data;
    },

    generateRandomData: function(count, min, max) {
        return Array.from({length: count}, () => 
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    }
};

// Exportez pour utilisation dans d'autres fichiers
window.COMMON = COMMON;