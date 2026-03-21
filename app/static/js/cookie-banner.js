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

    if (hasVerifiedAge) {
        // ✅ Cache l’age gate et affiche le bandeau cookie
        document.getElementById("age-gate").style.display = "none";
        document.getElementById("cookie-banner").style.display = "block";
    }
    // Sinon : age gate reste visible (display:block par défaut dans le HTML)
};
