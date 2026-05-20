const API = "http://127.0.0.1:8000";

//State
let currentPrompt = "";
let currentOutput = "";
let currentType = "text";
let modalPromptText = "";

//Generate Prompt
async function generatePrompt(refinement = null) {
  const inputEl = document.getElementById("inputPrompt");
  const prompt = (inputEl ? inputEl.value : currentPrompt).trim();
  const token = localStorage.getItem("token");
  const btn = document.getElementById("generateBtn");
  const btnArrow = document.getElementById("btnArrow");
  const spinner = document.getElementById("btnSpinner");

  if (!token) { window.location.href = "index.html"; return; }
  if (!prompt) { alert("Please enter an idea first."); return; }

  currentPrompt = prompt;

  // Loading state
  if (btn) { btn.disabled = true; }
  if (btnArrow) btnArrow.classList.add("d-none");
  if (spinner) spinner.classList.remove("d-none");

  try {
    const res = await fetch(`${API}/enhance-prompt`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({ prompt, refinement })
    });

    if (res.status === 401) { localStorage.removeItem("token"); window.location.href = "index.html"; return; }

    const data = await res.json();
    if (!res.ok) { alert(data.detail || "Enhancement failed."); return; }

    currentOutput = data.enhanced_prompt;
    currentType = data.prompt_type;

    showResultState(prompt, data.enhanced_prompt, data.prompt_type);

    // Fetch improvement questions for right panel
    fetchQuestions(prompt, data.prompt_type);

    // Refresh history sidebar
    loadHistory();

  } catch (e) {
    console.error("Error in generatePrompt:", e);
    if (e.name === "TypeError" && e.message.includes("fetch")) {
      alert("Cannot reach server. Is the backend running?");
    } else {
      alert("An unexpected error occurred. Check the console for details.");
    }
  } finally {
    if (btn) { btn.disabled = false; }
    if (btnArrow) btnArrow.classList.remove("d-none");
    if (spinner) spinner.classList.add("d-none");
  }
}

//Show Result State
function showResultState(prompt, output, type) {
  document.getElementById("inputState").classList.add("d-none");
  document.getElementById("resultState").classList.remove("d-none");
  const rightPanel = document.getElementById("rightPanel");
  if (rightPanel) rightPanel.classList.remove("d-none");

  // Lazy prompt
  document.getElementById("lazyDisplay").textContent = prompt;

  // Badge
  const badge = document.getElementById("promptTypeBadge");
  const badgeMap = {
    image: { text: "🖼️ Image", cls: "type-badge badge-image ms-2" },
    code: { text: "💻 Code", cls: "type-badge badge-code ms-2" },
    research: { text: "🔍 Research", cls: "type-badge badge-research ms-2" },
    text: { text: "📝 Text", cls: "type-badge badge-text ms-2" },
  };
  const b = badgeMap[type] || badgeMap.text;
  badge.textContent = b.text;
  badge.className = b.cls;

  // Reset save button
  const saveBtn = document.getElementById("saveLibraryBtn");
  if (saveBtn) {
    saveBtn.textContent = "💾 Save";
    saveBtn.disabled = false;
  }
  const saveMsg = document.getElementById("saveMsg");
  if (saveMsg) saveMsg.classList.add("d-none");

  // Render formatted output
  renderPromptOutput(output);
}

