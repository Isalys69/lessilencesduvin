function validateAge(isAdult) {
    if (isAdult) {
        // Crée un cookie de session (pas de durée → supprimé à la fermeture du navigateur)
        document.cookie = "age_verified=true; path=/";
        document.getElementById("age-gate").style.display = "none";
        document.getElementById("cookie-banner").style.display = "block"; // <-- Affiche le bandeau
    } else {
        window.location.href = "https://www.alcool-info-service.fr/";
    }
}

window.onload = function() {
    if (!document.cookie.includes("age_verified=true")) {
        document.getElementById("age-gate").style.display = "block";
    } else {
        document.getElementById("cookie-banner").style.display = "block"; // <-- Affiche le bandeau si cookie existe déjà
    }
}
