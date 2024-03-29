
function getLocalStorage(key) {
    const data = localStorage.getItem(key);
    return JSON.parse(data);
}

function setLocalStorage(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function getLocalStorageRuns(key) {
    let prev_data = localStorage.getItem(key);
    if (prev_data) return JSON.parse(prev_data);
    return {}
}

function setLocalStorageRuns(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function addRunToLocalStorage(key, data) {
    let prev_data = getLocalStorageRuns(key);
    prev_data[data['run_id']] = data;
    setLocalStorageRuns(key, prev_data);
}

export { getLocalStorage, setLocalStorage, getLocalStorageRuns, addRunToLocalStorage, setLocalStorageRuns };

