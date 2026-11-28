
document.addEventListener("DOMContentLoaded", () => {
    // Service worker
    if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
            navigator.serviceWorker.register("/service-worker.js").catch(() => {});
        });
    }

    // Confirmation des formulaires
    document.querySelectorAll("form[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!confirm(form.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    // Présence du membre connecté
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

    // Statut du serveur Dell et de Minecraft
    const dellBox = document.getElementById("dell-dashboard-status");

    if (dellBox) {
        const dellLabel = document.getElementById("dell-online-label");
        const minecraftLabel = document.getElementById("minecraft-online-label");
        const details = document.getElementById("dell-details");
        const lastUpdate = document.getElementById("dell-last-update");

        const setStatus = (element, online, name) => {
            if (!element) return;

            element.textContent = online ? "En ligne" : "Hors ligne";
            element.classList.toggle("status-online", online);
            element.classList.toggle("status-offline", !online);
        };

        const refreshDell = async () => {
            try {
                const response = await fetch("/api/dell/status", {
                    credentials: "same-origin",
                    cache: "no-store"
                });

                if (!response.ok) {
                    throw new Error("Statut indisponible");
                }

                const status = await response.json();

                setStatus(dellLabel, status.online, "Dell");
                setStatus(minecraftLabel, status.minecraft, "Minecraft");

                if (details) {
                    const data = status.data || {};
                    const lines = [];

                    if (data.cpu_percent !== undefined) {
                        lines.push("Processeur : " + data.cpu_percent + " %");
                    }

                    if (data.ram_percent !== undefined) {
                        lines.push("Mémoire RAM : " + data.ram_percent + " %");
                    }

                    if (data.ram_used_gb !== undefined && data.ram_total_gb !== undefined) {
                        lines.push(
                            "RAM utilisée : " +
                            data.ram_used_gb + " / " +
                            data.ram_total_gb + " Go"
                        );
                    }

                    details.textContent = lines.length
                        ? lines.join(" · ")
                        : (status.online
                            ? "Serveur connecté. En attente des informations système."
                            : "Le serveur Dell ne communique pas actuellement.");
                }

                if (lastUpdate) {
                    const age = Number(status.age || 0);

                    lastUpdate.textContent = status.online
                        ? "Dernière communication : il y a " + Math.max(0, Math.round(age)) + " seconde(s)"
                        : "Aucune communication récente";
                }

            } catch (_) {
                setStatus(dellLabel, false, "Dell");
                setStatus(minecraftLabel, false, "Minecraft");

                if (details) {
                    details.textContent = "Impossible de récupérer le statut du serveur.";
                }

                if (lastUpdate) {
                    lastUpdate.textContent = "Statut indisponible";
                }
            }
        };

        refreshDell();
        window.setInterval(refreshDell, 20000);
    }

    // Membres actuellement en ligne (administrateur)
    const onlineBox = document.getElementById("online-members");

    if (onlineBox && csrf) {
        const refreshOnline = async () => {
            try {
                const response = await fetch("/api/admin/presence", {
                    credentials: "same-origin",
                    cache: "no-store"
                });

                if (!response.ok) {
                    throw new Error("Erreur");
                }

                const result = await response.json();
                const members = result.online || [];

                if (!members.length) {
                    onlineBox.textContent = "Aucun membre en ligne actuellement.";
                    return;
                }

                onlineBox.replaceChildren();

                members.forEach((member) => {
                    const line = document.createElement("div");
                    line.className = "online-member";

                    const name = document.createElement("strong");
                    name.textContent = member.display_name || member.username || "Membre";

                    const detail = document.createElement("small");
                    detail.textContent =
                        (member.username || "") + " · " + (member.grade || "");

                    line.append(name, detail);
                    onlineBox.append(line);
                });

            } catch (_) {
                onlineBox.textContent =
                    "Impossible de charger la présence pour le moment.";
            }
        };

        refreshOnline();
        window.setInterval(refreshOnline, 20000);
    }
});
