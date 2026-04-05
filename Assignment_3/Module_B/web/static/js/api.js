/* api.js — fetch wrappers for Assignment 3 backend */

async function apiFetch(method, path, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    throw new Error(`Server error (${res.status}) while calling ${path}`);
  }
  if (!data.ok) throw new Error(data.error || "Request failed");
  return data;
}

const API = {
  tables:       ()           => apiFetch("GET",  "/api/tables"),
  wal:          ()           => apiFetch("GET",  "/api/wal"),
  recover:      ()           => apiFetch("GET",  "/api/acid/recover"),

  begin:        ()           => apiFetch("POST", "/api/txn/begin",    {}),
  commit:       (txn_id)     => apiFetch("POST", "/api/txn/commit",   {txn_id}),
  rollback:     (txn_id)     => apiFetch("POST", "/api/txn/rollback", {txn_id}),
  insert:       (txn_id, table, record) =>
                               apiFetch("POST", "/api/txn/insert",   {txn_id, table, record}),
  update:       (txn_id, table, key, record) =>
                               apiFetch("POST", "/api/txn/update",   {txn_id, table, key, record}),
  delete:       (txn_id, table, key) =>
                               apiFetch("POST", "/api/txn/delete",   {txn_id, table, key}),

  acidAtomicity:  ()         => apiFetch("POST", "/api/acid/atomicity",   {}),
  acidConsistency:()         => apiFetch("POST", "/api/acid/consistency", {}),
  acidIsolation:  ()         => apiFetch("POST", "/api/acid/isolation",   {}),
  acidDurability: ()         => apiFetch("POST", "/api/acid/durability",  {}),
  acidMulti:      (body)     => apiFetch("POST", "/api/acid/multi",       body),
  updateAllFacilities:()     => apiFetch("POST", "/api/acid/multi/facilities/update-all", {}),
  acidStress:     (body)     => apiFetch("POST", "/api/acid/stress",      body),
  loadStress:     (body)     => apiFetch("POST", "/api/stress/load",      body),
};
