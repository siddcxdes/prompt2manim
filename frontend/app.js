// ============================================
// app.js - Frontend logic for Prompt2Manim
// ============================================

// save the current plan so we can use it later for rendering
var currentPlan = null;


// --- UI HELPERS ---

function showElement(id) {
    document.getElementById(id).style.display = "";
}

function hideElement(id) {
    document.getElementById(id).style.display = "none";
}

function setStatus(text, type) {
    // type can be: "ready", "busy", "error"
    var dot = document.getElementById("statusDot");
    var label = document.getElementById("statusText");

    dot.className = "status-dot";
    if (type === "busy") {
        dot.classList.add("busy");
    } else if (type === "error") {
        dot.classList.add("error");
    }
    label.textContent = text;
}

function showError(message) {
    var box = document.getElementById("errorBox");
    var text = document.getElementById("errorText");
    text.textContent = message;
    box.style.display = "";
}

function hideError() {
    document.getElementById("errorBox").style.display = "none";
}


// --- EXAMPLE PROMPTS ---

function useExample(text) {
    document.getElementById("promptInput").value = text;
}


// --- GENERATE ---

function handleGenerate() {
    var prompt = document.getElementById("promptInput").value.trim();

    if (prompt === "") {
        showError("Please type a prompt first.");
        return;
    }

    // reset everything
    hideError();
    currentPlan = null;
    hideElement("emptyState");
    hideElement("planPreview");
    hideElement("videoSection");
    showElement("loadingState");

    // disable the button while working
    var btn = document.getElementById("generateBtn");
    btn.disabled = true;
    btn.textContent = "Working...";

    setStatus("Generating plan...", "busy");
    document.getElementById("loadingText").textContent = "Sending prompt to AI...";

    // call the backend
    fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt })
    })
    .then(function(response) {
        return response.json().then(function(data) {
            return { ok: response.ok, data: data };
        });
    })
    .then(function(result) {
        hideElement("loadingState");
        btn.disabled = false;
        btn.textContent = "Generate";

        if (!result.ok) {
            // something went wrong
            showError(result.data.error || "Something went wrong.");
            showElement("emptyState");
            setStatus("Error", "error");
            return;
        }

        // success! show the plan
        currentPlan = result.data.plan;
        showPlan(result.data.plan, result.data.summary);
        setStatus("Plan ready", "ready");
    })
    .catch(function(err) {
        hideElement("loadingState");
        showElement("emptyState");
        btn.disabled = false;
        btn.textContent = "Generate";
        showError("Network error. Is the server running?");
        setStatus("Error", "error");
    });
}


// --- SHOW PLAN ---

function showPlan(plan, summary) {
    // show stats
    var statsDiv = document.getElementById("planStats");
    statsDiv.innerHTML = ""
        + '<div class="stat"><span class="stat-val">' + summary.total_steps + '</span><span class="stat-lbl">Steps</span></div>'
        + '<div class="stat"><span class="stat-val">' + summary.total_duration.toFixed(1) + 's</span><span class="stat-lbl">Duration</span></div>';

    // show steps
    var listDiv = document.getElementById("stepsList");
    listDiv.innerHTML = "";

    var steps = plan.steps;
    for (var i = 0; i < steps.length; i++) {
        var step = steps[i];
        var row = document.createElement("div");
        row.className = "step-row";
        row.innerHTML = ""
            + '<span class="step-num">' + (i + 1) + '</span>'
            + '<span class="step-badge type-' + step.type + '">' + step.type + '</span>'
            + '<span class="step-content">' + escapeHtml(step.content) + '</span>'
            + '<span class="step-dur">' + step.duration + 's</span>';
        listDiv.appendChild(row);
    }

    showElement("planPreview");
}


// --- RENDER ---

function handleRender() {
    if (currentPlan === null) {
        showError("No plan to render. Generate one first.");
        return;
    }

    var quality = document.getElementById("qualitySelect").value;

    hideError();
    hideElement("planPreview");
    showElement("loadingState");

    var renderBtn = document.getElementById("renderBtn");
    renderBtn.disabled = true;

    setStatus("Rendering...", "busy");
    document.getElementById("loadingText").textContent = "Rendering animation with Manim... This may take a minute.";

    fetch("/api/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan: currentPlan, quality: quality })
    })
    .then(function(response) {
        return response.json().then(function(data) {
            return { ok: response.ok, data: data };
        });
    })
    .then(function(result) {
        hideElement("loadingState");
        renderBtn.disabled = false;

        if (!result.ok) {
            showElement("planPreview");
            showError(result.data.error || "Rendering failed.");
            setStatus("Render failed", "error");
            return;
        }

        // success! show the video
        var video = document.getElementById("videoPlayer");
        video.src = result.data.video_url;

        var downloadBtn = document.getElementById("downloadBtn");
        downloadBtn.href = result.data.video_url;

        showElement("videoSection");
        setStatus("Video ready", "ready");
    })
    .catch(function(err) {
        hideElement("loadingState");
        showElement("planPreview");
        renderBtn.disabled = false;
        showError("Network error during rendering.");
        setStatus("Error", "error");
    });
}


// --- RESET ---

function resetAll() {
    currentPlan = null;
    hideElement("planPreview");
    hideElement("videoSection");
    hideElement("loadingState");
    hideError();
    showElement("emptyState");
    document.getElementById("promptInput").value = "";
    setStatus("Ready", "ready");
}


// --- UTILITY ---

function escapeHtml(text) {
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}
