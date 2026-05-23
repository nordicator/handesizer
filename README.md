# handesizer

`handesizer` is a small gestural synthesizer built with Python. It uses a webcam to track your hand, turns a thumb/index pinch into a virtual knob, and sends that control data into a pyo synth engine. MIDI input can play notes while your hand controls the currently selected effect.

The project is currently set up around an Akai MPK Mini, but the core pieces are simple enough to adapt to other MIDI controllers.

## What It Does

- Opens the default webcam with OpenCV.
- Tracks one hand using MediaPipe hand landmarks.
- Detects a pinch between the thumb tip and index finger tip.
- Uses quick pinches to switch effect modes.
- Uses held pinches plus vertical hand movement to change effect values.
- Generates audio with pyo.
- Listens for MIDI notes with mido and python-rtmidi.
- Displays a live HUD over the camera feed showing the current effect, grip state, and value.

## Project Structure

```text
handesizer/
├── main.py           # Main app loop: camera, gestures, HUD, synth control
├── tracker.py        # MediaPipe hand tracking wrapper
├── synthesizer.py    # pyo synth engine and MIDI listener
├── requirements.txt  # Python dependencies
└── README.md
```

## How The App Works

`main.py` creates two main objects:

- `HandTracker`, which receives camera frames and returns MediaPipe hand landmarks.
- `StandaloneSynth`, which starts the pyo audio server and MIDI listener.

Every frame, the app checks the distance between:

- Landmark `4`: thumb tip
- Landmark `8`: index finger tip

If the distance is below the pinch threshold, the app treats your hand as pinching.

A short pinch under `0.4` seconds cycles the selected effect. A longer pinch grabs the current value, then moving your hand vertically changes that value. Moving up increases the value; moving down decreases it.

## Synth Engine

The synth currently has three oscillator sources:

- Supersaw
- Square wave
- Sine wave

These sources feed into an effect chain:

```text
oscillator selector -> Moog low-pass filter -> reverb -> chorus -> audio output
```

The active hand-controlled effect can be:

- `filter`: changes the Moog low-pass cutoff.
- `reverb`: changes the reverb wet/dry balance.
- `modulation`: changes the chorus wet/dry balance.

## Controls

### Hand Gestures

| Gesture | Action |
| --- | --- |
| Quick thumb/index pinch | Cycle to the next effect mode |
| Hold thumb/index pinch | Grab the current effect value |
| Move hand up while holding pinch | Increase the selected effect value |
| Move hand down while holding pinch | Decrease the selected effect value |
| Press `Esc` | Quit the app |

### MIDI Controls

The MIDI listener searches for a port name containing `MPK`, `mini`, or `Akai`.

| Input | Action |
| --- | --- |
| Notes on channel 0 | Play synth notes |
| Note off on channel 0 | Stop the synth voice |
| Drum pad note `36` on channel 9 | Select supersaw |
| Drum pad note `37` on channel 9 | Select square wave |
| Drum pad note `38` on channel 9 | Select sine wave |

If no Akai MPK Mini is detected, the app still runs, but no MIDI notes will control the synth.

## Requirements

This project has been tested with Python 3.11 and the pinned versions in `requirements.txt`.

Important packages:

- `opencv-contrib-python`: webcam input and display window
- `mediapipe`: hand landmark tracking
- `pyo`: audio synthesis
- `mido`: MIDI message handling
- `python-rtmidi`: MIDI backend for mido
- `numpy`: pinned below version 2 for MediaPipe compatibility

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If you are recreating the environment from scratch, use the pinned requirements instead of installing latest package versions manually. Newer MediaPipe versions removed the old `mp.solutions` API used by this project.

## Running

Start the app:

```bash
python main.py
```

You should see a window titled `Gestural Synth Interface`. Put one hand in view of the webcam. When tracking works, MediaPipe landmarks will be drawn over your hand and the HUD will show the current effect state.

Press `Esc` to quit.

## Calibration Notes

The current pinch threshold is:

```python
distance < 0.045
```

If pinch detection feels too sensitive or not sensitive enough, adjust that value in `main.py`.

The vertical modulation sensitivity is:

```python
sensitivity = 0.35
```

Lower values make smaller hand movements sweep the effect further. Higher values require larger hand movements.

## Common Warnings

### `WxPython is not found`

pyo prints this when WxPython is not installed:

```text
WxPython is not found for the current python version.
```

This is only a warning about pyo GUI support. The synth can still run.

### MediaPipe GL and TensorFlow Lite Logs

MediaPipe may print messages about GL, TensorFlow Lite, or feedback tensors. These are startup logs and are usually harmless.

### `module 'mediapipe' has no attribute 'solutions'`

This means the installed MediaPipe version is too new for this code. Install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

The project pins `mediapipe==0.10.21` because that version still provides `mp.solutions`.

### pyo API Errors

pyo APIs vary between versions. This project uses:

```python
Server(sr=44100, nchnls=2, ichnls=0, duplex=0)
MoogLP(...)
```

Those match the pinned `pyo==1.0.5` dependency.

## Development Ideas

- Add keyboard fallback controls for testing without a MIDI controller.
- Add visual sliders for the three effect parameters.
- Smooth hand values to reduce jitter.
- Add more oscillator sources or effects.
- Save and load presets.
- Add support for selecting MIDI ports from a config file.

## Current Limitations

- Only tracks one hand.
- MIDI port matching is hardcoded for Akai-style names.
- The synth is monophonic in practice.
- Gesture thresholds are hardcoded.
- The app assumes a working webcam and audio output device.
