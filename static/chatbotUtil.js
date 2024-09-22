function sendBotRes() {
    const msg = document.getElementById('chatInp').value;
    const data = {
        input: msg
    };

    fetch('/prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            console.log(result)
            document.getElementById('chatResponse').textContent = result.response;
        })
        .catch(error => {
            console.error(error);
        });
}

function sendUserInfo() {
    const name = document.getElementById('name').value;
    const age = document.getElementById('age').value;
    const sex = document.getElementById('sex').value;
    
    const data = {
        name: name,
        age: age,
        sex: sex,
    };

    fetch('/get_user_info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            console.log(result)
            //document.getElementById('chatResponse').textContent = result.response;
        })
        .catch(error => {
            console.error(error);
        });
}


