import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
import logging
import random

logger = logging.getLogger()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [web_info] %(message)s",
    handlers=[
        logging.StreamHandler()
    ])

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')

class WebInfo(object):

    def fetch_current_champions(self):
        """Fetches a list of all current league of legends champions and returns them as a list
        """
        champions_list = []
        html = self._open_with_selenium('https://na.leagueoflegends.com/en/game-info/champions/', '//*[@id="champion-grid-content"]/div/ul')
        soup = BeautifulSoup(html) 
        for ultag in soup.find_all('ul', {'class': 'champion-grid grid-list gs-container gs-no-gutter default-7-col content-center'}):
            for litag in ultag.find_all('li'):
                champions_list.append(litag.text)
        return champions_list

    def fetch_champion_statistics(self, champion_name):
        """Fetches match statistics for a given champion
                Args:
                    champion_name: name of a champion (Can include spaces & uppercase letters)

                Returns: 
                    A list of floating point values: The percent for (WinRate, PickRate, BanRate)
        """
        champion_statistics = []
        html = self._open_with_selenium('https://rankedboost.com/league-of-legends/build/{0}/'.format(champion_name.replace(' ', '-').lower()), '//*[@id="overview"]/p/span')
        soup = BeautifulSoup(html) 
        non_decimal = re.compile(r'[^\d.]+')
        for span in soup.find_all('span', {"class" : "top-10-number-text"}):
            for stats in span.find_all('span'):
                champion_statistics.append(non_decimal.sub('', stats.text))
        return champion_statistics

    def fetch_total_players(self):
        #get total number of ranked players
        html = self._open_with_selenium('https://na.op.gg/ranking/ladder/')
        soup = BeautifulSoup(html)
        non_decimal = re.compile(r'[^\d.]+')
        total_players = soup.find('span', attrs={'class':'Text'}).text.strip()
        total_players = non_decimal.sub('', total_players)
        return total_players

    def get_player_info(self, player_name, win):
        match_player = player.Player(username=player_name)
        html = self._open_with_selenium(f"https://na.op.gg/summoner/userName={match_player.get_formatted_name()}")
        soup = BeautifulSoup(html)
        match_player.ladder_ranking = soup.find('span', attrs={'class':'ranking'}).text.strip()
        match_player.level = soup.find('div', attrs={'class':'ProfileIcon'}).text.strip()
        avg_stats_box = soup.find('div', attrs={'class':'GameAverageStatsBox'})  
        preferred_lanes = ['','']
        for i, position in enumerate(avg_stats_box.findall('td', attrs={'class':'PositionStats'}).find('div', attrs={'class':'Name'}).text.strip()):
            preferred_lanes[i] = position
        if win:
            wins = soup.find('span', attrs={'class':'win'}).text.strip()
            total_wins = soup.find('span', attrs={'class':'WinLose'}).find('span', attrs={'class':'wins'}).text.strip().replace("W", "")
            wins = int(wins)-1
            total_wins = int(total_wins)-1
        else:
            losses = soup.find('span', attrs={'class':'lose'}).text.strip() 
            total_losses = soup.find('span', attrs={'class':'WinLose'}).find('span', attrs={'class':'losses'}).text.strip().replace("L", "")
            losses = int(losses)-1
            total_losses = int(total_losses)-1
        match_player.win_ratio = total_wins/(total_wins+total_losses)
        return

    def get_random_games(self, ladder_page_range, games):
        for i in range(games):
            html = self._open_with_selenium(f'https://na.op.gg/ranking/ladder/page={random.randint(ladder_page_range[0],ladder_page_range[1])}') 
            soup = BeautifulSoup(html)
            data = []
            table = soup.find('table', attrs={'class':'ranking-table'})
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele][1]) # Select only player names
            players = []
            for p, player in enumerate(data):
                #load player page
                team = p%5
                player = player.replace(" ", "_")
                html = self._open_with_selenium(f'https://na.op.gg/summoner/userName={player}')
                soup = BeautifulSoup(html)
                last_game = soup.find_all('div', 'GameItemWrap')[0]
                for i in range(10):
                    player = self.get_player_info(player_name, champion, )
                players.append(player) 

    def _open_with_selenium(self, uri, xpath=None, timeout=5):
        driver = webdriver.Chrome('/usr/local/bin/chromedriver',chrome_options=chrome_options)
        driver.get(uri)
        if xpath != None:
            try:
                element_present = EC.presence_of_element_located((By.XPATH, xpath))
                WebDriverWait(driver, timeout).until(element_present)
            except TimeoutException:
                print("Timed out waiting for League of Legends game-info page to load")   
        html = driver.page_source
        driver.close() 
        return html


if __name__ == "__main__":
    wi = WebInfo()
    print(wi.fetch_current_champions())
    print(wi.fetch_champion_statistics('Kindred'))
        

