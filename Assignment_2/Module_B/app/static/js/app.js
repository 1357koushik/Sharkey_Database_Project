/* ═══════════════════════════════════════════════
   app.js  —  Sports Club IITGN
   SPA router + all view renderers
═══════════════════════════════════════════════ */

// ── helpers ──────────────────────────────────
const $ = id => document.getElementById(id);
const el = (tag, cls, html) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html !== undefined) e.innerHTML = html;
  return e;
};
const badge = (text, cls) => `<span class="badge badge-${cls}">${text}</span>`;
const mono  = t => `<span class="mono">${t}</span>`;
const fmtDate = s => s ? s.split("T")[0].split(" ")[0] : "—";

function showAlert(id, msg, type="error") {
  const el = $(id);
  if (!el) return;
  el.textContent = msg;
  el.className = `alert alert-${type}`;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 4000);
}

function openModal(html) {
  const ov = el("div","modal-overlay");
  ov.innerHTML = `<div class="modal">${html}</div>`;
  ov.addEventListener("click", e => { if(e.target===ov) ov.remove(); });
  document.body.appendChild(ov);
  return ov;
}
function closeModal() {
  document.querySelector(".modal-overlay")?.remove();
}

function confirm(msg) {
  return new Promise(res => {
    const ov = openModal(`
      <div class="modal-header"><div class="modal-title">Confirm</div></div>
      <div class="modal-body"><p style="color:var(--text2)">${msg}</p></div>
      <div class="modal-footer">
        <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
        <button class="btn btn-danger btn-sm" id="confirm-yes">Confirm</button>
      </div>`);
    $("confirm-yes").onclick = () => { closeModal(); res(true); };
  });
}

// ── nav config ────────────────────────────────
const NAV_ALL = [
  { view:"dashboard",  icon:"⬡", label:"Dashboard" },
  { view:"members",    icon:"👥", label:"Members",      adminOnly: true },
  { view:"portfolio",  icon:"🪪", label:"My Portfolio", userOnly: true },
  { view:"players",    icon:"🏅", label:"Players",      adminOnly: true },
  { view:"coaches",    icon:"🏋", label:"Coaches",      adminOnly: true },
  { view:"teams",      icon:"🏆", label:"Teams" },
  { view:"facilities", icon:"🏟", label:"Facilities" },
  { view:"bookings",   icon:"📅", label:"Bookings" },
  { view:"equipment",  icon:"🎽", label:"Equipment",    adminOnly: true },
  { view:"events",     icon:"🎉", label:"Events" },
  { view:"complaints", icon:"📋", label:"Complaints" },
  { view:"attendance", icon:"✅", label:"Attendance" },
  { view:"stats",      icon:"📊", label:"My Stats",     userOnly: true },
  { view:"stats",      icon:"📊", label:"Player Stats", adminOnly: true },
];
const NAV_ADMIN = [
  { view:"auditlogs",  icon:"🔍", label:"Audit Logs", adminOnly:true },
  { view:"benchmark",  icon:"⚡", label:"Benchmark",  adminOnly:true },
];

// ── state ─────────────────────────────────────
let currentView = "dashboard";

function buildSidebar() {
  const nav = $("sidebar-nav");
  const u = API.currentUser;
  let html = `<div class="nav-section">Navigation</div>`;
  for (const n of NAV_ALL) {
    if (n.userOnly && u.role !== "user") continue;
    if (n.adminOnly && u.role !== "admin") continue;
    html += `<div class="nav-item${currentView===n.view?' active':''}" onclick="navigate('${n.view}')">
      <span class="nav-icon">${n.icon}</span><span>${n.label}</span></div>`;
  }
  if (u.role === "admin") {
    html += `<div class="nav-section" style="margin-top:8px">Admin</div>`;
    for (const n of NAV_ADMIN) {
      html += `<div class="nav-item${currentView===n.view?' active':''}" onclick="navigate('${n.view}')">
        <span class="nav-icon">${n.icon}</span><span>${n.label}</span></div>`;
    }
  }
  nav.innerHTML = html;
  $("user-info-bar").innerHTML = `
    <div class="uname">${u.username}</div>
    <div class="urole">${badge(u.role, u.role==="admin"?"admin":"user")}</div>`;
}

function navigate(view) {
  currentView = view;
  document.querySelectorAll(".view").forEach(v => v.classList.add("hidden"));
  $(`view-${view}`)?.classList.remove("hidden");
  buildSidebar();
  renderView(view);
}

async function renderView(view) {
  const container = $(`view-${view}`);
  container.innerHTML = `<div class="loading-state"><div class="spinner"></div> Loading…</div>`;
  try {
    switch(view) {
      case "dashboard":   await renderDashboard(container); break;
      case "members":     await renderMembers(container);   break;
      case "portfolio":   await renderPortfolio(container, API.currentUser.member_id); break;
      case "players":     await renderPlayers(container);   break;
      case "coaches":     await renderCoaches(container);   break;
      case "teams":       await renderTeams(container);     break;
      case "facilities":  await renderFacilities(container);break;
      case "bookings":    await renderBookings(container);  break;
      case "equipment":   await renderEquipment(container); break;
      case "events":      await renderEvents(container);    break;
      case "complaints":  await renderComplaints(container);break;
      case "attendance":  await renderAttendance(container);break;
      case "stats":       await renderStats(container);     break;
      case "auditlogs":   await renderAuditLogs(container); break;
      case "benchmark":   await renderBenchmark(container); break;
    }
  } catch(e) {
    container.innerHTML = `<div class="alert alert-error">${e.message}</div>`;
  }
}

// ── LOGIN / LOGOUT ────────────────────────────
async function doLogin() {
  const user = $("login-user").value.trim();
  const pass = $("login-pass").value.trim();
  if (!user || !pass) return showAlert("login-error","Please enter credentials");
  try {
    const data = await API.login(user, pass);
    API.token = data.session_token;
    API.currentUser = { username: data.username, role: data.role, member_id: data.member_id };
    localStorage.setItem("sc_token", data.session_token);
    localStorage.setItem("sc_user", JSON.stringify(API.currentUser));
    $("page-login").classList.remove("active");
    $("page-app").classList.add("active");
    buildSidebar();
    navigate("dashboard");
  } catch(e) {
    showAlert("login-error", e.message);
  }
}

async function doLogout() {
  try { await API.logout(); } catch(_) {}
  API.token = null; API.currentUser = null;
  localStorage.removeItem("sc_token");
  localStorage.removeItem("sc_user");
  $("page-app").classList.remove("active");
  $("page-login").classList.add("active");
  $("login-pass").value = "";
}

