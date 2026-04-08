(() => {
    "use strict";

    const inputEl    = document.getElementById("plantuml-input");
    const outputEl   = document.getElementById("drawio-output");
    const formatSel  = document.getElementById("format-select");
    const convertBtn = document.getElementById("convert-btn");
    const batchConvertBtn = document.getElementById("batch-convert-btn");
    const copyBtn    = document.getElementById("copy-btn");
    const downloadBtn = document.getElementById("download-btn");
    const fileInput = document.getElementById("file-input");
    const selectedFiles = document.getElementById("selected-files");
    const errorBanner = document.getElementById("error-banner");
    const batchStatus = document.getElementById("batch-status");

    let lastResult = null;
    let lastFormat = null;

    function showError(msg) {
        errorBanner.textContent = msg;
        errorBanner.classList.remove("hidden");
    }

    function hideError() {
        errorBanner.classList.add("hidden");
    }

    function showBatchStatus(message) {
        batchStatus.textContent = message;
        batchStatus.classList.remove("hidden");
    }

    function hideBatchStatus() {
        batchStatus.classList.add("hidden");
    }

    function setOutputButtons(enabled) {
        copyBtn.disabled = !enabled;
        downloadBtn.disabled = !enabled;
    }

    function triggerDownload(blob, filename) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    function updateSelectedFilesLabel() {
        const { files } = fileInput;
        if (!files || files.length === 0) {
            selectedFiles.textContent = "No files selected";
            return;
        }

        const fileNames = Array.from(files).map((file) => file.name);
        if (fileNames.length <= 3) {
            selectedFiles.textContent = fileNames.join(", ");
            return;
        }

        selectedFiles.textContent = `${fileNames.slice(0, 3).join(", ")} +${fileNames.length - 3} more`;
    }

    // ── Convert ────────────────────────────────
    convertBtn.addEventListener("click", async () => {
        hideError();
        hideBatchStatus();
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

    fileInput.addEventListener("change", updateSelectedFilesLabel);

    batchConvertBtn.addEventListener("click", async () => {
        hideError();
        hideBatchStatus();

        if (!fileInput.files || fileInput.files.length === 0) {
            showError("Please choose one or more PlantUML files to convert.");
            return;
        }

        batchConvertBtn.classList.add("loading");
        batchConvertBtn.disabled = true;
        setOutputButtons(false);
        outputEl.value = "";
        lastResult = null;
        lastFormat = null;

        try {
            const formData = new FormData();
            Array.from(fileInput.files).forEach((file) => {
                formData.append("files", file);
            });
            formData.append("format", formatSel.value);

            const resp = await fetch("/convert/batch", {
                method: "POST",
                body: formData,
            });

            if (!resp.ok) {
                const errorData = await resp.json();
                showError(errorData.error || "Batch conversion failed.");
                if (Array.isArray(errorData.failed) && errorData.failed.length > 0) {
                    showBatchStatus(errorData.failed.map((item) => `${item.file}: ${item.error}`).join("\n"));
                }
                return;
            }

            const blob = await resp.blob();
            const convertedCount = resp.headers.get("X-Converted-Count") || "0";
            const failedCount = resp.headers.get("X-Failed-Count") || "0";

            triggerDownload(blob, "converted-diagrams.zip");

            outputEl.value = [
                "Batch conversion complete.",
                `Format: ${formatSel.value === "json" ? "JSON" : "Draw.io XML"}`,
                `Selected files: ${fileInput.files.length}`,
                `Converted: ${convertedCount}`,
                `Failed: ${failedCount}`,
                "",
                "The ZIP also contains conversion-report.json with the per-file results.",
            ].join("\n");
            showBatchStatus(`Downloaded converted-diagrams.zip\nConverted: ${convertedCount}\nFailed: ${failedCount}`);
        } catch (err) {
            showError("Network error: " + err.message);
        } finally {
            batchConvertBtn.classList.remove("loading");
            batchConvertBtn.disabled = false;
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

        triggerDownload(new Blob([lastResult], { type: mime }), "diagram" + ext);
    });

    // ── Keyboard shortcut: Ctrl+Enter to convert ──
    inputEl.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            convertBtn.click();
        }
    });
})();
