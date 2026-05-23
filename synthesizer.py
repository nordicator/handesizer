import threading
import mido
from pyo import *

class StandaloneSynth:
    def __init__(self):
        # Explicitly configure: 0 input channels, 2 output channels, duplex off
        self.s = Server(sr=44100, nchnls=2, ichnls=0, duplex=0)
        
        # Force it to use the default system output device
        self.s.setOutputDevice(pa_get_default_output())
        
        self.s.boot()
        self.s.start()

        # Create your oscillator at a baseline volume of 0.3
        self.osc = SuperSaw(freq=220, detune=0.5, mul=0.3) 

        # We append .out() to the filter, but we initialize it with mul=0 (silent)
        # This acts as our master gate!
        self.synth_filter = MoogLP(input=self.osc, freq=1000, res=0.5, mul=0).out()

        self.midi_thread = threading.Thread(target=self._midi_listener, daemon=True)
        self.midi_thread.start()

    def _midi_listener(self):
        """Listens directly to the Akai MPK Mini hardware"""
        port_name = None
        for name in mido.get_input_names():
            if 'MPK' in name or 'mini' in name or 'Akai' in name:
                port_name = name
                break

        if port_name:
            try:
                with mido.open_input(port_name, virtual=False) as inport:
                    print(f"Connected to Akai on port: {port_name}")
                    for msg in inport:
                        if msg.type == 'note_on':
                            freq = 440.0 * (2.0 ** ((msg.note - 69) / 12.0))
                           
                           
                            self.osc.setFreq(freq)
                            # Open the volume gate on the filter output
                            self.synth_filter.setMul(0.4) 
                        elif msg.type == 'note_off':
                            # Shut the volume gate on the filter output
                            self.synth_filter.setMul(0)   
            except Exception as e:
                print(f"MIDI Error: {e}")
        else:
            print("Akai MPK Mini not found in system ports. Running in hand-only mode.")

    def modulate_filter(self, normalized_value):
        """Accepts a value from 0.0 to 1.0 from the hand tracker to tweak the sound"""
        # Map to an audible filter frequency sweep range (100Hz to 6000Hz)
        cutoff = (normalized_value * 5900) + 100
        self.synth_filter.setFreq(cutoff)