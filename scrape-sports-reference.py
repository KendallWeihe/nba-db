import requests
from bs4 import BeautifulSoup
import pdb
import numpy as np
import re
import os

teamsFile = open("./teams.txt", "r")
allTeams = teamsFile.read().splitlines()

def findTeamIndex(team):
    return allTeams.index(team)

website = "http://www.basketball-reference.com/"
dayLink = "boxscores/"
innerYear, year = "2017", "2017"

while 1:
    print dayLink
    r = requests.get(website+dayLink)
    outerSoup = BeautifulSoup(r.text, "html.parser")
    teams = outerSoup.findAll('table', class_='teams')
    boxScores = outerSoup.findAll('a', href=True, text='Final')
    for i in range(len(boxScores)):
        try:
            gameLink = str(boxScores[i]['href'])
            r = requests.get(website+gameLink)
            soup = BeautifulSoup(r.text, "html.parser")

            date = float(re.findall("[-+]?\d+[\.]?\d*[eE]?[-+]?\d*", gameLink)[0])

            tr1 = soup.findAll('table')[0].findAll('tfoot')[0].findAll('td')
            tr2 = soup.findAll('table')[2].findAll('tfoot')[0].findAll('td')

            team1_stats_today = []
            team2_stats_today = []
            for j in range(1,19):
                team1_stats_today.append(float(tr1[j].string))
                team2_stats_today.append(float(tr2[j].string))

            team1 = str(teams[i].findAll('a')[0].string).replace(" ", "-").replace("\'", "")
            team2 = str(teams[i].findAll('a')[2].string).replace(" ", "-").replace("\'", "")

            team1_index = findTeamIndex(team1)
            team2_index = findTeamIndex(team2)

            score1 = float(soup.findAll('div', class_='score')[0].string)
            score2 = float(soup.findAll('div', class_='score')[1].string)
            spread1 = score1 - score2
            spread2 = score2 - score1

            team1_out = [date] + team1_stats_today + team2_stats_today + [team2_index, score1, score2, spread1]
            team2_out = [date] + team2_stats_today + team1_stats_today + [team1_index, score1, score2, spread2]
            # team1_out = [date] + team1_stats_today + team2_stats_today + [score1, score2, spread1]
            # team2_out = [date] + team2_stats_today + team1_stats_today + [score1, score2, spread2]

            try:
                team1_stats = np.genfromtxt("./seasons/"+year+"/"+team1+".csv", delimiter=",")
                team1_stats = np.vstack((team1_stats, team1_out))
            except:
                team1_stats = np.array([team1_out])

            try:
                team2_stats = np.genfromtxt("./seasons/"+year+"/"+team2+".csv", delimiter=",")
                team2_stats = np.vstack((team2_stats, team2_out))
            except:
                team2_stats = np.array([team2_out])

            np.savetxt("./seasons/"+year+"/"+team1+".csv", team1_stats, delimiter=",")
            np.savetxt("./seasons/"+year+"/"+team2+".csv", team2_stats, delimiter=",")

        except:
            print gameLink
            pdb.set_trace()
            pass

    nextDate = str(outerSoup.findAll('a', class_='button2')[0].string)
    if re.findall("Dec", nextDate) and innerYear == year:
        innerYear = str(int(innerYear)-1)

    dayLink = str(outerSoup.findAll('a', class_='button2')[0]['href'])
    date = str(outerSoup.findAll('a', class_='button2')[0].string)
    if re.findall("Sep", date) and innerYear != year:
        year = str(int(year)-1)
        os.mkdir("./seasons/"+year)
