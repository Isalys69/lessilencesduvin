function validateAge(isAdult) {
    if (isAdult) {
        // ✅ Crée un cookie temporaire (valide le temps de la session)
        document.cookie = "age_verified=true; path=/";

        // ✅ Cache simplement le Age Gate sans recharger toute la page
        document.getElementById("age-gate").style.display = "none";

        // ✅ Affiche ensuite le bandeau cookie
        document.getElementById("cookie-banner").style.display = "block";
    } else {
        // 🔗 Redirection officielle vers affichage légal (Santé publique)
        window.location.href = "https://sante.gouv.fr/IMG/pdf/affiche_vente_a_emporter_-_affichage_caisses_enregistreuses_a5.pdf";
    }
}

window.onload = function() {
    const hasVerifiedAge = document.cookie.includes("age_verified=true");

    if (!hasVerifiedAge) {
        // 🔒 Affiche le Age Gate → bloque l’accès
        document.getElementById("age-gate").style.display = "block";

        // 🚫 Cache le bandeau cookie tant que l’âge n’est pas validé
        document.getElementById("cookie-banner").style.display = "none";
    } else {
        // ✅ Affiche le bandeau cookie normal
        document.getElementById("cookie-banner").style.display = "block";
    }
};
