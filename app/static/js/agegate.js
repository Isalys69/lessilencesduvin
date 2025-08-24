// Script de vérification d’âge – active ou désactive le bouton d’entrée

const checkbox = document.getElementById('confirmAge');
const enterBtn = document.getElementById('enterBtn');

checkbox.addEventListener('change', () => {
    if (checkbox.checked) {
        enterBtn.classList.remove("disabled");
    } else {
        enterBtn.classList.add("disabled");
    }
});
