function count_cfg(ctx, data) {
    let gradientStroke = ctx.createLinearGradient(0,0,0,400);
    gradientStroke.addColorStop(0, "#439CFA");
    gradientStroke.addColorStop(1, "#439CFA");
    let gradientFill = ctx.createLinearGradient(0,0,0,400);
    //gradientFill.addColorStop(0,"rgba(200,207,259,1)");
    gradientFill.addColorStop(0,"rgba(144,175,249,1)");
    gradientFill.addColorStop(1,"rgba(232,244,255,0.6");

    let dataset = {
        label: 'Count',
        data: data,
        fill: true,
        borderColor: gradientStroke,
        pointBorderColor: gradientStroke,
        pointBackgroundColor: gradientStroke,
        pointBorderWidth: 2,
        pointHoverRadius: 2,
        pointRadius: 2,
        backgroundColor: gradientFill,
        //hoverBackgroundColor:
        hoverBorderColor: "#FACD83",
        borderWidth: 2.5,
    };

    return cfg = {
        type: 'bar',
        data: {datasets: [dataset]},
        options: {
            legend: {
                position: "bottom"
            },
            animation: true,
            responsive: false,
            maintainAspectRatio: false,
            responsiveAnimationDuration: 150,
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: false,
                animationDuration: 0
            },
            scales: {
                xAxes: [{
                    barThickness: 30,
                    type: 'time',
                    time: {
                        padding: 15,
                        fontStyle: "bold",
                        parser: 'MM-DD HH:mm:ss',
                        unit: 'minute',
                        unitStepSize: 30,
                        displayFormat: {
                            hour: 'MM-DD HH:mm'
                        }
                    },
                    ticks: {
                        autoSkip: true,
                        source: 'auto'
                    }
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Work Count'
                    },
                    ticks: {
                        fontColor: "rgba(0,0,0,0.8)",
                        fontStyle: "bold",
                        maxTicksLimit: 5,
                        padding: 15,
                        beginAtZero: true,
                        stepValue: 5,
                        steps: 10
                    }
                }],
                tooltips: {
                    intersect: false,
                    mode: 'index',
                    callbacks: {
                        label: function (tooltipItem, myData) {
                            var label = myData.datasets[tooltipItem.datasetIndex].label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += parseFloat(tooltipItem.value).toFixed(2);
                            return label;
                        }
                    }
                }
            }
        }
    };
}

function temp_cfg(ctx, data) {
    let dataset = [
            {
                label: 'Joint 0',
                data: data[0],
                fill: false,
                backgroundColor: "rgba(255,99,132,0.2)",
                borderColor: "rgba(255,99,132)",
                borderWidth: 1,
                lineTension: 0.2,
                pointRadius: 1
            },
            {
                label: 'Joint 1',
                data: data[1],
                fill: false,
                backgroundColor: "rgba(255,205,86,0.2)",
                borderColor: "rgba(255,205,86)",
                borderWidth: 1,
                lineTension: 0.2,
                pointRadius: 1
            },
            {
                label: 'Joint 2',
                data: data[2],
                fill: false,
                backgroundColor: "rgba(75,192,192,0.2)",
                borderColor: "rgba(75,192,192)",
                borderWidth: 1,
                lineTension: 0.2,
                pointRadius: 1
            },
            {
                label: 'Joint 3',
                data: data[3],
                fill: false,
                backgroundColor: "rgba(255,159,64,0.2)",
                borderColor: "rgba(255,159,64)",
                borderWidth: 1,
                lineTension: 0.2,
                pointRadius: 1
            },
            {
                label: 'Joint 4',
                data: data[4],
                fill: false,
                backgroundColor: "rgba(54,162,235,0.2)",
                borderColor: "rgba(54,162,23)",
                borderWidth: 1,
                lineTension: 0.2,
                pointRadius: 1
            },
            {
                label: 'Joint 5',
                data: data[5],
                fill: false,
                backgroundColor: "rgba(255,99,132,0.2)",
                borderColor: "rgba(255,99,132)",
                borderWidth: 1,
                lineTension: 0.2,
                pointRadius: 1
            }
        ];
    return cfg = {
        type: 'line',
        data: {datasets: dataset},
        options: {
            legend: {
                position: "bottom"
            },
            animation: true,
            responsive: false,
            maintainAspectRatio: false,
            responsiveAnimationDuration: 150,
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true,
                animationDuration: 0
            },
            scales: {
                xAxes: [{
                    //barThickness: 30,
                    type: 'time',
                    time: {
                        //padding: 15,
                        fontStyle: "bold",
                        parser: 'MM-DD HH:mm',
                        unit: 'minute',
                        unitStepSize: 10,
                        round: 'minute',
                        displayFormat: {
                            hour: 'MM-DD HH:mm'
                        }
                    },
                    ticks: {
                        autoSkip: true,
                        source: 'auto'
                    }
                }],
                yAxes: [{
                    scaleLabel: {
                        labelString: 'Temperature',
                    },
                    ticks: {
                        fontColor: "rgba(0,0,0,1)",
                        fontStyle: "bold",
                        maxTicksLimit: 10,
                        //minValue: 20,
                        //padding: 15,
                        beginAtZero: false,
                        stepValue: 5,
                        steps: 10
                    }
                }]
            }
        }
    };
}

function analog_cfg(ctx, data) {
    let gradientStroke = ctx.createLinearGradient(0,0,0,400);
    gradientStroke.addColorStop(0, "#047BF8");
    gradientStroke.addColorStop(1, "#047BF8");
    let gradientFill = ctx.createLinearGradient(0,0,0,400);
    //gradientFill.addColorStop(0,"rgba(200,207,259,1)");
    gradientFill.addColorStop(0,"rgba(210,232,254,1)");
    gradientFill.addColorStop(1,"rgba(210,232,254,0.6)");
    let dataset = {
            label: 'Analog',
            data: data,
            fill: true,
            pointBorderColor: gradientStroke,
            pointBackgroundColor: gradientStroke,
            pointBorderWidth: 1.2,
            pointHoverRadius: 2,
            pointRadius: 1,
            backgroundColor: gradientFill,
            borderWidth: 1.4,
            borderColor: gradientStroke,
            hoverBorderColor: "#FACD83"
        };

    return cfg = {
        type: 'line',
        data: {datasets: [dataset]},
        options: {
            animation: true,
            responsive: false,
            maintainAspectRatio: false,
            responsiveAnimationDuration: 150,
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: false,
                animationDuration: 0
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        parser: 'MM-DD HH:mm',
                        unit: 'minute',
                        unitStepSize: 10,
                        round: 'minute',
                        displayFormat: {
                            hour: 'MM-D HH:mm '
                        }
                    },
                    ticks: {
                        autoSkip: true,
                        source: 'auto'
                    }
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Analog'
                    },
                    ticks: {
                        beginAtZero: true,
                        stepValue: 5,
                        steps: 10
                    }
                }],
                tooltips: {
                    intersect: false,
                    mode: 'index',
                    callbacks: {
                        label: function (tooltipItem, myData) {
                            var label = myData.datasets[tooltipItem.datasetIndex].label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += parseFloat(tooltipItem.value).toFixed(2);
                            return label;
                        }
                    }
                }
            }
        }
    };
}