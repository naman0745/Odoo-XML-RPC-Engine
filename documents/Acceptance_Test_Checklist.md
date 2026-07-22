# Acceptance Test Checklist

Prior to signing off on native executable compilations, Quality Assurance must evaluate the primary binary against these fundamental parameters exactly.

### File Parsing
- [ ] **Valid Workbook:** Place standard `test_reader.xlsx` file inside `Incoming Orders`. Start GUI. Import finishes securely. Odoo reflects PO cleanly.
- [ ] **Invalid Workbook:** Drop a `.txt` renamed to `.xlsx`. System gracefully parses and rejects.
- [ ] **Missing Vendor:** Provide a valid workbook mapping to a `x_vendor_code` that isn't native to the Odoo DB. System traps gracefully.

### System Safety
- [ ] **Workbook Open in Excel:** Physically open the target worksheet natively inside Microsoft Excel. Attempt to run import. The software rejects via `WinError 32` PermissionError explicitly on the validation string instead of breaking mid-flight.
- [ ] **Network Interruption:** Unplug NIC halfway through active Import workflow visually simulating connection severances. Evaluates timeout crash mapping robustly internally.
- [ ] **Directory Relocation Issues:** Hard-delete `Processed Orders` folder physically while the import occurs natively. System outputs PO to Odoo cleanly but raises "Warning: could not move workbook" instead of destroying application persistence natively.

### Duplicate Shield
- [ ] **Duplicate Workbook:** Copy the previously processed `.xlsx` file cleanly back into `Incoming Orders`. Renaming the file doesn't matter. Attempt re-run. System intercepts using fingerprint hash explicitly avoiding duplicate ERP insertions.

### UX Assertions
- [ ] **Multiple Workbooks:** Drop 5 `.xlsx` files into `Incoming Orders` concurrently. UI builds the selection map structurally.
- [ ] **GUI Responsiveness:** Attempt hovering objects natively and spamming mouse clicks while the application loops its Progress checklist during long imports. GUI remains 60fps unlocked cleanly.
- [ ] **Shutdown Hook:** Attempt pressing `[X]` at the very top right natively exactly during the "Extracting XML-RPC" visualization stage. Standard messagebox modal blocks you smoothly.
