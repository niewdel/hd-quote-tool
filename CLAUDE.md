# HD Hauling & Grading — Proposal Generator
## CLAUDE.md — Project Context for Cursor / Claude Code

---

## Project Overview

A single-page internal web app for HD Hauling & Grading to generate proposals, manage clients, track pipeline stages, and manage users. Built with a Flask backend and a fully self-contained single-file frontend (`index.html`). Deployed on Railway, source on GitHub, database on Supabase.

---

## Infrastructure

| Resource | Value |
|---|---|
| **Live URL** | https://web-production-e19b3.up.railway.app |
| **GitHub Repo** | https://github.com/niewdel/hd-quote-tool |
| **Railway Project ID** | (set in Railway dashboard — do not commit) |
| **Railway Service ID** | (set in Railway dashboard — do not commit) |
| **Supabase URL** | (set via SUPABASE_URL env var — do not commit) |
| **Supabase Anon Key** | (set via SUPABASE_KEY env var — do not commit) |

### Railway Environment Variables
```
APP_PIN=2025
SECRET_KEY=hd-hauling-secret-2025-xK9mP3
SUPABASE_URL=<set in Railway>
SUPABASE_KEY=<set in Railway>
SUPABASE_SERVICE_KEY=<set in Railway>
```

### Deployment
- Push to GitHub `main` branch → Railway auto-deploys (~60 seconds)
- Flask serves `index.html` as a static file from the root route `/`
- All other routes are API endpoints

---

## File Structure

```
/
├── index.html          # Entire frontend — single self-contained file (~159KB)
├── app.py              # Flask backend (~19KB, 25 routes)
├── generate_proposal.py    # PDF generator (ReportLab)
├── generate_change_order.py
├── generate_job_cost.py
├── generate_docx.py        # Word doc generator
├── hd_logo_cropped.png     # Logo for PDF cover page
├── hd_logo.png             # Logo for login bar (has extra padding)
├── requirements.txt
└── Procfile
```

---

## Database Schema (Supabase / PostgreSQL)

### `hd_users`
| Column | Type | Notes |
|---|---|---|
| id | int | PK, auto |
| username | text | lowercase, unique |
| full_name | text | |
| pin_hash | text | SHA256 of PIN |
| role | text | `admin` or `user` |
| active | bool | |
| created_at | timestamptz | |
| created_by | text | username of creator |

**RLS: DISABLED**

### `hd_access_log`
| Column | Type | Notes |
|---|---|---|
| id | int | PK |
| username | text | |
| full_name | text | |
| action | text | `login` or `logout` |
| success | bool | |
| ip_address | text | |
| user_agent | text | |
| logged_at | timestamptz | |

**RLS: DISABLED**

### `proposals` (quotes)
Stores saved proposal snapshots with JSON `snap` field containing all line items, sections, etc.

### `clients`
Client address book — name, company, phone, email, address, city_state, notes.

### `pipeline_stages`
9 stages: New Lead, Estimate Sent, Follow Up, Under Review, Approved, Scheduled, In Progress, Completed, Lost. Each has color, sort_order, counts_in_ratio.

---

## Backend (`app.py`) — API Routes

### Auth
| Method | Route | Description |
|---|---|---|
| POST | `/auth/login` | Username + PIN login. Checks `hd_users` table, falls back to `APP_PIN` env var |
| POST | `/auth/logout` | Clears session, logs to `hd_access_log` |
| GET | `/auth/check` | Returns `{authenticated, role, username, full_name}` |

### Proposals/Quotes
| Method | Route | Description |
|---|---|---|
| POST | `/quotes/save` | Save a proposal snapshot |
| GET | `/quotes/list` | List all saved proposals |
| DELETE | `/quotes/delete/<id>` | Delete a proposal |

### PDF/Word Generation
| Method | Route | Description |
|---|---|---|
| POST | `/generate-pdf` | Generate proposal PDF (ReportLab) |
| POST | `/generate-docx` | Generate proposal Word doc |
| POST | `/generate-change-order` | Generate change order PDF |
| POST | `/generate-job-cost` | Generate job cost sheet |

