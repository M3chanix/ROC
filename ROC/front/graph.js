window.onload = main;

function main() {

    var ctx = document.getElementById('myChart').getContext('2d');
    var speedData = {
        labels: ["0s", "10s", "20s", "30s", "40s", "50s", "60s"],
        datasets: [{
          label: "Car Speed",
          data: [0, 59, 75, 20, 20, 55, 40],
        }]
      };
       
      var chartOptions = {
        legend: {
          display: true,
          position: 'top',
          labels: {
            boxWidth: 80,
            fontColor: 'black'
          }
        }
      };
    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: speedData,
        options: chartOptions
    });

}