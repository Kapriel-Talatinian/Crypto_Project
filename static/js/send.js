document.addEventListener('DOMContentLoaded', function() {
    // Variables globales pour stocker les transactions
    let transactions = [];

    // Éléments DOM
    const csvFile = document.getElementById('csvFile');
    const csvPreview = document.getElementById('csvPreview');
    const manualForm = document.getElementById('manualForm');
    const transactionsTable = document.getElementById('transactionsTable');
    const txCount = document.getElementById('txCount');
    const totalAmount = document.getElementById('totalAmount');
    const estimatedFees = document.getElementById('estimatedFees');
    const finalTotal = document.getElementById('finalTotal');
    const sendTransactions = document.getElementById('sendTransactions');

    // Gestion de l'import CSV
    csvFile.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(event) {
            const csvData = event.target.result;
            const rows = csvData.split('\n');
            
            // Ignorer l'en-tête
            for (let i = 1; i < rows.length; i++) {
                const columns = rows[i].split(',');
                if (columns.length === 4) {
                    addTransaction({
                        name: columns[0].trim(),
                        address: columns[1].trim(),
                        amount: parseFloat(columns[2].trim()),
                        blockchain: columns[3].trim()
                    });
                }
            }
        };
        reader.readAsText(file);
    });

    // Gestion du formulaire manuel
    manualForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const transaction = {
            name: document.getElementById('name').value,
            address: document.getElementById('address').value,
            amount: parseFloat(document.getElementById('amount').value),
            blockchain: document.getElementById('blockchain').value
        };

        addTransaction(transaction);
        manualForm.reset();
    });

    // Fonction pour ajouter une transaction
    function addTransaction(transaction) {
        transactions.push(transaction);
        updateTransactionTable();
        updateTransactionSummary();
    }

    // Mise à jour du tableau des transactions
    function updateTransactionTable() {
        transactionsTable.innerHTML = '';
        
        transactions.forEach((tx, index) => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-gray-800/50';
            
            tr.innerHTML = `
                <td class="py-3 text-sm">${tx.name}</td>
                <td class="py-3 text-sm font-mono">${tx.address}</td>
                <td class="py-3 text-sm">${tx.amount} ${tx.blockchain}</td>
                <td class="py-3 text-sm">${tx.blockchain}</td>
                <td class="py-3 text-sm">
                    <span class="px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-500 text-xs">
                        En attente
                    </span>
                </td>
                <td class="py-3 text-sm">
                    <button onclick="removeTransaction(${index})" class="text-red-500 hover:text-red-400 transition-colors">
                        Supprimer
                    </button>
                </td>
            `;
            
            transactionsTable.appendChild(tr);
        });
    }

    // Mise à jour du résumé des transactions
    function updateTransactionSummary() {
        const total = transactions.reduce((sum, tx) => sum + tx.amount, 0);
        const count = transactions.length;
        
        txCount.textContent = count;
        totalAmount.textContent = total.toFixed(4);
        
        // Estimation des frais (exemple simplifié)
        const estimatedFeesValue = calculateEstimatedFees();
        estimatedFees.textContent = estimatedFeesValue.toFixed(4);
        
        finalTotal.textContent = (total + estimatedFeesValue).toFixed(4);
        
        // Activer/désactiver le bouton d'envoi
        sendTransactions.disabled = count === 0;
    }

    // Calcul des frais estimés
    function calculateEstimatedFees() {
        return transactions.reduce((sum, tx) => {
            switch(tx.blockchain) {
                case 'ETH':
                    return sum + 0.003; // ~$5 en ETH
                case 'BNB':
                    return sum + 0.001; // ~$0.3 en BNB
                case 'SOL':
                    return sum + 0.000001; // ~$0.0001 en SOL
                default:
                    return sum;
            }
        }, 0);
    }

    // Fonction pour supprimer une transaction
    window.removeTransaction = function(index) {
        transactions.splice(index, 1);
        updateTransactionTable();
        updateTransactionSummary();
    };

    // Gestion du bouton d'envoi
    sendTransactions.addEventListener('click', async function() {
        if (!window.ethereum) {
            alert('MetaMask est requis pour envoyer des transactions');
            return;
        }

        try {
            // Demander la connexion à MetaMask
            const accounts = await window.ethereum.request({ 
                method: 'eth_requestAccounts' 
            });
            
            // Pour chaque transaction
            for (const tx of transactions) {
                try {
                    // Envoi de la transaction
                    const transactionParameters = {
                        to: tx.address,
                        from: accounts[0],
                        value: '0x' + (tx.amount * 1e18).toString(16)
                    };

                    const txHash = await window.ethereum.request({
                        method: 'eth_sendTransaction',
                        params: [transactionParameters],
                    });

                    console.log('Transaction envoyée:', txHash);
                } catch (err) {
                    console.error('Erreur lors de l\'envoi:', err);
                    alert(`Erreur lors de l'envoi à ${tx.address}: ${err.message}`);
                }
            }
        } catch (err) {
            console.error('Erreur de connexion:', err);
            alert('Erreur de connexion à MetaMask');
        }
    });
});