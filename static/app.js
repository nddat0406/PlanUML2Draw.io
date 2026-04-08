(() => {
    "use strict";

    const inputEl    = document.getElementById("plantuml-input");
    const outputEl   = document.getElementById("drawio-output");
    const formatSel  = document.getElementById("format-select");
    const convertBtn = document.getElementById("convert-btn");
    const copyBtn    = document.getElementById("copy-btn");
    const downloadBtn = document.getElementById("download-btn");
    const errorBanner = document.getElementById("error-banner");

    let lastResult = null;
    let lastFormat = null;

    function showError(msg) {
        errorBanner.textContent = msg;
        errorBanner.classList.remove("hidden");
    }

    function hideError() {
        errorBanner.classList.add("hidden");
    }

    function setOutputButtons(enabled) {
        copyBtn.disabled = !enabled;
        downloadBtn.disabled = !enabled;
    }

    // ── Convert ────────────────────────────────
    convertBtn.addEventListener("click", async () => {
        hideError();
        const plantuml = inputEl.value.trim();
        if (!plantuml) {
            showError("Please enter some PlantUML content.");
            return;
        }

        convertBtn.classList.add("loading");
        convertBtn.disabled = true;
        setOutputButtons(false);
        outputEl.value = "";
        lastResult = null;

        try {
            const resp = await fetch("/convert", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    plantuml: plantuml,
                    format: formatSel.value,
                }),
            });

            const data = await resp.json();

            if (!resp.ok) {
                showError(data.error || "Conversion failed.");
                return;
            }

            lastResult = data.result;
            lastFormat = data.format;
            outputEl.value = data.result;
            setOutputButtons(true);
        } catch (err) {
            showError("Network error: " + err.message);
        } finally {
            convertBtn.classList.remove("loading");
            convertBtn.disabled = false;
        }
    });

    // ── Copy ───────────────────────────────────
    copyBtn.addEventListener("click", () => {
        if (!lastResult) return;
        navigator.clipboard.writeText(lastResult).then(() => {
            copyBtn.textContent = "Copied!";
            copyBtn.classList.add("copied");
            setTimeout(() => {
                copyBtn.textContent = "Copy";
                copyBtn.classList.remove("copied");
            }, 1500);
        });
    });

    // ── Download ───────────────────────────────
    downloadBtn.addEventListener("click", () => {
        if (!lastResult) return;
        const isJson = formatSel.value === "json";
        const ext = isJson ? ".json" : ".drawio";
        const mime = isJson ? "application/json" : "application/xml";

        const blob = new Blob([lastResult], { type: mime });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "diagram" + ext;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // ── Keyboard shortcut: Ctrl+Enter to convert ──
    inputEl.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            convertBtn.click();
        }
    });
})();
