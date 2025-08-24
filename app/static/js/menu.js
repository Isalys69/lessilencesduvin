// Script pour ouvrir/fermer le menu sur mobile

    const burgerBtn = document.getElementById('burgerBtn');
    const sidebarMenu = document.getElementById('sidebarMenu');
    const boutiqueMain = document.querySelector('.boutique-main');
    const sidebarOverlay = document.getElementById('sidebarOverlay');


    // Ouvre le menu burger
    burgerBtn.onclick = function() {
        sidebarMenu.classList.toggle('open');
        burgerBtn.classList.toggle('open');

        // On affiche l’overlay si menu ouvert
        if (sidebarMenu.classList.contains('open')) {
            // Calcule la largeur réelle du menu latéral
            const menuWidth = sidebarMenu.offsetWidth;
            boutiqueMain.style.transform = `translateX(${menuWidth}px)`;
            boutiqueMain.style.transition = "transform 0.25s";
            sidebarOverlay.style.display = 'block';
        } else {
            boutiqueMain.style.transform = 'translateX(0)';
            sidebarOverlay.style.display = 'none';
        }
    };

    // Ferme le menu si clic sur overlay
    sidebarOverlay.onclick = function() {
        sidebarMenu.classList.remove('open');
        burgerBtn.classList.remove('open');
        boutiqueMain.style.transform = 'translateX(0)';
        sidebarOverlay.style.display = 'none';
    };
