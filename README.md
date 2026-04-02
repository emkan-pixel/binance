# P2P Workflow Assistant (Desktop, English-Only UI)

This repository contains a modular Python desktop application for manual-assisted P2P workflows.

## Technical Specification (Cleaned)

### Product Scope
- Desktop app (English UI only) to support:
  - **Review Mode**: scrape filtered historical orders from Binance P2P All Orders and export structured Excel reports.
  - **Live Assistant Mode**: assign receiving accounts by capacity, prepare chat payloads, track assignments, and store proofs.
- Multi-platform ready architecture:
  - Binance (implemented first)
  - OKX (adapter scaffold)
  - Bybit (adapter scaffold)

### Hard Rules
- Preserve user-selected filters in Review Mode (never reload filtered listing unless explicitly requested).
- Open each order detail in a new tab, scrape details+chat, close tab, continue.
- Pagination uses **numeric page links**, not Next-only assumptions.
- Preserve session/cookies via persistent browser profile.
- Full UI, labels, logs, exports, settings are English only.

## Architecture Overview

Layered modular architecture:

1. **UI Layer** (`ui/`)
   - `MainWindow`: startup wizard + mode controls + logs + status widgets + account table.
2. **Application Services** (`review/`, `live/`, `export/`)
   - `ReviewService`: traverses filtered listing and order tabs.
   - `AllocationEngine`: capacity-based account assignment.
   - `ExcelExporter`: detailed sheet + account summary sheet.
3. **Provider Layer** (`providers/`)
   - `ExchangeProvider` interface.
   - `BinanceProvider` concrete implementation.
   - `OKXProvider`, `BybitProvider` stubs for future extension.
4. **Automation Layer** (`browser/`)
   - `BrowserSessionManager`: Playwright lifecycle, persistent profile, reconnect/recovery.
5. **Domain & Parsing** (`core/`, `parsing/`)
   - Dataclasses for orders, chats, accounts, assignments.
   - Flexible parser for mixed Arabic/English payment details.
6. **Persistence** (`persistence/`)
   - SQLite repositories for settings, accounts, orders, chat messages, assignments, exports, logs.

## Folder Structure

```text
src/p2p_assistant/
  main.py
  core/
    enums.py
    models.py
    logging_service.py
  browser/
    session_manager.py
  providers/
    base.py
    binance_provider.py
    okx_provider.py
    bybit_provider.py
  review/
    review_service.py
  parsing/
    chat_parser.py
  live/
    allocation_engine.py
  export/
    excel_exporter.py
  persistence/
    db.py
    repositories.py
  ui/
    main_window.py
```

## Database Schema (SQLite)

See `src/p2p_assistant/persistence/db.py`.

Key tables:
- `app_settings`
- `exchange_sessions`
- `receiving_accounts`
- `orders`
- `chat_messages`
- `order_assignments`
- `proof_images`
- `exports`
- `app_logs`

Design notes:
- Currency preserved per record (`fiat_currency`).
- Raw and normalized numeric values stored.
- Summary aggregation must group by `(account_number, beneficiary_name, fiat_currency)`.

## UI Layout Proposal

Main window sections:
- Top status bar:
  - Browser Status, Session Status, Current Mode, Current Platform, Active Exchange Account
- Startup assistant panel:
  - Open Account, Account Opened, Ads Published
- Mode controls:
  - Start Review, Start Live Assistant, Pause, Resume, Stop
- Export controls:
  - Export Detailed Orders, Export Account Summary, Open Export Folder
- Accounts panel:
  - Add/Edit/Delete/Activate/Deactivate/Reload/Reorder accounts + capacity columns
- Log console:
  - INFO/WARNING/ERROR/SUCCESS lines with timestamps and progress counters

## Implementation Plan (Phases)

1. **Foundation**
   - Core models, enums, logging bus, SQLite schema and repositories.
2. **Browser Stability**
   - Persistent profile manager, health checks, page/context recovery logic.
3. **Binance Review Mode**
   - Start from already-filtered listing.
   - Enumerate order rows, open detail tabs, scrape details + chat, parse payment info.
   - Numeric pagination traversal.
4. **Exports**
   - Detailed worksheet + account summary worksheet with per-currency aggregation.
5. **Live Assistant**
   - Capacity-based assignment engine and assignment persistence.
   - Compose/send payload and proof tracking hooks.
6. **UI integration**
   - Wire controls, status, logs, and long-running task orchestration.
7. **Future providers**
   - Implement OKX/Bybit adapters using the shared interface.

## Session Persistence / Recovery Strategy

- Playwright launched with `launch_persistent_context(user_data_dir=...)`.
- Reuse existing profile/cookies between app runs.
- On startup:
  1. open lightweight page,
  2. check login validity via provider predicate,
  3. if invalid, open login page and wait for manual login confirmation.
- On `Target page/context/browser has been closed`:
  - invalidate stale references,
  - recreate context/page,
  - resume workflow from last checkpoint where possible.

## Run Instructions

1. Create venv and install dependencies: `playwright`, `customtkinter`, `openpyxl`, `pandas`.
2. Install browsers: `playwright install chromium`.
3. Launch app:
   - `python -m p2p_assistant.main`
4. First run:
   - Click **Open Account**, complete manual login if prompted.
   - Confirm **Account Opened**, publish ads manually, click **Ads Published**.
   - Start preferred mode.

## Notes

This scaffold intentionally prioritizes:
- stable browser/session lifecycle,
- review traversal with detail-tab scraping,
- flexible payment parser,
- numeric pagination handling,
- two-sheet export,
- visible structured logging.
