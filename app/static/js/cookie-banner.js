function acceptCookies() {
    // durée en jours (ici 180 = 6 mois, conforme CNIL)
    const days = 180;
    document.cookie = "age_verified=true; path=/; max-age=" + days*24*60*60;
    document.getElementById("cookie-banner").style.display = "none";
}

window.onload = function() {
    if (!document.cookie.includes("age_verified=true")) {
        document.getElementById("cookie-banner").style.display = "block";
    }
}
