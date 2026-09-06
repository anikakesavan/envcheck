import { compare, scaffold } from "./calc.mjs";

const envInput = document.getElementById("env-input");
const exampleInput = document.getElementById("example-input");
const envFile = document.getElementById("env-file");
const exampleFile = document.getElementById("example-file");
const checkBtn = document.getElementById("check-btn");
const scaffoldBtn = document.getElementById("scaffold-btn");
const resultsEl = document.getElementById("results");

async function wireFileInput(fileInput, textArea) {
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files?.[0];
    if (!file) return;
    textArea.value = await file.text();
    fileInput.value = "";
  });
}

wireFileInput(envFile, envInput);
wireFileInput(exampleFile, exampleInput);

function renderResults() {
  const exampleText = exampleInput.value;
  if (!exampleText.trim()) {
    resultsEl.innerHTML = `<p class="empty-state">Paste or drop a .env.example to compare against.</p>`;
    return;
  }

  const result = compare(envInput.value, exampleText);

  if (result.isClean && result.extra.length === 0) {
    resultsEl.innerHTML = `<p class="ok-state">✓ Matches — nothing to report.</p>`;
    return;
  }

  const sections = [];
  if (result.missing.length) {
    sections.push(renderList("Missing", result.missing, "bad"));
  }
  if (result.empty.length) {
    sections.push(renderList("Empty", result.empty, "bad"));
  }
  if (result.extra.length) {
    sections.push(renderList("Extra (not in example)", result.extra, "warn"));
  }
  resultsEl.innerHTML = sections.join("");
}

function renderList(title, keys, tone) {
  const items = keys.map((k) => `<li>${escapeHtml(k)}</li>`).join("");
  return `
    <div class="result-group result-group--${tone}">
      <h3>${title} (${keys.length})</h3>
      <ul>${items}</ul>
    </div>
  `;
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

checkBtn.addEventListener("click", renderResults);
envInput.addEventListener("input", renderResults);
exampleInput.addEventListener("input", renderResults);

scaffoldBtn.addEventListener("click", () => {
  if (!exampleInput.value.trim()) return;
  const { text, added } = scaffold(envInput.value, exampleInput.value);
  envInput.value = text;
  renderResults();
  if (added > 0) {
    resultsEl.insertAdjacentHTML(
      "afterbegin",
      `<p class="ok-state">Filled in ${added} missing key(s) above — copy the updated .env out when you're ready.</p>`,
    );
  }
});

renderResults();
