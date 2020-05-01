var lastData = "";
function getStatusUpdates() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      data = JSON.parse(this.responseText);
      if(lastData == "") {
        postMessage(data);
        lastData = data;
      } else {
        newData = {}
        for(var cage in data) {
          if(data.hasOwnProperty(cage) && (!lastData.hasOwnProperty(cage) ||
          data[cage].food != lastData[cage].food || data[cage].water != lastData[cage].water)) {
            newData[cage] = data[cage];
            console.log(cage + " changed");
          }
        }
        for(var oldCage in lastData) {
          if(lastData.hasOwnProperty(oldCage) && !data.hasOwnProperty(oldCage)) {
            newData[oldCage] = {"food": false, "water": false};
          }
        }
        if(countProperties(newData) > 0) {
          postMessage(newData);
          lastData = data;
        }
      }
    }
  };
  xhttp.open("POST", "/", true);
  xhttp.send();
  setTimeout("getStatusUpdates()",500);
}

function countProperties(obj) {
    var count = 0;

    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            ++count;
    }

    return count;
}

getStatusUpdates();
