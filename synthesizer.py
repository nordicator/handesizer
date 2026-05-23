import threading
import mido
from pyo import *

class StandaloneSynth:
    def __init__(self):
        # Explicitly configure: 0 input channels, 2 output channels, duplex off
        self.s = Server(sr=44100, nchnls=2, ichnls=0, duplex=0)
        self.s.setOutputDevice(pa_get_default_output())
        self.s.boot()
        self.s.start()

        self.effects_list = ["filter", "reverb", "modulation"]
        self.effect_index = 0
        self.current_mode = self.effects_list[self.effect_index]

        # Create your oscillator at a baseline volume of 0.3
        self.saw_osc = SuperSaw(freq=220, detune=0.5, mul=0.3) 
        self.square_osc = LFO(freq=220, type=2, mul=0.3)
        self.sine_osc = Sine(freq=220, mul=0.3)

        self.active_soruce = Selector([self.saw_osc, self.square_osc, self.sine_osc], voice=0)


        self.filter = MoogLP(input=self.active_soruce, freq=1000, res=0.5, mul=0)
        self.reverb = Freeverb(input=self.filter, size=0.6, damp=0.5, bal=0.0)
        self.chorus = Chorus(input=self.reverb, depth=1, feedback=0.25, bal=0.0)
        self.final_output = self.chorus.out()



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
                        if msg.type == 'note_on' and msg.channel == 0:
                            freq = 440.0 * (2.0 ** ((msg.note - 69) / 12.0))
                            self.saw_osc.setFreq(freq)
                            self.square_osc.setFreq(freq)
                            self.sine_osc.setFreq(freq)
                            self.filter.setMul(0.4)

                        elif msg.type == 'note_off' and msg.channel == 0:
                            # Shut the volume gate on the filter output
                            self.filter.setMul(0) 
                        
                        elif msg.type == 'note_on' and msg.channel == 9:
                            if msg.note == 36:
                                self.active_soruce.setVoice(0) 
                                print("bank switch: supersaw active")
                            elif msg.note == 37: 
                                self.active_soruce.setVoice(1)
                                print("Bank Switch: Square Wave Active")
                            elif msg.note == 38: 
                                self.active_soruce.setVoice(2)
                                print("Bank Switch: Sine Wave Active")

            except Exception as e:
                print(f"MIDI Error: {e}")
        
    def cycle_effect_mode(self):
        """Triggered by a quick single pinch to cycle active fx type"""
        self.effect_index = (self.effect_index + 1) % len(self.effects_list)
        self.current_mode = self.effects_list[self.effect_index]
        print(f"effect selected: {self.current_mode.upper()}")
        
    def tweak_effect_knob(self, normalized_rotation):
        percentage = int(normalized_rotation * 100)
        if self.current_mode == "filter":
            cutoff = (normalized_rotation * 4940) + 60
            self.filter.setFreq(cutoff)
        elif self.current_mode == "reverb":
            self.reverb.setBal(normalized_rotation * 0.8)
        elif self.current_mode == "modulation":
            self.chorus.setBal(normalized_rotation * 0.9)

        return percentage