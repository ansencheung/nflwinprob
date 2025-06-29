from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import numpy as np
import pdb
from selenium.webdriver.chrome.service import Service



'''
This is the first of the scripts and proves that I can
move the cursor
'''
id = input("Enter the ID of the game you want to scrape: ")
#save_name = "SEA_DET_2022"

def find_home_and_away(gameID:str=id, driver = None):
    if driver == None:
        s = Service('../chromedriver_win32_107/chromedriver.exe')
        driver = webdriver.Chrome(service=s)
    desired_http = 'https://www.espn.com/nfl/game/_/gameId/' + gameID
    driver.get(desired_http)
    away_path = "//*[@id='linescore']/tbody/tr[1]/td[1]"
    home_path = "//*[@id='linescore']/tbody/tr[2]/td[1]"
    home = driver.find_element(By.XPATH, home_path)
    away = driver.find_element(By.XPATH, away_path)
    print(f'home: {home.text} away: {away.text}')
    
    return home.text, away.text

teams = find_home_and_away()
options = webdriver.ChromeOptions()
options.add_experimental_option(
    'excludeSwitches', 
    ['enable-logging'])
s = Service('../chromedriver_win32_107/chromedriver.exe')
driver = webdriver.Chrome(service=s)
url = 'https://www.espn.com/nfl/game/_/gameId/' + id
driver.get(url)

#important/interesting xpaths
most_recent_play_xpath = "//*[@id='gameFlowPopup-185']/div[3]/p[2]" #play data, time, etc
graph_xpath = "//*[@id='gameFlow-graph']/div/div" #The path for the plot play-by-play
percent_xpath = "//*[@id='gameFlowPopup-185']/div[1]/h5"
game_date_xpath = "//*[@id='gamepackage-game-information']/article/div/div[1]/div/div[1]/span/span[2]"

def print_vals():
    play = driver.find_element(By.XPATH, most_recent_play_xpath)
    percent = driver.find_element(By.XPATH, percent_xpath)
    home_team = teams[0]
    favored_team = percent.text[0:3].replace(" ", "")
    #print(favored_team)
    if favored_team == home_team:
        win_prob = 100 - float(percent.text[3:-1].replace(" ", ""))
    else:
        win_prob = float(percent.text[3:-1].replace(" ", ""))
    print('================')
    print(f'Win probability: {percent.text}')
    print(f'Most recent play: {play.text[0:12]}')
    print(f'Corrected win prob: {win_prob}')
    
def get_date():
    #element = driver.find_element(By.XPATH, game_date_xpath)
    date = driver.find_element(By.XPATH, game_date_xpath).text
    date = date.replace(" ", "").replace(",","")
    
    return date
    
def get_vals():
    play = driver.find_element(By.XPATH, most_recent_play_xpath)
    percent = driver.find_element(By.XPATH, percent_xpath)
    home_team = teams[0]
    favored_team = percent.text[0:3].replace(" ","")
    #print(favored_team)
    if favored_team == home_team:
        win_prob = 100 - float(percent.text[3:-1].replace(" ", ""))
    else:
        win_prob = float(percent.text[4:-1].replace(" ", ""))
    return play.text, percent.text, win_prob

plot_element = driver.find_element(By.XPATH, graph_xpath)
actions = ActionChains(driver)
actions.move_to_element(plot_element).perform()

def find_first_play():
    v = get_vals()
    relevant_text = v[0][0:13]
    cursor_at_first_play = False
    while cursor_at_first_play == False:
        #time.sleep(0.1)
        prev_vals = get_vals()
        actions.move_by_offset(-1,0).perform() #move cursor left one pixel
        new_vals = get_vals()
        if new_vals != prev_vals:
            print_vals()
            if new_vals[0][0:13] == "(15:00 - 1st)":
                cursor_at_first_play = True
    print("**********First Play has been reached!*************")
            
find_first_play()
actions.move_by_offset(-1,0).perform()

def clean_datastring(string):
    at_colon = False  
    minute = ''
    second = '' 
    quarter = 0     
    on_second = False
    for i in string:
        if at_colon == False:
            if i == ':':
                at_colon = True
                on_second = True
            else:
                minute += i
        else:
        
            if on_second == True:
                if i != ' ':
                    second += i
                else:
                    on_second = False
            else:
                if i == '1':
                    quarter = 1
                elif i == '2':
                    quarter = 2
                elif i == '3':
                    quarter = 3
                elif i == '4':
                    quarter = 4
                    
    minute = int(minute)
    second = int(second)
    
    return minute, second, quarter

def clean_time(string):
    cleaned_string = clean_datastring(string)
    minute, second, quarter = cleaned_string[0], cleaned_string[1], cleaned_string[2]
    quarter_seconds = (quarter  - 1)*15*60
    minutes_elapsed = 16 - minute
    minute_seconds = minutes_elapsed*60
    seconds_elapsed = 60 - second
    total_seconds_elapsed = quarter_seconds+minute_seconds+seconds_elapsed
    return total_seconds_elapsed

def log_plays():
    home_team = teams[0]
    v = get_vals()
    cursor_at_end = False
    #times, probabilities = [], []
    data = []
    c=0
    while cursor_at_end == False:
        #time.sleep(0.1)
        prev_vals = get_vals()
        actions.move_by_offset(1,0).perform()
        new_vals = get_vals()
        
        if new_vals[0][0:12] == "(0:00 - 4th)":
            cursor_at_end = True
        
        if new_vals != prev_vals:
            #times.append(new_vals[0][1:6])
            #probabilities.append(new_vals[1])
            favored_team = new_vals[1][0:3]
            #pdb.set_trace()
            #print(favored_team)
            if favored_team == home_team:
                win_prob = 100 - float(new_vals[1][4:-1])
            else:
                win_prob = float(new_vals[1][4:-1])
            #print(win_prob)
            data.append([new_vals[0][1:13], new_vals[1], clean_time(new_vals[0][1:13]), new_vals[2]])
            print_vals()
            
        if c==50:
            #cursor_at_end = True
            pass
            
        c+=1
            
    #print(times, probabilities)
    #return times, probabilities
    print(data)
    return data

rows = log_plays()

date = get_date()
teams = find_home_and_away()
save_name = f'../Data/{teams[0]}_vs_{teams[1]}_{date}.csv'

#from matplotlib import pyplot as plt
#plt.plot(rows)
away_team = teams[1]
win_pct_name = f'{away_team}_win_pct'
df = pd.DataFrame(rows, columns=["raw_time", "raw_win_pct", "clean_time", win_pct_name])
df.to_csv(save_name)
from matplotlib import pyplot as plt
plt.plot(df['clean_time'], df[win_pct_name])
plt.show()
'''
np.savetxt(save_name,
           rows,
           delimiter = ", ",
           fmt ='% s')
'''