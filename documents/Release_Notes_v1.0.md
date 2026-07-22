# Purchase Order Importer v1.0 - Release Notes

This marks the official V1 production release of the PO Importer natively coupling desktop spreadsheet files with Odoo ERP operations.

## Major Features
- **Headless & Graphical Interfacing:** Allows automated cron scripts alongside standard desktop UX paths smoothly utilizing the exact identical controllers.
- **Robust Exception Translation:** Prevents the tool from natively crashing abruptly by pushing failure architectures back down to XML-RPC exceptions. 
- **Workspace Encapsulation:** Discovers local environments explicitly avoiding fixed strings. Constructs paths utilizing natively secure `pathlib` references preventing configuration burdens for end-staff across workstations.
- **Smart OS Integrations:** Rejects Tkinter window destructions safely while daemon loops parse backend Odoo transactions. Natively handles file moves cleanly, safely decoupling file permission failures from critical ERP commits.

## Architectural Decisions
- The GUI operates completely passively (`Passive View` pattern). All intelligence natively lives inside standard Python structures so future web-wrappers (e.g., FastAPI) can plug over the configuration simply without rewriting validations.
- Utilizes cryptographically stable checksum fingerprints rather than filename comparisons to trace uniqueness.

## Known Limitations
- Modifying connection architectures (`config/settings.py`) presently requires engineering re-packaging for `.exe` distributions natively rather than dynamically prompting users (addressed functionally via ENV injection natively).
- Extremely large batch workbooks (>1000 items) will still timeout standard XML-RPC bindings currently capped globally across operations rather than paginating.

## Future Roadmap (V2.0+)
- **Rollback Safety (Transactions):** Currently missing automatic `.unlink()` destruction triggers to pull broken POs out of the Odoo pipeline completely if local manifests crash safely.
- **ErrorCode Translators:** Upgrading raw Python tracebacks in the GUI dynamically to human-readable error maps.
- **Batch Paginated Delivery:** Delivering rows across 50-index batches per XML-RPC stroke.
