function getStatusUpdates(cageID) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      data = JSON.parse(this.responseText);
        if(countProperties(newData) > 0) {
          postMessage(data);
        }
      }
    }
  };
  xhttp.open("POST", "/cage/" + cageID + "/updates", true);
  xhttp.send();
  setTimeout("getStatusUpdates()",500);
}

self.onmessage = function(msg) {
    if(msg.substr(0,5) == "cageID") {
        var cageID = msg.substr(7,msg.length - 1);
        getStatusUpdates(cageID);
    } else if(msg.substr(0,6) == "refresh") {
        var cageID = msg.substr(8,msg.length - 1);
        if(cageID == "all") {
            var xhttp = new XMLHttpRequest();
              xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                  data = JSON.parse(this.responseText);
                    if(countProperties(newData) > 0) {

                    }
                  }
                }
              };
              xhttp.open("POST", "/refresh/" + cageID, true);
              xhttp.send();
        }
    }
}

function countProperties(obj) {
    var count = 0;

    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            ++count;
    }

    return count;
}


