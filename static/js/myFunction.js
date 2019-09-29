function current_date() {
    $.ajax({
        type: "GET",
        url: "/date/now",
        success: (date)=>{
            $('.time span').empty();
            $('.time').append("<span>" + date + "</span>")
        }
    });
}