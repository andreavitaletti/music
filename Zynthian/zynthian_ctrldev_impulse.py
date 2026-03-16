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
