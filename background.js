// UserStamp background service worker (MV3).
// Keeps the toolbar badge in sync with the current mode:
//   solo or team -> "ON" on a green background
//   off          -> "OFF" on a red background

const BADGE_GREEN = "#188038";
const BADGE_RED = "#C8102E";

async function refreshBadge() {
  const { userstamp_mode } = await chrome.storage.local.get("userstamp_mode");
  const mode = userstamp_mode || "off";

  await chrome.action.setBadgeTextColor({ color: "#FFFFFF" });

  if (mode === "solo" || mode === "team") {
    await chrome.action.setBadgeBackgroundColor({ color: BADGE_GREEN });
    await chrome.action.setBadgeText({ text: "ON" });
  } else {
    await chrome.action.setBadgeBackgroundColor({ color: BADGE_RED });
    await chrome.action.setBadgeText({ text: "OFF" });
  }
}

// Update on install, browser startup, and whenever the mode changes.
chrome.runtime.onInstalled.addListener(refreshBadge);
chrome.runtime.onStartup.addListener(refreshBadge);

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.userstamp_mode) {
    refreshBadge();
  }
});

// Run once when the service worker first spins up.
refreshBadge();
