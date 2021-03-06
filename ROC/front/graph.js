window.onload = main;

function main() {
    // TODO написать логику первой страницы по выбору нужных данных

    document.getElementById("analyze").onclick = async () => {
        
        document.getElementById("first-page").classList.add("hidden")
        document.getElementById("graph-page").classList.remove("hidden")
        
        loaded_data = await get_normalized_data()
        main_graph(loaded_data)
    }
}

async function get_normalized_data() {
    // TODO
    // обратится к серверу по урлу /api/normalize,
    // распарсить и вернуть полученный в ответ json
    forms = get_forms_data()
    dataset1 = await api_get_filtered(forms.first)
    dataset2 = await api_get_filtered(forms.second)
    // result = await api_get_normalized(dataset1, dataset2)
    return await api_get_normalized(dataset1, dataset2)
    return {
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
}

async function api_get_normalized(class1, class2) {
    // TODO
    // 1) combine class1 and class2 into one object with Class field
    // 2) return await axios.post('/api/normalized') ...
    resp = await axios.post('/api/normalize', {first: class1, second: class2})
    return resp.data
}


async function api_get_filtered(filters) {
    resp = await axios.get('/api/test', {params: filters})
    return resp.data;
}

function get_forms_data() {
    return {
        first: {
            Sample:                 document.getElementById('Sample-1').value,
            Tissue:                 document.getElementById('Tissue-1').value,
            Diagnosis:              document.getElementById('Diagnosis-1').value,
            Date:                   document.getElementById('Date-1').value,
            File:                   document.getElementById('File-1').value,
            Source:                 document.getElementById('Source-1').value,
            Material:               document.getElementById('Material-1').value,
            Operator_RNA_Isolation: document.getElementById('Operator_RNA_Isolation-1').value,
            Operator_PCR:           document.getElementById('Operator_PCR-1').value,
            RNA_Concentration:      document.getElementById('RNA_Concentration-1').value
        },
        second: {
            Sample:                 document.getElementById('Sample-2').value,
            Tissue:                 document.getElementById('Tissue-2').value,
            Diagnosis:              document.getElementById('Diagnosis-2').value,
            Date:                   document.getElementById('Date-2').value,
            File:                   document.getElementById('File-2').value,
            Source:                 document.getElementById('Source-2').value,
            Material:               document.getElementById('Material-2').value,
            Operator_RNA_Isolation: document.getElementById('Operator_RNA_Isolation-2').value,
            Operator_PCR:           document.getElementById('Operator_PCR-2').value,
            RNA_Concentration:      document.getElementById('RNA_Concentration-2').value
        }
    }
}

function main_graph(loaded_data) {
    elem = document.getElementById('data_selection');
    for (var key in loaded_data) {
        div = new ClickSelectableElement(key)
        div.on_unselect = function() {
            myLineChart.data.datasets.splice(
                myLineChart.data.datasets.findIndex(
                    (elem) => elem.label === this.elem.textContent
                ),
                1
            )
            myLineChart.update()
        }
        div.on_select = function() {
            entry = loaded_data[this.elem.textContent];
            myLineChart.data.datasets.push({
                label: this.elem.textContent,
                data: map2((a, b, index) => {return {x: a, y: b}}, entry.fpr, entry.tpr),
                borderWidth: 2,
                borderColor: getRandomColor(),
                showLine: true,
                fill: false
            })
            myLineChart.update()
        }
        elem.appendChild(div.elem)
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
        elements: {
            line: {
                tension: 0
            }
        },
        legend: {
            display: true,
            position: 'bottom',
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

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function map2(func, arr1, arr2) {
    return arr1.map((value, index) => func(value, arr2[index], index))
}

class ClickSelectableElement {
    constructor (textContent) {
        this.elem = document.createElement('div')
        this.elem.classList.add('data_entry')
        this.elem.textContent = textContent
        this.selected = false

        this.elem.onclick = () => {
            if (this.selected) {
                this.elem.classList.remove('selected')
                this.on_unselect(this)
                this.selected = false
            } else {
                this.elem.classList.add('selected')
                this.on_select(this)
                this.selected = true
            }
        }
    }
}