### Pipeline
| Method | Route | Description |
|---|---|---|
| GET | `/pipeline/list` | List all proposals with pipeline stage |
| GET | `/pipeline/stages` | List pipeline stages |
| POST | `/pipeline/move` | Move proposal to new stage |

### Clients
| Method | Route | Description |
|---|---|---|
| GET | `/clients/list` | List all clients |
| POST | `/clients/save` | Save/update a client |
| DELETE | `/clients/delete/<id>` | Delete a client |

### Admin (require admin role)
| Method | Route | Description |
|---|---|---|
| GET | `/admin/users` | List all users (pins stripped) |
| POST | `/admin/users` | Create new user |
| PATCH | `/admin/users/<id>` | Update user (name, role, pin, active) |
| GET | `/admin/logs` | Activity log with optional `?username=` filter |

---

## Frontend (`index.html`) — Architecture

### Single-File Design
The entire frontend is one HTML file. All CSS, JS, and HTML in one file. No build step, no bundler. This is intentional — keeps deployment simple.

### Panels (navigation sections)
| Panel ID | Nav Label | Description |
|---|---|---|
| `panel-build` | Build Proposal | Main proposal builder |
| `panel-co` | Change Orders | Change order form |
| `panel-saved` | Saved Proposals | Load/manage saved proposals |
| `panel-pipeline` | Pipeline | Kanban-style deal pipeline |
| `panel-clients` | Clients | Client address book |
| `panel-analytics` | Analytics | Revenue/win rate charts |
| `panel-settings` | Settings | Material prices, badges, library |
| `panel-admin` | Admin | User management + activity log |

### Authentication Flow
1. Page loads → startup IIFE calls `/auth/check`
2. If authenticated: hides login screen, shows app, calls `boot()`, then `showAdminElements()`
3. If not: shows login screen with canvas animation
4. `doLogin()` → POST `/auth/login` → on success: set `window._userRole`, call `boot()`, `showAdminElements()`
5. `doLogout()` → POST `/auth/logout` → `location.reload()`

### Admin Nav Visibility
- `nav-admin` element has `data-admin-hidden` attribute by default
- CSS: `[data-admin-hidden]{display:none}`
- `showAdminElements()` calls `removeAttribute('data-admin-hidden')` on all `[data-admin-hidden]` elements
- **Critical**: `boot()` crashes if called when sections/DOM aren't ready — wrapped in `try/catch` so `showAdminElements()` always runs after

### Key Global Variables
```js
window._userRole      // 'admin' or 'user'
window._userName      // full name
window._userUsername  // username
window._adminUsers    // {id: userObject} map for edit modal

// Pricing data
MAT        // {material: costPerTon} — editable in Settings
MAT_DEFAULT // original defaults (for reset)
LBS        // {material: lbsPerTon} — hidden, not shown in UI
DRATE      // {material: defaultBidRate}
DDEPTH     // {material: defaultDepth}
LBADGE     // {material: badgeCssClass}
LTYPES     // array of material names

// Concrete types
CTYPES     // [{id, name, desc, unit, cy_per_lf}]
           // cy_per_lf = cubic yards per linear foot

// Badge definitions
BADGE_DEFS // {cssClass: {label, color}} — editable in Settings

// Bid Items Library
BID_LIBRARY  // [{id, name, desc, unit, rate}] — persisted in localStorage
_libId       // auto-increment counter for library items

// Job cost
jcCrewRate      // crew day rate ($)
jcOverheadPct   // overhead %
jcProductivity  // tons/day (note: variable name is jcProductivity, NOT productivity)

// Proposal state
sections    // pavement sections array
concItems   // concrete items array
extraItems  // additional items array [{id, name, desc, qty, unit, price, subtotal}]
```

### Material Pricing System
- Materials stored in `MAT` object (cost $/ton) — editable in Settings
- `LBS` stores density (lbs/ton) — used internally for tonnage calc, NOT shown in UI
- `DRATE` stores default bid rates, `DDEPTH` stores default depths
- `LBADGE` maps material name → CSS badge class
- `renderMatTable()` renders the settings table — all rows are deletable including defaults
- Density column intentionally removed from UI (still used in calculations)

