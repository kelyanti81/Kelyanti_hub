document.addEventListener("DOMContentLoaded", () => {
    // Enregistrement du service worker pour la PWA.
    if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
            navigator.serviceWorker.register("/service-worker.js")
                .catch((error) => {
                    console.error("Service worker :", error);
                });
        });
    }

    // Confirmation avant les suppressions.
    document.querySelectorAll("form[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!confirm(form.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });
});