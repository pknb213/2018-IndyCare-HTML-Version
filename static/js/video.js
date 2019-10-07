let vid = document.getElementById("dashcam");

function myFunction() {
  let text1 = vid.addTextTrack("caption");
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
            if (res === 'ready') {  // Test
                video.style.display = 'block';
                msg.style.display = 'none';
                video.setAttribute('src', '/static/Chronograf.mp4');
                console.log("Clip : ready");
            } else if (res === 'ok') {
                video.style.display = 'block';
                msg.style.display = 'none';
                video.setAttribute('poster', '/clip/poster');
                video.setAttribute('src', '/clip/' + sn + '/1?ts=' + new Date().valueOf());
                //console.log(video);
                console.log("Clip : ok");
            } else {
                $("#clip_msg").append("<p> Please, Refresh</p>");
                video.style.display = 'block';
                msg.style.display = 'none';
                video.setAttribute('poster', '/clip/poster/error');
                console.log("Clip : else");
            }
        },
        error: (request, status, error) => {
            let video = document.getElementById("clip");
            let msg = document.getElementById("clip_msg");
            video.style.display = 'block';
            msg.style.display = 'none';
            video.setAttribute('poster', '/clip/poster/error');
            $('#clip_msg').append("<p>" + status + "</p>");
            console.log("Load Black Box Fail : "+  status + " " + error);
            console.log(request);
        }
    });
}