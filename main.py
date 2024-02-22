from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
import datetime
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
url = "https://www.betika.com/en-ke/live"
driver.get(url)
driver.implicitly_wait(10)



class Match:
    def __init__(self, home_team, away_team, home_team_current_score, away_team_current_score, odd_1, odd_x, odd_2):
        self.home_team = home_team
        self.away_team = away_team
        self.home_team_current_score = home_team_current_score
        self.away_team_current_score = away_team_current_score
        self.odd_1 = odd_1
        self.odd_x = odd_x
        self.odd_2 = odd_2


def login_details(phone, passphrase):
    login_button = driver.find_element(By.XPATH,
                                       "//a[@class='top-session-button button button__secondary outline link'][text()='Login']")
    login_button.click()
    driver.implicitly_wait(10)
    phone_number = driver.find_element(By.XPATH, "//input[@type='text'][@class='input']")
    phone_number.send_keys(phone)
    password = driver.find_element(By.XPATH, "//input[@type='password'][@class='input']")
    password.send_keys(passphrase)
    driver.implicitly_wait(10)
    login = driver.find_element(By.XPATH,
                                "//button[@class='button account__payments__submit session__form__button login button button__secondary'][span='Login']")
    login.click()


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
        arr.to_csv(csv_file_path, mode='a', header=False) #append to the end

    print("Saved to csv file")


def recording_time():
    current_datetime = datetime.datetime.now()

    # Format the date and time as a string
    r_date = current_datetime.strftime("%Y-%m-%d")
    r_rtime = current_datetime.strftime("%H:%M:%S")

    return r_date,r_rtime


def selection_algorithm(game_obj):
    if game_obj.odd_1 < 1.3:
        return game_obj.home_team
    elif game_obj.odd_x < 1.3:
        return "X"
    elif game_obj.odd_2 < 1.3:
        return game_obj.away_team
    else:
        return "N/A"


def main():
    login_details("0115361123", "Kereskwe1")
    filter_for_ongoing()

    live_matches = driver.find_elements(By.XPATH, "//div[@class='live-match']")

    #Match data collection
    games = []
    match_array = []
    for i, match in enumerate(live_matches):
        teams = match.find_element(By.XPATH, ".//div[@class='live-match__teams']")
        # Separate the two teams and store the teams and scores
        hteam = teams.text.split("\n")[0]

        # Find the index where letters start for hteam
        index_of_first_letter = next((i for i, char in enumerate(hteam) if not char.isdigit()), len(hteam))
        hteam_scores = hteam[:index_of_first_letter]
        hteam_labels = hteam[index_of_first_letter:]

        ateam = teams.text.split("\n")[1]
        index_of_first_letter = next((i for i, char in enumerate(ateam) if not char.isdigit()), len(ateam))
        ateam_scores = ateam[:index_of_first_letter]
        ateam_labels = ateam[index_of_first_letter:]

        # separate the odds
        odds = match.find_element(By.XPATH, ".//div[@class='live-match__odds__container']")

        #obtain the individual divs so that we can use the buttons for odd placing
        if odds.text.count("\n") == 2:
            oddlist = odds.text.split("\n")
            odds_1 = float(oddlist[0]) if oddlist[0] != "-" else float('inf')
            odds_x = float(oddlist[1]) if oddlist[1] != "-" else float('inf')
            odds_2 = float(oddlist[2]) if oddlist[2] != "-" else float('inf')
        else:
            oddlist = odds.text.split("\n")
            odds_1 = float(oddlist[0]) if oddlist[0] != "-" else float('inf')
            odds_x = float('inf')
            odds_2 = float(oddlist[1]) if oddlist[1] != "-" else float('inf')

        match_object = Match(hteam_labels, ateam_labels, hteam_scores, ateam_scores, odds_1, odds_x, odds_2)
        match_array.append(match_object)
        games.append({"Date":recording_time()[0],"Time":recording_time()[1],"Home":hteam_labels,"Away":ateam_labels,"1":odds_1,"X":odds_x,"2":odds_2,"Expected Winner":selection_algorithm(match_object)})

    print(games)
    print(f"Total Matches: {len(live_matches)}")
    save_csv_to_file(games,"dryrun.csv")



main()


driver.quit()



