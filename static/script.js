window.onload=(ev) => {
    // Make Discord Connection Link
    var url = "https://discord.com/api/oauth2/authorize?client_id=1043495092977152061&redirect_uri=";
    var url2= "&response_type=code&scope=identify%20email%20connections%20guilds";
    var domain = "https://" + document.location.hostname;
    if (domain == "https://localhost"){ // Fix for local tests
        domain = "http://" + document.location.host;
    };
    url = url + domain+ "/oauth/callback" + url2;
    let aref = document.getElementById('login-discord');
    if (aref){ // Check if it exists
        aref.href = url;
    };
    
}

function clockUpdate(){
    let date = new Date();
    let hh = date.getHours();
    let mm = date.getMinutes();
    if (hh == 0){
        hh = 12;
    }
    if (hh > 12){
        hh = hh - 12;
    }
    hh = (hh < 10) ? "0" + hh : hh;
    mm = (mm < 10) ? "0" + mm : mm;
    let time = hh +":"+ mm;
    document.getElementById('clock').innerText = time;
    let t = setTimeout(function() { clockUpdate() },1000*15); // Update ever 1/4 minute
}
clockUpdate()

// Overlay
function OverlayOpen(url,faid=NaN){
    if (faid){
        var Overid = "overlay-"+faid;
    }
    else{
        var Overid = "overlay";
    };
    var d = document.getElementById(Overid);
    if (d.style.display=="none"){
        d.style.display = "block";
        if (!faid){
            $('#overlay').load(url);   
        }
    }
    else{
        if (d.style.display=="block"){
            d.style.display = "none";
        }
        else{
            d.style.display = "none"
        };
    };
    
}

function hideOverlay(id=NaN){
    if (id){
        var d = document.getElementById(id);
    }
    else{
        var d = document.getElementById('overlay');
    }
    d.style.display = "none";
}

window.addEventListener('click',(event)=>{
    var over = document.getElementsByClassName('overlay');
    for (i = 0; i <over.length; i++){
        var x = over[i];
        if (event.target === x){
            x.style.display = 'none';
        };
    }
})

function loadExternalHtml(filename,item){
    console.log(filename)
    fetch(filename)
    .then(response=> response.text())
    .then(text=> item.innerHTML = text);
}

function readSingleFile(target) {
    //Retrieve the first (and only!) File from the FileList object
    var f = target;

    if (f) {
        var r = new FileReader();
        r.onload = function (e) {
            var contents = e.target.result;
            document.getElementById("ReadResult").innerHTML = contents;
        }
        r.readAsText(f);
        console.log('TEste')
    } else {
        alert("Failed to load file");
    }
}