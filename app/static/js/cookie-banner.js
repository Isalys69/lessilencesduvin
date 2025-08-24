// cookie-banner.js – gestion du bandeau RGPD cookies

function acceptCookies() {
    // Crée un cookie de session (disparaît à la fermeture du navigateur)
    document.cookie = "cookies_accepted=true; path=/";

    // Ancienne version pour un cookie persistant :
    // const d = new Date();
    // d.setTime(d.getTime() + (180*24*60*60*1000)); // 180 jours
    // document.cookie = "cookies_accepted=true; expires=" + d.toUTCString() + "; path=/";

    document.getElementById('cookie-banner').style.display = 'none';
}

function hasCookie(name) {
    return document.cookie.split(';').some(c => c.trim().startsWith(name + '='));
}

window.onload = function() {
    if (!hasCookie('cookies_accepted')) {
        document.getElementById('cookie-banner').style.display = 'block';
    }
}