// ── AUTO-LOGIN from localStorage ──────────────
(async function init() {
  const t = localStorage.getItem("sc_token");
  const u = localStorage.getItem("sc_user");
  // JWT tokens have 3 parts separated by dots — clear old session hex tokens
  if (t && t.split(".").length !== 3) { localStorage.clear(); }
  const t2 = localStorage.getItem("sc_token");
  if (t2 && u) {
    API.token = t2;
    try {
      await API.isAuth();
      API.currentUser = JSON.parse(u);
      $("page-login").classList.remove("active");
      $("page-app").classList.add("active");
      buildSidebar();
      navigate("dashboard");
      return;
    } catch(_) { localStorage.clear(); }
  }
  $("page-login").classList.add("active");
  $("login-user").addEventListener("keydown", e => { if(e.key==="Enter") doLogin(); });
  $("login-pass").addEventListener("keydown", e => { if(e.key==="Enter") doLogin(); });
})();

// ══════════════════════════════════════════════
// VIEWS
// ══════════════════════════════════════════════

// ── DASHBOARD ─────────────────────────────────
async function renderDashboard(c) {
  const isAdmin = API.currentUser.role === "admin";
  let stats = {};
  if (isAdmin) stats = await API.getDashboard();

  c.innerHTML = `
  <div class="page-header">
    <div>
      <div class="page-title">Good day, <span>${API.currentUser.username}</span></div>
      <div class="page-subtitle">Sports Club Management · IIT Gandhinagar</div>
    </div>
  </div>
  ${isAdmin ? `
  <div class="stat-grid">
    ${statCard("👥","Members",   stats.total_members,   "")}
    ${statCard("🏅","Players",   stats.total_players,   "")}
    ${statCard("🏋","Coaches",   stats.total_coaches,   "")}
    ${statCard("🛡","Admins",    stats.total_admins,    "")}
    ${statCard("🏆","Teams",     stats.total_teams,     "accent")}
    ${statCard("🎉","Events",    stats.total_events,    "")}
    ${statCard("📋","Open Issues",stats.open_complaints,"accent")}
    ${statCard("🎽","Active Loans",stats.active_loans,  "")}
  </div>
  <div class="card">
    <div class="card-title">Recent Activity</div>
    <div class="log-strip">
      <div class="log-strip-row" style="color:var(--text3);font-size:10px">
        <div>TIMESTAMP</div><div>ACTION</div><div>STATUS</div><div>DETAIL</div>
      </div>
      ${(stats.recent_logs||[]).map(l=>`
        <div class="log-strip-row">
          <div style="color:var(--text3)">${l.Timestamp}</div>
          <div style="color:var(--text)">${l.Action}</div>
          <div class="log-status-${l.Status}">${l.Status}</div>
          <div style="color:var(--text3)">—</div>
        </div>`).join("")}
    </div>
  </div>` : `
  <div class="card">
    <div class="card-title">Your Account</div>
    <p style="color:var(--text2);margin-bottom:14px">Welcome back! Use the sidebar to navigate.</p>
    <div class="flex gap-2">
      <button class="btn btn-primary btn-sm" onclick="navigate('portfolio')">View My Portfolio</button>
      <button class="btn btn-ghost btn-sm" onclick="navigate('bookings')">My Bookings</button>
    </div>
  </div>`}`;
}

function statCard(icon, label, val, cls) {
  return `<div class="stat-card${cls?' stat-'+cls:''}">
    <div class="s-icon">${icon}</div>
    <div class="s-val">${val ?? "—"}</div>
    <div class="s-label">${label}</div>
  </div>`;
}

