import logging

from zyngine.ctrldev.zynthian_ctrldev_base import zynthian_ctrldev_base


class zynthian_ctrldev_impulse_zynsampler(zynthian_ctrldev_base):
    dev_ids = ["Impulse IN 1", "Impulse  Impulse ", "Impulse  Impulse MIDI In "]

    # ADD THIS LINE:
    unroute_from_chains = False

    def __init__(self, state_manager, idev_in, idev_out=None):
        super().__init__(state_manager, idev_in, idev_out)
        logging.warning(f"Impulse controller __init__ called, idev_in={idev_in}")

    def midi_event(self, event):
        """
        By overriding this, you can intercept knobs/sliders.
        To just let notes pass through to the synth,
        return False or call the super method.
        """
        """
        chains = list(self.chain_manager.chains.keys())
        for chain_id in chains:
            chain = self.chain_manager.chains[chain_id]
            logging.warning(
                f"chain_id={chain_id} name='{chain.get_name()}' desc='{chain.get_description()}'"
            )
         """

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

        # MMC SysEx messages
        #
        if event[0] == 0xF0 and len(event) >= 6 and event[3] == 0x06:
            cmd = event[4]
            # Find ZynSampler chain
            zynsampler_chain = None
            for chain_id in self.chain_manager.chains.keys():
                chain = self.chain_manager.chains[chain_id]
                if "ZynSampler" in chain.get_name():
                    zynsampler_chain = chain
                    break

            # THIS BLOCK WAS INCORRECTLY INDENTED INSIDE THE FOR LOOP
            if zynsampler_chain:
                proc = zynsampler_chain.get_processors()[0]
                transport_ctrl = proc.controllers_dict.get("transport")
                if transport_ctrl:
                    if cmd == 0x01:  # Stop
                        transport_ctrl.set_value("stopped")
                        logging.warning("MMC Stop -> ZynSampler")
                    elif cmd == 0x02:  # Play
                        transport_ctrl.set_value("playing")
                        logging.warning("MMC Play -> ZynSampler")
                    elif cmd == 0x06:  # Record
                        record_ctrl = proc.controllers_dict.get("record")
                        if record_ctrl:
                            record_ctrl.set_value("recording")
                        logging.warning("MMC Rec -> ZynSampler")
            return
        # Return False to tell Zynthian:
        # "I'm not consuming this event, pass it to the synth engine."
        return False
