// Functions for navbar

async function handleLogout(event)
{
    event.preventDefault();
    await fetch("/api/users/logout", {method : "POST"});
    window.location.href = "/";
}

window.addEventListener("load", function() {
    document.getElementById("logout").onclick = handleLogout;
});
