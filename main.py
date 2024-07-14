from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    csv_file_path = f'C:\\Users\\Techron\\PycharmProjects\\LiveBetAssist\\{file_name}'

    if not os.path.exists(csv_file_path):
        arr.to_csv(csv_file_path)
    else:
        arr.to_csv(csv_file_path, mode='a', header=False)  #append to the end

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
def selection_algorithm(game_obj):
    # if game_obj.odd_1 < 1.3:
    #     return game_obj.home_team
    # elif game_obj.odd_x < 1.3:
    #     return "X"
    # elif game_obj.odd_2 < 1.3:
    #     return game_obj.away_team
    # else:
    #     return "N/A"

    # Consider games with 3 odds
    if game_obj.odd_1 is not float('inf') and game_obj.odd_x is not float('inf') and game_obj.odd_2 is not float('inf'):
        # If either odd is less than 2 and the others are above 3
        if game_obj.odd_1 < 2 and game_obj.odd_x > 3 and game_obj.odd_2 > 3:
            return game_obj.home_team
        if game_obj.odd_2 < 2 and game_obj.odd_1 > 3 and game_obj.odd_x > 3:
            return game_obj.away_team
        if game_obj.odd_x < 2 and game_obj.odd_2 > 3 and game_obj.odd_1 > 3:
            return "Draw"


def place_bet(bet_amount):
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
        match_data = {}
        teams = match.find_element(By.XPATH, ".//div[@class='live-match__teams']")
        # Separate the two teams and store the teams and scores
        hteam = teams.text.split("\n")[0]

        # Find the index where letters start for hteam
        index_of_first_letter = next((i for i, char in enumerate(hteam) if not char.isdigit()), len(hteam))
        hteam_scores = hteam[:index_of_first_letter]
        hteam_labels = hteam[index_of_first_letter:]

        match_data['home_team_scores'] = hteam_scores
        match_data['home_team'] = hteam_labels

        ateam = teams.text.split("\n")[1]
        index_of_first_letter = next((i for i, char in enumerate(ateam) if not char.isdigit()), len(ateam))
        ateam_scores = ateam[:index_of_first_letter]
        ateam_labels = ateam[index_of_first_letter:]

        match_data['away_team_scores'] = ateam_scores
        match_data['away_team'] = ateam_labels

        # separate the odds
        odds = match.find_element(By.XPATH, ".//div[@class='live-match__odds__container']")

        #obtain the individual divs so that we can use the buttons for odd placing
        if odds.text.count("\n") == 2:
            oddlist = odds.text.split("\n")
            odds_1 = float(oddlist[0]) if oddlist[0] != "-" else "-"
            odds_x = float(oddlist[1]) if oddlist[1] != "-" else "-"
            odds_2 = float(oddlist[2]) if oddlist[2] != "-" else "-"

            match_data['odd_no'] = 3
            match_data['odd_1'] = odds_1
            match_data['odd_x'] = odds_x
            match_data['odd_2'] = odds_2

        else:
            oddlist = odds.text.split("\n")
            odds_1 = float(oddlist[0]) if oddlist[0] != "-" else float('inf')
            odds_2 = float(oddlist[1]) if oddlist[1] != "-" else float('inf')

            match_data['odd_no'] = 2
            match_data['odd_1'] = odds_1
            match_data['odd_2'] = odds_2

        match_array.append(match_data)
        # games.append(
        #     {"Date": recording_time()[0], "Time": recording_time()[1], "Home": hteam_labels, "Away": ateam_labels,
        #      "1": odds_1, "X": odds_x, "2": odds_2, "Expected Winner": selection_algorithm(match_data)})

    pprint.pprint(match_array)
    print(f"Total Matches: {len(live_matches)}")

    # save_csv_to_file(games, "dryrun.csv")


main()

driver.quit()