// ── MEMBERS ───────────────────────────────────
async function renderMembers(c) {
  const members = await API.getMembers();
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">Members</div><div class="page-subtitle">${members.length} total</div></div>
    ${isAdmin ? `<button class="btn btn-primary btn-sm" onclick="openAddMember()">+ Add Member</button>` : ""}
  </div>
  <div id="members-alert"></div>
  <div class="table-wrap">
    <table>
      <thead><tr>
        <th>ID</th><th>Name</th><th>Gender</th><th>Email</th>
        ${isAdmin?"<th>Phone</th>":""}
        <th>Age</th>${isAdmin?"<th>DOB</th>":""}
        <th>Actions</th>
      </tr></thead>
      <tbody>
      ${members.map(m => `<tr>
        <td>${mono(m.Member_ID)}</td>
        <td><b style="color:var(--text)">${m.Name}</b></td>
        <td>${m.Gender==="M"?badge("M","blue"):badge("F","purple")}</td>
        <td style="color:var(--text3);font-size:12px">${m.Email}</td>
        ${isAdmin?`<td style="font-family:var(--font-mono);font-size:12px">${m.Phone_Number||"—"}</td>`:""}
        <td>${m.Age}</td>
        ${isAdmin?`<td style="color:var(--text3);font-size:12px">${m.DOB||"—"}</td>`:""}
        <td>
          <div class="flex gap-2">
            <button class="btn btn-ghost btn-sm btn-icon" onclick="viewPortfolio('${m.Member_ID}')" title="Portfolio">🪪</button>
            ${isAdmin?`<button class="btn btn-danger btn-sm btn-icon" onclick="deleteMember('${m.Member_ID}')" title="Delete">🗑</button>`:""}
          </div>
        </td>
      </tr>`).join("")}
      </tbody>
    </table>
  </div>`;
}

function viewPortfolio(id) { navigate("portfolio"); renderPortfolio($("view-portfolio"), id); }

async function deleteMember(id) {
  if (!await confirm(`Delete member ${id}? This will cascade delete all related records.`)) return;
  try {
    await API.deleteMember(id);
    navigate("members");
  } catch(e) { alert(e.message); }
}

function openAddMember() {
  openModal(`
    <div class="modal-header"><div class="modal-title">Add Member</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div id="add-member-alert"></div>
      <div class="form-group"><label>Member ID</label><input id="m-id" placeholder="e.g. M41"/></div>
      <div class="form-group"><label>Name</label><input id="m-name" placeholder="Full name"/></div>
      <div class="form-group"><label>Gender</label>
        <select id="m-gender"><option value="M">Male</option><option value="F">Female</option></select></div>
      <div class="form-group"><label>Email</label><input id="m-email" type="email" placeholder="user@iitgn.ac.in"/></div>
      <div class="form-group"><label>Phone</label><input id="m-phone" placeholder="9000000041"/></div>
      <div class="form-group"><label>Age</label><input id="m-age" type="number" placeholder="20"/></div>
      <div class="form-group"><label>Date of Birth</label><input id="m-dob" type="date"/></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitAddMember()">Create</button>
    </div>`);
}

async function submitAddMember() {
  const d = {
    Member_ID: $("m-id").value.trim(), Name: $("m-name").value.trim(),
    Gender: $("m-gender").value, Email: $("m-email").value.trim(),
    Phone_Number: $("m-phone").value.trim(), Age: parseInt($("m-age").value),
    DOB: $("m-dob").value || null
  };
  try {
    await API.createMember(d);
    closeModal(); navigate("members");
  } catch(e) { showAlert("add-member-alert", e.message); }
}

// ── PORTFOLIO ─────────────────────────────────
async function renderPortfolio(c, memberId) {
  if (!memberId) memberId = API.currentUser.member_id;
  try {
    const p = await API.getPortfolio(memberId);
    const m = p.member;
    const initials = m.Name.split(" ").map(x=>x[0]).join("").slice(0,2).toUpperCase();
    const roleColor = p.role_type==="admin"?"accent": p.role_type==="coach"?"blue":"green";
    c.innerHTML = `
    <div class="page-header">
      <div><div class="page-title">Member Portfolio</div></div>
      ${API.currentUser.role==="admin"?`<button class="btn btn-ghost btn-sm" onclick="navigate('members')">← Members</button>`:""}
    </div>
    <div class="portfolio-hero">
      <div class="portfolio-avatar">${initials}</div>
      <div>
        <div class="portfolio-name">${m.Name}</div>
        <div class="portfolio-email">${m.Email}</div>
        <div class="portfolio-meta">
          ${badge(m.Gender==="M"?"Male":"Female", "blue")}
          ${badge(p.role_type, roleColor)}
          ${badge("Age " + m.Age, "purple")}
          ${m.DOB?badge("DOB: "+m.DOB,"blue"):""}
          ${m.Phone_Number?badge(m.Phone_Number,"purple"):""}
          ${p.player_info?badge("Roll #"+p.player_info.Roll_No,"green"):""}
          ${p.player_info&&p.player_info.Blood_Group?badge(p.player_info.Blood_Group,"red"):""}
          ${p.player_info&&p.player_info.Height?badge("H: "+p.player_info.Height+"cm","green"):""}
          ${p.player_info&&p.player_info.Weight?badge("W: "+p.player_info.Weight+"kg","blue"):""}
          ${p.admin_info?badge("Admin Lvl "+p.admin_info.Admin_Level,"yellow"):""}
          ${p.admin_info&&p.admin_info.Department?badge(p.admin_info.Department,"purple"):""}
          ${p.admin_info&&p.admin_info.Office_Location?badge(p.admin_info.Office_Location,"blue"):""}
          ${p.coach_info?badge("Coach: "+p.coach_info.Sport_Name,"blue"):""}
          ${p.coach_info&&p.coach_info.Years_Experience?badge(p.coach_info.Years_Experience+" yrs exp","green"):""}
        </div>
      </div>
    </div>
    <div class="section-tabs">
      ${["stats","teams","attendance","loans","bookings","complaints"].map(t=>`
        <button class="tab-btn${t==="stats"?" active":""}" onclick="switchTab(this,'ptab-${t}')">${t.charAt(0).toUpperCase()+t.slice(1)}</button>`).join("")}
    </div>
    <div id="ptab-stats">   ${portfolioTable("Performance Stats",  p.stats,        ["Metric_Name","Metric_Value","Recorded_Date","Event_ID"])}</div>
    <div id="ptab-teams"    class="hidden">${portfolioTable("Teams",   p.teams,        ["Team_Name","Category","Sport_Name"])}</div>
    <div id="ptab-attendance" class="hidden">${portfolioTable("Attendance", p.attendance, ["Session","Date","Status"])}</div>
    <div id="ptab-loans"    class="hidden">${portfolioTable("Equipment Loans", p.equipment_loans, ["Equipment_Name","Quantity","Issue_Time","Return_Time"])}</div>
    <div id="ptab-bookings" class="hidden">${portfolioTable("Facility Bookings", p.facility_bookings, ["Facility_Name","Time_In","Time_Out"])}</div>
    <div id="ptab-complaints" class="hidden">${portfolioTable("Complaints", p.complaints, ["Complaint_ID","Description","Status","Date_Filed"])}</div>`;
  } catch(e) {
    c.innerHTML = `<div class="alert alert-error">${e.message}</div>`;
  }
}

function portfolioTable(title, rows, cols) {
  if (!rows || !rows.length) return `<div class="card"><div class="card-title">${title}</div><div class="empty-state"><div class="ei">📭</div>No records</div></div>`;
  return `<div class="card">
    <div class="card-title">${title}</div>
    <div class="table-wrap">
      <table>
        <thead><tr>${cols.map(c=>`<th>${c.replace(/_/g," ")}</th>`).join("")}</tr></thead>
        <tbody>${rows.map(r=>`<tr>${cols.map(c=>{
          const v = r[c]??""
          if (c==="Status") return `<td>${v==="Present"||v==="Available"||v==="Resolved"?badge(v,"green"):badge(v,"red")}</td>`;
          if (c==="Return_Time"||c==="Time_Out") return `<td>${v?badge("Returned","green"):badge("Active","yellow")}</td>`;
          return `<td style="color:var(--text2)">${v||"—"}</td>`;
        }).join("")}</tr>`).join("")}</tbody>
      </table>
    </div>
  </div>`;
}

function switchTab(btn, tabId) {
  document.querySelectorAll(".tab-btn").forEach(b=>b.classList.remove("active"));
  btn.classList.add("active");
  document.querySelectorAll("[id^='ptab-']").forEach(d=>d.classList.add("hidden"));
  $(tabId)?.classList.remove("hidden");
}

// ── PLAYERS ───────────────────────────────────
async function renderPlayers(c) {
  const rows = await API.getPlayers();
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">Players</div><div class="page-subtitle">${rows.length} registered</div></div>
    ${isAdmin?`<button class="btn btn-primary btn-sm" onclick="openAddPlayer()">+ Add Player</button>`:""}
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th>Member ID</th><th>Roll No</th><th>Name</th><th>Gender</th><th>Age</th><th>Height</th><th>Weight</th><th>Blood Group</th><th>Email</th>${isAdmin?"<th>Actions</th>":""}</tr></thead>
    <tbody>${rows.map(r=>`<tr>
      <td>${mono(r.Member_ID)}</td>
      <td>${mono(r.Roll_No)}</td>
      <td><b style="color:var(--text)">${r.Name}</b></td>
      <td>${r.Gender==="M"?badge("M","blue"):badge("F","purple")}</td>
      <td>${r.Age}</td>
      <td style="color:var(--text3);font-size:12px">${r.Height||"—"}</td>
      <td style="color:var(--text3);font-size:12px">${r.Weight||"—"}</td>
      <td>${r.Blood_Group?badge(r.Blood_Group,"red"):"—"}</td>
      <td style="color:var(--text3);font-size:12px">${r.Email}</td>
      ${isAdmin?`<td><button class="btn btn-danger btn-sm btn-icon" onclick="deletePlayer('${r.Member_ID}')">🗑</button></td>`:""}
    </tr>`).join("")}</tbody>
  </table></div>`;
}

