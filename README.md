# IPA Audio Generator

Python scripts for generating and saving MP3 audio files from International Phonetic Alphabet (IPA) transcriptions using [IPA Reader](https://ipa-reader.com/).

These scripts automate IPA Reader with Playwright and capture the generated audio for use as auditory stimuli in research and experimental tasks.

## Scripts

### `single_ipa_reader.py`

Generates an MP3 file for a single IPA transcription.

This script is useful for testing IPA Reader and generating individual audio stimuli.

### `batch_ipa_reader.py`

Generates MP3 files for multiple IPA transcriptions stored in an Excel spreadsheet.

The script:

- Reads IPA transcriptions from an Excel file
- Enters each transcription into IPA Reader
- Generates the corresponding audio
- Captures and saves each audio response as an MP3 file
- Creates a CSV manifest documenting the generated files and their status

## Requirements

- Python 3
- Playwright
- pandas
- openpyxl

Install the required Python packages with:

```bash
python3 -m pip install playwright pandas openpyxl
python3 -m playwright install chromium
