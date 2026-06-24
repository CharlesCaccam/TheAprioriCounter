import { analyzeSample, analyzeUpload, checkHealth } from "./api.js";
import { renderStats, renderDashboard, renderRules, showLoading, showError } from "./ui.js";

const state = {
  headers: [],
  rows: [],
  eda: null,
  rules: [],
  sort: "lift",
  query: "",
  favorites: new Set(),
  sourceLabel: "",
};

const $ = (id) => document.getElementById(id);
const dropzone = $("dropzone");
const fileInput = $("fileInput");
const fileName = $("fileName");
const browseBtn = $("browseBtn");
const sampleBtn = $("sampleBtn");
const ctaSample = $("ctaSample");
const ctaUpload = $("ctaUpload");
const runBtn = $("runBtn");
const supRange = $("supRange");
const confRange = $("confRange");
const liftRange = $("liftRange");
const supVal = $("supVal");
const confVal = $("confVal");
const liftVal = $("liftVal");
const statsArea = $("statsArea");
const rulesArea = $("rulesArea");
const dashboardArea = $("dashboardArea");
const searchInput = $("searchInput");
const sortFilters = $("sortFilters");
const navToggle = $("navToggle");
const navLinks = document.querySelector(".nav-links");

function params() {
  return {
    min_support: parseFloat(supRange.value),
    min_confidence: parseFloat(confRange.value),
    min_lift: parseFloat(liftRange.value),
  };
}

function syncSliderLabels() {
  supVal.textContent = parseFloat(supRange.value).toFixed(2);
  confVal.textContent = parseFloat(confRange.value).toFixed(2);
  liftVal.textContent = parseFloat(liftRange.value).toFixed(2);
}

[supRange, confRange, liftRange].forEach((r) =>
  r.addEventListener("input", () => {
    syncSliderLabels();
    if (state.eda) recompute();
  })
);
syncSliderLabels();

async function applyResult(payload) {
  state.headers = payload.headers;
  state.rows = payload.rows;
  state.eda = payload.eda;
  state.rules = payload.model.rules;
  state.sourceLabel = payload.source;
  renderStats(statsArea, state.eda, payload.model);
  renderDashboard(dashboardArea, state.eda, state.headers, state.rows);
  renderRules(rulesArea, state.rules, {
    query: state.query,
    sort: state.sort,
    favorites: state.favorites,
    onFavoriteToggle: (key, btn) => {
      if (state.favorites.has(key)) {
        state.favorites.delete(key);
        btn.classList.remove("active");
        btn.textContent = "♡";
      } else {
        state.favorites.add(key);
        btn.classList.add("active");
        btn.textContent = "♥";
      }
    },
  });
}

async function recompute() {
  showLoading(rulesArea);
  try {
    let payload;
    if (state.pendingFile) {
      payload = await analyzeUpload(state.pendingFile, params());
    } else {
      payload = await analyzeSample(params());
    }
    await applyResult(payload);
  } catch (err) {
    showError(rulesArea, err.message);
  }
}

function readFileSmart(file, callback) {
  const reader = new FileReader();
  reader.onload = (ev) => {
    const text = ev.target.result;
    if (text.indexOf("\uFFFD") !== -1) {
      const retry = new FileReader();
      retry.onload = (ev2) => callback(ev2.target.result, file);
      retry.readAsText(file, "ISO-8859-1");
    } else {
      callback(text, file);
    }
  };
  reader.readAsText(file);
}

async function loadFile(file) {
  state.pendingFile = file;
  fileName.textContent = `✓ ${file.name} — sending to backend…`;
  runBtn.disabled = false;
  await recompute();
  document.getElementById("dashboard").scrollIntoView({ behavior: "smooth", block: "start" });
}

browseBtn.addEventListener("click", () => fileInput.click());
ctaUpload.addEventListener("click", () => {
  document.getElementById("brew").scrollIntoView({ behavior: "smooth" });
  fileInput.click();
});
fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) loadFile(file);
});

["dragenter", "dragover"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("drag");
  })
);
["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag");
  })
);
dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) loadFile(file);
});

async function useSample() {
  state.pendingFile = null;
  fileName.textContent = "✓ CoffeeBeanAndTeaLeafCoffeeShopData1.csv — sample till";
  runBtn.disabled = false;
  await recompute();
  document.getElementById("dashboard").scrollIntoView({ behavior: "smooth", block: "start" });
}
sampleBtn.addEventListener("click", useSample);
ctaSample.addEventListener("click", useSample);
runBtn.addEventListener("click", recompute);

searchInput.addEventListener("input", (e) => {
  state.query = e.target.value.trim();
  renderRules(rulesArea, state.rules, {
    query: state.query,
    sort: state.sort,
    favorites: state.favorites,
    onFavoriteToggle: () => {},
  });
});

sortFilters.addEventListener("click", (e) => {
  const btn = e.target.closest(".chip");
  if (!btn) return;
  sortFilters.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
  btn.classList.add("active");
  state.sort = btn.dataset.sort;
  renderRules(rulesArea, state.rules, {
    query: state.query,
    sort: state.sort,
    favorites: state.favorites,
    onFavoriteToggle: () => {},
  });
});

navToggle.addEventListener("click", () => navLinks.classList.toggle("open"));

checkHealth().catch(() => {
  fileName.textContent = "⚠ Backend offline — start uvicorn first";
});
