document.addEventListener("DOMContentLoaded", function () {
  const plotDataScript = document.getElementById("plot-data");
  const avgDiffScript = document.getElementById("avg-difficulty");
  const avgQualScript = document.getElementById("avg-quality");

  if (!plotDataScript || !avgDiffScript || !avgQualScript) return;

  const plotData = JSON.parse(plotDataScript.textContent);
  const avgDiff = JSON.parse(avgDiffScript.textContent);
  const avgQual = JSON.parse(avgQualScript.textContent);

  if (plotData.length === 0) return;

  const ctx = document.getElementById("directorChart");
  if (!ctx) return;

  // Custom plugin to draw average lines
  const averageLinesPlugin = {
    id: "averageLines",
    afterDatasetsDraw(chart, args, options) {
      const {
        ctx,
        chartArea: { top, bottom, left, right },
        scales: { x, y },
      } = chart;

      ctx.save();
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);

      // Draw vertical line for Average Difficulty (Red)
      if (avgDiff > 0) {
        const xPos = x.getPixelForValue(avgDiff);
        if (xPos >= left && xPos <= right) {
          ctx.strokeStyle = "rgba(255, 99, 132, 0.8)";
          ctx.beginPath();
          ctx.moveTo(xPos, top);
          ctx.lineTo(xPos, bottom);
          ctx.stroke();
        }
      }

      // Draw horizontal line for Average Quality (Green)
      if (avgQual > 0) {
        const yPos = y.getPixelForValue(avgQual);
        if (yPos >= top && yPos <= bottom) {
          ctx.strokeStyle = "rgba(75, 192, 192, 0.8)";
          ctx.beginPath();
          ctx.moveTo(left, yPos);
          ctx.lineTo(right, yPos);
          ctx.stroke();
        }
      }

      ctx.restore();
    },
  };

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
    plugins: [averageLinesPlugin],
  });
});