async function deletePlayer(id) {
  if (!await confirm(`Remove player record for ${id}?`)) return;
  try { await API.deletePlayer(id); navigate("players"); } catch(e) { alert(e.message); }
}

function openAddPlayer() {
  openModal(`
    <div class="modal-header"><div class="modal-title">Add Player</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div id="ap-alert"></div>
      <div class="form-group"><label>Member ID (must exist)</label><input id="ap-mid" placeholder="M41"/></div>
      <div class="form-group"><label>Roll No</label><input id="ap-roll" type="number" placeholder="121"/></div>
      <div class="form-group"><label>Height (cm)</label><input id="ap-height" type="number" placeholder="175"/></div>
      <div class="form-group"><label>Weight (kg)</label><input id="ap-weight" type="number" placeholder="70"/></div>
      <div class="form-group"><label>Blood Group</label>
        <select id="ap-blood"><option value="">— Select —</option>
          <option>A+</option><option>A-</option><option>B+</option><option>B-</option>
          <option>AB+</option><option>AB-</option><option>O+</option><option>O-</option>
        </select></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitPlayer()">Add</button>
    </div>`);
}
async function submitPlayer() {
  try {
    await API.createPlayer({
      Member_ID: $("ap-mid").value.trim(),
      Roll_No: parseInt($("ap-roll").value),
      Height: $("ap-height").value ? parseFloat($("ap-height").value) : null,
      Weight: $("ap-weight").value ? parseFloat($("ap-weight").value) : null,
      Blood_Group: $("ap-blood").value || null
    });
    closeModal(); navigate("players");
  } catch(e) { showAlert("ap-alert", e.message); }
}


// ── COACHES ───────────────────────────────────
async function renderCoaches(c) {
  const rows = await API.getCoaches();
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">Coaches</div><div class="page-subtitle">${rows.length} registered</div></div>
    ${isAdmin?`<button class="btn btn-primary btn-sm" onclick="openAddCoach()">+ Add Coach</button>`:""}
  </div>
  <div class="table-wrap"><table>
    <thead><tr>
      <th>Member ID</th><th>Coach ID</th><th>Name</th><th>Sport</th>
      <th>Experience</th><th>Salary</th><th>Joining Date</th><th>Email</th>
      ${isAdmin?"<th>Actions</th>":""}
    </tr></thead>
    <tbody>${rows.map(r=>`<tr>
      <td>${mono(r.Member_ID)}</td>
      <td>${mono(r.Coach_ID)}</td>
      <td><b style="color:var(--text)">${r.Name}</b></td>
      <td>${badge(r.Sport_Name,"blue")}</td>
      <td>${r.Years_Experience!=null?r.Years_Experience+" yrs":"—"}</td>
      <td>${r.Salary!=null?"₹"+r.Salary:"—"}</td>
      <td style="color:var(--text3);font-size:12px">${r.Joining_Date||"—"}</td>
      <td style="color:var(--text3);font-size:12px">${r.Email||"—"}</td>
      ${isAdmin?`<td><button class="btn btn-danger btn-sm btn-icon" onclick="deleteCoach('${r.Member_ID}')">🗑</button></td>`:""}
    </tr>`).join("")}</tbody>
  </table></div>`;
}

async function deleteCoach(id) {
  if (!await confirm(`Remove coach record for ${id}?`)) return;
  try { await API.deleteCoach(id); navigate("coaches"); } catch(e) { alert(e.message); }
}

function openAddCoach() {
  openModal(`
    <div class="modal-header"><div class="modal-title">Add Coach</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div id="ac-alert"></div>
      <div class="form-group"><label>Member ID (must exist)</label><input id="ac-mid" placeholder="M21"/></div>
      <div class="form-group"><label>Coach ID (unique number)</label><input id="ac-cid" type="number" placeholder="21"/></div>
      <div class="form-group"><label>Sport ID</label><input id="ac-sport" placeholder="S01"/></div>
      <div class="form-group"><label>Years Experience</label><input id="ac-exp" type="number" placeholder="5"/></div>
      <div class="form-group"><label>Salary</label><input id="ac-sal" type="number" placeholder="50000"/></div>
      <div class="form-group"><label>Joining Date</label><input id="ac-date" type="date"/></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitCoach()">Add</button>
    </div>`);
}

async function submitCoach() {
  try {
    await API.createCoach({
      Member_ID: $("ac-mid").value.trim(),
      Coach_ID: parseInt($("ac-cid").value),
      Sport_ID: $("ac-sport").value.trim(),
      Years_Experience: $("ac-exp").value ? parseInt($("ac-exp").value) : 0,
      Salary: $("ac-sal").value ? parseFloat($("ac-sal").value) : 0,
      Joining_Date: $("ac-date").value || null
    });
    closeModal(); navigate("coaches");
  } catch(e) { showAlert("ac-alert", e.message); }
}

// ── TEAMS ─────────────────────────────────────
async function renderTeams(c) {
  const rows = await API.getTeams();
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">Teams</div><div class="page-subtitle">${rows.length} teams</div></div>
    ${isAdmin?`<button class="btn btn-primary btn-sm" onclick="openAddTeam()">+ Add Team</button>`:""}
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th><th>Team Name</th><th>Category</th><th>Sport</th><th>Coach</th><th>Roster</th>${isAdmin?"<th>Actions</th>":""}</tr></thead>
    <tbody>${rows.map(r=>`<tr>
      <td>${mono(r.Team_ID)}</td>
      <td><b style="color:var(--text)">${r.Team_Name}</b></td>
      <td>${badge(r.Category, r.Category==="Hallabol"?"yellow":"blue")}</td>
      <td>${r.Sport_Name}</td>
      <td style="color:var(--text3)">${r.Coach_Name}</td>
      <td><button class="btn btn-ghost btn-sm" onclick="openRoster('${r.Team_ID}','${r.Team_Name}')">View</button></td>
      ${isAdmin?`<td><button class="btn btn-danger btn-sm btn-icon" onclick="deleteTeam('${r.Team_ID}')">🗑</button></td>`:""}
    </tr>`).join("")}</tbody>
  </table></div>`;
}

