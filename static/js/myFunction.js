function init() {   // Not Use
    const param = new URLSearchParams(document.location.search);
    return param.get('sn');
}

function current_date() {
    $.ajax({
        type: "GET",
        url: "/date/now",
        success: (date) => {
            $('.time span').empty();
            $('.time').append("<span>" + date + "</span>")
        }
    });
}

function get_kpi(sn) {
    let arr = [];
    $.ajax({
        url: "/kpi/" + sn,
        type: "GET",
        async: false,
        success: (res) => {
            arr = res
        }
    });

    return arr;
}

function data_table_for_history(sn) {
    // $.fn.dataTable.ext.errMode = 'none';
    $('#dataTable_history').DataTable({
        width: "650px",
        processing: true,
        searching: false,
        paging: false,
        lengthChange: false,
        bInfo: false,
        ajax: {
            "url": "/list/events2/" + sn,
            "type": "GET",
            "dataSrc": "",
        },
        columns: [
            {"data": "occurrence_time"},
            {"data": "code"},
            {"data": "down"}
        ],
        order: [[0, 'desc']]
    });
}

function data_table(sn) {
    // $.fn.dataTable.ext.errMode = 'none';
    $('#dataTable').DataTable({
        processing: true,
        searching: false,
        paging: false,
        lengthChange: false,
        bInfo: false,
        scrollXInner: '550px',
        scrollX: '530px',
        scrollY: false,
        ajax: {
            "url": "/list/events/" + sn,
            "type": "GET",
            "dataSrc": "",
        },
        columns: [
            {"data": "occurrence_time"},
            {"data": "code"},
            {"data": "down"}
        ],
        order: [[0, 'desc']]
    });
}


function get_opdata_for_creation(kpi) {
    $.ajax({
        url: "/opdata/" + kpi.sn + '/' + kpi.axis + '/' + kpi.key + '/recent/' + kpi.period,
        dataType: "json",
    }).done(function (data) {
        switch (kpi.key) {
            case 'count':
                create_count_chart(kpi.kpi, data);
                break;
            case 'mean':
                if(kpi.axis === '6')
                    create_mean_chart_for_temp(kpi.kpi, data);
                else if(kpi.axis === '1')
                    create_mean_chart_for_analog(kpi.kpi, data);
                else
                    return "Get Opdata Fail";
                break;
            case 'none':

                break;
        }
    });
}

function get_opdata_for_refresh(kpi) {
    $.ajax({
        url: "/opdata/" + kpi.sn + '/' + kpi.axis + '/' + kpi.key + '/recent/' + kpi.period,
        dataType: "json",
    }).done(function (data) {
        switch (kpi.key) {
            case 'count':
                refresh_count_chart(kpi.kpi, data);
                break;
            case 'mean':
                if(kpi.axis === '6')
                    refresh_temp_chart(kpi.kpi, data);
                else if(kpi.axis === '1')
                    refresh_anlog_chart(kpi.kpi, data);
                else
                    return "Get Opdata Fail";
                break;
            case 'none':

                break;
        }
    });
}



function create_count_chart(kpi_num, data) {
    let ctx = document.getElementById('myCountChart').getContext('2d');
    ctx.canvas.width = 490;
    ctx.canvas.height = 300;

    let ctx2 = document.getElementById("myCountChart_second").getContext('2d');
    ctx2.canvas.width = 600;
    ctx2.canvas.height = 350;

    let cfg = count_cfg(ctx, data);

    window[kpi_num] = new Chart(ctx, cfg);
    window.chart1 = new Chart(ctx2, cfg);
}

function create_mean_chart_for_temp(kpi_num, data) {
    let ctx = document.getElementById('myTempChart').getContext('2d');
    ctx.canvas.width = 1200;
    ctx.canvas.height = 300;
    let ctx2 = document.getElementById("myTempChart_second").getContext('2d');
    ctx2.canvas.width = 1050;
    ctx2.canvas.height = 350;

    let cfg = temp_cfg(ctx, data);

    window[kpi_num] = new Chart(ctx, cfg);
    window.chart2 = new Chart(ctx2, cfg);
}

