console.log("analyze.js loaded", document.getElementById('priceChart'));

document.addEventListener('DOMContentLoaded', function() {
  const dataEl = document.getElementById('chart-data');
  if (!dataEl) return;

  const cd = JSON.parse(dataEl.textContent);
  const ctx = document.getElementById('priceChart').getContext('2d');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: cd.dates,
      datasets: [
        {
          label: 'Close Price',
          data: cd.prices,
          borderColor: 'rgba(0,123,255,0.8)',
          backgroundColor: 'rgba(0,123,255,0.2)',
          fill: false,
          pointRadius: 0,
          borderWidth: 2
        },
        {
          label: '20-Day SMA',
          data: cd.sma20,
          borderColor: 'rgba(40,167,69,0.8)',
          borderDash: [5,5],
          pointRadius: 0,
          borderWidth: 1
        },
        {
          label: '50-Day SMA',
          data: cd.sma50,
          borderColor: 'rgba(220,53,69,0.8)',
          borderDash: [5,5],
          pointRadius: 0,
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'bottom' },
        tooltip: { enabled: true }
      },
      scales: {
        x: { title: { display: true, text: 'Date' } },
        y: { title: { display: true, text: 'Price (USD)' } }
      }
    }
  });
});