//Render Structured Output
function renderPromptOutput(text, targetEl) {
  const container = targetEl || document.getElementById("outputPrompt");
  if (!container) return;
  // Split by **Section** headings
  const sectionRegex = /\*\*([^*]+)\*\*/g;
  const parts = text.split(sectionRegex);

  let html = "";

  for (let i = 1; i < parts.length; i += 2) {
    const heading = parts[i].trim();
    const body = (parts[i + 1] || "").trim();

    const bodyHtml = body
      .split("\n")
      .reduce((acc, line) => {
        const trimmed = line.trim();
        if (trimmed.startsWith("•") || trimmed.startsWith("-")) {
          const content = trimmed.replace(/^[•\-]\s*/, "");
          acc.push(`<li>${content}</li>`);
        } else if (trimmed) {
          acc.push(`<p class="mb-1">${trimmed}</p>`);
        }
        return acc;
      }, [])
      .join("");

    const wrappedBody = bodyHtml
      .replace(/(<li>.*?<\/li>)+/gs, (match) => `<ul class="mb-0">${match}</ul>`);

    html += `
      <div class="prompt-section">
        <span class="prompt-section-title">${heading}</span>
        <div class="prompt-section-body">${wrappedBody}</div>
      </div>`;
  }

  // If parsing failed (no ** headings found), just show as plain text
  if (!html) {
    html = `<p style="white-space:pre-wrap">${text}</p>`;
  }

  container.innerHTML = html;
}

//Edit Lazy Prompt
function toggleEdit() {
  const editDiv = document.getElementById("lazyEdit");
  const displayDiv = document.getElementById("lazyDisplay");
  const btn = document.getElementById("editToggleBtn");

  if (editDiv.classList.contains("d-none")) {
    document.getElementById("editInput").value = currentPrompt;
    editDiv.classList.remove("d-none");
    displayDiv.classList.add("d-none");
    btn.textContent = "✕ Cancel";
  } else {
    cancelEdit();
  }
}

function cancelEdit() {
  document.getElementById("lazyEdit").classList.add("d-none");
  document.getElementById("lazyDisplay").classList.remove("d-none");
  document.getElementById("editToggleBtn").textContent = "✏️ Edit";
}

async function saveEdit() {
  const newPrompt = document.getElementById("editInput").value.trim();
  if (!newPrompt) { alert("Prompt cannot be empty."); return; }

  currentPrompt = newPrompt;
  document.getElementById("lazyDisplay").textContent = newPrompt;
  cancelEdit();

  // Regenerate with the new prompt
  await regenerateFromEdit(newPrompt);
}

async function regenerateFromEdit(prompt) {
  const token = localStorage.getItem("token");
  const outputEl = document.getElementById("outputPrompt");
  outputEl.innerHTML = `<p class="text-muted small">Regenerating...</p>`;

  try {
    const res = await fetch(`${API}/enhance-prompt`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({ prompt })
    });

    if (res.status === 401) { localStorage.removeItem("token"); window.location.href = "index.html"; return; }

    const data = await res.json();
    if (!res.ok) { outputEl.innerHTML = `<p class="text-danger">Enhancement failed.</p>`; return; }

    currentOutput = data.enhanced_prompt;
    currentType = data.prompt_type;

    const badge = document.getElementById("promptTypeBadge");
    const badgeMap = {
      image: { text: "🖼️ Image", cls: "type-badge badge-image ms-2" },
      code: { text: "💻 Code", cls: "type-badge badge-code ms-2" },
      research: { text: "🔍 Research", cls: "type-badge badge-research ms-2" },
      text: { text: "📝 Text", cls: "type-badge badge-text ms-2" },
    };
    const b = badgeMap[data.prompt_type] || badgeMap.text;
    badge.textContent = b.text;
    badge.className = b.cls;

    // Reset save state on regeneration
    const saveBtn = document.getElementById("saveLibraryBtn");
    if (saveBtn) { saveBtn.textContent = "💾 Save"; saveBtn.disabled = false; }
    const saveMsg = document.getElementById("saveMsg");
    if (saveMsg) saveMsg.classList.add("d-none");

    renderPromptOutput(data.enhanced_prompt);
    fetchQuestions(prompt, data.prompt_type);

  } catch (e) {
    console.error("Error in regenerateFromEdit:", e);
    if (e.name === "TypeError" && e.message.includes("fetch")) {
      outputEl.innerHTML = `<p class="text-danger">Cannot reach server.</p>`;
    } else {
      outputEl.innerHTML = `<p class="text-danger">An internal error occurred.</p>`;
    }
  }
}