async function openRoster(teamId, teamName) {
  const rows = await API.getRoster(teamId);
  openModal(`
    <div class="modal-header"><div class="modal-title">${teamName} Roster</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div class="table-wrap"><table>
        <thead><tr><th>Roll No</th><th>Member ID</th><th>Name</th></tr></thead>
        <tbody>${rows.map(r=>`<tr><td>${mono(r.Roll_No)}</td><td>${mono(r.Member_ID)}</td><td>${r.Name}</td></tr>`).join("")}</tbody>
      </table></div>
    </div>`);
}

async function deleteTeam(id) {
  if (!await confirm(`Delete team ${id}?`)) return;
  try { await API.deleteTeam(id); navigate("teams"); } catch(e) { alert(e.message); }
}

function openAddTeam() {
  openModal(`
    <div class="modal-header"><div class="modal-title">Add Team</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div id="at-alert"></div>
      <div class="form-group"><label>Team ID</label><input id="at-id" placeholder="T21"/></div>
      <div class="form-group"><label>Team Name</label><input id="at-name" placeholder="Hallabol..."/></div>
      <div class="form-group"><label>Category</label><select id="at-cat"><option>Hallabol</option><option>Inter IIT</option></select></div>
      <div class="form-group"><label>Sport ID</label><input id="at-sport" placeholder="S01"/></div>
      <div class="form-group"><label>Coach ID (number)</label><input id="at-coach" type="number" placeholder="1"/></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitTeam()">Create</button>
    </div>`);
}
async function submitTeam() {
  try {
    await API.createTeam({ Team_ID:$("at-id").value.trim(), Team_Name:$("at-name").value.trim(),
      Category:$("at-cat").value, Sport_ID:$("at-sport").value.trim(), Coach_ID:parseInt($("at-coach").value) });
    closeModal(); navigate("teams");
  } catch(e) { showAlert("at-alert", e.message); }
}

// ── FACILITIES ────────────────────────────────
async function renderFacilities(c) {
  const rows = await API.getFacilities();
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header"><div><div class="page-title">Facilities</div></div></div>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th><th>Name</th><th>Description</th><th>Status</th>${isAdmin?"<th>Actions</th>":""}</tr></thead>
    <tbody>${rows.map(r=>`<tr>
      <td>${mono(r.Facility_ID)}</td>
      <td><b style="color:var(--text)">${r.Facility_Name}</b></td>
      <td style="color:var(--text3);font-size:12px">${r.Facility_Description}</td>
      <td>${r.Status==="Available"?badge("Available","green"):r.Status==="Maintenance"?badge("Maintenance","yellow"):badge("Closed","red")}</td>
      ${isAdmin?`<td><button class="btn btn-ghost btn-sm" onclick="openEditFacility(${r.Facility_ID},'${r.Status}')">Edit</button></td>`:""}
    </tr>`).join("")}</tbody>
  </table></div>`;
}

function openEditFacility(id, status) {
  openModal(`
    <div class="modal-header"><div class="modal-title">Update Facility #${id}</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div class="form-group"><label>Status</label>
        <select id="ef-status">
          <option${status==="Available"?" selected":""}>Available</option>
          <option${status==="Maintenance"?" selected":""}>Maintenance</option>
          <option${status==="Closed"?" selected":""}>Closed</option>
        </select></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitFacility(${id})">Update</button>
    </div>`);
}
async function submitFacility(id) {
  try { await API.updateFacility(id,{Status:$("ef-status").value}); closeModal(); navigate("facilities"); }
  catch(e) { alert(e.message); }
}

// ── BOOKINGS ──────────────────────────────────
async function renderBookings(c) {
  const rows = await API.getBookings();
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">Bookings</div><div class="page-subtitle">${rows.length} bookings</div></div>
    <button class="btn btn-primary btn-sm" onclick="openAddBooking()">+ New Booking</button>
  </div>
  <div id="bk-alert"></div>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th>${isAdmin?"<th>Member</th>":""}<th>Facility</th><th>Time In</th><th>Time Out</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>${rows.map(r=>`<tr>
      <td>${mono(r.Booking_ID)}</td>
      ${isAdmin?`<td>${r.Name||r.Member_ID}</td>`:""}
      <td><b style="color:var(--text)">${r.Facility_Name}</b></td>
      <td style="font-family:var(--font-mono);font-size:12px">${r.Time_In}</td>
      <td style="font-family:var(--font-mono);font-size:12px">${r.Time_Out||"—"}</td>
      <td>${r.Time_Out?badge("Completed","green"):badge("Active","yellow")}</td>
      <td><div class="flex gap-2">
        ${!r.Time_Out?`<button class="btn btn-success btn-sm" onclick="checkoutBooking(${r.Booking_ID})">Check Out</button>`:""}
        <button class="btn btn-danger btn-sm btn-icon" onclick="deleteBooking(${r.Booking_ID})">🗑</button>
      </div></td>
    </tr>`).join("")}</tbody>
  </table></div>`;
}

async function checkoutBooking(id) {
  const now = new Date().toISOString().replace("T"," ").slice(0,19);
  try { await API.updateBooking(id,{Time_Out:now}); navigate("bookings"); } catch(e) { alert(e.message); }
}
async function deleteBooking(id) {
  if (!await confirm("Delete this booking?")) return;
  try { await API.deleteBooking(id); navigate("bookings"); } catch(e) { alert(e.message); }
}

function openAddBooking() {
  openModal(`
    <div class="modal-header"><div class="modal-title">New Booking</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div id="ab-alert"></div>
      <div class="form-group"><label>Facility ID (1-20)</label><input id="ab-fac" type="number" min="1" max="20"/></div>
      <div class="form-group"><label>Time In (YYYY-MM-DD HH:MM:SS)</label><input id="ab-tin" placeholder="2026-03-20 09:00:00"/></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitBooking()">Book</button>
    </div>`);
}
async function submitBooking() {
  try {
    await API.createBooking({Facility_ID:parseInt($("ab-fac").value), Time_In:$("ab-tin").value.trim()});
    closeModal(); navigate("bookings");
  } catch(e) { showAlert("ab-alert", e.message); }
}

