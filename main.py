from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
import pandas as pd
import os
import datetime
import pprint
from dotenv import load_dotenv

options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
url = "https://www.betika.com/en-ke/live"
driver.get(url)
wait = WebDriverWait(driver, 20)


def login_details(phone, passphrase):
    try:
        login_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@class='top-session-button button button__secondary outline link'][text()='Login']")))
        login_button.click()

        phone_number = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='text'][@class='input']")))
        phone_number.send_keys(phone)

        password = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password'][@class='input']")))
        password.send_keys(passphrase)

        login = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//button[@class='button account__payments__submit session__form__button login button button__secondary']")))
        login.click()
    except Exception as e:
        print(f"Error during login: {e}")


def filter_for_ongoing():
    driver.implicitly_wait(10)
    filter_button = driver.find_element(By.XPATH, "//span[@class='match-filter__button__label'][text()='Filters']")
    filter_button.click()
    driver.implicitly_wait(10)
    team_to_win = driver.find_element(By.XPATH, "(//button[@class='match-filter__group__action'])[3]")
    team_to_win.click()
    driver.implicitly_wait(10)
    apply = driver.find_element(By.XPATH, "//button[@class='match-filter__apply']")
    apply.click()


def save_csv_to_file(arr, file_name):
    arr = pd.DataFrame(arr)
    csv_file_path = str(os.path.join(os.path.dirname(__file__), file_name))

    if not os.path.exists(csv_file_path):
        arr.to_csv(csv_file_path)
    else:
        arr.to_csv(csv_file_path, mode='a', header=False)

    print("Saved to csv file")


def recording_time():
    current_datetime = datetime.datetime.now()

    # Format the date and time as a string
    r_date = current_datetime.strftime("%Y-%m-%d")
    r_rtime = current_datetime.strftime("%H:%M:%S")

    return r_date, r_rtime


# if one odd is below 2 and the others are above2,
# as small slips as possible max(3-4)
# should reach at least 2x odds
#they should not be equal to avoid chances of draws
def selection_algorithm(match):
    # for match in matches:
    if match["odd_no"] == 2:
        if match['home_team']['odds'] == '-' or match['away_team']['odds'] == '-':
            return None
        if match['home_team']['score'] > match['away_team']['score']:
            if match['home_team']['odds'] > (match['away_team']['odds'] + 1.5):
                return match['home_team']
        elif match['away_team']['score'] > match['home_team']['score']:
            if match['away_team']['odds'] > (match['home_team']['odds'] + 1.5):
                return match['away_team']
        else:
            if match['away_team']['odds'] > (match['home_team']['odds'] + 2):
                return match['away_team']
            if match['home_team']['odds'] > (match['away_team']['odds'] + 2):
                return match['home_team']
    else:
        if match['home_team']['odds'] == '-' or match['away_team']['odds'] == '-' or match['odd_x'] == '-':
            return None
        pass


def place_bet(bet_amount):
    remove_all_btn = driver.find_element(By.CLASS_NAME, "button__title")
    remove_all_btn.click()

    alert = wait.until(EC.alert_is_present())
    alert = Alert(driver)
    alert.accept()

    betslip = driver.find_element(By.XPATH, "//div[@class='betslip']")
    expected_odds = driver.find_element(By.XPATH, "//span[@='betslip__details__row__value']")

    bet_amount_input = betslip.find_element(By.TAG_NAME, "input")
    bet_amount_input.send_keys(Keys.CONTROL + "a")
    bet_amount_input.send_keys(Keys.DELETE)
    bet_amount_input.send_keys(bet_amount)


def main():
    login_details("0115361123", "Kereskwe1")
    filter_for_ongoing()

    live_matches = driver.find_elements(By.XPATH, "//div[@class='live-match']")

    #Match data collection
    games = []
    match_array = []
    for i, match in enumerate(live_matches):
        match_data = {'home_team': {}, 'away_team': {}}
        teams = match.find_element(By.XPATH, ".//div[@class='live-match__teams']")
        # Separate the two teams and store the teams and scores
        hteam = teams.text.split("\n")[0]

        # Find the index where letters start for hteam
        index_of_first_letter = next((i for i, char in enumerate(hteam) if not char.isdigit()), len(hteam))
        hteam_scores = hteam[:index_of_first_letter]
        hteam_labels = hteam[index_of_first_letter:]

        match_data['home_team']['name'] = hteam_labels
        match_data['home_team']['score'] = hteam_scores

        ateam = teams.text.split("\n")[1]
        index_of_first_letter = next((i for i, char in enumerate(ateam) if not char.isdigit()), len(ateam))
        ateam_scores = ateam[:index_of_first_letter]
        ateam_labels = ateam[index_of_first_letter:]

        match_data['away_team']['name'] = ateam_labels
        match_data['away_team']['score'] = ateam_scores

        # separate the odds
        odds = match.find_element(By.XPATH, ".//div[@class='live-match__odds__container']")

        #obtain the individual divs so that we can use the buttons for odd placing
        if odds.text.count("\n") == 2:
            oddlist = odds.text.split("\n")
            odds_1 = float(oddlist[0]) if oddlist[0] != "-" else "-"
            odds_x = float(oddlist[1]) if oddlist[1] != "-" else "-"
            odds_2 = float(oddlist[2]) if oddlist[2] != "-" else "-"

            match_data['odd_no'] = 3
            match_data['home_team']['odds'] = odds_1
            match_data['away_team']['odds'] = odds_2
            match_data['odd_x'] = odds_x


        else:
            oddlist = odds.text.split("\n")
            odds_1 = float(oddlist[0]) if oddlist[0] != "-" else "-"
            odds_2 = float(oddlist[1]) if oddlist[1] != "-" else "-"

            match_data['odd_no'] = 2
            match_data['home_team']['odds'] = odds_1
            match_data['away_team']['odds'] = odds_2
            match_data['expected_winner'] = selection_algorithm(match_data)

        match_array.append(match_data)

    pprint.pprint(match_array, sort_dicts=False)
    predictions = []
    for match in match_array:
        if 'expected_winner' in match and match['expected_winner'] is not None:
            predictions.append(match['expected_winner'])

    save_csv_to_file(match_array,'test.csv')

    print(f"Total matches: {len(match_array)}  Predictions: {len(predictions)}")

main()

driver.quit()