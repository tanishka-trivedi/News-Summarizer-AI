// ---------------- Theme toggle ----------------
const root = document.documentElement;
const themeToggle = document.getElementById("theme-toggle");

function applyTheme(theme) {
  root.setAttribute("data-theme", theme);
  localStorage.setItem("lucid-theme", theme);
}

(function initTheme() {
  const saved = localStorage.getItem("lucid-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(saved || (prefersDark ? "dark" : "light"));
})();

themeToggle.addEventListener("click", () => {
  const current = root.getAttribute("data-theme");
  applyTheme(current === "dark" ? "light" : "dark");
});

// ---------------- Tabs ----------------
const tabButtons = document.querySelectorAll(".tab-btn");
const panelText = document.getElementById("panel-text");
const panelUrl = document.getElementById("panel-url");
let activeTab = "text";

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    activeTab = btn.dataset.tab;
    panelText.classList.toggle("hidden", activeTab !== "text");
    panelUrl.classList.toggle("hidden", activeTab !== "url");
  });
});

// ---------------- Options ----------------
const modeSelect = document.getElementById("mode-select");
const numSentences = document.getElementById("num-sentences");
const numSentencesValue = document.getElementById("num-sentences-value");
const sentenceCountWrap = document.getElementById("sentence-count-wrap");

numSentences.addEventListener("input", () => {
  numSentencesValue.textContent = numSentences.value;
});

modeSelect.addEventListener("change", () => {
  sentenceCountWrap.style.opacity = modeSelect.value === "abstractive" ? "0.4" : "1";
  sentenceCountWrap.style.pointerEvents = modeSelect.value === "abstractive" ? "none" : "auto";
});

// ---------------- Summarize ----------------
const summarizeBtn = document.getElementById("summarize-btn");
const btnLabel = summarizeBtn.querySelector(".btn-label");
const btnSpinner = summarizeBtn.querySelector(".btn-spinner");
const errorMsg = document.getElementById("error-msg");

const outputEmpty = document.getElementById("output-empty");
const outputResult = document.getElementById("output-result");
const summaryText = document.getElementById("summary-text");
const statSource = document.getElementById("stat-source");
const statSummary = document.getElementById("stat-summary");
const statMode = document.getElementById("stat-mode");
const copyBtn = document.getElementById("copy-btn");

function setLoading(isLoading) {
  summarizeBtn.disabled = isLoading;
  btnLabel.classList.toggle("hidden", isLoading);
  btnSpinner.classList.toggle("hidden", !isLoading);
}

function showError(message) {
  errorMsg.textContent = message;
  errorMsg.classList.remove("hidden");
}

function clearError() {
  errorMsg.classList.add("hidden");
  errorMsg.textContent = "";
}

summarizeBtn.addEventListener("click", async () => {
  clearError();

  const payload = {
    mode: modeSelect.value,
    num_sentences: Number(numSentences.value),
  };

  if (activeTab === "url") {
    const url = document.getElementById("article-url").value.trim();
    if (!url) {
      showError("Please enter a URL.");
      return;
    }
    payload.url = url;
  } else {
    const text = document.getElementById("article-text").value.trim();
    if (!text) {
      showError("Please paste some article text.");
      return;
    }
    payload.text = text;
  }

  setLoading(true);
  try {
    const res = await fetch("/api/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }

    summaryText.textContent = data.summary;
    statSource.textContent = `Source: ${data.source_word_count} words`;
    statSummary.textContent = `Summary: ${data.summary_word_count} words`;
    statMode.textContent = data.mode === "abstractive" ? "AI-generated" : "Extractive";

    outputEmpty.classList.add("hidden");
    outputResult.classList.remove("hidden");
    copyBtn.classList.remove("hidden");
  } catch (err) {
    showError("Could not reach the server. Please check your connection and try again.");
  } finally {
    setLoading(false);
  }
});

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(summaryText.textContent).then(() => {
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
  });
});
