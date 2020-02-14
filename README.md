Registry files for initial configuration of Beckhoff CX50xx PLCs
================================================================

1. Copy the contents of, e.g., `CBx053_CE600_HPS_v406b_TC31_B4022.29.zip` to an
   empty SD card
2. Run `python create.py` to update PLC name + IP address registry files in
   `RegFiles` from `templates`
3. Replace the `RegFiles` contents on the SD card with that of this repository
   (`to_copy\RegFiles`)
4. Copy `to_copy\System` from the repository root to the card, merging with the
   destination files
5. Start up the PLC
6. Likely the PLC name + AMS Net ID did not get applied, so navigate to
   \RegFiles using explorer and double click:
    a. `ident.reg` 
    b. `ams_net_id.reg`
