

async function sendBeaconJson(path, data)
{
     let params = new Blob(
         [JSON.stringify(data)], 
         {type : 'application/json'}
     );

    try {
        navigator.sendBeacon(path, params);
    } catch(err) {
        console.log('Error sending beacon: ' + err);
    }
}

export { sendBeaconJson };