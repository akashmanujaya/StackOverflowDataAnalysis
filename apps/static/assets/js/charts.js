charts = {
    overallTrendChart: null,
    initFirstOverallTrendChart: function(x_axis, y_axis){
    let chartConfig = {
      maintainAspectRatio: false,
      legend: {
        display: false
      },
      tooltips: {
        backgroundColor: '#f5f5f5',
        titleFontColor: '#333',
        bodyFontColor: '#666',
        bodySpacing: 4,
        xPadding: 12,
        mode: "nearest",
        intersect: 0,
        position: "nearest"
      },
      responsive: true,
      scales: {
        yAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(29,140,248,0.0)',
            zeroLineColor: "transparent",
          },
          ticks: {
            suggestedMin: 50,
            suggestedMax: 110,
            padding: 20,
            fontColor: "#ff8a76"
          }
        }],
        xAxes: [{
          barPercentage: 1.6,
          gridLines: {
            drawBorder: false,
            color: 'rgba(220,53,69,0.1)',
            zeroLineColor: "transparent",
          },
          ticks: {
            padding: 20,
            fontColor: "#ff8a76"
          }
        }]
      }
    };

    let ctx = document.getElementById("overall_trends").getContext('2d');

    let gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
    gradientStroke.addColorStop(1, 'rgba(72,72,176,0.1)');
    gradientStroke.addColorStop(0.4, 'rgba(72,72,176,0.0)');
    gradientStroke.addColorStop(0, 'rgba(119,52,169,0)');

    let config = {
      type: 'line',
      data: {
        labels: x_axis,
        datasets: [{
          label: "No. of Questions",
          fill: true,
          backgroundColor: gradientStroke,
          borderColor: '#fd7700',
          borderWidth: 2,
          borderDash: [],
          borderDashOffset: 0.0,
          pointBackgroundColor: '#f84d4d',
          pointBorderColor: 'rgba(255,255,255,0)',
          pointHoverBackgroundColor: '#f84d4d',
          pointBorderWidth: 20,
          pointHoverRadius: 4,
          pointHoverBorderWidth: 15,
          pointRadius: 4,
          data: y_axis,
        }]
      },
      options: chartConfig
    };

    if (this.overallTrendChart) {
      this.overallTrendChart.destroy();
    }

    this.overallTrendChart = new Chart(ctx, config);
  },

    initComplexityHistogram: function(labels, frequencies){
        let ctx = document.getElementById("complexity_histogram").getContext('2d');

        let config = {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: "Frequency",
              backgroundColor: 'rgba(192,110,75,0.2)',
              borderColor: 'rgb(246,125,38)',
              borderWidth: 1,
              data: frequencies,
            }]
          },
          options: {
            responsive: true,
            scales: {
              yAxes: [{
                ticks: {
                  beginAtZero: true
                }
              }]
            }
          }
        };

        new Chart(ctx, config);
    },

    initScoreComplexityScatter: function(data){
        let ctx = document.getElementById("score_vs_complexity_scatter").getContext('2d');

        let config = {
        type: 'scatter',
        data: {
          datasets: [{
            label: "Complexity vs Score",
            data: data,
            backgroundColor: 'rgba(192,116,75,0.2)',
            borderColor: 'rgb(250,139,44)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            xAxes: [{
              type: 'linear',
              position: 'bottom',
              ticks: {
                beginAtZero: true
              }
            }]
          }
        }
      };

        new Chart(ctx, config);
    },

    initComplexityQuartileOverTime: function(dates, firstQuartile, median, thirdQuartile) {
        let ctx = document.getElementById("complexity_quartile_over_time").getContext('2d');
        let config = {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'First Quartile',
                    data: firstQuartile,
                    fill: false,
                    borderColor: 'rgb(192,85,75)',
                }, {
                    label: 'Median',
                    data: median,
                    fill: false,
                    borderColor: 'rgb(250,139,44)',
                }, {
                    label: 'Third Quartile',
                    data: thirdQuartile,
                    fill: false,
                    borderColor: 'rgb(252,187,92)',
                }]
            },
            options: {
                responsive: true,
                scales: {
                    xAxes: [{
                        type: 'time',
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Date'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Complexity'
                        }
                    }]
                }
            }
        };

        new Chart(ctx, config);
    },

    initComplexityStatisticsOfTags: function (labels, means, medians, modes){
        let ctx = document.getElementById("tag_statistics").getContext('2d');
        let config = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Mean',
                    data: means,
                    backgroundColor: 'rgba(246,38,38,0.75)'
                }, {
                    label: 'Median',
                    data: medians,
                    backgroundColor: 'rgba(255,185,75,0.75)'
                }, {
                    label: 'Mode',
                    data: modes,
                    backgroundColor: 'rgba(246,125,38,0.75)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    xAxes: [{}],
                    yAxes: [{}]
                }
            }
        };

        new Chart(ctx, config);
    }

};


