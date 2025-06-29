import re
import time
from bs4 import BeautifulSoup #type: ignore

def getIds(driver, url):
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    scripts = soup.find_all("script")

    # Find raw JSON from the correct script block
    script_text = ""
    for script in scripts:
        if 'scoreboard' in script.text and 'evts' in script.text:
            script_text = script.text
            break

    if not script_text:
        raise Exception("Could not find script containing scoreboard and evts")


    ids = re.findall(r'\{"id":"(\d+)"\s*,\s*"competitors"\s*:', script_text)

    return(ids)