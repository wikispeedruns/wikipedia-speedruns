// Functions for navbar

async function handleLogout()
{
    await fetch("/api/users/logout", {method : "POST"});
    window.location.href = "/";
}

window.addEventListener("onload", function() {
    document.getElementById("logout").onclick = handleLogout;
});