### Concrete CY Calculation
```js
// cy_per_lf values per concrete type:
// 18" Standard C&G: 0.028, 24": 0.037, 30": 0.046
// 6" Vertical Curb: 0.012, 6" Mountable: 0.012
// Valley Gutter: 0.049, Ribbon Curb: 0.019
// Concrete Flume: 0.019, Thickened Edge: 0.009

function calcConcCY(item) {
  // returns cubic yards = qty * cy_per_lf
}
```
CY is displayed in green next to each concrete row result.

### Settings Panel Cards (in order)
1. **Sender Information** — name, email, phone for proposal header
2. **Job Cost Defaults** — crew day rate, overhead %, productivity (t/day)
3. **Material Prices** — editable table (cost, rate, depth, badge) + delete all rows
4. **Layer Badges** — add/remove/rename badge types (Base, Binder, Surface, Millings, Concrete)
5. **Bid Items Library** — reusable line items with descriptions

### Bid Items Library
- Stored in `localStorage` key `hd_bid_library`
- `renderLibraryList()` — renders in Settings
- `openLibraryPicker()` — modal picker in Build Proposal
- Clicking "Insert" in picker adds item to `extraItems` with name, desc, unit, price pre-filled

### Additional Items (Extra Items)
- Each item has: `{id, name, desc, qty, unit, price, subtotal}`
- Description field added (`updExtraDesc()` function)
- "From Library" button opens `openLibraryPicker()` modal
- `renderExtra()` built with DOM API (not innerHTML strings) to avoid escaping issues

### Login Page
- Full-screen black background with animated red particle network canvas (`initLoginCanvas()`)
- Canvas: 60 nodes drifting, connected with red lines when within 160px
- White top bar with HD logo
- "HD HAULING & GRADING" title: `font-size:30px`, red, letter-spaced
- Username + PIN fields, ACCESS TOOL button

### Admin Panel
- **User Management tab**: table of all users, Edit button for all (including self), Deactivate for others only
- **Activity Log tab**: timestamped logins with IP, filterable by user
- Edit user modal uses `window._adminUsers[id]` lookup (not JSON.stringify inline) to avoid escaping issues with special chars in names

---

## Known Issues & Important Notes

### ⚠️ File Editing Warning
**Do NOT edit `index.html` using string concatenation or template literals with mixed quote styles.** All previous corruption was caused by this. Always use:
- DOM API (`createElement`, `addEventListener`) for dynamic content
- Simple string replacements with consistent quote style
- Test with `src.includes('functionName')` before pushing

### ⚠️ boot() Error Handling
`boot()` is wrapped in `try/catch` in both the doLogin and auth/check paths because `renderJCDefaults()` can throw if called before the DOM is ready. `showAdminElements()` must always run AFTER boot(), even if boot throws.

### ⚠️ Variable Name: `jcProductivity`
The productivity variable is `jcProductivity` — NOT `productivity`. Using `productivity` causes a ReferenceError that crashes `boot()`.

### ⚠️ Admin Nav
Uses `data-admin-hidden` attribute + CSS `[data-admin-hidden]{display:none}`. Do NOT use inline `style.display=''` (empty string) to show it — this clears the inline style but the CSS class rule still hides it. Use `removeAttribute('data-admin-hidden')` instead.

### ⚠️ Pushing to GitHub
The only safe way to push is via the GitHub Contents API with proper base64 encoding:
```js
const bytes = new TextEncoder().encode(src);
let bin = '';
for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
const b64 = btoa(bin);
// Verify roundtrip before pushing:
const rt = new TextDecoder('utf-8').decode(Uint8Array.from(atob(b64), c => c.charCodeAt(0))) === src;
```
Always verify roundtrip. Never use `btoa(unescape(encodeURIComponent(src)))` — causes file doubling.

### renderExtra() and renderBadgeList()
These functions MUST use the DOM API, not innerHTML string building. Previous versions using HTML strings caused `SyntaxError: Unexpected identifier` that broke the entire app.

---

## Default Seed Data

