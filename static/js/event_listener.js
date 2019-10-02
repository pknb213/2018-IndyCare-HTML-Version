function event_listener(sn) {
    const event_source = new EventSource("/stream?channel=" + sn + "_event");
    event_source.addEventListener('message', function (event) {
        console.log(event);
        $("#dataTable").DataTable().ajax.reload();
        $("#history_table").DataTable().ajax.reload();
    }, false);
    event_source.addEventListener('fail', function (event) {
        alert(event);
    }, false);
    event_source.addEventListener('error', function (event) {
        //alert(event['message']);
    }, false);
}