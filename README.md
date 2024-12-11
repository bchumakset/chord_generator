# Chord Progression Generator

This Python script generates a randomly selected chord progression based on the specified mood and outputs it as a `.wav` file. The user can customize various parameters such as BPM, mood, key, tone, wave type, and ADSR envelope.

## Available Options:
--help : Shows all available parameters.  
--bpm (default: 120): Sets the beats per minute (BPM) for the chord progression.  
--mood (choices: epic, sad, cool, happy): Defines the mood of the progression. If not specified, a random mood will be selected.  
--key (choices: C, C#, D, D#, E, F, F#, G, G#, A, A#, B): Defines the key of the progression. If not specified, the key of C will be used by default.  
--tone (choices: high, normal, low, default: normal): Sets the tone of the progression. "high" doubles the frequency, "low" halves it, and "normal" keeps it at standard pitch.  
--wave (choices: sine, saw, triangle, square): Sets the waveform for the sound generation.  
--adsr (default: 0.1 0.3 0.75 0.15): Defines the ADSR envelope parameters in the order of Attack (A), Decay (D), Sustain (S), and Release (R). Each value should be a float.  
--output (default: clip.wav): Sets the name of the output WAV file.  

## Running the Script
To run the script, open your terminal, navigate to the directory containing the script, and run the following command:  
`python3 chord_progression_generator.py [OPTIONS]`

## Example Commands:
1. Generate a chord progression with default settings and save as clip.wav:  
`python3 chord_generator.py`

2. Generate a "happy" mood chord progression in the key of "D" with a "high" tone:  
`python3 chord_generator.py --bpm 172 --mood happy --key D --tone normal --output happy_progression.wav`

3. Generate a "sad" mood chord progression with a "sine" waveform and a custom ADSR envelope:  
`python3 chord_generator.py --mood sad --wave square --adsr 0.2 0.4 0.5 0.3 --output sad_progression.wav`

## Requirements
- Python 3.x
- Required Python packages:
  - `numpy`
  - `argparse`

To install the required packages, run:

```bash
pip install numpy