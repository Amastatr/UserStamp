// UserStamp content script.
// On each supported AI-chat site, tags the message a user sends with the
// person at the seat: prepends "[USER · <label>] " to the front of the
// composed text when the user sends (Enter without Shift, or the send button).
//
// This is a label the team agrees to set, not authentication. Everything is
// read from chrome.storage.local; nothing is transmitted.

(() => {
  "use strict";

  const MIDDOT = "·"; // ·
  const TAG_PREFIX = "[USER " + MIDDOT; // idempotency / detection marker

  // ---- Cached settings (read synchronously on send) ----------------------
  // The send path must run synchronously before the site dispatches the
  // message, so we keep a live in-memory copy of storage rather than awaiting
  // a read inside the keydown/click handler.
  let settings = {
    mode: "off",
    soloLabel: "",
    roster: [],
    activeSeatId: "",
    frequency: "every",
  };

  const STORAGE_KEYS = [
    "userstamp_mode",
    "userstamp_solo_label",
    "userstamp_roster",
    "userstamp_active_seat_id",
    "userstamp_frequency",
  ];

  function loadSettings() {
    chrome.storage.local.get(STORAGE_KEYS, (res) => {
      settings.mode = res.userstamp_mode || "off";
      settings.soloLabel = res.userstamp_solo_label || "";
      settings.roster = Array.isArray(res.userstamp_roster)
        ? res.userstamp_roster
        : [];
      settings.activeSeatId = res.userstamp_active_seat_id || "";
      settings.frequency = res.userstamp_frequency || "every";
    });
  }

  loadSettings();

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area !== "local") return;
    if (changes.userstamp_mode) settings.mode = changes.userstamp_mode.newValue || "off";
    if (changes.userstamp_solo_label) settings.soloLabel = changes.userstamp_solo_label.newValue || "";
    if (changes.userstamp_roster) settings.roster = Array.isArray(changes.userstamp_roster.newValue) ? changes.userstamp_roster.newValue : [];
    if (changes.userstamp_active_seat_id) settings.activeSeatId = changes.userstamp_active_seat_id.newValue || "";
    if (changes.userstamp_frequency) settings.frequency = changes.userstamp_frequency.newValue || "every";
  });

  function currentLabel() {
    if (settings.mode === "solo") return (settings.soloLabel || "").trim();
    if (settings.mode === "team") {
      const seat = settings.roster.find((s) => s && s.id === settings.activeSeatId);
      return seat ? (seat.label || "").trim() : "";
    }
    return "";
  }

  // ---- Small, self-contained "new conversation" detector -----------------
  // In "first" frequency we stamp only the first message of a new
  // conversation. We allow a stamp when we land on a fresh/empty chat path,
  // and suppress further stamps until the next time a new chat is started.
  // Navigating from a new-chat path to a conversation id (which happens right
  // after the first message) is the SAME conversation, so it does not re-arm.
  function isNewChatPath(path) {
    const p = (path || "/").replace(/\/+$/, "") || "/";
    return p === "/" || p === "/new" || p === "/app" || p === "/chat";
  }

  let allowFirst = isNewChatPath(location.pathname);
  let lastPath = location.pathname;

  function onPathChange() {
    const p = location.pathname;
    if (p === lastPath) return;
    lastPath = p;
    if (isNewChatPath(p)) allowFirst = true;
  }

  (function watchPath() {
    const fire = () => onPathChange();
    const wrap = (method) => {
      const orig = history[method];
      if (typeof orig !== "function") return;
      history[method] = function () {
        const r = orig.apply(this, arguments);
        fire();
        return r;
      };
    };
    wrap("pushState");
    wrap("replaceState");
    window.addEventListener("popstate", fire);
    setInterval(fire, 1000);
  })();

  // ---- Composer discovery & text insertion -------------------------------
  function isEditable(el) {
    return !!el && (el.tagName === "TEXTAREA" || el.tagName === "INPUT" || el.isContentEditable === true);
  }

  function isVisible(el) {
    if (!el) return false;
    if (el.offsetParent !== null) return true;
    const r = el.getClientRects();
    return r && r.length > 0;
  }

  const COMPOSER_SELECTORS = [
    "#prompt-textarea", // ChatGPT
    'div.ProseMirror[contenteditable="true"]', // Claude
    'div.ql-editor[contenteditable="true"]', // Gemini
    "textarea", // Grok / fallback
    'div[contenteditable="true"]', // generic fallback
  ];

  function getComposer() {
    const a = document.activeElement;
    if (isEditable(a)) return a;
    for (const sel of COMPOSER_SELECTORS) {
      const el = document.querySelector(sel);
      if (el && isVisible(el)) return el;
    }
    return null;
  }

  function getComposerFromEvent(e) {
    const t = e.target;
    if (isEditable(t)) return t;
    if (t && typeof t.closest === "function") {
      const ce = t.closest('[contenteditable="true"], textarea, input');
      if (ce && isEditable(ce)) return ce;
    }
    return getComposer();
  }

  function readText(el) {
    if (el.value !== undefined && el.value !== null) return el.value;
    return el.textContent || "";
  }

  function prependToValueField(el, text) {
    const proto =
      el.tagName === "TEXTAREA"
        ? HTMLTextAreaElement.prototype
        : HTMLInputElement.prototype;
    const desc = Object.getOwnPropertyDescriptor(proto, "value");
    const setter = desc && desc.set;
    const newValue = text + el.value;
    if (setter) {
      setter.call(el, newValue);
    } else {
      el.value = newValue;
    }
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }

  function prependToContentEditable(el, text) {
    el.focus();
    const sel = window.getSelection();
    if (sel) {
      const range = document.createRange();
      range.selectNodeContents(el);
      range.collapse(true); // caret at the very start
      sel.removeAllRanges();
      sel.addRange(range);
    }
    // execCommand('insertText') fires beforeinput/input so React, ProseMirror
    // and Quill all observe the change and keep their internal state in sync.
    document.execCommand("insertText", false, text);
  }

  function prepend(el, text) {
    if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
      prependToValueField(el, text);
    } else {
      prependToContentEditable(el, text);
    }
  }

  // ---- The send hook -----------------------------------------------------
  function maybeStamp(el) {
    if (!isEditable(el)) return;
    if (settings.mode === "off") return;

    const label = currentLabel();
    if (!label) return; // no label -> nothing to stamp with

    if (settings.frequency === "first" && !allowFirst) return;

    const existing = readText(el);
    if (!existing.trim()) return; // empty composer; nothing will send
    if (existing.indexOf(TAG_PREFIX) !== -1) return; // idempotent

    prepend(el, TAG_PREFIX + " " + label + "] ");

    if (settings.frequency === "first") allowFirst = false;
  }

  function isSendButton(btn) {
    if (!btn) return false;
    const testid = (btn.getAttribute("data-testid") || "").toLowerCase();
    if (testid.indexOf("send") !== -1) return true;
    const aria = (btn.getAttribute("aria-label") || "").toLowerCase();
    if (/send|submit/.test(aria)) return true;
    if ((btn.getAttribute("type") || "").toLowerCase() === "submit") return true;
    return false;
  }

  document.addEventListener(
    "keydown",
    (e) => {
      if (e.key !== "Enter" || e.shiftKey) return;
      // Leave IME composition untouched (Japanese/Chinese etc.).
      if (e.isComposing || e.keyCode === 229) return;
      const el = getComposerFromEvent(e);
      maybeStamp(el);
    },
    true // capture: run before the site's own send handler
  );

  document.addEventListener(
    "click",
    (e) => {
      const btn =
        e.target && typeof e.target.closest === "function"
          ? e.target.closest("button")
          : null;
      if (!isSendButton(btn)) return;
      const el = getComposer();
      maybeStamp(el);
    },
    true // capture
  );
})();
