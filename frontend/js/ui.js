/**
 * UI rendering — stats, dashboard, association-rule tickets.
 */

export function fmtPct(v) {
  return (v * 100).toFixed(1) + "%";
}

export function renderStats(container, eda, model) {
  const topLift = model?.metrics?.top_lift;
  container.innerHTML = `
    <div class="stats-receipt">
      <div class="r-title">REGISTER SUMMARY</div>
      <div class="r-sub">from backend model</div>
      <div class="stat-line"><span class="label">Transactions</span><span class="leader"></span><span class="value">${eda.transaction_count}</span></div>
      <div class="stat-line"><span class="label">Unique items</span><span class="leader"></span><span class="value">${eda.unique_items}</span></div>
      <div class="stat-line"><span class="label">Rules brewed</span><span class="leader"></span><span class="value">${model.metrics.rule_count}</span></div>
      <div class="stat-line"><span class="label">Strongest lift</span><span class="leader"></span><span class="value">${topLift != null ? topLift.toFixed(2) + "×" : "—"}</span></div>
    </div>`;
}

export function renderDashboard(container, eda, headers, rows) {
  if (!eda.transaction_count) {
    container.innerHTML = `
      <div class="empty">
        <div class="icon">📊</div>
        <h3>Dashboard waiting for a file</h3>
        <p>Upload a CSV or use the sample dataset to see order details.</p>
      </div>`;
    return;
  }

  const topItems = eda.top_items.slice(0, 6);
  container.innerHTML = `
    <div class="dashboard-grid">
      <div class="data-card"><div class="card-label">Loaded orders</div><div class="card-value">${eda.transaction_count}</div></div>
      <div class="data-card"><div class="card-label">Unique items</div><div class="card-value">${eda.unique_items}</div></div>
      <div class="data-card"><div class="card-label">Avg. items / order</div><div class="card-value">${eda.avg_items_per_order}</div></div>
      <div class="data-card"><div class="card-label">Detected columns</div><div class="card-value">${eda.column_count}</div></div>
    </div>
    <div class="table-preview">
      <div class="table-meta">
        <div class="table-title">Ledger preview</div>
        <div class="table-note">${rows.length} total orders · ${headers.length} columns loaded</div>
      </div>
      <div class="top-items">
        ${topItems.map((item) => `<span class="item-pill">${item.name} · ${item.count}</span>`).join("")}
      </div>
      <div class="table-scroll">
        <table class="data-table">
          <thead><tr>${headers.map((h) => `<th>${h || "Column"}</th>`).join("")}</tr></thead>
          <tbody>
            ${rows.map((row) => `<tr>${row.map((cell) => `<td${cell ? "" : ' class="empty-cell"'}>${cell ? cell : "—"}</td>`).join("")}</tr>`).join("")}
          </tbody>
        </table>
      </div>
    </div>`;
}

function ticketHTML(r, i, favorites) {
  const key = r.antecedent.join("+") + ">" + r.consequent.join("+");
  const isFav = favorites.has(key);
  const strong = r.lift >= 2;
  const no = String(i + 1).padStart(3, "0");
  return `
    <article class="ticket">
      <div class="perf"></div>
      <div class="ticket-body">
        <div class="ticket-head">
          <span class="ticket-no">SLIP NO. ${no}</span>
          <button class="fav-btn ${isFav ? "active" : ""}" data-key="${key}" aria-label="Mark favorite">${isFav ? "♥" : "♡"}</button>
        </div>
        <div class="rule-line">${r.antecedent.join(", ")} <span class="arrow">→</span> ${r.consequent.join(", ")}</div>
        <div class="rule-sub">often ordered together</div>
        <div class="divider"></div>
        <div class="metric-row">
          <div class="metric"><div class="m-val">${fmtPct(r.support)}</div><div class="m-lab">Support</div></div>
          <div class="metric"><div class="m-val">${fmtPct(r.confidence)}</div><div class="m-lab">Confidence</div></div>
          <div class="metric"><div class="m-val">${r.lift.toFixed(2)}×</div><div class="m-lab">Lift</div></div>
        </div>
      </div>
      <div class="ticket-footer">
        <div class="barcode"></div>
        <div class="perf"></div>
      </div>
      ${strong ? '<div class="stamp">STRONG PAIR</div>' : ""}
    </article>`;
}

export function renderRules(container, rules, { query, sort, favorites, onFavoriteToggle }) {
  let list = rules.slice();
  if (query) {
    const q = query.toLowerCase();
    list = list.filter(
      (r) =>
        r.antecedent.some((it) => it.toLowerCase().includes(q)) ||
        r.consequent.some((it) => it.toLowerCase().includes(q))
    );
  }
  list.sort((a, b) => b[sort] - a[sort]);
  list = list.slice(0, 30);

  if (!list.length) {
    container.innerHTML = `
      <div class="empty">
        <div class="icon">🧾</div>
        <h3>No rules match the till</h3>
        <p>Try loosening the brewing strength, or clear the search.</p>
      </div>`;
    return;
  }

  container.innerHTML = `<div class="ticket-grid">${list.map((r, i) => ticketHTML(r, i, favorites)).join("")}</div>`;
  container.querySelectorAll(".fav-btn").forEach((btn) => {
    btn.addEventListener("click", () => onFavoriteToggle(btn.dataset.key, btn));
  });
}

export function showLoading(container) {
  container.innerHTML = `<div class="loading-row"><span class="spinner"></span> brewing the rules…</div>`;
}

export function showError(container, message) {
  container.innerHTML = `
    <div class="empty">
      <div class="icon">⚠️</div>
      <h3>Backend unavailable</h3>
      <p>${message}</p>
      <p style="margin-top:12px;font-size:13px;">Start the API: <code>uvicorn app.main:app --reload</code> from the backend folder.</p>
    </div>`;
}
