from playwright.sync_api import sync_playwright

TEST_IPA = "dæp"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    audio_saved = False

    def save_audio(response):
        global audio_saved

        content_type = response.headers.get("content-type", "")

        if "audio/mpeg" in content_type and not audio_saved:
            print("Audio found!")

            audio_bytes = response.body()

            with open("test_audio.mp3", "wb") as f:
                f.write(audio_bytes)

            audio_saved = True
            print("Saved as test_audio.mp3")

    page.on("response", save_audio)

    page.goto("https://ipa-reader.com/")
    page.wait_for_load_state("networkidle")

    page.locator("input").first.fill(TEST_IPA)

    print("Generating audio...")
    page.get_by_role("button", name="Read").click()

    page.wait_for_timeout(5000)

    browser.close()

print("Finished.")
