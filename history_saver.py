####Script to save historical fantasy football stats to thumb drive.




from pylab import *
import pandas as pd
import lineup_pickup_trade as lpt
import os
import requests as rq
from bs4 import BeautifulSoup
import string
import pickle

def GetHistory(pos,fldr):
    subfldr = fldr + '/' + pos
    os.mkdir(subfldr)

    urls = {}
    years= list(range(2001,2019))
    if pos == 'QB':
        for yr in years:
            urls[yr] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek=&PosID=10&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'RB':
        for yr in years:
            urls[yr] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek=&PosID=20&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'WR':
        for yr in years:
            urls[yr] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek=&PosID=30&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'TE':
        for yr in years:
            urls[yr] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek=&PosID=40&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'DST':
        for yr in years:
            urls[yr] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek=&PosID=99&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'K':
        for yr in years:
            urls[yr] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek=&PosID=80&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'

    for yr,url in urls.items():
        historical_stats = pd.concat([pd.read_html(url+'&cur_page='+str(p))[7] for p in range(5)])
        cols = ['Player'] + list(historical_stats.iloc[1][1:].values)
        historical_stats.drop([0,1],inplace = True)
        historical_stats.columns = cols
        ranknms = [(int(nm.split('.')[0]),nm.split('.')[1][1:]) for nm in historical_stats.iloc[:,0]]
        historical_stats.loc[:,'Player'] = [rn[1] for rn in ranknms]
        historical_stats.index = [rn[0] for rn in ranknms]
        historical_stats.to_pickle(subfldr + '/' + str(yr))


    return


def GetWeekHistory(pos,fldr):
    subfldr = fldr + '/' + pos
    os.mkdir(subfldr)

    urls = {}
    years= list(range(2001,2019))
    weeks= list(range(1,18))
    if pos == 'QB':
        for yr in years:
            urls[yr] = {}
            for wk in weeks:
                urls[yr][wk] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek='+str(wk)+'&PosID=10&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'RB':
        for yr in years:
            urls[yr] = {}
            for wk in weeks:
                urls[yr][wk] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek='+str(wk)+'&PosID=20&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'WR':
        for yr in years:
            urls[yr] = {}
            for wk in weeks:
                urls[yr][wk] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek='+str(wk)+'&PosID=30&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'TE':
        for yr in years:
            urls[yr] = {}
            for wk in weeks:
                urls[yr][wk] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek='+str(wk)+'&PosID=40&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'DST':
        for yr in years:
            urls[yr] = {}
            for wk in weeks:
                urls[yr][wk] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek='+str(wk)+'&PosID=99&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'
    elif pos == 'K':
        for yr in years:
            urls[yr] = {}
            for wk in weeks:
                urls[yr][wk] = 'https://www.fftoday.com/stats/playerstats.php?Season='+str(yr)+'&GameWeek='+str(wk)+'&PosID=80&LeagueID=193033&order_by=FFPtsPerG&sort_order=DESC'

    historical_stats = {}

    for yr,urlset in urls.items():
        subsubfld = subfldr + '/' + str(yr)
        os.mkdir(subsubfld)
        for wk,url in urlset.items():
            historical_stats = pd.concat([pd.read_html(url+'&cur_page='+str(p))[7] for p in range(5)])
            cols = ['Player'] + list(historical_stats.iloc[1][1:].values)
            historical_stats.drop([0,1],inplace = True)
            historical_stats.columns = cols
            ranknms = [(int(nm.split('.')[0]),nm.split('.')[1][1:]) for nm in historical_stats.iloc[:,0]]
            historical_stats.loc[:,'Player'] = [rn[1] for rn in ranknms]
            historical_stats.index = [rn[0] for rn in ranknms]
            historical_stats.to_pickle(subsubfld+'/'+str(wk))

    return

tmky = {'ARI':'ARI', 'ATL':'ATL', 'BAL':'BAL', 'BUF':'BUF', 'CAR':'CAR', 'CHI':'CHI', 'CIN':'CIN', 'CLE':'CLE', 'DAL':'DAL',
       'DEN':'DEN', 'DET':'DET', 'GNB':'GB', 'HOU':'HOU', 'IND':'IND', 'JAX':'JAC', 'KAN':'KC', 'LAC':'LAC', 'LAR':'LAR','MIA':'MIA', 'MIN':'MIN',
       'NOR':'NO', 'NWE':'NE', 'NYG':'NYG', 'NYJ':'NYJ', 'OAK':'OAK', 'PHI':'PHI', 'PIT':'PIT','SDG':'SD', 'SEA':'SEA',
       'SFO':'SF', 'STL':'STL', 'TAM':'TB', 'TEN':'TEN', 'WAS':'WAS'}

