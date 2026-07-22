# Purchase Order Importer: Developer Guide

Welcome to the internal engineering guide for the PO Importer.

## Application Architecture
The utility forces a strict layered separation of concerns:
1. **Presentation Layer:** (`gui/`) Custom stateless Tkinter bindings reflecting data given by the controller.
2. **Orchestration Layer:** (`controllers/`) Manages state transfers (`GuiController`) or logical data validation mapping pipes (`ImportController`).
3. **Services Layer:** (`services/`) Represents atomic models inside Odoo (`PartnerService`, `PO_Service`). Strictly handles standard dictionaries.
4. **Data Access Layer:** (`connection/`) The XML-RPC client.

## Dependency Injection (DI)
No module should initialize foreign architectures inherently inside its bounds, specifically avoiding hidden DB triggers.
All configurations traverse downward originally from `gui/app.py` or `main.py` (the Composition Root). To build a new service, you must instantiate it in the root bootstrap and inject it explicitly into the `ImportController`.

## Threading Model
Since creating a purchase order via `xmlrpc.client.ServerProxy` is a blocking IO task naturally waiting on server acknowledgement, running this on the main GUI thread causes operating systems to denote the software as "Unresponsive".
We solve this using python's native `threading`:
1. `_start_import()` in `GuiController` passes control to `_worker()` running on a Daemon thread.
2. The UI enters a cyclical `after(0)` loop advancing visual checklists asynchronously.
3. Upon backend thread conclusion, the daemon hooks `self.window.after(0, self._on_import_finished, result)` passing the object perfectly back to the main UI loop, preventing Tkinter threading collisions natively.

## Duplicate Protection
We utilize cryptographic `md5` hashing against the byte-level `.xlsx` definition instead of relying on subjective Excel parameters (which could overlap if businesses merely forget to change dates).
Validation happens in `import_controller.py` verifying if the internal `WorkspaceManager` state tracks the newly generated footprint.

## File Movement Workflow
File movement executes immediately after positive confirmation from Odoo inside `main.py` explicitly, or seamlessly by the `_on_import_finished()` method on the GUI. Failures during file relocation are caught and warned, leaving PO execution perfectly cleanly executed across the backend natively.

## Adding New Features
1. To pull alternative Excel formats: Update `excel/row_mapper.py` `COLUMN_MAPPING`.
2. To extract different product validations: Implement the check in `services/product_service.py` natively using `self.client.search()`.
3. To add a new UI screen: Map it in `gui/views/` inheriting `ttk.Frame`, then register it through `main_window.register_views()`.
