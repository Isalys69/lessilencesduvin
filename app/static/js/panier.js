function ajouterPanier(id) {
  fetch('/panier/ajouter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vin_id: id })
  })
  .then(async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      window.location.reload();
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