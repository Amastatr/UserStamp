// UserStamp popup logic. Reads and writes chrome.storage.local only.

const MIDDOT = "·";

const DEFAULTS = {
  userstamp_mode: "off",
  userstamp_solo_label: "",
  userstamp_roster: [],
  userstamp_active_seat_id: "",
  userstamp_frequency: "every",
};

const el = (id) => document.getElementById(id);

let state = { ...DEFAULTS };

function tagFor(label) {
  const l = (label || "").trim();
  if (!l) return null;
  return "[USER " + MIDDOT + " " + l + "] ";
}

function genId() {
  return "seat-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);
}

function save(partial) {
  Object.assign(state, partial);
  return chrome.storage.local.set(partial);
}

// ---- Rendering -----------------------------------------------------------
function renderMode() {
  document.querySelectorAll('input[name="mode"]').forEach((r) => {
    r.checked = r.value === state.userstamp_mode;
  });
  document.querySelectorAll('input[name="frequency"]').forEach((r) => {
    r.checked = r.value === state.userstamp_frequency;
  });

  el("soloSection").classList.toggle("hidden", state.userstamp_mode !== "solo");
  el("teamSection").classList.toggle("hidden", state.userstamp_mode !== "team");

  const on = state.userstamp_mode === "solo" || state.userstamp_mode === "team";
  el("statusDot").classList.toggle("on", on);
  el("statusDot").textContent = on ? "ON" : "OFF";
}

function renderSolo() {
  el("soloLabel").value = state.userstamp_solo_label || "";
  const tag = tagFor(state.userstamp_solo_label);
  const preview = el("soloPreview");
  if (tag) {
    preview.innerHTML = "";
    preview.append(document.createTextNode(tag + "summarize this"));
  } else {
    preview.innerHTML = '<span class="muted">Type a signature to preview the tag.</span>';
  }
}

function renderTeam() {
  const roster = state.userstamp_roster || [];

  // Active-seat dropdown
  const select = el("activeSeat");
  select.innerHTML = "";
  if (roster.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No seats yet";
    select.appendChild(opt);
    select.disabled = true;
  } else {
    select.disabled = false;
    roster.forEach((seat) => {
      const opt = document.createElement("option");
      opt.value = seat.id;
      opt.textContent = seat.label;
      select.appendChild(opt);
    });
    // Make sure an active seat is selected.
    if (!roster.some((s) => s.id === state.userstamp_active_seat_id)) {
      state.userstamp_active_seat_id = roster[0].id;
      chrome.storage.local.set({ userstamp_active_seat_id: state.userstamp_active_seat_id });
    }
    select.value = state.userstamp_active_seat_id;
  }

  // Preview of active seat
  const active = roster.find((s) => s.id === state.userstamp_active_seat_id);
  const tag = active ? tagFor(active.label) : null;
  const preview = el("teamPreview");
  if (tag) {
    preview.innerHTML = "";
    preview.append(document.createTextNode(tag + "summarize this"));
  } else {
    preview.innerHTML = '<span class="muted">Add a seat to preview the tag.</span>';
  }

  // Seat list with remove controls
  const list = el("seatList");
  list.innerHTML = "";
  roster.forEach((seat) => {
    const item = document.createElement("div");
    item.className = "seat-item";

    const name = document.createElement("span");
    name.className = "name";
    name.textContent = seat.label;
    item.appendChild(name);

    const remove = document.createElement("button");
    remove.textContent = "Remove";
    remove.addEventListener("click", () => removeSeat(seat.id));
    item.appendChild(remove);

    list.appendChild(item);
  });
}

function renderAll() {
  renderMode();
  renderSolo();
  renderTeam();
}

// ---- Actions -------------------------------------------------------------
function addSeat() {
  const input = el("newSeat");
  const label = input.value.trim();
  if (!label) return;
  const roster = (state.userstamp_roster || []).slice();
  const seat = { id: genId(), label };
  roster.push(seat);

  const partial = { userstamp_roster: roster };
  // First seat becomes the active seat.
  if (!state.userstamp_active_seat_id || roster.length === 1) {
    partial.userstamp_active_seat_id = seat.id;
  }
  save(partial).then(() => {
    input.value = "";
    renderTeam();
  });
}

function removeSeat(id) {
  const roster = (state.userstamp_roster || []).filter((s) => s.id !== id);
  const partial = { userstamp_roster: roster };
  if (state.userstamp_active_seat_id === id) {
    partial.userstamp_active_seat_id = roster.length ? roster[0].id : "";
  }
  save(partial).then(renderTeam);
}

// ---- Wiring --------------------------------------------------------------
function init() {
  chrome.storage.local.get(Object.keys(DEFAULTS), (res) => {
    state = { ...DEFAULTS, ...res };
    if (!Array.isArray(state.userstamp_roster)) state.userstamp_roster = [];
    renderAll();
  });

  document.querySelectorAll('input[name="mode"]').forEach((r) => {
    r.addEventListener("change", () => {
      if (r.checked) save({ userstamp_mode: r.value }).then(renderAll);
    });
  });

  document.querySelectorAll('input[name="frequency"]').forEach((r) => {
    r.addEventListener("change", () => {
      if (r.checked) save({ userstamp_frequency: r.value });
    });
  });

  el("soloLabel").addEventListener("input", (e) => {
    save({ userstamp_solo_label: e.target.value });
    renderSolo();
  });

  el("activeSeat").addEventListener("change", (e) => {
    save({ userstamp_active_seat_id: e.target.value }).then(renderTeam);
  });

  el("addSeat").addEventListener("click", addSeat);
  el("newSeat").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addSeat();
    }
  });
}

document.addEventListener("DOMContentLoaded", init);
