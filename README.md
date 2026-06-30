# UserStamp · AI Contextualizers

Tags each AI-chat message with the team member sending it, for shared
subscriptions. Manifest V3, local only.

UserStamp is the third in the **AI Contextualizers** line, after
TimeStamp and GeoStamp. It prepends a small `[USER · <label>]` tag to the
front of each message you send so a team sharing one AI subscription can
attribute work to a person. It is a label the team agrees to set, not
authentication.

Works on ChatGPT, Claude, Gemini, and Grok.

## Install (unpacked)

1. Open `chrome://extensions`.
2. Enable **Developer mode**.
3. Click **Load unpacked** and select this folder.

## Modes

- **Off** (default) — does nothing.
- **Solo** — stamps with your own signature.
- **Team** — keep a roster of seats and stamp with the active seat.

Set the frequency to stamp **every message** or just the **first message per
conversation**.

The seat label is stored locally on this device (`chrome.storage.local`) and
is never transmitted.

## AI Contextualizers
One of three sibling extensions, TimeStamp, GeoStamp, and UserStamp, by Amastatr Innovation Haus, sharing one discipline: stamps fire once, on send only, and everything stays local.