// ── EQUIPMENT ─────────────────────────────────
async function renderEquipment(c) {
  const [equip, loans] = await Promise.all([API.getEquipment(), API.getLoans()]);
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header"><div><div class="page-title">Equipment</div></div>
    <button class="btn btn-primary btn-sm" onclick="openLoanModal()">+ Issue Loan</button>
  </div>
  <div class="card">
    <div class="card-title">Inventory</div>
    <div class="table-wrap"><table>
      <thead><tr><th>ID</th><th>Name</th><th>Sport</th><th>Qty</th><th>Status</th>${isAdmin?"<th>Actions</th>":""}</tr></thead>
      <tbody>${equip.map(r=>`<tr>
        <td>${mono(r.Equipment_ID)}</td>
        <td><b style="color:var(--text)">${r.Equipment_Name}</b></td>
        <td>${r.Sport_Name}</td>
        <td>${mono(r.Total_Qty)}</td>
        <td>${r.Status==="Available"?badge("Available","green"):r.Status==="Damaged"?badge("Damaged","red"):badge("Out of Stock","yellow")}</td>
        ${isAdmin?`<td><div class="flex gap-2">
          <button class="btn btn-ghost btn-sm" onclick="openEditEquip('${r.Equipment_ID}','${r.Status}',${r.Total_Qty})">Edit</button>
          <button class="btn btn-danger btn-sm btn-icon" onclick="deleteEquip('${r.Equipment_ID}')">🗑</button>
        </div></td>`:""}
      </tr>`).join("")}</tbody>
    </table></div>
  </div>
  <div class="card">
    <div class="card-title">Active Loans</div>
    <div class="table-wrap"><table>
      <thead><tr><th>Member</th><th>Equipment</th><th>Qty</th><th>Issued</th><th>Returned</th></tr></thead>
      <tbody>${loans.map(r=>`<tr>
        <td>${r.Name||r.Member_ID}</td>
        <td>${r.Equipment_Name}</td>
        <td>${mono(r.Quantity)}</td>
        <td style="font-family:var(--font-mono);font-size:12px">${r.Issue_Time}</td>
        <td>${r.Return_Time?badge("Returned","green"):badge("Out","yellow")}</td>
      </tr>`).join("")}</tbody>
    </table></div>
  </div>`;
}

function openEditEquip(id, status, qty) {
  openModal(`
    <div class="modal-header"><div class="modal-title">Edit Equipment ${id}</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div class="form-group"><label>Qty</label><input id="eq-qty" type="number" value="${qty}"/></div>
      <div class="form-group"><label>Status</label><select id="eq-st">
        <option${status==="Available"?" selected":""}>Available</option>
        <option${status==="Damaged"?" selected":""}>Damaged</option>
        <option${status==="Out of Stock"?" selected":""}>Out of Stock</option>
      </select></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitEditEquip('${id}')">Save</button>
    </div>`);
}
async function submitEditEquip(id) {
  try { await API.updateEquipment(id,{Total_Qty:parseInt($("eq-qty").value), Status:$("eq-st").value}); closeModal(); navigate("equipment"); }
  catch(e) { alert(e.message); }
}
async function deleteEquip(id) {
  if (!await confirm("Delete equipment?")) return;
  try { await API.deleteEquipment(id); navigate("equipment"); } catch(e) { alert(e.message); }
}

function openLoanModal() {
  openModal(`
    <div class="modal-header"><div class="modal-title">Issue Equipment Loan</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div id="ln-alert"></div>
      <div class="form-group"><label>Equipment ID</label><input id="ln-eid" placeholder="E01"/></div>
      <div class="form-group"><label>Quantity</label><input id="ln-qty" type="number" value="1"/></div>
      <div class="form-group"><label>Issue Time</label><input id="ln-time" placeholder="2026-03-20 09:00:00"/></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitLoan()">Issue</button>
    </div>`);
}
async function submitLoan() {
  try {
    await API.createLoan({Equipment_ID:$("ln-eid").value.trim(), Quantity:parseInt($("ln-qty").value), Issue_Time:$("ln-time").value.trim()});
    closeModal(); navigate("equipment");
  } catch(e) { showAlert("ln-alert", e.message); }
}

// ── EVENTS ────────────────────────────────────
async function renderEvents(c) {
  const rows = await API.getEvents();
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">Events</div></div>
    ${isAdmin?`<button class="btn btn-primary btn-sm" onclick="openAddEvent()">+ Add Event</button>`:""}
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th><th>Name</th><th>Facility</th><th>Start</th><th>End</th><th>Status</th>${isAdmin?"<th>Actions</th>":""}</tr></thead>
    <tbody>${rows.map(r=>`<tr>
      <td>${mono(r.Event_ID)}</td>
      <td><b style="color:var(--text)">${r.Event_Name}</b></td>
      <td style="color:var(--text3)">${r.Facility_Name}</td>
      <td style="font-family:var(--font-mono);font-size:12px">${fmtDate(r.Start_Time)}</td>
      <td style="font-family:var(--font-mono);font-size:12px">${fmtDate(r.End_Time)}</td>
      <td>${badge(r.Attendance_Status, r.Attendance_Status==="Completed"?"green":r.Attendance_Status==="Cancelled"?"red":"yellow")}</td>
      ${isAdmin?`<td><div class="flex gap-2">
        <button class="btn btn-ghost btn-sm" onclick="openEditEvent('${r.Event_ID}','${r.Attendance_Status}')">Edit</button>
        <button class="btn btn-danger btn-sm btn-icon" onclick="deleteEvent('${r.Event_ID}')">🗑</button>
      </div></td>`:""}
    </tr>`).join("")}</tbody>
  </table></div>`;
}

