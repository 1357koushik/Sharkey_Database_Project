/* app.js — Assignment 3 Frontend Logic */

// ── Navigation ────────────────────────────────────────────────────────────────

let _currentView = "dashboard";

function nav(view) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.getElementById("view-" + view).classList.add("active");
  document.querySelector(`.nav-item[data-view="${view}"]`)?.classList.add("active");
  _currentView = view;
  if (view === "dashboard") loadDashTables();
  if (view === "tables")    loadTables();
  if (view === "wal")       loadWal();
  if (view === "manual")    refreshManualTables();
}

// ── Utilities ─────────────────────────────────────────────────────────────────

function fmt(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

function opBadge(op) {
  return `<span class="op-badge op-${op}">${op}</span>`;
}

function renderTable(rows, caption) {
  if (!rows || rows.length === 0)
    return `<p style="color:var(--text3);font-size:12px">No records in ${caption}.</p>`;
  const cols = Object.keys(rows[0]);
  return `
    <table class="data-table">
      <thead><tr>${cols.map(c => `<th>${c}</th>`).join("")}</tr></thead>
      <tbody>
        ${rows.map(row => `<tr>${cols.map(c =>
          `<td class="${typeof row[c]==='number'?'mono':''}">${fmt(row[c])}</td>`
        ).join("")}</tr>`).join("")}
      </tbody>
    </table>`;
}

function showLoading(id) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = `<div class="loading">Loading…</div>`;
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

async function loadDashTables() {
  showLoading("dash-tables");
  try {
    const d = await API.tables();
    let html = "";
    for (const [name, rows] of Object.entries(d.tables)) {
      html += `<div style="margin-bottom:18px">
        <div style="font-size:12px;font-weight:700;color:var(--accent);margin-bottom:6px">
          ${name} <span style="color:var(--text3);font-weight:400">(${rows.length} records · B+ Tree)</span>
        </div>
        ${renderTable(rows, name)}
      </div>`;
    }
    document.getElementById("dash-tables").innerHTML = html;
  } catch (e) {
    document.getElementById("dash-tables").innerHTML =
      `<p style="color:var(--red)">${e.message}</p>`;
  }
}

// ── Tables view ───────────────────────────────────────────────────────────────

async function loadTables() {
  showLoading("tables-view");
  try {
    const d = await API.tables();
    let html = "";
    for (const [name, rows] of Object.entries(d.tables)) {
      html += `<div class="card">
        <div class="card-title">${name} &nbsp;<span style="color:var(--text3);font-weight:400;text-transform:none;letter-spacing:0">${rows.length} records</span></div>
        ${renderTable(rows, name)}
      </div>`;
    }
    document.getElementById("tables-view").innerHTML = html;
  } catch (e) {
    document.getElementById("tables-view").innerHTML =
      `<p style="color:var(--red)">${e.message}</p>`;
  }
}

// ── WAL view ──────────────────────────────────────────────────────────────────

async function loadWal() {
  showLoading("wal-view");
  try {
    const d = await API.wal();
    const counts = d.counts || {};
    const recent = d.recent || [];

    let statsHtml = `<div class="metric-grid">
      <div class="metric-card"><div class="metric-val">${d.total}</div><div class="metric-label">Total Records</div></div>
      ${Object.entries(counts).map(([op, n]) =>
        `<div class="metric-card">
          <div class="metric-val" style="font-size:18px">${n}</div>
          <div class="metric-label">${opBadge(op)}</div>
        </div>`
      ).join("")}
    </div>`;

    let tableHtml = recent.length === 0
      ? `<p style="color:var(--text3);font-size:12px">WAL is empty.</p>`
      : `<div style="overflow-x:auto">
          <table class="wal-table">
            <thead><tr>
              <th>LSN</th><th>Txn</th><th>Op</th>
              <th>Table</th><th>Key</th><th>Before</th><th>After</th>
            </tr></thead>
            <tbody>
              ${[...recent].reverse().map(r => `<tr>
                <td class="mono">${r.lsn}</td>
                <td class="mono" style="color:var(--accent)">${r.txn_id}</td>
                <td>${opBadge(r.op)}</td>
                <td>${r.table || "—"}</td>
                <td class="mono">${r.key || "—"}</td>
                <td class="mono" style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${JSON.stringify(r.before)}">${r.before ? JSON.stringify(r.before).slice(0,50) : "—"}</td>
                <td class="mono" style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${JSON.stringify(r.after)}">${r.after  ? JSON.stringify(r.after).slice(0,50)  : "—"}</td>
              </tr>`).join("")}
            </tbody>
          </table>
        </div>`;

    document.getElementById("wal-view").innerHTML =
      `<div class="card"><div class="card-title">WAL Statistics</div>${statsHtml}</div>
       <div class="card"><div class="card-title">Last ${recent.length} Records (newest first)</div>${tableHtml}</div>`;
  } catch (e) {
    document.getElementById("wal-view").innerHTML =
      `<p style="color:var(--red)">${e.message}</p>`;
  }
}

// ── ACID result renderer ──────────────────────────────────────────────────────

function renderAcidResult(containerId, d) {
  const passed = d.passed !== false && d.committed !== false;
  const verdict = d.verdict || "";

  // Steps
  let stepsHtml = "";
  if (d.steps) {
    stepsHtml = `<ul class="step-trace">
      ${d.steps.map(s => {
        const cls = s.crash ? "step-crash" : (s.ok !== false ? "step-ok" : "");
        return `<li>
          <span class="step-num ${cls}">${s.step}</span>
          <span>${s.action}</span>
        </li>`;
      }).join("")}
    </ul>`;
  }

  // State comparison
  let cmpHtml = "";
  if (d.pre && d.post) {
    cmpHtml = `<div class="state-cmp">
      <div class="state-box">
        <h4>Pre-State</h4>
        ${Object.entries(d.pre).map(([k,v]) => `<div><b style="color:var(--text1)">${k}</b>: ${v}</div>`).join("")}
      </div>
      <div class="state-box">
        <h4>Post-State</h4>
        ${Object.entries(d.post).map(([k,v]) => `<div><b style="color:var(--text1)">${k}</b>: ${v}</div>`).join("")}
      </div>
    </div>`;
  }

  // Log (isolation)
  let logHtml = "";
  if (d.log) {
    logHtml = `<div style="margin-top:10px">
      <div class="card-title">Execution Log</div>
      <div class="op-log">
        ${d.log.map(line =>
          `<div class="${line.startsWith("[A]")?'log-ok':line.startsWith("[B]")?'log-inf':''}">
            ${line}
          </div>`
        ).join("")}
      </div>
    </div>`;
  }

  // Extra fields
  let extraHtml = "";
  const skip = new Set(["ok","test","passed","committed","steps","pre","post","verdict","log","tables","inject_fail"]);
  for (const [k, v] of Object.entries(d)) {
    if (skip.has(k)) continue;
    if (typeof v === "object" && v !== null) continue;
    extraHtml += `<div style="color:var(--text2);font-size:12px;margin-top:4px">
      <b>${k}</b>: <span class="mono">${v}</span>
    </div>`;
  }

  const el = document.getElementById(containerId);
  el.classList.remove("hidden");
  el.innerHTML = `
    <div class="${passed ? 'result-pass' : 'result-fail'}">${verdict}</div>
    ${stepsHtml}
    ${cmpHtml}
    ${logHtml}
    ${extraHtml}
  `;
}

// ── ACID tests ────────────────────────────────────────────────────────────────

async function runAcid(test) {
  const id = "result-" + test;
  const el = document.getElementById(id);
  el.classList.remove("hidden");
  el.innerHTML = `<div class="loading">Running ${test} test…</div>`;
  try {
    let d;
    if      (test === "atomicity")   d = await API.acidAtomicity();
    else if (test === "consistency") d = await API.acidConsistency();
    else if (test === "isolation")   d = await API.acidIsolation();
    else if (test === "durability")  d = await API.acidDurability();
    renderAcidResult(id, d);
    if (_currentView === "dashboard") loadDashTables();
  } catch (e) {
    el.innerHTML = `<div class="result-fail">❌ ${e.message}</div>`;
  }
}

async function runMulti() {
  const id    = "result-multi";
  const el    = document.getElementById(id);
  el.classList.remove("hidden");
  el.innerHTML = `<div class="loading">Executing 3-table transaction…</div>`;
  try {
    const d = await API.acidMulti({
      member_id:   document.getElementById("multi-member").value,
      facility_id: Number(document.getElementById("multi-facility").value),
      inject_fail: document.getElementById("multi-fail").value === "true",
    });
    renderAcidResult(id, d);
    loadDashTables();
  } catch (e) {
    el.innerHTML = `<div class="result-fail">❌ ${e.message}</div>`;
  }
}

async function updateAllFacilities() {
  const id = "result-multi";
  const el = document.getElementById(id);
  el.classList.remove("hidden");
  el.innerHTML = `<div class="loading">Changing maintenance facilities to available…</div>`;
  try {
    const d = await API.updateAllFacilities();
    renderAcidResult(id, d);
    loadDashTables();
  } catch (e) {
    el.innerHTML = `<div class="result-fail">❌ ${e.message}</div>`;
  }
}

async function runRecovery() {
  const id = "result-recovery";
  const el = document.getElementById(id);
  el.classList.remove("hidden");
  el.innerHTML = `<div class="loading">Running ARIES recovery…</div>`;
  try {
    const d = await API.recover();
    const r = d.recovery;
    el.innerHTML = `
      <div class="${r.status==='recovered'?'result-pass':'result-pass'}">
        ♻️ Recovery complete — status: <b>${r.status}</b>
      </div>
      <div style="margin-top:10px;font-size:13px;color:var(--text2);line-height:2">
        <div>WAL records scanned: <b class="mono">${r.records}</b></div>
        <div>Committed txns REDOed: <b class="mono">${(r.committed||[]).join(", ") || "none"}</b></div>
        <div>Loser txns UNDOed: <b class="mono">${(r.undone||[]).join(", ") || "none"}</b></div>
      </div>`;
  } catch (e) {
    el.innerHTML = `<div class="result-fail">❌ ${e.message}</div>`;
  }
}

// ── Manual Transaction ────────────────────────────────────────────────────────

let _activeTxnId = null;

function logLine(msg, cls = "") {
  const log = document.getElementById("manual-log");
  const div = document.createElement("div");
  div.className = cls;
  div.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  log.prepend(div);
}

async function manualBegin() {
  try {
    const d = await API.begin();
    _activeTxnId = d.txn_id;
    document.getElementById("manual-txn-id").textContent = `Active Transaction: ${_activeTxnId}`;
    document.getElementById("manual-txn-id").classList.remove("hidden");
    document.getElementById("manual-op-panel").classList.remove("hidden");
    document.getElementById("btn-commit").disabled   = false;
    document.getElementById("btn-rollback").disabled = false;
    logLine(`BEGIN ${_activeTxnId}`, "log-inf");
    refreshManualTables();
  } catch (e) {
    logLine(`BEGIN failed: ${e.message}`, "log-err");
  }
}

async function manualCommit() {
  if (!_activeTxnId) return;
  try {
    const d = await API.commit(_activeTxnId);
    logLine(`COMMIT ${_activeTxnId} → state=${d.state}`, "log-ok");
    _resetManual();
    refreshManualTables();
  } catch (e) {
    logLine(`COMMIT failed: ${e.message}`, "log-err");
  }
}

async function manualRollback() {
  if (!_activeTxnId) return;
  try {
    const d = await API.rollback(_activeTxnId);
    logLine(`ROLLBACK ${_activeTxnId} → state=${d.state}`, "log-err");
    _resetManual();
    refreshManualTables();
  } catch (e) {
    logLine(`ROLLBACK failed: ${e.message}`, "log-err");
  }
}

function _resetManual() {
  _activeTxnId = null;
  document.getElementById("manual-txn-id").classList.add("hidden");
  document.getElementById("manual-op-panel").classList.add("hidden");
  document.getElementById("btn-commit").disabled   = true;
  document.getElementById("btn-rollback").disabled = true;
}

function manualTableChange() {
  const tbl = document.getElementById("man-table").value;
  const placeholders = {
    Member:    '{"Member_ID":"M06","Name":"New Member","Gender":"F","Email":"user6@iitgn.ac.in","Phone_Number":"900000006","Age":23,"DOB":"","Image":""}',
    Facility:  '{"Facility_ID":6,"Facility_Name":"TT Arena","Facility_Description":"ITTF competition tables","Status":"Available"}',
    Booking:   '{"Booking_ID":10,"Facility_ID":1,"Member_ID":"M01","Time_In":"2026-04-06 10:00:00","Time_Out":"2026-04-06 11:00:00"}',
    Complaint: '{"Complaint_ID":"C10","Member_ID":"M01","Description":"Temporary complaint","Status":"Open","Date":"2026-04-05","Resolved_By":""}',
  };
  document.getElementById("man-record").placeholder = placeholders[tbl] || "";
}

async function manualExec() {
  if (!_activeTxnId) { logLine("No active transaction. Click BEGIN first.", "log-err"); return; }
  const op    = document.getElementById("man-op").value;
  const table = document.getElementById("man-table").value;
  const key   = document.getElementById("man-key").value.trim();

  let recordRaw = document.getElementById("man-record").value.trim();
  let record = null;
  if (recordRaw) {
    try { record = JSON.parse(recordRaw); }
    catch { logLine("Invalid JSON in record field", "log-err"); return; }
  }

  try {
    if (op === "insert") {
      await API.insert(_activeTxnId, table, record);
      logLine(`INSERT into ${table}: ${JSON.stringify(record)}`, "log-ok");
    } else if (op === "update") {
      if (!key) { logLine("Key required for UPDATE", "log-err"); return; }
      await API.update(_activeTxnId, table, key, record);
      logLine(`UPDATE ${table}[${key}]: ${JSON.stringify(record)}`, "log-ok");
    } else if (op === "delete") {
      if (!key) { logLine("Key required for DELETE", "log-err"); return; }
      await API.delete(_activeTxnId, table, key);
      logLine(`DELETE ${table}[${key}]`, "log-ok");
    }
    refreshManualTables();
  } catch (e) {
    logLine(`${op.toUpperCase()} failed: ${e.message}`, "log-err");
  }
}

async function refreshManualTables() {
  try {
    const d = await API.tables();
    let html = "";
    for (const [name, rows] of Object.entries(d.tables)) {
      html += `<div style="margin-bottom:14px">
        <div style="font-size:11px;color:var(--accent);font-weight:700;margin-bottom:6px">${name}</div>
        ${renderTable(rows, name)}
      </div>`;
    }
    document.getElementById("manual-tables").innerHTML = html;
  } catch (e) {
    document.getElementById("manual-tables").innerHTML =
      `<p style="color:var(--red)">${e.message}</p>`;
  }
}

function renderLatencyBar(sorted) {
  if (!sorted.length) return "";
  const max = sorted[sorted.length-1];
  if (max <= 0) return "";
  const buckets = 10;
  const bsize   = max / buckets;
  const counts  = Array(buckets).fill(0);
  sorted.forEach(v => {
    const b = Math.min(Math.floor(v / bsize), buckets-1);
    counts[b]++;
  });
  const maxCount = Math.max(...counts);
  return `<div style="display:flex;align-items:flex-end;gap:4px;height:80px">
    ${counts.map((c, i) => {
      const h = maxCount > 0 ? Math.round((c/maxCount)*70) : 0;
      const lo = Math.round(i * bsize);
      const hi = Math.round((i+1) * bsize);
      return `<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px">
        <div title="${c} ops in ${lo}–${hi}ms"
             style="width:100%;height:${h}px;background:var(--accent);border-radius:3px 3px 0 0;opacity:.8"></div>
        <div style="font-size:9px;color:var(--text3)">${lo}</div>
      </div>`;
    }).join("")}
  </div>`;
}

function renderStressResult(d) {
  const el = document.getElementById("result-stress");
  const errorRows = Object.entries(d.errors || {});
  const resultRows = (d.results || []).map(item => `
    <tr>
      <td class="mono">${item.member_id}</td>
      <td class="mono">${item.booking_id}</td>
      <td>${item.ok ? '<span class="result-inline ok">BOOKED</span>' : '<span class="result-inline fail">REJECTED</span>'}</td>
      <td class="mono">${item.latency_ms}</td>
      <td>${item.error || "—"}</td>
    </tr>
  `).join("");

  el.classList.remove("hidden");
  el.innerHTML = `
    <div class="${d.passed ? "result-pass" : "result-fail"}">${d.verdict}</div>
    <div class="metric-grid">
      <div class="metric-card"><div class="metric-val">${d.attempts}</div><div class="metric-label">Concurrent Members</div></div>
      <div class="metric-card"><div class="metric-val">${d.initial_stock}</div><div class="metric-label">Allowed Winners</div></div>
      <div class="metric-card"><div class="metric-val">${d.successful_bookings}</div><div class="metric-label">Successful Bookings</div></div>
      <div class="metric-card"><div class="metric-val">${d.rejected_bookings}</div><div class="metric-label">Rejected Attempts</div></div>
      <div class="metric-card"><div class="metric-val">${d.final_stock}</div><div class="metric-label">Final Bookings</div></div>
      <div class="metric-card"><div class="metric-val">${d.bookings_created ?? d.orders_created}</div><div class="metric-label">Bookings Created</div></div>
    </div>
    <div class="stress-summary">
      <div><b>Critical operation:</b> ${d.critical_operation}</div>
      <div><b>Expected final bookings:</b> <span class="mono">${d.expected_final_stock}</span></div>
      <div><b>Delay per booking:</b> <span class="mono">${d.delay_ms} ms</span></div>
    </div>
    <div style="margin-top:14px">
      <div class="card-title">Latency Distribution</div>
      ${renderLatencyBar(d.latency_ms || []) || `<p class="empty-state" style="padding:8px 0">No latency samples available.</p>`}
    </div>
    ${errorRows.length ? `
      <div style="margin-top:14px">
        <div class="card-title">Rejected Reasons</div>
        <div class="stress-errors">
          ${errorRows.map(([msg, count]) => `<div><span class="mono">${count}</span> × ${msg}</div>`).join("")}
        </div>
      </div>` : ""}
    <div style="margin-top:14px;overflow-x:auto">
      <div class="card-title">Per-User Outcome</div>
      <table class="data-table">
        <thead>
          <tr><th>Member</th><th>Booking</th><th>Status</th><th>Latency (ms)</th><th>Note</th></tr>
        </thead>
        <tbody>${resultRows}</tbody>
      </table>
    </div>
  `;
}

async function runStress() {
  const el = document.getElementById("result-stress");
  el.classList.remove("hidden");
  el.innerHTML = `<div class="loading">Running concurrent booking stress test…</div>`;
  try {
    const d = await API.acidStress({
      attempts: Number(document.getElementById("stress-attempts").value),
      stock: Number(document.getElementById("stress-stock").value),
      delay_ms: Number(document.getElementById("stress-delay").value),
    });
    renderStressResult(d);
  } catch (e) {
    el.innerHTML = `<div class="result-fail">❌ ${e.message}</div>`;
  }
}

function renderLoadStressResult(d) {
  const el = document.getElementById("result-loadtest");
  const errorRows = Object.entries(d.errors || {});
  const opRows = Object.entries(d.op_counts || {});
  el.classList.remove("hidden");
  el.innerHTML = `
    <div class="${d.passed ? "result-pass" : "result-fail"}">${d.verdict}</div>
    <div class="metric-grid">
      <div class="metric-card"><div class="metric-val">${d.total_requests}</div><div class="metric-label">Total Requests</div></div>
      <div class="metric-card"><div class="metric-val">${d.concurrency}</div><div class="metric-label">Concurrency</div></div>
      <div class="metric-card"><div class="metric-val">${d.successful_requests}</div><div class="metric-label">Successful</div></div>
      <div class="metric-card"><div class="metric-val">${d.failed_requests}</div><div class="metric-label">Failed</div></div>
      <div class="metric-card"><div class="metric-val">${d.throughput_rps}</div><div class="metric-label">Req/Sec</div></div>
      <div class="metric-card"><div class="metric-val">${d.p95_latency_ms}</div><div class="metric-label">P95 Latency (ms)</div></div>
    </div>
    <div class="stress-summary">
      <div><b>Average latency:</b> <span class="mono">${d.avg_latency_ms} ms</span></div>
      <div><b>Max latency:</b> <span class="mono">${d.max_latency_ms} ms</span></div>
      <div><b>Total duration:</b> <span class="mono">${d.duration_s} s</span></div>
    </div>
    <div style="margin-top:14px">
      <div class="card-title">Latency Distribution</div>
      ${renderLatencyBar(d.latency_ms || []) || `<p class="empty-state" style="padding:8px 0">No latency samples available.</p>`}
    </div>
    <div style="margin-top:14px">
      <div class="card-title">Operation Mix</div>
      <div class="stress-errors">
        ${opRows.map(([name, count]) => `<div><span class="mono">${count}</span> × ${name}</div>`).join("")}
      </div>
    </div>
    ${errorRows.length ? `
      <div style="margin-top:14px">
        <div class="card-title">Errors Under Load</div>
        <div class="stress-errors">
          ${errorRows.map(([msg, count]) => `<div><span class="mono">${count}</span> × ${msg}</div>`).join("")}
        </div>
      </div>` : ""}
  `;
}

async function runLoadStress() {
  const el = document.getElementById("result-loadtest");
  el.classList.remove("hidden");
  el.innerHTML = `<div class="loading">Running high-volume stress test…</div>`;
  try {
    const d = await API.loadStress({
      requests: Number(document.getElementById("load-requests").value),
      concurrency: Number(document.getElementById("load-concurrency").value),
    });
    renderLoadStressResult(d);
  } catch (e) {
    el.innerHTML = `<div class="result-fail">❌ ${e.message}</div>`;
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  loadDashTables();
  manualTableChange();
});