function create_mean_chart_for_analog(kpi_num, data) {
    let ctx = document.getElementById('myAnalog').getContext('2d');
    ctx.canvas.width = 500;
    ctx.canvas.height = 400;
    let ctx2 = document.getElementById('myAnalog_second').getContext('2d');
    let ctx3 = document.getElementById('myAnalog_third').getContext('2d');

    let cfg = analog_cfg(ctx, data);

    window.chart3 = new Chart(ctx, cfg);
    window.chart4 = new Chart(ctx2, cfg);
    window.chart5 = new Chart(ctx3, cfg);
}

function refresh_count_chart(kpi_num, data) {
    // 안됨 씨발 -> 그냥 destroy 후 새로 생성으로 바꿈
    // chart.data.datasets[0].data = data
    // chart.update()
    let ctx = document.getElementById('myCountChart').getContext('2d');
    ctx.canvas.width = 490;
    ctx.canvas.height = 300;

    let ctx2 = document.getElementById("myCountChart_second").getContext('2d');
    ctx2.canvas.width = 600;
    ctx2.canvas.height = 350;

    let cfg = count_cfg(ctx, data);

    window[kpi_num].destroy();
    window.chart1.destroy();
    window[kpi_num] = new Chart(ctx, cfg);
    window.chart1 = new Chart(ctx2, cfg);
}

function refresh_temp_chart(kpi_num, data) {
    let ctx = document.getElementById('myTempChart').getContext('2d');
    ctx.canvas.width = 1200;
    ctx.canvas.height = 300;
    let ctx2 = document.getElementById("myTempChart_second").getContext('2d');
    ctx2.canvas.width = 1050;
    ctx2.canvas.height = 350;

    let cfg = temp_cfg(ctx, data);

    window[kpi_num].destroy();
    window.chart2.destroy();
    window[kpi_num] = new Chart(ctx, cfg);
    window.chart2 = new Chart(ctx2, cfg);
}

function refresh_anlog_chart(kpi_num, data) {
    let ctx = document.getElementById('myAnalog').getContext('2d');
    ctx.canvas.width = 500;
    ctx.canvas.height = 400;
    let ctx2 = document.getElementById('myAnalog_second').getContext('2d');
    let ctx3 = document.getElementById('myAnalog_third').getContext('2d');

    let cfg = analog_cfg(ctx, data);

    window.chart3.destroy();
    window.chart4.destroy();
    window.chart5.destroy();
    window.chart3 = new Chart(ctx, cfg);
    window.chart4 = new Chart(ctx2, cfg);
    window.chart5 = new Chart(ctx3, cfg);
}

function create_chart_from_kpi(sn, kpi_arr) {
    kpi_arr.forEach(load_kpi);
    
    function load_kpi(kpi) {
        if(kpi === false || kpi === 'none')
            return "Fail";

        if(!('axis' in kpi) || !('key' in kpi)) return "Fail";
        else{
            let sn = kpi.sn;
            let kpi_num = kpi.kpi;
            let axis = kpi.axis;
            let key = kpi.key;
            let label = kpi.label;
            let period = kpi.period;

            get_opdata_for_creation(kpi);

        }
    }
}

function refresh_chart_from_kpi(sn, kpi_arr) {
    kpi_arr.forEach(load_kpi);

    function load_kpi(kpi) {
        if(kpi === false || kpi === 'none')
            return "Fail";

        if(!('axis' in kpi) || !('key' in kpi)) return "Fail";
        else{
            let sn = kpi.sn;
            let kpi_num = kpi.kpi;
            let axis = kpi.axis;
            let key = kpi.key;
            let label = kpi.label;
            let period = kpi.period;

            get_opdata_for_refresh(kpi);

        }
    }
}