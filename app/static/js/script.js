document.addEventListener("DOMContentLoaded", function () {
  const etatChartElement = document.getElementById('etatChart');

  if (etatChartElement) {
    const data = {
      labels: JSON.parse(etatChartElement.dataset.labels),
      datasets: [{
        label: 'Nombre de candidatures',
        data: JSON.parse(etatChartElement.dataset.values),
        backgroundColor: [
          '#42a5f5', '#66bb6a', '#ffa726', '#ef5350', '#ab47bc', '#26c6da'
        ]
      }]
    };

    const config = {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 }
          }
        }
      }
    };

    new Chart(etatChartElement, config);
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  document.querySelectorAll(".routine-list li").forEach(item => {
    const startParts = item.dataset.start.split(":").map(Number);
    const endParts = item.dataset.end.split(":").map(Number);
    const startMinutes = startParts[0] * 60 + startParts[1];
    const endMinutes = endParts[0] * 60 + endParts[1];

    if (currentMinutes >= startMinutes && currentMinutes < endMinutes) {
      item.classList.add("active");
    }
  });
});
