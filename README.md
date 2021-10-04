Registry files for initial configuration of Beckhoff PLCs for PCDS usage.

Installation
============

Requires Python 3.8+ and dependencies in ``requirements.txt``.

```bash
$ pip install -r requirements.txt
```

How to use
----------

1. Run the PLC image generator with your appropriate settings.
```bash
# Console usage:
$ python console.py --help

# For a cx50xx named "plc_name" and an IP address of 1.2.3.4, run:
$ python console.py --model cx50xx plc_name 1.2.3.4 'plc description here'` 

# Alternatively, run the GUI and enter parameters there:
$ python gui.py
```
2. Mount your PLC CF card. Delete all files on it.
3. Navigate to ``images/plc_name``.
4. Copy all files generated here onto your PLC CF card.
5. Eject it safely.
6. Insert the CF card into the PLC and boot it up.
7. Verify your settings were applied correctly.

Notes
-----

* X000 is MAC ID 2
* X001 is MAC ID 1
