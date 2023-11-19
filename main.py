from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options = options)
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


login_details("0115361123", "Kereskwe1")
filter_for_ongoing()

live_matches = driver.find_elements(By.XPATH, "//div[@class='live-match']")

#Match data collection
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

    # print(f"Home team: {hteam_labels}, Home team scores: {hteam_scores}")
    # print(f"Away team: {ateam_labels}, Away team scores: {ateam_scores}")

    # separate the odds
    odds = match.find_element(By.XPATH, ".//div[@class='live-match__odds__container']")
    odds = odds.text
    if odds.count("\n") == 2:
        oddlist = odds.split("\n")
        odds_1 = float(oddlist[0]) if oddlist[0] != "-" else 0
        odds_x = float(oddlist[1]) if oddlist[1] != "-" else 0
        odds_2 = float(oddlist[2]) if oddlist[2] != "-" else 0
    else:
        oddlist = odds.split("\n")
        odds_1 = float(oddlist[0]) if oddlist[0] != "-" else 0
        odds_x = 0
        odds_2 = float(oddlist[1]) if oddlist[1] != "-" else 0

    match_object = Match(hteam_labels, ateam_labels, hteam_scores, ateam_scores, odds_1, odds_x, odds_2)
    match_array.append(match_object)

for match in match_array:
    if match.odd_1<1.3 or match.odd_2<1.3 or match.odd_x<1.2:
        print(match.home_team,match.odd_1,match.odd_x,match.odd_2)
