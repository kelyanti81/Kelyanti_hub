document.addEventListener("DOMContentLoaded", () => {
    if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
            navigator.serviceWorker.register("/service-worker.js").catch(() => {});
        });
    }

    document.querySelectorAll("form[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!confirm(form.dataset.confirm)) event.preventDefault();
        });
    });

    const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
    const heartbeat = async () => {
        if (!csrf) return;
        try {
            await fetch("/api/presence", {
                method: "POST",
                headers: { "X-CSRF-Token": csrf },
                credentials: "same-origin"
            });
        } catch (_) {}
    };
    heartbeat();
    window.setInterval(heartbeat, 35000);

    const onlineBox = document.getElementById("online-members");
    if (onlineBox && csrf) {
        const refreshOnline = async () => {
            try {
                const response = await fetch("/api/admin/presence", { credentials: "same-origin" });
                if (!response.ok) throw new Error("Erreur");
                const result = await response.json();
                if (!result.online.length) {
                    onlineBox.innerHTML = "<p>Aucun membre en ligne actuellement.</p>";
                    return;
                }
                onlineBox.replaceChildren();
                result.online.forEach((member) => {
                    const line = document.createElement("div");
                    line.className = "online-member";
                    const name = document.createElement("strong");
                    name.textContent = member.display_name;
                    const detail = document.createElement("small");
                    detail.textContent = member.username + " · " + member.grade;
                    line.append(name, detail);
                    onlineBox.append(line);
                });
            } catch (_) {
                onlineBox.textContent = "Impossible de charger la présence pour le moment.";
            }
        };
        refreshOnline();
        window.setInterval(refreshOnline, 20000);
    }
});
