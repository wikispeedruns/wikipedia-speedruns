

function getLocalStorageRuns(key) {
    let prev_data = localStorage.getItem(key);
    if (prev_data) return JSON.parse(prev_data);
    return {}
}

function setLocalStorageRuns(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function addRunToLocalStorage(key, data) {
    let prev_data = getLocalStorageRuns();
    const ind = Object.keys(prev_data).length
    prev_data[ind] = data;
    setLocalStorageRuns(key, prev_data);

    return ind;
}

export { getLocalStorageRuns, addRunToLocalStorage, setLocalStorageRuns };

