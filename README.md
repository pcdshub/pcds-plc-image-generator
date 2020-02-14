Registry files for initial configuration of Beckhoff CX50xx PLCs
================================================================

1. Copy the contents of, e.g., `CBx053_CE600_HPS_v406b_TC31_B4022.29.zip` to an empty SD card
2. Run `templates\populate.py` to update PLC name + IP address registry files
3. Copy \*.reg from the repository root to \RegFiles
4. Start up the PLC
5. Likely the PLC name + AMS Net ID did not get applied, so navigate to
   \RegFiles using explorer and double click:
    a. `ident.reg` 
    b. `ams_net_id.reg`
