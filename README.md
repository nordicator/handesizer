# handesizer

A webcam-controlled synth experiment. MediaPipe tracks your hand, OpenCV shows the camera view, and pyo generates audio. Pinch gestures control the current synth effect while MIDI input from an Akai MPK Mini can play notes and switch waveforms.

## Features

- Tracks one hand with MediaPipe.
- Uses thumb/index pinch gestures as a virtual control.
- Quick pinch cycles between effect modes: filter, reverb, and modulation.
- Hold a pinch and move your hand up/down to adjust the selected effect.
- Supports Akai MPK Mini note input and drum-pad waveform switching.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Press `Esc` to quit the camera window.

## Controls

- `Quick pinch`: cycle the active effect mode.
- `Hold pinch`: grab the current effect value.
- `Move up/down while pinching`: increase or decrease the selected effect.
- `MPK Mini keys`: play synth notes.
- `MPK Mini pads 36/37/38`: switch between supersaw, square, and sine sources.

## Notes

The pyo `WxPython is not found` message is a warning about optional GUI support, not a crash. MediaPipe may also print TensorFlow Lite and GL startup logs when the app starts.
