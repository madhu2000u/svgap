# power-on-v0.1 study taskpack (8 tasks)

Frozen power-on prevalence taskpack. Every task declares power_on = "reset_required"
and ships a safe reference (resets operational state on power-on) and an unsafe
reference (omits the reset). Both references pass the functional testbench; only the
unsafe reference raises REF-XPROP-001. Property: REF-XPROP-001. Reference variants
per task: 2.
