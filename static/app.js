
// Kelyanti Hub - Application JavaScript

document.addEventListener("DOMContentLoaded", () => {

    // Animation d'apparition des panneaux
    const panels = document.querySelectorAll(
        ".panel, .dashboard-card, .login-card"
    );

    panels.forEach((panel, index) => {
        panel.style.animation = `hubAppear 0.35s ease ${index * 0.05}s both`;
    });

    // Confirmation avant suppression d'un membre
    document.querySelectorAll("form[data-confirm]").forEach(form => {
        form.addEventListener("submit", event => {
            const message = form.dataset.confirm;

            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Fermeture des notifications
    document.querySelectorAll(".notice").forEach(notice => {
        setTimeout(() => {
            notice.classList.add("notice-hidden");
        }, 6000);
    });

});

// Installation PWA
if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/service-worker.js")
            .then(registration => {
                console.log("Kelyanti Hub : application prête", registration.scope);
            })
            .catch(error => {
                console.error("Erreur PWA :", error);
            });
    });
}