def MakeDataPoint(playerDF, scoring,offdvoa,defdvoa, minyr = 2001,key = tmky):
    player_data_tmp = []
    stillin = False
    for rw in playerDF.index:
        yr = int(playerDF.loc[rw][('','Year')])
        if yr >= minyr:
            if yr == 2019:
                stillin = True
            gmnum = int(playerDF.loc[rw][('','G#')])
            thests = ['-'.join(s) for s in playerDF.columns if '' != s[0]]
            rowret = pd.Series(index = thests)
            rowret.loc['Age'] = float(playerDF.loc[rw][('','Age')])

            team = playerDF.loc[rw][('','Tm')]#Get DVOA for team
            rowret.loc['Tm_overall'] = float(offdvoa[yr].loc[key[team],'OFF.  DVOA'].replace("%",""))
            rowret.loc['Tm_rushing'] = float(offdvoa[yr].loc[key[team],'RUSH  OFF.'].replace("%",""))
            rowret.loc['Tm_passing'] = float(offdvoa[yr].loc[key[team],'PASS  OFF.'].replace("%",""))
            opp = playerDF.loc[rw][('','Opp')]#Get DVOA for opponent
            # print(defdvoa[yr].index)
            rowret.loc['Opp_overall'] = float(defdvoa[yr].loc[key[team],'DEF.  DVOA'].replace("%",""))
            rowret.loc['Opp_rushing'] = float(defdvoa[yr].loc[key[team],'RUSH  DEF.'].replace("%",""))
            rowret.loc['Opp_passing'] = float(defdvoa[yr].loc[key[team],'PASS  DEF.'].replace("%",""))
            if opp == 'JAX':
                opp = 'JAC'

            pts_scored = 0
            for pt in scoring:
                if tuple(pt.split('-')) in playerDF.columns:
                    pts_scored += scoring[pt]*float(playerDF.loc[rw][tuple(pt.split('-'))])

            for stat in rowret.index:
                if not (stat in ["Age",'Tm_overall','Tm_rushing','Tm_passing','Opp_overall','Opp_rushing','Opp_passing']):
                    colmn = playerDF.loc[:rw][tuple(stat.split('-'))].values
                    weights = np.array([1/(i+1) for i in range(len(colmn))])
                    Z = sum(weights)
                    colmn = np.array([float(s.replace('%','')) if type(s) == str else s for s in colmn]).astype(float)
                    rowret.loc[stat] = sum(colmn*weights)/Z

            player_data_tmp += [(rowret,pts_scored,yr,gmnum,rw)]
    player_data = {}
    for dat in player_data_tmp:
        yr = dat[2]
        gn = dat[3]
        season_total = sum([tp[1] for tp in player_data_tmp if tp[2] == yr])
        Ross = [tp[1] for tp in player_data_tmp if (tp[2] == yr and tp[3] > gn)]
        if len(Ross):
            ROSA = np.mean(Ross)
            ROST = sum(Ross)
        else:
            ROSA = 0
            ROST = 0
        player_data[int(dat[4])] = ([str(dt) for dt in dat[0].index],[float(dt) for dt in dat[0].values],float(dat[1]),float(season_total),float(ROSA),float(ROST))
    return player_data,stillin,key[team]

pos = ['QB', 'RB', 'WR', 'TE','DST','K']

scoringrules = {"Rushing-Yds":0.1,"Rushing-TD":6,"Receiving-Yds":0.1, "Receiving-Rec":0.5,"Receiving-TD":0.6,"Passing-Yds":0.04,"Passing-TD":4,"Passing-Int":-2.0,"Fumbles-Fmb":-2.0}

odvs = {}
ddvs = {}
for yr in range(2000,2018):
    off = pd.read_html("https://www.footballoutsiders.com/stats/teamoff/"+str(yr))[0]
    off.fillna('Blank',inplace = True)
    off.columns = off.loc[0]
    off.rename(columns = {'OFFENSE  DVOA':'OFF.  DVOA','PASS  OFF':'PASS  OFF.','RUSH  OFF':'RUSH  OFF.'}, inplace = True)
    off.index = off.loc[:,'TEAM']
    off.rename(index = {'JAX':'JAC', 'LARM': 'LAR', 'LACH':'LAC'}, inplace = True)
    # print(yr,off.columns)

    defe = pd.read_html("https://www.footballoutsiders.com/stats/teamdef/"+str(yr))[0]
    defe.fillna('Blank',inplace = True)
    defe.columns = defe.loc[0]
    defe.rename(columns = {'DEFENSE  DVOA':'DEF.  DVOA','DEF  DVOA':'DEF.  DVOA','PASS  DEF':'PASS  DEF.','RUSH  DEF':'RUSH  DEF.'}, inplace = True)
    defe.index = defe.loc[:,'TEAM']
    defe.rename(index = {'JAX':'JAC', 'LARM': 'LAR', 'LACH':'LAC'}, inplace = True)
    # print(yr,defe.columns)


    off = off[off.loc[:,'Blank'] != 'Blank']
    odvs[yr] = off
    defe = defe[defe.loc[:,'Blank'] != 'Blank']
    ddvs[yr] = defe

