


function submit(event)
{
    if(event.keyCode == 13 || event.which == 13){
        send_msg()
    }
}

// This function makes a request to the server then returns a promise
function makeRequest (method, url, data = '') {
  return new Promise(function (resolve, reject) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.onload = function () {
      if (this.status >= 200 && this.status < 300) {
        resolve(xhr.response);
      } else {
        reject({
          status: this.status,
          statusText: xhr.statusText
        });
      }
    };
    xhr.onerror = function () {
      reject({
        status: this.status,
        statusText: xhr.statusText
      });
    };
    if(data != '')
    {
        xhr.send(data);
    }else{
        xhr.send();
    }
    
  });
}

function send_msg()
{
    //display user message in the chat window
    var message = document.getElementById('message').value.toLowerCase();
    if (message != '')
    {
        add_msg(message)

        var data = new FormData();
        data.append('sess', sessionStorage.getItem('session'))
        data.append('msg', message);

        makeRequest('POST', '/query',data)
            .then(function (resp) {
                data = JSON.parse(resp)
                add_response(data['msg'], document.getElementById("response-body").lastChild.firstChild)
            })
            .catch(function (err) {
                console.error('Augh, there was an error!', err.statusText);
            });
    
        //Clear the input field
        document.getElementById('message').value = ''
    }
   
}

function approve(event)
{
    var input_grp = event.target.parentNode.parentNode;
    var user_msg = event.target.parentNode.parentNode.parentNode.parentNode.childNodes[0].innerText;
    var bot_resp = event.target.parentNode.parentNode.parentNode.parentNode.childNodes[1].innerText;
    

    var data = new FormData();
    data.append('query', user_msg);
    data.append('response', bot_resp);
    data.append('status', 'approved');

     makeRequest('POST', '/save',data)
        .then(function (resp) {
            console.log('Got approval, Thanks!')
            disable_buttons(input_grp); 
        })
        .catch(function (err) {
                console.error('Augh, there was an error!', err.statusText);
        });
}

function reject(event)
{
    
    var input_grp = event.target.parentNode.parentNode;
    /*
    var user_msg = event.target.parentNode.parentNode.parentNode.parentNode.childNodes[0].innerText;
    var bot_resp = event.target.parentNode.parentNode.parentNode.parentNode.childNodes[1].innerText;

    var data = new FormData();
    data.append('query', user_msg);
    data.append('response', bot_resp);
    data.append('status', 'rejected');

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/save', true);
    xhr.onload = function () {
        var json = JSON.parse(this.responseText);
    };
    xhr.send(data);
    */
    disable_buttons(input_grp);  
}

function suggest(event)
{
    var input_grp = event.target.parentNode.parentNode;
    var user_msg = event.target.parentNode.parentNode.parentNode.parentNode.childNodes[0].innerText;
    var user_sug = event.target.parentNode.parentNode.childNodes[3].firstChild.value;
    
    if(user_sug != '')
    {
        var data = new FormData();
        data.append('query', user_msg);
        data.append('response', user_sug);
        data.append('status', 'suggestion');

        makeRequest('POST', '/save',data)
            .then(function (resp) {
                console.log('Got suggestion, Thanks!')
                disable_buttons(input_grp); 
            })
            .catch(function (err) {
                console.error('Augh, there was an error!', err.statusText);
            });
    }
}

function disable_buttons(obj)
{
    for (i=0; i < 4; i++){
        obj.childNodes[i].firstChild.setAttribute("disabled","disabled");
        //obj.childNodes[i].firstChild.style.visibility = 'hidden';
    }
}

function add_msg(msg)
{
     //console.log(msg)
     var html = [
                    '<div class="jumbotron" id="user-query">',
                        '<div class="bubble me">',
                            msg,
                        '</div>',
                    '</div>'].join('');

    var div = document.createElement('div');
    div.innerHTML = html;
    document.getElementById('response-body').appendChild(div);
    scroll_bottom()
}

function add_response(msg, obj)
{
    var html = [
                    '<div class="bubble you">',
                     msg,
                    '</div>',
                    ].join('');

    obj.insertAdjacentHTML('beforeend', html)
    scroll_bottom() 
}

function scroll_bottom() 
{
  var elem = document.getElementById('content');
  elem.scrollTop = elem.scrollHeight;
}
