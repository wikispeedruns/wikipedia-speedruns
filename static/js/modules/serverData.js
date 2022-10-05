let serverData = {};

function setServerData(obj) {
    serverData = obj;
    console.log(serverData)
}
console.log(serverData)

export { serverData, setServerData };