for yr in range(2018,2020):
    off = pd.read_html("https://www.footballoutsiders.com/stats/teamoff/"+str(yr))[0]
    off.index = off.loc[:,'TEAM']
    off.rename(index = {'JAX':'JAC', 'LARM': 'LAR', 'LACH':'LAC'}, inplace = True)
    off.rename(columns = {'OFF.DVOA':'OFF.  DVOA','PASSOFF':'PASS  OFF.','RUSHOFF':'RUSH  OFF.','OFFENSE  DVOA':'OFF.  DVOA','PASS  OFF':'PASS  OFF.','RUSH  OFF':'RUSH  OFF.','OFF  DVOA':'OFF.  DVOA'}, inplace = True)
    # print(yr,off.columns)

    defe = pd.read_html("https://www.footballoutsiders.com/stats/teamdef/"+str(yr))[0]
    defe.index = defe.loc[:,'TEAM']
    defe.rename(index = {'JAX':'JAC', 'LARM': 'LAR', 'LACH':'LAC'}, inplace = True)
    defe.rename(columns = {'DEF.DVOA':'DEF.  DVOA','DEF  DVOA':'DEF.  DVOA','PASSDEF':'PASS  DEF.','RUSHDEF':'RUSH  DEF.','DEFENSE  DVOA':'DEF.  DVOA','PASS  DEF':'PASS  DEF.','RUSH  DEF':'RUSH  DEF.'}, inplace = True)
    # print(yr,defe.columns)
    odvs[yr] = off
    ddvs[yr] = defe



# AllData = {}
# AllData['QB'] = {}
# AllData['RB'] = {}
# AllData['WR'] = {}
# AllData['TE'] = {}

pfr_namekeys = {}

for position in ['QB','RB', 'WR', 'TE']:
    posdata = {}
    for let in string.ascii_uppercase:
        res =rq.get("https://www.pro-football-reference.com/players/"+let+"/")
        sp = BeautifulSoup(res.text)
        for pa in sp.find_all('p'):
            if position in pa.get_text() and '/players/' in str(pa.a):
                nm = str(pa.a.get("href"))
                link = 'https://www.pro-football-reference.com'+nm[:-4]+'/gamelog/'#nm[:-4]
                try:
                    plDF = pd.read_html(link)[0]
                    goon = True
                except:
                    goon = False

                # try:
                if goon:
                    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
                    thests2 = [s if 'Unnamed' not in s[0] else ('',s[1]) for s in plDF.columns]
                    plDF.columns = thests2
                    plDF.fillna(0, inplace = True)
                    print(nm)
                    plDF = plDF[(plDF.loc[:,[('', 'Rk')]] != 'Rk').values]


                    # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                    #dict of tuples keyed by game # in career. tuple is (stat key, stat array, fantasy points, season total points, ROS point average, ROS point total)
                    plydata,needname,cteam = MakeDataPoint(plDF,scoringrules,odvs,ddvs)
                    if cteam = 'JAC':
                        cteam = 'JAX'
                    if len(plydata):
                        posdata[nm]= plydata
                    if needname:
                        pfr_namekeys[nm] = pa.get_text().split('(')[0] + '- ' + cteam
                # except:
                #     None
    with open('playerdata/'+position+'data.pkl','wb') as handle:
        pickle.dump(posdata,handle)

with open('playerdata/pfr_namekeys.pkl','wb') as handle:
    pickle.dump(pfr_namekeys,handle)




# yearly_folder = '/Volumes/Untitled/YearlyFFballHistory'
# weekly_folder = '/Volumes/Untitled/WeeklyFFballHistory'

# os.mkdir(yearly_folder)
# os.mkdir(weekly_folder)

# for p in pos:
#     # GetHistory(p,yearly_folder)
#     GetWeekHistory(p,weekly_folder)
