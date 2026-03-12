from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


def autofill_website(url: str, field_data: dict) -> dict:
    """
    Opens URL in Chrome and fills form fields by their ID.
    Input:  url string, field_data dict {field_id: value}
    Output: dict {success, filled, failed}
    """
    filled = []
    failed = []

    # Setup Chrome options
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    # Start Chrome browser
    print(f"Opening Chrome and navigating to: {url}")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # Open the URL
        driver.get(url)
        time.sleep(2)

        # Try to fill each field
        for field_id, value in field_data.items():
            if not value:
                continue
            try:
                # Wait for field to appear
                el = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, field_id))
                )
                el.clear()
                el.send_keys(str(value))
                filled.append(field_id)
                print(f"Filled: {field_id} = {value}")
            except Exception as e:
                failed.append(field_id)
                print(f"Could not fill: {field_id} — {e}")

        print(f"Autofill complete. Filled: {len(filled)}, Failed: {len(failed)}")
        print("Browser left open for user to verify and submit.")

        # Keep browser open — user submits manually
        return {
            'success': True,
            'filled':  filled,
            'failed':  failed,
            'message': f'Filled {len(filled)} fields. Please verify and submit in the browser.'
        }

    except Exception as e:
        print(f"Autofill error: {e}")
        driver.quit()
        return {
            'success': False,
            'error':   str(e),
            'filled':  filled,
            'failed':  failed
        }

