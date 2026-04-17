/* api.js — thin fetch wrapper */
const API = {
  token: null,
  currentUser: null,

  headers() {
    const h = { "Content-Type": "application/json" };
    if (this.token) h["Authorization"] = `Bearer ${this.token}`;
    return h;
  },

  async req(method, url, body) {
    const opts = { method, headers: this.headers() };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
  },

  get:    (url)       => API.req("GET",    url),
  post:   (url, body) => API.req("POST",   url, body),
  put:    (url, body) => API.req("PUT",    url, body),
  delete: (url)       => API.req("DELETE", url),

  // Auth
  login:   (user, password) => API.post("/login",  { user, password }),
  logout:  ()               => API.post("/logout",  {}),
  isAuth:  ()               => API.get("/isAuth"),

  // Members
  getMembers:     ()   => API.get("/members/"),
  getMember:      (id) => API.get(`/members/${id}`),
  getPortfolio:   (id) => API.get(`/members/portfolio/${id}`),
  createMember:   (d)  => API.post("/members/", d),
  updateMember:   (id, d) => API.put(`/members/${id}`, d),
  deleteMember:   (id) => API.delete(`/members/${id}`),

  // Coaches
  getCoaches:   ()    => API.get("/coaches/"),
  createCoach:  (d)   => API.post("/coaches/", d),
  deleteCoach:  (id)  => API.delete(`/coaches/${id}`),

  // Players
  getPlayers:   ()    => API.get("/players/"),
  createPlayer: (d)   => API.post("/players/", d),
  deletePlayer: (id)  => API.delete(`/players/${id}`),

  // Teams
  getTeams:      ()    => API.get("/teams/"),
  getRoster:     (id)  => API.get(`/teams/${id}/roster`),
  createTeam:    (d)   => API.post("/teams/", d),
  deleteTeam:    (id)  => API.delete(`/teams/${id}`),

  // Facilities
  getFacilities:    ()     => API.get("/facilities/"),
  updateFacility:   (id,d) => API.put(`/facilities/${id}`, d),

  // Bookings
  getBookings:   ()    => API.get("/bookings/"),
  createBooking: (d)   => API.post("/bookings/", d),
  updateBooking: (id,d)=> API.put(`/bookings/${id}`, d),
  deleteBooking: (id)  => API.delete(`/bookings/${id}`),

  // Equipment
  getEquipment:  ()    => API.get("/equipment/"),
  getLoans:      ()    => API.get("/equipment/loans"),
  createLoan:    (d)   => API.post("/equipment/loans", d),
  updateEquipment:(id,d)=> API.put(`/equipment/${id}`, d),
  deleteEquipment:(id) => API.delete(`/equipment/${id}`),

  // Events
  getEvents:    ()    => API.get("/events/"),
  createEvent:  (d)   => API.post("/events/", d),
  updateEvent:  (id,d)=> API.put(`/events/${id}`, d),
  deleteEvent:  (id)  => API.delete(`/events/${id}`),

  // Complaints
  getComplaints:   ()    => API.get("/complaints/"),
  createComplaint: (d)   => API.post("/complaints/", d),
  resolveComplaint:(id)  => API.put(`/complaints/${id}`, {}),
  deleteComplaint: (id)  => API.delete(`/complaints/${id}`),

  // Attendance
  getAttendance:  ()  => API.get("/attendance/"),
  markAttendance: (d) => API.post("/attendance/", d),

  // Stats
  getStats:    ()       => API.get("/stats/"),
  createStat:  (d)      => API.post("/stats/", d),
  deleteStat:  (m,n,dt) => API.delete(`/stats/${m}/${encodeURIComponent(n)}/${dt}`),

  // Admin
  getLogs:      (limit) => API.get(`/admin/logs?limit=${limit||100}`),
  getUsers:     ()      => API.get("/admin/users"),
  createUser:   (d)     => API.post("/admin/users", d),
  deleteUser:   (id)    => API.delete(`/admin/users/${id}`),
  getBenchmark: ()      => API.get("/admin/benchmark"),
  getDashboard: ()      => API.get("/admin/dashboard"),
};
