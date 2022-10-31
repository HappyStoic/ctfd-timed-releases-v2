function mySubmit(e){
  let data = {
    "nonce": e.target[0].value,
    "release": e.target[1].value
  }
  if(data.release === ""){
    err("missing release date time")
    return
  }

  fetch(e.target.action,{
    method: e.target.method,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
    body: new URLSearchParams(data)
  }).then(res => {
    if (res.status === 200) {
      location.reload()
    } else {
      msg = res.statusText + "(" + res.status + ") "
      res.json().then(json => {
        msg += json["error"]
        err(msg)
      }).catch(() => {
        err(msg)
      })
    }
  });
}

function err(msg){
  alert(msg)
}

window.addEventListener("DOMContentLoaded", function() {
  var items = document.getElementsByClassName("update-timed-release")
  for (let item of items) {
    item.addEventListener("submit", function(e) {
      e.preventDefault();
      mySubmit(e)
   })
  }
});