function openEditEvent(id, status) {
  openModal(`
    <div class="modal-header"><div class="modal-title">Update Event ${id}</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div class="form-group"><label>Status</label><select id="ev-st">
        <option${status==="Completed"?" selected":""}>Completed</option>
        <option${status==="Cancelled"?" selected":""}>Cancelled</option>
        <option${status==="Postponed"?" selected":""}>Postponed</option>
        <option${status==="Preponed"?" selected":""}>Preponed</option>
      </select></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitEditEvent('${id}')">Update</button>
    </div>`);
}
async function submitEditEvent(id) {
  try { await API.updateEvent(id,{Attendance_Status:$("ev-st").value}); closeModal(); navigate("events"); }
  catch(e) { alert(e.message); }
}
async function deleteEvent(id) {
  if (!await confirm("Delete event?")) return;
  try { await API.deleteEvent(id); navigate("events"); } catch(e) { alert(e.message); }
}

function openAddEvent() {
  openModal(`
    <div class="modal-header"><div class="modal-title">Add Event</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div id="ae-alert"></div>
      <div class="form-group"><label>Event ID</label><input id="ae-id" placeholder="EV21"/></div>
      <div class="form-group"><label>Name</label><input id="ae-name"/></div>
      <div class="form-group"><label>Facility ID</label><input id="ae-fac" type="number"/></div>
      <div class="form-group"><label>Description</label><textarea id="ae-desc"></textarea></div>
      <div class="form-group"><label>Start (YYYY-MM-DD HH:MM:SS)</label><input id="ae-start" placeholder="2026-04-01 09:00:00"/></div>
      <div class="form-group"><label>End</label><input id="ae-end" placeholder="2026-04-01 12:00:00"/></div>
      <div class="form-group"><label>Status</label><select id="ae-st">
        <option>Completed</option><option>Cancelled</option><option>Postponed</option><option>Preponed</option>
      </select></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitAddEvent()">Create</button>
    </div>`);
}
async function submitAddEvent() {
  try {
    await API.createEvent({Event_ID:$("ae-id").value.trim(),Event_Name:$("ae-name").value.trim(),
      Facility_ID:parseInt($("ae-fac").value),Description:$("ae-desc").value.trim(),
      Start_Time:$("ae-start").value.trim(),End_Time:$("ae-end").value.trim(),Attendance_Status:$("ae-st").value});
    closeModal(); navigate("events");
  } catch(e) { showAlert("ae-alert",e.message); }
}

// ── COMPLAINTS ────────────────────────────────
async function renderComplaints(c) {
  const rows = await API.getComplaints();
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">Complaints</div></div>
    <button class="btn btn-primary btn-sm" onclick="openFileComplaint()">+ File Complaint</button>
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th>${isAdmin?"<th>Raised By</th>":""}<th>Description</th><th>Status</th><th>Date Filed</th>${isAdmin?"<th>Actions</th>":""}</tr></thead>
    <tbody>${rows.map(r=>`<tr>
      <td>${mono(r.Complaint_ID)}</td>
      ${isAdmin?`<td>${r.Raised_By_Name||r.Raised_By}</td>`:""}
      <td style="color:var(--text2);max-width:300px">${r.Description}</td>
      <td>${r.Status==="Resolved"?badge("Resolved","green"):badge("Open","red")}</td>
      <td style="color:var(--text3);font-size:12px">${r.Date_Filed||"—"}</td>
      ${isAdmin?`<td><div class="flex gap-2">
        ${r.Status==="Open"?`<button class="btn btn-success btn-sm" onclick="resolveComplaint('${r.Complaint_ID}')">Resolve</button>`:""}
        <button class="btn btn-danger btn-sm btn-icon" onclick="deleteComplaint('${r.Complaint_ID}')">🗑</button>
      </div></td>`:""}
    </tr>`).join("")}</tbody>
  </table></div>`;
}
async function resolveComplaint(id) {
  try { await API.resolveComplaint(id); navigate("complaints"); } catch(e) { alert(e.message); }
}
async function deleteComplaint(id) {
  if (!await confirm("Delete complaint?")) return;
  try { await API.deleteComplaint(id); navigate("complaints"); } catch(e) { alert(e.message); }
}
function openFileComplaint() {
  openModal(`
    <div class="modal-header"><div class="modal-title">File Complaint</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div id="fc-alert"></div>
      <div class="form-group"><label>Complaint ID</label><input id="fc-id" placeholder="C21"/></div>
      <div class="form-group"><label>Description</label><textarea id="fc-desc" placeholder="Describe the issue…"></textarea></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitComplaint()">Submit</button>
    </div>`);
}
async function submitComplaint() {
  try {
    await API.createComplaint({Complaint_ID:$("fc-id").value.trim(), Description:$("fc-desc").value.trim()});
    closeModal(); navigate("complaints");
  } catch(e) { showAlert("fc-alert", e.message); }
}

// ── ATTENDANCE ────────────────────────────────
async function renderAttendance(c) {
  const rows = await API.getAttendance();
  const isAdmin = API.currentUser.role === "admin";
  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">Attendance</div></div>
    ${isAdmin?`<button class="btn btn-primary btn-sm" onclick="openMarkAttendance()">+ Mark</button>`:""}
  </div>
  <div class="table-wrap"><table>
    <thead><tr>${isAdmin?"<th>Member</th>":""}<th>Session</th><th>Date</th><th>Status</th></tr></thead>
    <tbody>${rows.map(r=>`<tr>
      ${isAdmin?`<td>${r.Name||r.Member_ID}</td>`:""}
      <td style="color:var(--text)">${r.Session}</td>
      <td style="font-family:var(--font-mono);font-size:12px">${r.Date}</td>
      <td>${r.Status==="Present"?badge("Present","green"):badge("Absent","red")}</td>
    </tr>`).join("")}</tbody>
  </table></div>`;
}
function openMarkAttendance() {
  openModal(`
    <div class="modal-header"><div class="modal-title">Mark Attendance</div><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div id="ma-alert"></div>
      <div class="form-group"><label>Member ID</label><input id="ma-mid" placeholder="M01"/></div>
      <div class="form-group"><label>Session</label><input id="ma-session" placeholder="PE Session"/></div>
      <div class="form-group"><label>Date (YYYY-MM-DD)</label><input id="ma-date" placeholder="2026-03-20"/></div>
      <div class="form-group"><label>Status</label><select id="ma-status"><option>Present</option><option>Absent</option></select></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost btn-sm" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary btn-sm" onclick="submitAttendance()">Mark</button>
    </div>`);
}
async function submitAttendance() {
  try {
    await API.markAttendance({Member_ID:$("ma-mid").value.trim(), Session:$("ma-session").value.trim(),
      Date:$("ma-date").value.trim(), Status:$("ma-status").value});
    closeModal(); navigate("attendance");
  } catch(e) { showAlert("ma-alert", e.message); }
}

