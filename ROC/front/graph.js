window.onload = main;

function map2(func, arr1, arr2) {
    return arr1.map((value, index) => func(value, arr2[index], index))
}

function main() {

    loaded_data = {
        "hsa-miR-133a-3p/hsa-miR-320c-3p": {
            "fpr": [0.0, 0.1, 1.0],
            "tpr": [0.0, 0.0, 1.0],
            "threshold": [2.1151888228028066, 1.1151888228028066, 0.0],
            "auc": 0.25
        },
        "hsa-miR-133a-3p/hsa-miR-92b-3p": {
            "fpr": [0.0, 0.2, 1.0],
            "tpr": [0.0, 0.0, 1.0],
            "threshold": [1.8300340904301433, 0.8300340904301433, 0.0],
            "auc": 0.25
        },
        "hsa-miR-133a-3p/hsa-miR-15b-5p": {
            "fpr": [0.0, 0.3, 1.0],
            "tpr": [0.0, 0.0, 1.0],
            "threshold": [2.050267488864508, 1.0502674888645078, 0.0],
            "auc": 0.25
        },
        "hsa-miR-133a-3p/hsa-miR-151a-3p": {
            "fpr": [0.0, 0.4, 1.0],
            "tpr": [0.0, 0.0, 1.0],
            "threshold": [2.0185484081062706, 1.0185484081062706, 0.0],
            "auc": 0.25
        },
        "hsa-miR-133a-3p/hsa-miR-142-5p": {
            "fpr": [0.0, 0.5, 1.0],
            "tpr": [0.0, 0.0, 1.0],
            "threshold": [2.045503924399479, 1.0455039243994786, 0.0],
            "auc": 0.25
        },
        "hsa-miR-133a-3p/hsa-miR-193a-5p": {
            "fpr": [0.0, 0.5, 1.0],
            "tpr": [0.0, 0.0, 1.0],
            "threshold": [1.9941413370633843, 0.9941413370633844, 0.0],
            "auc": 0.25
        }
    }

    elem = document.getElementById('data_selection');
    for (var key in loaded_data) {
        div = document.createElement('div')
        div.textContent = key
        div.onclick = function (click) {
            classList = click.target.classList
            if (classList.contains('selected')) {
                classList.remove('selected')
                myLineChart.data.datasets.splice(
                    myLineChart.data.datasets.findIndex(
                        (elem) => elem.label === click.target.textContent
                    ),
                    1
                )
            } else {
                classList.add('selected')
                entry = loaded_data[click.target.textContent];
                myLineChart.data.datasets.push({
                    label: click.target.textContent,
                    data: map2((a, b, index) => {return {x: a, y: b}}, entry.fpr, entry.tpr),
                    borderWidth: 1,
                    borderColor: 'green',
                    showLine: true,
                    fill: false
                })
            }
            myLineChart.update()
        }
        elem.appendChild(div)
    }
    

    var ctx = document.getElementById('myChart').getContext('2d');
    var speedData = {
        datasets: [{
          label: "1",
          data: [
              {x: 0, y: 0},
              {x: 0.5, y:0.5},
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