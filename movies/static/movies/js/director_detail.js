document.addEventListener("DOMContentLoaded", function () {
  const plotDataScript = document.getElementById("plot-data");
  if (!plotDataScript) return;

  const plotData = JSON.parse(plotDataScript.textContent);

  if (plotData.length === 0) return;

  const ctx = document.getElementById("directorChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Movies",
          data: plotData,
          backgroundColor: "rgba(54, 162, 235, 0.6)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
          pointRadius: 6,
          pointHoverRadius: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: "linear",
          position: "bottom",
          title: {
            display: true,
            text: "Difficulty (1-5)",
          },
          min: 1,
          max: 5,
          grid: {
            color: "rgba(0, 0, 0, 0.1)",
          },
        },
        y: {
          title: {
            display: true,
            text: "Quality (1-5)",
          },
          min: 1,
          max: 5,
          grid: {
            color: "rgba(0, 0, 0, 0.1)",
          },
        },
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              const point = context.raw;
              return `${point.title} (Diff: ${point.x}, Qual: ${point.y})`;
            },
          },
        },
        legend: {
          display: false,
        },
      },
      onClick: (e, activeElements, chart) => {
        if (activeElements.length > 0) {
          const dataIndex = activeElements[0].index;
          const url = chart.data.datasets[0].data[dataIndex].url;
          if (url) {
            window.location.href = url;
          }
        }
      },
    },
  });
});