// ── STATS ─────────────────────────────────────
async function renderStats(c) {
  const isAdmin = API.currentUser.role === "admin";
  const rows = await API.getStats();

  // For regular users — filter to only their own stats
  const myId = API.currentUser.member_id;
  const display = isAdmin ? rows : rows.filter(r => r.Member_ID === myId);

  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">${isAdmin?"Player Stats":"My Stats"}</div>
    <div class="page-subtitle">${display.length} records</div></div>
    ${isAdmin?`<button class="btn btn-primary btn-sm" onclick="openAddStat()">+ Add Stat</button>`:""}
  </div>
  <div class="table-wrap"><table>
    <thead><tr>
      ${isAdmin?"<th>Member ID</th>":""}
      <th>Metric</th><th>Value</th><th>Date</th><th>Event</th>
      ${isAdmin?"<th>Actions</th>":""}
    </tr></thead>
    <tbody>${display.map(r=>`<tr>
      ${isAdmin?`<td>${mono(r.Member_ID)}</td>`:""}
      <td><b style="color:var(--text)">${r.Metric_Name}</b></td>
      <td style="color:var(--text2)">${r.Metric_Value}</td>
      <td style="color:var(--text3);font-size:12px">${r.Recorded_Date}</td>
      <td style="color:var(--text3);font-size:12px">${r.Event_ID||"—"}</td>
      ${isAdmin?`<td><button class="btn btn-danger btn-sm btn-icon" onclick="deleteStat('${r.Member_ID}','${r.Metric_Name}','${r.Recorded_Date}')">🗑</button></td>`:""}
    </tr>`).join("")}</tbody>
  </table></div>`;
}

// ── AUDIT LOGS ────────────────────────────────
async function renderAuditLogs(c) {
  const data = await API.getLogs(200);
  c.innerHTML = `
  <div class="page-header">
    <div><div class="page-title">Audit Logs</div><div class="page-subtitle">Last ${data.length} entries</div></div>
    <button class="btn btn-ghost btn-sm" onclick="navigate('auditlogs')">↺ Refresh</button>
  </div>
  <div class="card" style="padding:0">
    <div style="padding:14px 18px;display:flex;gap:8px;font-family:var(--font-mono);font-size:10px;color:var(--text3);border-bottom:1px solid var(--border)">
      <div style="width:130px">TIMESTAMP</div>
      <div style="width:90px">STATUS</div>
      <div style="width:90px">ACTION</div>
      <div style="width:90px">TABLE</div>
      <div style="width:90px">USER</div>
      <div>DETAILS</div>
    </div>
    <div style="max-height:70vh;overflow-y:auto">
    ${data.map(l=>`
      <div class="log-entry" style="padding:8px 18px">
        <div class="log-ts">${l.Timestamp}</div>
        <div class="log-status-${l.Status}">${l.Status}</div>
        <div style="width:90px;color:var(--text);font-size:11px">${l.Action}</div>
        <div style="width:90px;color:var(--text3)">${l.Table_Name||"—"}</div>
        <div style="width:90px;color:var(--text2)">${l.Username||"anon"}</div>
        <div class="log-detail">${l.Details||"—"}</div>
      </div>`).join("")}
    </div>
  </div>`;
}

// ── BENCHMARK ─────────────────────────────────
async function renderBenchmark(c) {
  c.innerHTML = `<div class="page-header"><div><div class="page-title">Performance <span>Benchmark</span></div><div class="page-subtitle">SQL Index Analysis — 500 iterations per query</div></div>
    <button class="btn btn-primary btn-sm" id="run-bench-btn" onclick="runBench()">▶ Run Benchmark</button>
  </div>
  <div id="bench-results">
    <div class="card">
      <div class="card-title">About This Benchmark</div>
      <p style="color:var(--text3);line-height:1.7;font-size:13px">
        Each query is executed 500 times and total time is measured in milliseconds.<br>
        The EXPLAIN QUERY PLAN shows whether the DB engine uses an index scan or a full table scan.<br>
        Indexes applied: <span style="color:var(--accent);font-family:var(--font-mono)">idx_userlogin_username, idx_session_token, idx_booking_facility_time, idx_attendance_member_date, idx_complaint_status</span>
      </p>
    </div>
    <div class="alert alert-info">Click <b>Run Benchmark</b> to execute queries and see results.</div>
  </div>`;
}

async function runBench() {
  const btn = $("run-bench-btn");
  btn.disabled = true; btn.textContent = "Running…";
  const res = $("bench-results");
  res.innerHTML = `<div class="loading-state"><div class="spinner"></div> Executing 500× per query…</div>`;
  try {
    const d = await API.getBenchmark();
    const t = d.timings_500_iterations;
    const explain = d.explain_plans;
    const timingKeys = Object.keys(t);
    res.innerHTML = `
    <div class="bench-grid">
      ${timingKeys.map(k=>`
        <div class="bench-card">
          <div class="bench-label">${k.replace(/_/g," ").toUpperCase()}</div>
          <div><span class="bench-val">${t[k]}</span><span class="bench-unit">ms / 500 iters</span></div>
          <div style="margin-top:6px;font-size:11px;color:var(--text3)">${(t[k]/500).toFixed(4)} ms avg/call</div>
        </div>`).join("")}
    </div>
    <div class="card">
      <div class="card-title">EXPLAIN QUERY PLAN — Index Verification</div>
      <p style="color:var(--text3);font-size:12px;margin-bottom:14px">
        Lines containing <b style="color:var(--green)">USING INDEX</b> confirm index usage vs <b style="color:var(--red)">SCAN TABLE</b> (full table scan).
      </p>
      ${Object.entries(explain).map(([qname, plan])=>`
        <div style="margin-bottom:14px">
          <div style="font-family:var(--font-mono);font-size:11px;color:var(--accent);margin-bottom:6px">${qname}</div>
          <div class="explain-box">${plan.map(row=>{
            const detail = row.detail||row[3]||JSON.stringify(row);
            const colored = detail.includes("USING INDEX")||detail.includes("SEARCH") ?
              `<span style="color:var(--green)">${detail}</span>` :
              `<span style="color:var(--red)">${detail}</span>`;
            return colored;
          }).join("\n")}</div>
        </div>`).join("")}
    </div>`;
  } catch(e) {
    res.innerHTML = `<div class="alert alert-error">${e.message}</div>`;
  }
  btn.disabled = false; btn.textContent = "▶ Run Benchmark";
}