//Fetch Questions
async function fetchQuestions(prompt, promptType) {
  const token = localStorage.getItem("token");
  const container = document.getElementById("questionsList");
  if (!container) return;
  container.innerHTML = `<p class="text-muted small">Loading questions...</p>`;

  try {
    const res = await fetch(`${API}/suggest-questions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({ prompt, prompt_type: promptType })
    });

    const data = await res.json();
    if (!res.ok || !data.questions) { container.innerHTML = ""; return; }

    renderQuestions(data.questions);
  } catch (e) {
    container.innerHTML = "";
  }
}

function renderQuestions(questions) {
  const container = document.getElementById("questionsList");
  container.innerHTML = "";

  questions.forEach((q, i) => {
    const item = document.createElement("div");
    item.className = "question-item";
    item.innerHTML = `
      <div class="question-header" onclick="toggleQuestion(${i})">
        <span class="q-number">${i + 1}</span>
        <span class="q-text">${q}</span>
        <span class="q-chevron" id="chevron-${i}">▾</span>
      </div>
      <div class="question-body" id="qbody-${i}">
        <textarea rows="2" placeholder="Your answer..." id="qanswer-${i}"></textarea>
      </div>`;
    container.appendChild(item);
  });
}

function toggleQuestion(i) {
  const body = document.getElementById(`qbody-${i}`);
  const chevron = document.getElementById(`chevron-${i}`);
  const isOpen = body.classList.contains("open");
  body.classList.toggle("open", !isOpen);
  chevron.classList.toggle("open", !isOpen);
}

// Improve Prompt
async function improvePrompt() {
  const refineText = document.getElementById("refineInput").value.trim();
  const answers = [];

  // Collect answered questions
  document.querySelectorAll("[id^='qanswer-']").forEach((el, i) => {
    if (el.value.trim()) {
      answers.push(`${el.value.trim()}`);
    }
  });

  const combinedRefinement = [...answers, refineText].filter(Boolean).join(". ");
  if (!combinedRefinement) { alert("Please answer at least one question or add a refinement note."); return; }

  const btn = document.querySelector(".improve-btn");
  const btnText = document.getElementById("improveBtnText");
  const spinner = document.getElementById("improveSpinner");

  btn.disabled = true;
  btnText.textContent = "Improving...";
  spinner.classList.remove("d-none");

  const token = localStorage.getItem("token");
  const outputEl = document.getElementById("outputPrompt");
  outputEl.innerHTML = `<p class="text-muted small">Regenerating with your inputs...</p>`;

  try {
    const res = await fetch(`${API}/enhance-prompt`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({ prompt: currentPrompt, refinement: combinedRefinement })
    });

    const data = await res.json();
    if (!res.ok) { outputEl.innerHTML = `<p class="text-danger">Improvement failed.</p>`; return; }

    currentOutput = data.enhanced_prompt;
    renderPromptOutput(data.enhanced_prompt);
    document.getElementById("refineInput").value = "";

    // Reset save state after improvement
    const saveBtn = document.getElementById("saveLibraryBtn");
    if (saveBtn) { saveBtn.textContent = "💾 Save"; saveBtn.disabled = false; }
    const saveMsg = document.getElementById("saveMsg");
    if (saveMsg) saveMsg.classList.add("d-none");

  } catch (e) {
    console.error("Error in improvePrompt:", e);
    if (e.name === "TypeError" && e.message.includes("fetch")) {
      outputEl.innerHTML = `<p class="text-danger">Cannot reach server.</p>`;
    } else {
      outputEl.innerHTML = `<p class="text-danger">An internal error occurred.</p>`;
    }
  } finally {
    btn.disabled = false;
    btnText.textContent = "Improve Prompt";
    spinner.classList.add("d-none");
  }
}

//Library: Save
async function saveToLibrary() {
  const token = localStorage.getItem("token");
  if (!currentOutput) return;

  const saveBtn = document.getElementById("saveLibraryBtn");
  const saveMsg = document.getElementById("saveMsg");

  saveBtn.disabled = true;
  saveBtn.textContent = "Saving...";

  try {
    const res = await fetch(`${API}/library/save`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({
        lazy_prompt: currentPrompt,
        enhanced_prompt: currentOutput,
        prompt_type: currentType
      })
    });

    if (!res.ok) {
      saveBtn.textContent = "💾 Save";
      saveBtn.disabled = false;
      alert("Failed to save prompt.");
      return;
    }

    saveBtn.textContent = "✅ Saved";
    saveMsg.classList.remove("d-none");
    setTimeout(() => saveMsg.classList.add("d-none"), 2500);

    // Refresh library sidebar
    loadLibrary();

  } catch (e) {
    saveBtn.textContent = "💾 Save";
    saveBtn.disabled = false;
    alert("Cannot reach server.");
  }
}

//Library cache (maps id → prompt data to avoid inline-attribute escaping)
const _libraryCache = {};

//Library: Load & Render
async function loadLibrary() {
  const token = localStorage.getItem("token");
  const container = document.getElementById("libraryList");
  if (!container) return;

  try {
    const res = await fetch(`${API}/library`, {
      headers: { "Authorization": "Bearer " + token }
    });

    if (!res.ok) return;

    const prompts = await res.json();

    if (!prompts.length) {
      container.innerHTML = `<p class="library-empty text-muted small">No saved prompts yet.</p>`;
      return;
    }

    // Store all prompts in cache so onclick only needs to pass the id
    prompts.forEach(p => { _libraryCache[p.id] = p; });

    container.innerHTML = prompts.map(p => `
      <div class="library-item" onclick="viewLibraryPrompt(${p.id})">
        <div class="library-item-type">${{ image: '🖼️', code: '💻', research: '🔍', text: '📝' }[p.prompt_type] || '📝'}</div>
        <div class="library-item-text">
          <div class="library-item-title">${truncate(p.lazy_prompt, 40)}</div>
          <div class="library-item-date">${formatDate(p.created_at)}</div>
        </div>
        <button class="library-delete-btn" onclick="deleteLibraryPrompt(event, ${p.id})" title="Delete">✕</button>
      </div>
    `).join("");

  } catch (e) {
    // silently fail — library is a background load
  }
}

//Library: View
function viewLibraryPrompt(id) {
  const p = _libraryCache[id];
  if (!p) return;

  const modal = document.getElementById("libraryModal");
  document.getElementById("modalLazy").textContent = p.lazy_prompt;

  // Render directly into the modal container — no tempDiv needed
  const modalEnhanced = document.getElementById("modalEnhanced");
  renderPromptOutput(p.enhanced_prompt, modalEnhanced);

  modalPromptText = p.enhanced_prompt;
  modal.classList.remove("d-none");
}

function closeLibraryModal(event) {
  if (!event || event.target === document.getElementById("libraryModal")) {
    document.getElementById("libraryModal").classList.add("d-none");
  }
}

function copyModalPrompt() {
  navigator.clipboard.writeText(modalPromptText).then(() => {
    const btn = document.querySelector("#libraryModal .ghost-btn");
    btn.textContent = "✅ Copied!";
    setTimeout(() => { btn.textContent = "📋 Copy Enhanced Prompt"; }, 2000);
  });
}

//Library: Delete
async function deleteLibraryPrompt(event, id) {
  event.stopPropagation();
  const token = localStorage.getItem("token");

  try {
    const res = await fetch(`${API}/library/${id}`, {
      method: "DELETE",
      headers: { "Authorization": "Bearer " + token }
    });

    if (res.ok || res.status === 204) {
      loadLibrary();
    }
  } catch (e) {
    // silent fail
  }
}

//Helpers

// ─── History cache (maps id → history data) ───────────────────────────────────
const _historyCache = {};

// ─── History: Load & Render ───────────────────────────────────────────────────
async function loadHistory() {
  const token = localStorage.getItem("token");
  const container = document.getElementById("historyList");
  if (!container) return;

  try {
    const res = await fetch(`${API}/history`, {
      headers: { "Authorization": "Bearer " + token }
    });

    if (!res.ok) return;

    const entries = await res.json();

    if (!entries.length) {
      container.innerHTML = `<p class="history-empty text-muted small">No history yet.</p>`;
      return;
    }

    entries.forEach(h => { _historyCache[h.id] = h; });

    container.innerHTML = entries.map(h => `
      <div class="history-item" onclick="viewHistoryItem(${h.id})">
        <div class="history-item-type">${{ image: '🖼️', code: '💻', research: '🔍', text: '📝' }[h.prompt_type] || '📝'}</div>
        <div class="history-item-text">
          <div class="history-item-title">${truncate(h.lazy_prompt, 38)}</div>
          <div class="history-item-date">${formatDate(h.created_at)}</div>
        </div>
        <button class="history-delete-btn" onclick="deleteHistoryItem(event, ${h.id})" title="Delete">✕</button>
      </div>
    `).join("");

  } catch (e) {
    // silently fail
  }
}

// ─── History: View ────────────────────────────────────────────────────────────
function viewHistoryItem(id) {
  const h = _historyCache[id];
  if (!h) return;

  currentPrompt = h.lazy_prompt;
  currentOutput = h.enhanced_prompt;
  currentType = h.prompt_type;

  showResultState(h.lazy_prompt, h.enhanced_prompt, h.prompt_type);
  fetchQuestions(h.lazy_prompt, h.prompt_type);
}

// ─── History: Delete single ───────────────────────────────────────────────────
async function deleteHistoryItem(event, id) {
  event.stopPropagation();
  const token = localStorage.getItem("token");

  try {
    const res = await fetch(`${API}/history/${id}`, {
      method: "DELETE",
      headers: { "Authorization": "Bearer " + token }
    });

    if (res.ok || res.status === 204) {
      loadHistory();
    }
  } catch (e) {
    // silent fail
  }
}

// ─── History: Clear all ───────────────────────────────────────────────────────
async function clearHistory() {
  const token = localStorage.getItem("token");

  try {
    const res = await fetch(`${API}/history`, {
      method: "DELETE",
      headers: { "Authorization": "Bearer " + token }
    });

    if (res.ok || res.status === 204) {
      loadHistory();
    }
  } catch (e) {
    // silent fail
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function copyPrompt() {
  const copyMsg = document.getElementById("copyMsg");
  navigator.clipboard.writeText(currentOutput).then(() => {
    copyMsg.classList.remove("d-none");
    setTimeout(() => copyMsg.classList.add("d-none"), 2000);
  });
}

function fillChip(text) {
  const input = document.getElementById("inputPrompt");
  if (input) { input.value = text + " "; input.focus(); }
}

function newPrompt() {
  currentPrompt = "";
  currentOutput = "";
  document.getElementById("inputState").classList.remove("d-none");
  document.getElementById("resultState").classList.add("d-none");
  const rightPanel = document.getElementById("rightPanel");
  if (rightPanel) rightPanel.classList.add("d-none");
  const input = document.getElementById("inputPrompt");
  if (input) { input.value = ""; input.focus(); }
}

function toggleRefineBox() {
  const content = document.getElementById("refineContent");
  const toggle = document.getElementById("refineToggle");
  const isHidden = content.style.display === "none";
  content.style.display = isHidden ? "" : "none";
  toggle.classList.toggle("collapsed", !isHidden);
}

function truncate(str, maxLen) {
  if (!str) return "";
  return str.length > maxLen ? str.slice(0, maxLen) + "…" : str;
}

function escStr(str) {
  return (str || "").replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\n/g, " ");
}

function formatDate(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

//Init
document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("inputPrompt");
  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        generatePrompt();
      }
    });
  }

  // Load library and history on page open
  loadLibrary();
  loadHistory();
});