### Admin User
- Username: `justin`
- Full Name: Justin Ledwein
- PIN: `2025`
- Role: admin

### Default Materials
```js
MAT = {'ABC base':45, 'Mill & Pave':35, 'B25.0C':85, 'I19.0C':92, 'S9.5B':95, 'S9.5C':95}
LBS = {'ABC base':150, 'Mill & Pave':115, 'B25.0C':115, 'I19.0C':115, 'S9.5B':115, 'S9.5C':115}
```

### Default Project Note (pre-filled)
"All work to be performed in accordance with NCDOT standards. Site must be clear of debris prior to mobilization. Any unforeseen conditions encountered during construction may be subject to additional charges via written change order. Payment due within 30 days of invoice."

---

## Pending / Future Work

- [ ] Scheduling module + built-in calendar
- [ ] Badge Manager: dynamically inject CSS for custom badge colors when app loads
- [ ] Settings: `renderMatTable()` badge dropdown should pull from `BADGE_DEFS` dynamically
- [ ] Admin: edit own profile (PIN change) — UI shows Edit button but server-side PATCH works
- [ ] PDF: include line item descriptions in the bid table output
- [ ] Concrete items: allow custom `cy_per_lf` override per item
- [ ] Phase tabs: multi-phase support partially built but not fully wired

---

## Common Tasks

### Add a new API route
1. Edit `app.py`
2. Add route with `@app.route(...)` decorator
3. Use `@require_auth` or `@require_admin` decorator as needed
4. Push to GitHub → Railway redeploys

### Add a new settings card
1. Add HTML card div inside `#panel-settings` in `index.html`
2. Add JS render function (use DOM API, not innerHTML strings)
3. Call the render function from `showPanel()` when `name === 'settings'`
4. Persist to `localStorage` if user-editable

### Update material pricing defaults
Edit the `MAT`, `LBS`, `DRATE`, `DDEPTH`, `LBADGE` objects near line ~920 in `index.html`.

### Add a new concrete type
Add an entry to `CTYPES` array with `{id, name, desc, unit:'LF', cy_per_lf:X}`.

### Create a new user
Use the Admin panel in the app, or POST to `/admin/users` with `{username, full_name, pin, role}`.

---

## Skill References

- Before performing any algorithmic art tasks, read and follow the instructions in `skills/algorithmic-art/SKILL.md`.
- Before performing any brand guidelines tasks, read and follow the instructions in `skills/brand-guidelines/SKILL.md`.
- Before performing any canvas design tasks, read and follow the instructions in `skills/canvas-design/SKILL.md`.
- Before performing any Claude API tasks, read and follow the instructions in `skills/claude-api/SKILL.md`.
- Before performing any document co-authoring tasks, read and follow the instructions in `skills/doc-coauthoring/SKILL.md`.
- Before performing any Word document (.docx) tasks, read and follow the instructions in `skills/docx/SKILL.md`.
- Before performing any frontend design tasks, read and follow the instructions in `skills/frontend-design/SKILL.md`.
- Before performing any internal communications tasks, read and follow the instructions in `skills/internal-comms/SKILL.md`.
- Before performing any MCP server building tasks, read and follow the instructions in `skills/mcp-builder/SKILL.md`.
- Before performing any PDF tasks, read and follow the instructions in `skills/pdf/SKILL.md`.
- Before performing any PowerPoint (.pptx) tasks, read and follow the instructions in `skills/pptx/SKILL.md`.
- Before performing any skill creation tasks, read and follow the instructions in `skills/skill-creator/SKILL.md`.
- Before performing any Slack GIF creation tasks, read and follow the instructions in `skills/slack-gif-creator/SKILL.md`.
- Before performing any theme/styling tasks, read and follow the instructions in `skills/theme-factory/SKILL.md`.
- Before performing any web artifact building tasks, read and follow the instructions in `skills/web-artifacts-builder/SKILL.md`.
- Before performing any web application testing tasks, read and follow the instructions in `skills/webapp-testing/SKILL.md`.
- Before performing any spreadsheet (.xlsx) tasks, read and follow the instructions in `skills/xlsx/SKILL.md`.
