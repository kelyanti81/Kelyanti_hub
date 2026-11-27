
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.dataset.confirm;
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll(".panel, .dashboard-card").forEach((element, index) => {
        element.style.animation = `hubAppear .35s ease ${index * 0.04}s both`;
    });

    if ("serviceWorker" in navigator && location.protocol === "https:") {
        navigator.serviceWorker.register("/service-worker.js")
            .catch((error) => console.error("Service Worker :", error));
    }
});

const style = document.createElement("style");
style.textContent = `
@keyframes hubAppear {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}`;
document.head.appendChild(style);
