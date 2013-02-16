# pyv6

A wild attempt to port xv6 to Python.

I'm taking a top-down approach, mocking up the layer below the one I'm working
on at any given time.

At some point, this will converge with [Cleese](https://github.com/jtauber/cleese).


## Status

The commands in `pyv6/bin` (the user-space commands) have had their first pass 
conversion.

The actual system calls those make are mocked up for now. Forking is emulated
with greenlets.

See `pyv6/tests.py` for the smoke tests for what I've done so far.

See also `translating.txt` for some notes on translating C idioms to Python.


James Tauber 
jtauber@jtauber.com
