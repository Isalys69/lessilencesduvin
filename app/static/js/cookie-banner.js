function validateAge(isAdult) {
    if (isAdult) {
        // Crée un cookie de session (pas de durée → supprimé à la fermeture du navigateur)
        document.cookie = "age_verified=true; path=/";
        window.location.href = "/"; // recharge vers la page d’accueil
    } else {
        window.location.href = "https://sante.gouv.fr/IMG/pdf/affiche_vente_a_emporter_-_affichage_caisses_enregistreuses_a5.pdf";
    }
}

window.onload = function() {
    if (!document.cookie.includes("age_verified=true")) {
        document.getElementById("age-gate").style.display = "block";
    } else {
        document.getElementById("cookie-banner").style.display = "block"; // <-- Affiche le bandeau si cookie existe déjà
    }
}
