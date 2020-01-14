window.onload = main;

function main() {

    var ctx = document.getElementById('myChart').getContext('2d');
    var speedData = {
        datasets: [{
          label: "Car Speed",
          data: [
              {x: 0, y: 0},
              {x: 0.2, y:0.8},
              {x: 1, y: 1}
          ],
          borderWidth: 1,
          borderColor: 'black',
          showLine: true,
          fill: false
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
        type: 'scatter',
        data: speedData,
        options: chartOptions
    });

}