from playwright.sync_api import sync_playwright
import pandas as pd
from pathlib import Path
import time

# -----------------------------
# SETTINGS
# -----------------------------

INPUT_FILE = "/Users/michaelabrooks/Downloads/auditory_pseudowords.xlsx"
SHEET_NAME = 0
IPA_COLUMN = "IPA"

OUTPUT_DIR = Path("ipa_audio")
OUTPUT_DIR.mkdir(exist_ok=True)

WAIT_BETWEEN_ITEMS = 1.0
AUDIO_TIMEOUT_MS = 10000

# -----------------------------
# LOAD IPA ITEMS
# -----------------------------

df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

if IPA_COLUMN not in df.columns:
    raise ValueError(
        f"Column '{IPA_COLUMN}' not found.\n"
        f"Available columns are: {list(df.columns)}"
    )

# Remove blank IPA rows
df = df[df[IPA_COLUMN].notna()].copy()
df[IPA_COLUMN] = df[IPA_COLUMN].astype(str).str.strip()
df = df[df[IPA_COLUMN] != ""].copy()

# Reset row numbers
df = df.reset_index(drop=True)

print(f"Found {len(df)} IPA items.")

# Create filenames
df["audio_file"] = [
    f"stimulus_{i:03d}.mp3"
    for i in range(1, len(df) + 1)
]

df["status"] = ""

# -----------------------------
# GENERATE AUDIO
# -----------------------------

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("Opening IPA Reader...")

    page.goto("https://ipa-reader.com/")
    page.wait_for_load_state("networkidle")

    for i, row in df.iterrows():

        ipa = row[IPA_COLUMN]
        filename = row["audio_file"]
        output_path = OUTPUT_DIR / filename

        print(f"\n[{i + 1}/{len(df)}] IPA: {ipa}")

        # A list lets the response handler modify the value
        audio_response = []

        def capture_audio(response):

            content_type = response.headers.get(
                "content-type", ""
            ).lower()

            if (
                "audio/mpeg" in content_type
                and len(audio_response) == 0
            ):
                audio_response.append(response)

        page.on("response", capture_audio)

        try:

            # Find IPA input
            text_box = page.locator("input").first

            # Clear previous IPA
            text_box.fill("")

            # Enter new IPA
            text_box.fill(ipa)

            # Click Read
            page.get_by_role(
                "button",
                name="Read"
            ).click()

            # Wait for audio
            elapsed = 0

            while (
                len(audio_response) == 0
                and elapsed < AUDIO_TIMEOUT_MS
            ):
                page.wait_for_timeout(250)
                elapsed += 250

            # Check whether audio was received
            if len(audio_response) == 0:

                print("  ERROR: No audio response received.")

                df.loc[i, "status"] = "failed"

            else:

                # Retrieve MP3 data
                audio_bytes = audio_response[0].body()

                # Save MP3
                with open(output_path, "wb") as f:
                    f.write(audio_bytes)

                print(f"  Saved: {output_path}")

                df.loc[i, "status"] = "saved"

        except Exception as e:

            print(f"  ERROR: {e}")

            df.loc[i, "status"] = "failed"

        finally:

            # Stop listening for this item's response
            page.remove_listener(
                "response",
                capture_audio
            )

        # Brief pause before next item
        time.sleep(WAIT_BETWEEN_ITEMS)

    browser.close()

# -----------------------------
# SAVE MANIFEST
# -----------------------------

manifest_path = OUTPUT_DIR / "audio_manifest.csv"

df.to_csv(
    manifest_path,
    index=False,
    encoding="utf-8-sig"
)

# -----------------------------
# SUMMARY
# -----------------------------

successful = (df["status"] == "saved").sum()
failed = (df["status"] == "failed").sum()

print("\n-----------------------------")
print("FINISHED")
print("-----------------------------")

print(f"Successfully generated: {successful}")
print(f"Failed: {failed}")
print(f"Total: {len(df)}")

print(f"\nAudio folder: {OUTPUT_DIR}")
print(f"Manifest: {manifest_path}")
