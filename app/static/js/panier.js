function ajouterPanier(id) {
  fetch('/panier/ajouter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vin_id: id })
  })
  .then(async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      alert(data.message || "Impossible d’ajouter ce vin au panier.");
      return;
    }
    majCompteurPanier();
  })
  .catch(err => console.error('Erreur panier :', err));
}

function majCompteurPanier() {
  fetch("/panier/compteur")
    .then(res => res.json())
    .then(data => {
      const compteur = document.getElementById("compteur-panier");
      if (compteur) compteur.textContent = data.compteur;
    })
    .catch(err => console.error("Erreur mise à jour compteur :", err));
}


document.addEventListener("click", (e) => {
  const btn = e.target.closest(".js-ajouter-panier");
  if (!btn) return;

  // Si bouton marqué comme désactivé
  const isDisabled =
    btn.classList.contains("disabled") ||
    btn.getAttribute("aria-disabled") === "true";

  if (isDisabled) {
    const msg =
      btn.dataset.disabledReason || "Action indisponible.";
    alert(msg);
    return;
  }

  const vinId = parseInt(btn.dataset.vinId, 10);
  if (!vinId) return;

  ajouterPanier(vinId);
});