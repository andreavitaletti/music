# Impulse

![](/assets/image-2026382726945.png)


cd /zynthian/zynthian-ui/zyngine/ctrldev

file: zynthian_ctrldev_impulse.py

```python

from zyngine.ctrldev.zynthian_ctrldev_base import zynthian_ctrldev_base
import logging
import subprocess

class zynthian_ctrldev_impulse(zynthian_ctrldev_base):

    # Keep a broad match for debugging
    dev_ids = ['Impulse IN 1', 'Impulse  Impulse ', 'Impulse  Impulse MIDI In ']

	# True if input device must be unrouted from chains when driver is loaded
	# see zynthian_ctrldev_base.py
    unroute_from_chains = False

    def __init__(self, state_manager, idev_in, idev_out=None):
        super().__init__(state_manager, idev_in, idev_out)
        logging.warning("Impulse controller __init__ called")

    def midi_event(self, ev):
        """Logs all MIDI events"""
        logging.warning(f"Impulse MIDI event: {ev}")
        if ev[0] == "cc":
            cc = ev[2]
            val = ev[3]
            logging.warning(f"Impulse CC {cc} -> {val}")
        if ev[0] == "note_on":
            note = ev[2]
            vel = ev[3]
            logging.warning(f"Impulse PAD {note} velocity {vel}")
        if ev[0] == "note_off":
            note = ev[2]
            logging.warning(f"Impulse PAD {note} released")
        return False

```

```
systemctl restart zynthian
journalctl -f | grep Impulse
```

![image-2026382644317.png](/assets/image-2026382644317.png)

```
(venv) root@zynthian:~# journalctl -f | grep Impulse
Mar 08 17:28:00 zynthian startx[12826]: WARNING:zynthian_ctrldev_impulse.__init__: Impulse controller __init__ called
Mar 08 17:28:08 zynthian startx[12826]: WARNING:zynthian_ctrldev_impulse.midi_event: Impulse MIDI event: b'\x90V\x13'
Mar 08 17:28:08 zynthian startx[12826]: WARNING:zynthian_ctrldev_impulse.midi_event: Impulse MIDI event: b'\x80V\x00'
Mar 08 17:28:09 zynthian startx[12826]: WARNING:zynthian_ctrldev_impulse.midi_event: Impulse MIDI event: b'\x90VD'
Mar 08 17:28:09 zynthian startx[12826]: WARNING:zynthian_ctrldev_impulse.midi_event: Impulse MIDI event: b'\x80V\x00'
Mar 08 17:28:10 zynthian startx[12826]: WARNING:zynthian_ctrldev_impulse.midi_event: Impulse MIDI event: b'\x90M\x1d'
Mar 08 17:28:10 zynthian startx[12826]: WARNING:zynthian_ctrldev_impulse.midi_event: Impulse MIDI event: b'\x80M\x00'
Mar 08 17:28:11 zynthian startx[12826]: WARNING:zynthian_ctrldev_impulse.midi_event: Impulse MIDI event: b"\x90L'"
Mar 08 17:28:11 zynthian startx[12826]: WARNING:zynthian_ctrldev_impulse.midi_event: Impulse MIDI event: b'\x80L\x00'

```

## Cambio chain e transport


![](assets/Impulse61.png)
```python
from zyngine.ctrldev.zynthian_ctrldev_base import zynthian_ctrldev_base
import logging

class zynthian_ctrldev_impulse(zynthian_ctrldev_base):
    dev_ids = ['Impulse IN 1', 'Impulse  Impulse ', 'Impulse  Impulse MIDI In ']
    
    # ADD THIS LINE:
    unroute_from_chains = False

    def __init__(self, state_manager, idev_in, idev_out=None):
        super().__init__(state_manager, idev_in, idev_out)
        logging.warning(f"Impulse controller __init__ called, idev_in={idev_in}")
        
    def midi_event(self, event):
        '''
        By overriding this, you can intercept knobs/sliders.
        To just let notes pass through to the synth, 
        return False or call the super method.
        '''
        # Log to prove it's working
        logging.warning(f"Impulse MIDI: {event}")
        evtype = (event[0] >> 4) & 0x0F
        
        # This is used to change the progam by the buttons on the keyboard
        if evtype == 0xC:
            pgm = event[1]
            chains = list(self.chain_manager.chains.keys())
            logging.warning(f"Program Change: pgm={pgm}, chains={chains}")
            if pgm < len(chains):
                self.chain_manager.set_active_chain_by_id(chains[pgm])

        if event[0] == 0xF0 and len(event) >= 6 and event[3] == 0x06:
            cmd = event[4]
            if cmd == 0x01:    # Stop
                self.state_manager.stop_midi_playback()
                logging.warning("MMC Stop")
            elif cmd == 0x02:  # Play
                self.state_manager.toggle_midi_playback()
                logging.warning("MMC Play")
            elif cmd == 0x06:  # Record
                self.state_manager.toggle_midi_record()
                logging.warning("MMC Rec")
            return
            
        # Return False to tell Zynthian: 
        # "I'm not consuming this event, pass it to the synth engine."
        return False
```

