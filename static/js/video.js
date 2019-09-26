var vid = document.getElementById("dashcam");

function myFunction() {
  var text1 = vid.addTextTrack("caption");
  text1.addCue(new TextTrackCue("Test text", 1.000, 4.000, "", "", "", true));
}

function load_clip(sn) {
    console.log("Started Ajax");
    $.ajax({
        type: "GET",
        url: "/clip/" + sn + "/check",
        success: (res) => {
            console.log("Res : " + res);
            let video = document.getElementById("clip");
            let msg = document.getElementById('clip_msg');
            if (res === 'ready') {
                video.style.display = 'block';
                msg.style.display = 'none';
                video.setAttribute('src', '/static/Chronograf.mp4');
                console.log("Clip : ready");
            } else if (res === 'ok') {
                video.style.display = 'block';
                msg.style.display = 'none';
                video.setAttribute('poster', '/clip/poster');
                video.setAttribute('src', '/clip/' + sn + '/1?ts=' + new Date().valueOf());
                console.log(video);
                console.log("Clip : ok");
            } else {
                $("#clip_msg").append("<p> Please, Refresh</p>");
                video.style.display = 'block';
                msg.style.display = 'block';
                video.setAttribute('src', '');
            }
        },
        error: (request, status, error) => {
            let video = document.getElementById("black_box_clip");
            let msg = document.getElementById("black_box_message");
            video.style.display = 'none';
            msg.style.display = 'block';
            $('#clip_msg').append("<p>" + status + "</p>");
            console.log("Load Black Box Fail " + request + status + error);
        }
    });
}