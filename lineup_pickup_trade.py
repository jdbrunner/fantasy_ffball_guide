######################################################################
#
#		fantasy football team management helper
#
#
#
#
######################################################################

## run in IDLE with exec(open('lineup_pickup_trade.py').read())


from pylab import *
import pandas as pd
import sys
from scipy.stats import nbinom
import numpy as np
import requests as rq
from bs4 import BeautifulSoup

# Display size
pd.set_option('display.max_colwidth', 200)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

nfl_teams = {'Buffalo':'Bills', 'Miami':'Dolphins', 'New England':'Patriots', 'New York NYJ':'Jets',
				'Baltimore':'Ravens', 'Cincinnati':'Bengals', 'Cleveland':'Browns', 'Pittsburgh':'Steelers',
				'Houston':'Texans', 'Indianapolis':'Colts', 'Jacksonville':'Jaguars', 'Tennessee':'Titans',
				'Denver':'Broncos', 'Kansas City':'Chiefs', 'Los Angeles LAC':'Chargers', 'Oakland':'Raiders',
				'Dallas':'Cowboys', 'New York NYG':'Giants', 'Philadelphia':'Eagles', 'Washington':'Redskins',
				'Chicago':'Bears', 'Detroit':'Lions', 'Green Bay':'Packers', 'Minnesota':'Vikings',
				'Atlanta':'Falcons', 'Carolina':'Panthers', 'New Orleans':'Saints', 'Tampa Bay':'Buccaneers',
				'Arizona':'Cardinals', 'Los Angeles LAR':'Rams', 'Seattle':'Seahawks', 'San Francisco':'49ers'}






position_map = {'QB':['QB'],'RB': ['RB','GLB','FB','3RB','HB'], 'WR': ['WR1','WR2','WR3','WR'],'TE': ['TE'], 'DST':['DST','DST'],'K':['K']}
inv_position_map ={'QB':'QB','RB':'RB','HB':'RB','GLB':'RB','FB':'RB','3RB':'RB', 'WR1':'WR','WR2':'WR','WR3':'WR','WR':'WR','TE': 'TE', 'K':'K', 'DST':'DST', 'DST':'DST'}

OffensePoints = {'Passing Yards': 1/25, 'Passing TD':4, 'Interception Thrown':-1, 'Sack Taken':0, 'Rushing Yards':1/10, 'Rusing TD':6, 'Reception':0.5, 'Receiving Yards':1/10, 'Receiving TD':6, 'Return Yards':0, 'Return TD':6, '2 Point Conversion':2, 'Fumble':0, 'Fumble Lost':-2}

DefensePoints = {'Sack':1, 'Interception':2, 'Fumble Recovery':2, 'Touchdown':6, 'Safety':2, 'Blocked Kick':2, 'Return Touchdown':6, 'Points Allowed: 0':10, 'Points Allowed: 1-6':7, 'Points Allowed: 7-13':4, 'Points Allowed: 14-20':1, 'Points Allowed: 21-27':0, 'Points Allowed: 28-34': -1, 'Points Allowed: 35+':-4, 'Tackle for loss':0, 'Extra Point Returned':2}

Roster = {'QB':1, 'RB': 2, 'WR':2, 'TE':1, 'FLEX':1, 'SUPERFLEX':0, 'DST':1, 'K':1, 'BENCH':7}

def make_clickable(val):
    # target _blank to open new window
    return '<a target="_blank" href="{}">{}</a>'.format(val, val)


def download_info(scoring):

	if scoring == "standard":
		url_1 = ""
	elif scoring == "half":
		url_1 = "half-point-ppr-"
	elif scoring == "ppr":
		url_1 = "ppr-"

	fp_urls = {'QB':"https://www.fantasypros.com/nfl/rankings/qb.php",
					'RB': "https://www.fantasypros.com/nfl/rankings/"+url_1+"rb.php",
					'WR': "https://www.fantasypros.com/nfl/rankings/"+url_1+"wr.php",
					'TE': "https://www.fantasypros.com/nfl/rankings/"+url_1+"te.php",
					'FLEX': "https://www.fantasypros.com/nfl/rankings/"+url_1+"flex.php",
					'DST': "https://www.fantasypros.com/nfl/rankings/dst.php",
					'K': "https://www.fantasypros.com/nfl/rankings/k.php"}

	match_urls = {'QB':"https://www.fantasypros.com/nfl/matchups/qb.php",
				'RB': "https://www.fantasypros.com/nfl/matchups/rb.php",
				'WR': "https://www.fantasypros.com/nfl/matchups/wr.php",
				'TE': "https://www.fantasypros.com/nfl/matchups/te.php",
				'K': "https://www.fantasypros.com/nfl/matchups/k.php",
				'DST': "https://www.fantasypros.com/nfl/matchups/dst.php"}

	ros_urls = {'QB':"https://www.fantasypros.com/nfl/rankings/ros-qb.php",'RB': "https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"rb.php",'WR': "https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"wr.php",'TE': "https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"te.php",'FLEX':"https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"flex.php",'DST': "https://www.fantasypros.com/nfl/rankings/ros-dst.php",'K':"https://www.fantasypros.com/nfl/rankings/ros-k.php"}

	snap_count_urls = {'QB':"https://www.fantasypros.com/nfl/reports/snap-counts/qb.php",
				'RB': "https://www.fantasypros.com/nfl/reports/snap-counts/rb.php",
				'WR': "https://www.fantasypros.com/nfl/reports/snap-counts/wr.php",
				'TE': "https://www.fantasypros.com/nfl/reports/snap-counts/te.php"}

	snap_count_perc_urls = {'QB':"https://www.fantasypros.com/nfl/reports/snap-counts/qb.php?show=perc",
				'RB': "https://www.fantasypros.com/nfl/reports/snap-counts/rb.php?show=perc",
				'WR': "https://www.fantasypros.com/nfl/reports/snap-counts/wr.php?show=perc",
				'TE': "https://www.fantasypros.com/nfl/reports/snap-counts/te.php?show=perc"}

	snap_analysis_urls = {'QB':"https://www.fantasypros.com/nfl/reports/snap-count-analysis/qb.php?scoring=HALF",
				'RB': "https://www.fantasypros.com/nfl/reports/snap-count-analysis/rb.php?scoring=HALF",
				'WR': "https://www.fantasypros.com/nfl/reports/snap-count-analysis/wr.php?scoring=HALF",
				'TE': "https://www.fantasypros.com/nfl/reports/snap-count-analysis/te.php?scoring=HALF"}

	targets_urls = {'RB': "https://www.fantasypros.com/nfl/reports/targets/rb.php",'WR': "https://www.fantasypros.com/nfl/reports/targets/wr.php",'TE': "https://www.fantasypros.com/nfl/reports/targets/te.php"}



	for p in fp_urls:
		fant_pros = pd.read_html(fp_urls[p])[0]
		fant_pros.to_pickle('leagueinfo/' + p +'.ecr')


	for p in match_urls:
		matchups = pd.read_html(match_urls[p])[0]
		matchups.to_pickle('leagueinfo/'+p+'.matchups')

	for p in ros_urls:
		fant_pros_ros = pd.read_html(ros_urls[p])[0]
		fant_pros_ros.to_pickle('leagueinfo/' + p +'.ros')

	ros_overall = pd.read_html("https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"overall.php")[0]
	ros_overall.to_pickle('leagueinfo/overall.ros')

	for p in snap_count_urls:
		snap_counts = pd.read_html(snap_count_urls[p])[0]
		snap_counts.to_pickle('leagueinfo/' + p +'.snc')

	for p in snap_count_perc_urls:
		snap_count_perc = pd.read_html(snap_count_perc_urls[p])[0]
		snap_count_perc.to_pickle('leagueinfo/' + p +'.snp')

	for p in snap_analysis_urls:
		snap_analysis = pd.read_html(snap_analysis_urls[p])[0]
		snap_analysis.to_pickle('leagueinfo/' + p +'.sna')

	for p in targets_urls:
		targets = pd.read_html(targets_urls[p])[0]
		targets.to_pickle('leagueinfo/' + p +'.targets')

	kicker_stats = pd.read_html("https://www.fantasypros.com/nfl/stats/k.php")[0]
	kicker_stats.to_pickle('leagueinfo/kicker.stats')

	defense_stats = pd.read_html("https://www.fantasypros.com/nfl/stats/dst.php")[0]
	defense_stats.to_pickle('leagueinfo/dst.stats')

	return None




def draw_score(probs,alldata):


	# ranu = np.random.rand(len(probs))
	# rank_draw = sum([ranu[i] < probs[i] for i in range(len(probs))])
	# ranu = np.random.rand()
	# rank_draw = sum([ranu < probs[i] for i in range(len(probs))])#np.where(withran == ranu)
	# rank_draw = min(rank_draw,len(alldata)-1)

	ranu = np.random.rand()
	rank_draw = min([i for i in range(len(probs)) if probs[i] < ranu] + [len(alldata)])
	rank_draw = min(rank_draw,len(alldata)-1)




	distr = alldata[rank_draw]
	distr.sort()

	norml = len(distr)

	scr_draw = np.random.randint(0,high = norml)
	score = distr[scr_draw]

	return rank_draw,score

def estimate_score(avg_rk,std_rk,statscr,alldata,posSize,numtrials =1000):

	rnk = 0
	score = 0

	ecr = avg_rk*statscr
	kparm = std_rk + 0.2*avg_rk
	probs = np.array([1/(1+np.exp((i-ecr)/kparm)) for i in range(posSize)])#make_pb_CDF(mu,kparm,posSize)



	for j in range(numtrials):
		r,s = draw_score(probs,alldata)
		rnk += r
		score += s
	return rnk/numtrials, score/numtrials


def get_statvec(tp,kys):
    statdic = dict([(tp[0][i],tp[1][i]) for i in range(len(tp[0]))])
    return (tp[2],[statdic[stat] if stat in statdic.keys() else 0 for stat in kys])

def get_statvec_noopp(tp,kys):
    statdic = dict([(tp[0][i],tp[1][i]) for i in range(len(tp[0]))])
    newkys = [ky for ky in kys if 'Opp' not in ky]
    return (tp[2],[statdic[stat] if stat in statdic.keys() else 0 for stat in newkys])

#player is index from player_list, alldata is positional data from PFR, datakey is name to url from PFR, oppo is week's opponent, ddvs is defense DVOA DF
def get_GNeighbor_Score(player,alldata,datakey,oppo,ddvs):
	playerall = alldata[datakey[player]]
	lastgm = max(playerall.keys())
	playernow = playerall[lastgm]
	# oppo = playerlist.loc[player,'Opp'].split(' ')[1]
	playerdat = copy(playernow[1])
	playerdat[-3] = float(ddvs.loc[oppo,'DEF.  DVOA'].replace('%',''))
	playerdat[-2] = float(ddvs.loc[oppo,'RUSH  DEF.'].replace('%',''))
	playerdat[-1] = float(ddvs.loc[oppo,'PASS  DEF.'].replace('%',''))

	flat_Data_wkly = [get_statvec(tp,playernow) for di in alldata.values() for tp in di.values()]

	bnd = 10**(-1)
	weights = np.ones(len(playerdat))
	alldists = [(fd[0],(bnd/np.sqrt(2*np.pi**len(playerdat)))*np.exp(-0.5*np.dot(playerdat - fd[1],weights*np.array(playerdat - fd[1]))*bnd)) for fd in flat_Data]
	scling = sum([f[1] for f in alldists])
	scorepred = (1/scling)*sum([d[0]*d[1] for d in alldists])

	flat_data_ros = [get_statvec_noopp(tp,playernow) for di in alldata.values() for tp in di.values()]
	player_ros = playerdat[:-3]

	weightsros = np.ones(len(player_ros))
	alldists_ros = [(fd[0],(bnd/np.sqrt(2*np.pi**len(player_ros)))*np.exp(-0.5*np.dot(player_ros - fd[1],weightsros*np.array(player_ros - fd[1]))*bnd)) for fd in flat_data_ros]
	scling_ros = sum([f[1] for f in alldists_ros])
	scorepred_ros = (1/scling_ros)*sum([d[0]*d[1] for d in alldists_ros])

	return scorepred,scorepred_ros

def make_rosters_from_espn(league_URL,yourswid,yourespn_s2,teams = {}):


	nfltms = {'22': 'ARI','1': 'ATL','2': 'BUF','33': 'BAL','29': 'CAR','3': 'CHI','4': 'CIN','5': 'CLE','6': 'DAL','7': 'DEN','8': 'DET','9': 'GB','34':'HOU','11': 'IND','30':'JAC','12': 'KC','24': 'LAC','14': 'LAR','15': 'MIA','16': 'MIN','17': 'NE','18': 'NO','19': 'NYG','20': 'NYJ','13': 'OAK','21': 'PHI','23': 'PIT','26': 'SEA','25': 'SF','27': 'TB','10': 'TEN','28':'WAS','0':'FA'}


	posdict = {1:'QB',2:'RB',3:'WR',4:'TE',5:'K',16:'DST'}


	req1 = rq.get(league_URL, params = {'view':'mTeam'}, cookies = {'swid':yourswid,'espn_s2':yourespn_s2})
	pg1 = req1.json()

	tmids = dict([(tm['id'],tm['location'] + ' ' + tm['nickname']) for tm in pg1['teams']])#for tm in pg['teams']:

	req2 = rq.get(league_URL, params = {'view':'mMatchup'}, cookies = {'swid':yourswid,'espn_s2':yourespn_s2})
	pg2 = req2.json()

	rostertab = pd.DataFrame(columns = ['Pos','Player','FTeam'])

	rosters = {}

	for tm in pg2['teams']:
		rostertab = pd.DataFrame(columns = ['Pos','Player','FTeam'], index = range(len(tm['roster']['entries'])))
		fteam = tmids[tm['id']]
		rwcnt = 0
		for pl in tm['roster']['entries']:
			plnm = pl["playerPoolEntry"]['player']['fullName']
			plnm = ' '.join(plnm.split(' ')[:2])
			# print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
			# print(plnm)
			plpos = posdict[int(pl["playerPoolEntry"]['player']['defaultPositionId'])]
			nfltm = nfltms[str(pl["playerPoolEntry"]['player']['proTeamId'])]
			if plpos == 'DST':
				plnm = nfltm
			rostertab.loc[rwcnt,'Pos'] = plpos
			rostertab.loc[rwcnt,'Player'] = plnm + ' - '+nfltm
			rostertab.loc[rwcnt,'FTeam'] = fteam
			rwcnt += 1
		rosters[fteam] = rostertab

	return rosters




def make_rosters_from_yahoo(league_URL,positional,player_list,teams = {}):
	req = rq.get(league_URL)
	sp = BeautifulSoup(req.text)

	cols = ['Pos','Player']

	rosters = dict()
	# for i in range(len(teams)):
	for d in sp.find_all('div'):
		if len(d.find_all('table')) ==1 and len(d.find_all('p')) == 1:

			table = d.find_all('table')[0]

			the_rost = pd.DataFrame(index = range(len(table.find_all('tr'))-1),columns = cols) # I know the size


			row_marker = 0
			for row in table.find_all('tr')[1:]:
				column_marker = 0
				columns = row.find_all('td')
				for column in columns:
					the_rost.loc[row_marker,cols[column_marker]] = str(column.get_text())
					column_marker += 1
				row_marker +=1
			# the_rost = make_table_from_yahoo(d.find_all('table')[0])#raw_rosters[i].copy()
			tmnam = d.find_all('p')[0].a.text
			# print(the_rost.loc[:,'Player'])
			the_rost['Pos'] = ['    ']*len(the_rost)
			for ii in the_rost.index:
				if 'DEF' in the_rost.loc[ii,'Player']:
					for tm in positional['DST']['Team']:
						if ' '+tm.lower()+' ' in str(the_rost.loc[ii,'Player']).lower():
							the_rost.loc[ii,'Player'] = positional['DST'].index[positional['DST']['Team']==tm][0]
							the_rost.loc[ii,'Pos'] = 'DST'
				else:
					for pl in player_list.index:
						if player_list.loc[pl,'Pos.'] != 'DST':
							plnm1 = pl.split(' - ')[0].replace('.','')
							plnm2 = pl.split(' - ')[0]
							pltm = pl.split(' - ')[1]
							if pltm == 'JAC':
								pltm = 'JAX'
							chk1 = plnm1.split(' ')[0] in the_rost.loc[ii, 'Player'] and plnm1.split(' ')[1] in the_rost.loc[ii, 'Player'] and pltm in the_rost.loc[ii, 'Player'].upper()
							chk2 = plnm2.split(' ')[0] in the_rost.loc[ii, 'Player'] and plnm2.split(' ')[1] in the_rost.loc[ii, 'Player'] and pltm in the_rost.loc[ii, 'Player'].upper()
							if chk1 or chk2:
								the_rost.loc[ii,'Player'] = pl
								the_rost.loc[ii,'Pos'] = player_list[player_list['Pos.'] != 'FLEX'].loc[pl, 'Pos.']
			if len(teams):
				rosters[teams[tmnam]] = the_rost
			else:
				rosters[tmnam] = the_rost



	return rosters


########################### Add Expert Rankings ######################################
def initialize_league(week,scoring,league_URL,site = "yahoo",teams = {},yourswid = " ",yourespn_s2 = " "):

	'''
	Data Frames Created:
	Description - name - index - columns
	full player list - player_list - player name - Team Pos Depth Notes ROS_Avg ROS_Best ROS_Std TOS_Notes
	list of (position) [dictionary] - positional['position'] - same as above - same as above
	expert consensus rankings (weekly) from fantasy pros [dictionary] - fant_pros['position'] - int - Rank Name Opp Best Worst Avg Std Dev Notes
	list of matchups [dictionary] - matchups['position'] - player name - ECR 1 2 3 ... 17 (week numbers)
	rest of schedule rankings from fantasy pros [dictionary] - ros_rks['position'] - player name - Rank Name Bye Best Worst Avg Std Dev ADP vs ADP
	various stat dataframes - targets, snaps, etc
	'''

	if scoring == "standard":
		url_1 = ""
	elif scoring == "half":
		url_1 = "half-point-ppr-"
	elif scoring == "ppr":
		url_1 = "ppr-"


	fp_urls = {'QB':"https://www.fantasypros.com/nfl/rankings/qb.php",
					'RB': "https://www.fantasypros.com/nfl/rankings/"+url_1+"rb.php",
					'WR': "https://www.fantasypros.com/nfl/rankings/"+url_1+"wr.php",
					'TE': "https://www.fantasypros.com/nfl/rankings/"+url_1+"te.php",
					'FLEX': "https://www.fantasypros.com/nfl/rankings/"+url_1+"flex.php",
					'DST': "https://www.fantasypros.com/nfl/rankings/dst.php",
					'K': "https://www.fantasypros.com/nfl/rankings/k.php"}



	dst_teams = {'Chicago Bears':'CHI', 'Jacksonville Jaguars':'JAC', 'Los Angeles Rams':'LAR', 'Baltimore Ravens':'BAL', 'Minnesota Vikings':'MIN', 'Los Angeles Chargers':'LAC', 'Cleveland Browns':'CLE', 'Houston Texans':'HOU', 'New Orleans Saints':'NO', 'New England Patriots':'NE', 'Denver Broncos':'DEN', 'Buffalo Bills':'BUF', 'Dallas Cowboys':'DAL', 'Philadelphia Eagles':'PHI', 'Seattle Seahawks':'SEA', 'Pittsburgh Steelers':'PIT', 'Kansas City Chiefs':'KC', 'Tennessee Titans':'TEN', 'Indianapolis Colts':'IND', 'Carolina Panthers':'CAR', 'Atlanta Falcons':'ATL', 'Green Bay Packers':'GB', 'New York Jets':'NYJ', 'Washington Redskins':'WAS', 'Arizona Cardinals':'ARI', 'Detroit Lions':'DET', 'San Francisco 49ers':'SF', 'New York Giants':'NYG', 'Miami Dolphins':'MIA', 'Tampa Bay Buccaneers':'TB', 'Cincinnati Bengals':'CIN', 'Oakland Raiders':'OAK'}


	historical = {}
	for ps in fp_urls:
		if ps != 'FLEX':
			# historical[ps] = GetHistory(ps)
			historical[ps] = GetHistoryFromUSB(ps)

	fant_pros = {}
	ros_rks = {}
	positional = {}
	#add rankings
	for p in fp_urls:
		try:
			fant_pros[p] = pd.read_pickle('leagueinfo/' + p +'.ecr')
		except:
			download_info(scoring)
			fant_pros[p] = pd.read_pickle('leagueinfo/' + p +'.ecr')

		try:
			ros_temp = pd.read_pickle('leagueinfo/'+p+'.ros')
		except:
			download_info(scoring)
			ros_temp = pd.read_pickle('leagueinfo/'+p+'.ros')

		fant_pros[p].drop('WSIS', axis = 1, inplace = True)
		fant_pros[p].rename(columns = {fant_pros[p].columns[1]:'Name',fant_pros[p].columns[0]:'Rank'}, inplace = True)#
		fant_pros[p].drop([col for col in fant_pros[p].columns if "Unnamed" in col], axis = 1, inplace = True)
		#
		fant_pros[p].dropna(inplace = True)
		fant_pros[p].drop(index = [indd for indd in fant_pros[p].index if 'google' in fant_pros[p].loc[indd,'Opp']], inplace = True)
		#


		player_names_fmted2 = [(ind,fant_pros[p].Name.loc[ind].split(' ')[0] + ' ' + fant_pros[p].Name.loc[ind].split(' ')[-2],fant_pros[p].Name.loc[ind].split(' ')[-1]) for ind in fant_pros[p].index if '(' not in fant_pros[p].Name.loc[ind].split(' ')[-2]] + [(ind,fant_pros[p].Name.loc[ind].split('(')[1].split(')')[0],fant_pros[p].Name.loc[ind].split('(')[1].split(')')[0]) for ind in fant_pros[p].index if '(' in fant_pros[p].Name.loc[ind]]

		player_names = ros_temp.iloc[:,2]
		player_names.dropna(inplace = True)
		player_names.drop(index = [indd for indd in player_names.index if 'google' in player_names.loc[indd]], inplace = True)


		player_names_fmted = [(ind,player_names.loc[ind].split(' ')[0] + ' ' + player_names.loc[ind].split(' ')[-2],player_names.loc[ind].split(' ')[-1]) for ind in player_names.index if '(' not in player_names.loc[ind].split(' ')[-2]] + [(ind,player_names.loc[ind].split('(')[1].split(')')[0],player_names.loc[ind].split('(')[1].split(')')[0]) for ind in player_names.index if '(' in player_names.loc[ind]]



		fant_pros[p].loc[:,"FixedName"] = [pl[1] for pl in player_names_fmted2]
		fant_pros[p].loc[:,"Team"]=[pl[2] for pl in player_names_fmted2]

		positional[p] = pd.DataFrame(index = [pl[1]+" - " + pl[2] for pl in player_names_fmted])
		fant_pros[p].index = [pl[1]+" - " + pl[2] for pl in player_names_fmted2]


		ros_rks[p] = ros_temp
		num_po = len(ros_rks[p])
		ros_rks[p].drop(ros_rks[p].columns[1],axis = 1, inplace = True)
		ros_rks[p].rename(columns = {ros_rks[p].columns[1]:'Name',ros_rks[p].columns[0]:'Rank'}, inplace = True)
		ros_rks[p].Name = ros_rks[p].Name.astype(str)
		ros_rks[p] = ros_rks[p][invert(ros_rks[p].Name == 'nan')]


		ros_rks[p].drop(index = [indd for indd in ros_rks[p].index if 'google' in str(ros_rks[p].loc[indd,'Rank'])], inplace = True)

		# if p != 'DST':
		# 	names = [nm.split(' ')[0] + ' '+nm.split(' ')[1][:-2] + ' - '+nm.split(' ')[-1] for nm in ros_rks[p].loc[:,'Name']]
		# else:
		# 	names = [nm.split(')')[1].split(' ')[0] + ' - '+nm.split(')')[1].split(' ')[0] for nm in ros_rks[p].loc[:,'Name']]
		ros_rks[p].index =  [pl[1]+" - " + pl[2] for pl in player_names_fmted]
		ros_rks[p].drop('Name', axis = 1, inplace = True)



		for ply in positional[p].index:
			ros_row = ros_rks[p].loc[ply]
			if ply in fant_pros[p].index:
				fp_row = fant_pros[p].loc[ply]
				positional[p].loc[ply,'Name'] = fp_row['FixedName']
				positional[p].loc[ply,'Team'] = fp_row['Team']
				if p != 'FLEX':
					positional[p].loc[ply,'Pos.'] = p
				else:
					positional[p].loc[ply,'Pos.'] = ''.join([l for l in fp_row['Pos'] if not l.isdigit()])
				positional[p].loc[ply,'Avg'] = float(fp_row['Avg'])#.astype(float)
				positional[p].loc[ply,'Best'] = float(fp_row['Best'])#.astype(float)
				positional[p].loc[ply,'Worst'] = float(fp_row['Worst'])#.astype(float)
				positional[p].loc[ply,'Std_Dev'] = float(fp_row['Std Dev'])#.astype(float)
				positional[p].loc[ply,'Opp'] = fp_row['Opp']
				if p != "DST":
					positional[p].loc[ply,'Info'] = "http://www.google.com/search?q="+"+".join(ply.lower().split(" ")[:-1])+"+fantasy"
				else:
					positional[p].loc[ply,'Info'] = "http://www.google.com/search?q="+ply+"+defense+fantasy"

			else:
				positional[p].loc[ply,'Name'] = ply.split(' - ')[0]#fp_row['FixedName']
				positional[p].loc[ply,'Team'] = ply.split(' - ')[1]
				if p != 'FLEX':
					positional[p].loc[ply,'Pos.'] = p
				else:
					positional[p].loc[ply,'Pos.'] = ''.join([l for l in ros_row['Pos'] if not l.isdigit()])
				positional[p].loc[ply,'Avg'] = 1000#float(ros_rks['Avg'])#.astype(float)
				positional[p].loc[ply,'Best'] = 1000#float(ros_rks['Best'])#.astype(float)
				positional[p].loc[ply,'Worst'] = 1000#float(ros_rks['Worst'])#.astype(float)
				positional[p].loc[ply,'Std_Dev'] = 0#float(ros_rks['Std Dev'])#.astype(float)
				positional[p].loc[ply,'Opp'] = 'BYE'#ros_rks['Opp']
				if p != "DST":
					positional[p].loc[ply,'Info'] = "http://www.google.com/search?q="+"+".join(ply.lower().split(" ")[:-1])+"+fantasy"
				else:
					positional[p].loc[ply,'Info'] = "http://www.google.com/search?q="+ply+"+defense+fantasy"


		#
		# for nm in positional[p].index:
		# 	# if nm in ros_rks[p].index:

			positional[p].loc[ply,'ROS_Avg'] = float(ros_row['Avg'])#.values.astype(float)
			positional[p].loc[ply,'ROS_Best'] = float(ros_row['Best'])#.values.astype(float)
			positional[p].loc[ply,'ROS_Worst'] = float(ros_row['Worst'])#.values.astype(float)
			positional[p].loc[ply,'ROS_Std'] = float(ros_row['Std Dev'])#.values.astype(float)
			# else:
			# 	positional[p].loc[nm,'ROS_Avg'] = num_po
			# 	positional[p].loc[nm,'ROS_Best'] = num_po
			# 	positional[p].loc[nm,'ROS_Worst'] = num_po
			# 	positional[p].loc[nm,'ROS_Std'] = num_po


	match_urls = {'QB':"https://www.fantasypros.com/nfl/matchups/qb.php",
				'RB': "https://www.fantasypros.com/nfl/matchups/rb.php",
				'WR': "https://www.fantasypros.com/nfl/matchups/wr.php",
				'TE': "https://www.fantasypros.com/nfl/matchups/te.php",
				'K': "https://www.fantasypros.com/nfl/matchups/k.php",
				'DST': "https://www.fantasypros.com/nfl/matchups/dst.php"}
	### Name of player in "Player" column, matchup for week N in columns "N", in format TEAM## where ## is the difficutly,
	##			with higer number meaning more difficult, according to fantasy pros.
	matchups = {}
	for p in match_urls:
		try:
			matchups[p] = pd.read_pickle('leagueinfo/'+p+'.matchups')
		except:
			download_info(scoring)
			matchups[p] = pd.read_pickle('leagueinfo/'+p+'.matchups')
		for i in matchups[p]:
			matchups[p].loc[:,i] = matchups[p].loc[:,i].astype(str)
		matchups[p].Player = matchups[p].Player.astype(str)
		if p != 'DST':
			names = [nm.split(' ')[0] + ' '+nm.split(' ')[1] + ' - '+nm.split(' ')[-1] for nm in matchups[p].Player]
		else:
			names =  [dst_teams[nm] + ' - ' + dst_teams[nm] for nm in matchups[p].Player]
		matchups[p].index = names
		matchups[p].drop('Player',axis = 1, inplace = True)

	matchups['FLEX'] = pd.concat([matchups[p] for p in ['WR','RB','TE']])


	# ros_urls = {'QB':"https://www.fantasypros.com/nfl/rankings/ros-qb.php",'RB': "https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"rb.php",'WR': "https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"wr.php",'TE': "https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"te.php",'FLEX':"https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"flex.php",'DST': "https://www.fantasypros.com/nfl/rankings/ros-dst.php",'K':"https://www.fantasypros.com/nfl/rankings/ros-k.php"}
	#
	#
	#
	# for p in ros_urls:
	#



	player_list = pd.concat([positional[p] for p in positional.keys() if p != "FLEX"])

	try:
		ros_overall = pd.read_pickle('leagueinfo/overall.ros')
	except:
		download_info(scoring)
		ros_overall = pd.read_pickle('leagueinfo/overall.ros')
	ros_overall.drop(ros_overall.columns[1],axis=1,inplace = True)
	ros_overall.rename(columns = {ros_overall.columns[1]:'Name',ros_overall.columns[0]:'Rank'}, inplace = True)
	ros_overall = ros_overall[invert([isnan(nm) for nm in ros_overall.Name.str.contains('')])]

	names = array([nm.split(' ')[0] + ' '+nm.split(' ')[1][:-2] + ' - '+nm.split(' ')[-1] for nm in ros_overall.loc[:,'Name']])
	defs = array(ros_overall[ros_overall.Pos.str.contains('DST')].index)
	names[defs] = [nm.split(')')[1].split(' ')[0] + ' - ' + nm.split(')')[1].split(' ')[0] for nm in ros_overall.loc[defs,'Name']]


	player_list = player_list.loc[~player_list.index.duplicated(keep='first')]

	ros_overall.index = names
	for nm in player_list.index:
		num_po = len(ros_rks[player_list.loc[nm,"Pos."]])
		if nm in ros_overall.index:
			ros_row = ros_overall.loc[nm]
			player_list.loc[nm,'ROS_Avg_ov'] = float(ros_row['Avg'])#.values.astype(float)
			player_list.loc[nm,'ROS_Best_ov'] = float(ros_row['Best'])#.values.astype(float)
			player_list.loc[nm,'ROS_Worst_ov'] = float(ros_row['Worst'])#.values.astype(float)
			player_list.loc[nm,'ROS_Std_ov'] = float(ros_row['Std Dev'])#.values.astype(float)
		else:
			player_list.loc[nm,'ROS_Avg_ov'] = num_po
			player_list.loc[nm,'ROS_Best_ov'] = num_po
			player_list.loc[nm,'ROS_Worst_ov'] = num_po
			player_list.loc[nm,'ROS_Std_ov'] = num_po

	#
	#
	#
	snap_count_urls = {'QB':"https://www.fantasypros.com/nfl/reports/snap-counts/qb.php",
				'RB': "https://www.fantasypros.com/nfl/reports/snap-counts/rb.php",
				'WR': "https://www.fantasypros.com/nfl/reports/snap-counts/wr.php",
				'TE': "https://www.fantasypros.com/nfl/reports/snap-counts/te.php"}

	snap_count_perc_urls = {'QB':"https://www.fantasypros.com/nfl/reports/snap-counts/qb.php?show=perc",
				'RB': "https://www.fantasypros.com/nfl/reports/snap-counts/rb.php?show=perc",
				'WR': "https://www.fantasypros.com/nfl/reports/snap-counts/wr.php?show=perc",
				'TE': "https://www.fantasypros.com/nfl/reports/snap-counts/te.php?show=perc"}

	snap_analysis_urls = {'QB':"https://www.fantasypros.com/nfl/reports/snap-count-analysis/qb.php?scoring=HALF",
				'RB': "https://www.fantasypros.com/nfl/reports/snap-count-analysis/rb.php?scoring=HALF",
				'WR': "https://www.fantasypros.com/nfl/reports/snap-count-analysis/wr.php?scoring=HALF",
				'TE': "https://www.fantasypros.com/nfl/reports/snap-count-analysis/te.php?scoring=HALF"}
	#
	### Name of player in "Player" column, snaps for week N in columns "N", total in "TTL", average in "AVG"
	snap_counts = dict()
	snap_count_perc = dict()
	for p in snap_count_urls:
		try:
			snap_counts[p] = pd.read_pickle('leagueinfo/'+ p + '.snc')
		except:
			download_info(scoring)
			snap_counts[p] = pd.read_pickle('leagueinfo/'+ p + '.snc')
		snap_counts[p].Player = snap_counts[p].Player.astype(str)
		names = array([nm[:nm.rfind('.')-1] if nm.rfind('.')!= -1 else nm[:nm.rfind(')')+1] for nm in snap_counts[p].loc[:,'Player']])
		snap_counts[p].index = [names[i] + ' - ' + snap_counts[p].loc[i,'Team'] for i in range(len(names))]
		snap_counts[p].drop('Player',axis = 1, inplace = True)

	for p in snap_count_perc_urls:
		try:
			snap_count_perc[p] = pd.read_pickle('leagueinfo/'+ p + '.snp')
		except:
			download_info(scoring)
			snap_count_perc[p] = pd.read_pickle('leagueinfo/'+ p + '.snp')
		snap_count_perc[p].Player = snap_count_perc[p].Player.astype(str)
		names = array([nm[:nm.rfind('.')-1] if nm.rfind('.')!= -1 else nm[:nm.rfind(')')+1] for nm in snap_count_perc[p].loc[:,'Player']])
		snap_count_perc[p].index = [names[i] + ' - ' + snap_count_perc[p].loc[i,'Team'] for i in range(len(names))]
		snap_count_perc[p].drop('Player',axis = 1, inplace = True)
	#

	snap_analysis = dict()
	for p in snap_analysis_urls:
		try:
			snap_analysis[p] = pd.read_pickle('leagueinfo/'+ p + '.sna')
		except:
			download_info(scoring)
			snap_analysis[p] = pd.read_pickle('leagueinfo/'+ p + '.sna')
		snap_analysis[p].Player = snap_analysis[p].Player.astype(str)
		names = [nm[:nm.find(' ',nm.find(' ')+1)] if nm.find(' ',nm.find(' ')+1) != -1 else nm for nm in snap_analysis[p].Player]
		snap_analysis[p].index = [names[i] + ' - ' + snap_analysis[p].loc[i,'Team'] for i in range(len(names))]
		snap_analysis[p].drop('Player',axis = 1, inplace = True)

	snap_analysis['FLEX'] = pd.concat([snap_analysis[p] for p in ['WR','RB','TE']])
	#
	targets_urls = {'RB': "https://www.fantasypros.com/nfl/reports/targets/rb.php",'WR': "https://www.fantasypros.com/nfl/reports/targets/wr.php",'TE': "https://www.fantasypros.com/nfl/reports/targets/te.php"}
	targets = dict()
	for p in targets_urls:

		try:
			targets[p] = pd.read_pickle('leagueinfo/'+ p + '.targets')
		except:
			download_info(scoring)
			targets[p] = pd.read_pickle('leagueinfo/'+ p + '.targets')

		targets[p].Player = targets[p].Player.astype(str)
		names = [nm[:nm.find(' ',nm.find(' ')+1)] if nm.find(' ',nm.find(' ')+1) != -1 else nm for nm in targets[p].Player]
		targets[p].index = [names[i] + ' - ' + targets[p].loc[i,'Team'] for i in range(len(names))]
		targets[p].drop('Player',axis = 1, inplace = True)

	targets['FLEX'] = pd.concat([targets[p] for p in ['WR','RB','TE']])

	for p in targets.keys():
		targets[p].drop_duplicates(inplace = True)

	try:
		kicker_stats = pd.read_pickle('leagueinfo/kicker.stats')
	except:
		download_info(scoring)
		kicker_stats = pd.read_pickle('leagueinfo/kicker.stats')

	kicker_names = [nm[:nm.find(' ',nm.find(' ')+1)] if nm.find(' ',nm.find(' ')+1) != -1 else nm for nm in kicker_stats.Player]
	kicker_teams = [tm[tm.find('(')+1:tm.find(')')] for tm in kicker_stats.Player]
	kicker_stats.index =  [kicker_names[i] + ' - ' + kicker_teams[i] for i in range(len(kicker_names))]
	kicker_stats['Player'] = kicker_teams
	kicker_stats.rename(columns = {'Player':'Team'}, inplace = True)

	try:
		defense_stats = pd.read_pickle('leagueinfo/dst.stats')
	except:
		download_info(scoring)
		defense_stats = pd.read_pickle('leagueinfo/dst.stats')

	defense_stats.index = [nm.split('(')[1].split(')')[0]+' - '+nm.split('(')[1].split(')')[0]for nm in defense_stats.loc[:,'Player']]




########################
	for p in positional:
		for ply in positional[p].index:
			pp = positional[p].loc[ply,'Pos.']#in case of flex!
			rkkk = min(int(positional[pp].loc[ply,'Avg']) -1,len(historical[pp][1]) - 1)
			rkkk2 = min(int(positional[pp].loc[ply,'ROS_Avg']) -1,len(historical[pp][1]) - 1)
			positional[p].loc[ply,'Wk_FP_Pred'] = historical[pp][1][rkkk]
			positional[p].loc[ply,'ROS_FP_Pred'] = historical[pp][1][rkkk2]
			if ply in matchups[pp].index:
				mtch = matchups[pp].loc[ply,str(week)]
				if mtch != 'nan':
					if mtch != 'BYE':
						if positional[p].loc[ply,'Opp'] != 'BYE/HURT':
							positional[p].loc[ply,'Weekly Matchup Rank'] = ''.join([d for d in mtch if d.isdigit()])
						else:
							positional[p].loc[ply,'Weekly Matchup Rank'] = 129
					else:
						positional[p].loc[ply,'Weekly Matchup Rank'] = 129
					rosmtch = matchups[pp].loc[ply,[str(i) for i in range(week,18)]]
					rosmtch_nums = [float(''.join([d for d in st if d.isdigit()])) for st in rosmtch if st != 'BYE']
					positional[p].loc[ply,'ROS Matchup Rank'] = mean(rosmtch_nums)
				else:
					positional[p].loc[ply,'Weekly Matchup Rank'] = 129
					positional[p].loc[ply,'ROS Matchup Rank'] = 129

			else:
				positional[p].loc[ply,'Weekly Matchup Rank'] = 129
				positional[p].loc[ply,'ROS Matchup Rank'] = 129
			if pp not in ['K','DST']:
				if ply in snap_analysis[pp].index:
					positional[p].loc[ply,'FP/G'] = snap_analysis[pp].loc[ply,'Fantasy Pts']/snap_analysis[pp].loc[ply,'Games']
					positional[p].loc[ply,'Snap %'] = snap_analysis[pp].loc[ply,'Snap %']/100
					positional[p].loc[ply,'Utility %'] = snap_analysis[pp].loc[ply,'Util %']/100
					positional[p].loc[ply,'Use %'] = positional[p].loc[ply,'Snap %']*positional[p].loc[ply,'Utility %']
					if p != 'QB':
						if ply in targets[pp].index:
							positional[p].loc[ply,'Avg Targets'] = targets[pp].loc[ply,'AVG']
							stscr_wk = positional[p].loc[ply,'FP/G']*positional[p].loc[ply,'Use %']*positional[p].loc[ply,'Avg Targets']*(((32-float(positional[p].loc[ply,'Weekly Matchup Rank']))/32)*(1/2)+(1/2))
							stscr_ros = positional[p].loc[ply,'FP/G']*positional[p].loc[ply,'Use %']*positional[p].loc[ply,'Avg Targets']*(((32-float(positional[p].loc[ply,'ROS Matchup Rank']))/32)*(1/2)+(1/2))
					else:
						stscr_wk = positional[p].loc[ply,'FP/G']*positional[p].loc[ply,'Use %']*(((32-float(positional[p].loc[ply,'Weekly Matchup Rank']))/32)*(1/2)+(1/2))
						stscr_ros = positional[p].loc[ply,'FP/G']*positional[p].loc[ply,'Use %']*(((32-float(positional[p].loc[ply,'ROS Matchup Rank']))/32)*(1/2)+(1/2))
					positional[p].loc[ply,'Weekly Stat Score'] = stscr_wk
					positional[p].loc[ply,'ROS Stat Score'] = stscr_ros
				else:
					positional[p].loc[ply,'Weekly Stat Score'] = 0
					positional[p].loc[ply,'ROS Stat Score'] = 0
			elif p == 'K':
				if ply in kicker_stats.index:
					positional[p].loc[ply,'FP/G'] = kicker_stats.loc[ply,'FPTS/G']
					positional[p].loc[ply,'FGA'] = kicker_stats.loc[ply,'FGA']
					positional[p].loc[ply,'PCT'] = kicker_stats.loc[ply,'PCT']/100
					stscr_wk = positional[p].loc[ply,'FP/G']*positional[p].loc[ply,'FGA']*positional[p].loc[ply,'PCT']*(((32-float(positional[p].loc[ply,'Weekly Matchup Rank']))/32)*(1/2)+(1/2))
					stscr_ros = positional[p].loc[ply,'FP/G']*positional[p].loc[ply,'FGA']*positional[p].loc[ply,'PCT']*(((32-float(positional[p].loc[ply,'ROS Matchup Rank']))/32)*(1/2)+(1/2))
					positional[p].loc[ply, 'Weekly Stat Score'] = stscr_wk
					positional[p].loc[ply, 'ROS Stat Score'] = stscr_ros
				else:
					positional[p].loc[ply,'Weekly Stat Score'] = 0
					positional[p].loc[ply,'ROS Stat Score'] = 0
			elif p == 'DST':
				if ply in defense_stats.index:
					positional[p].loc[ply,'FP/G'] = defense_stats.loc[ply,'FPTS/G']
					positional[p].loc[ply,'Turnovers'] = defense_stats.loc[ply,'INT'] + defense_stats.loc[ply,'FR']
					stscr_wk = (((32-float(positional[p].loc[ply,'Weekly Matchup Rank']))/32)*(1/2)+(1/2))*positional[p].loc[ply,'FP/G']
					stscr_ros = (((32-float(positional[p].loc[ply,'ROS Matchup Rank']))/32)*(1/2)+(1/2))*positional[p].loc[ply,'FP/G']
					positional[p].loc[ply, 'Weekly Stat Score'] = stscr_wk
					positional[p].loc[ply, 'ROS Stat Score'] = stscr_ros
				else:
					positional[p].loc[ply,'Weekly Stat Score'] = 0
					positional[p].loc[ply,'ROS Stat Score'] = 0

	posdatadists = {}
	for pp in ['QB','RB','WR','TE','K','DST']:
		posdatadists[pp] = np.load('leagueinfo/'+pp+'distribution.npy').astype(float)

	for p in positional:
		# posdist = np.load('leagueinfo/'+p+'.distribution')
		for ply in positional[p].index:
			pp = positional[p].loc[ply,'Pos.']#in case of flex!
			wkstmax = max(positional[pp].loc[:,'Weekly Stat Score'])
			rosstmax = max(positional[pp].loc[:,'ROS Stat Score'])
			qw = 0.8 - (week-1)*(0.6/16)
			# wk_scal = (positional[p].loc[ply,'Weekly Stat Score']/wkstmax)*(1-qw) + qw
			# ros_scal = (positional[p].loc[ply,'ROS Stat Score']/wkstmax)*(1-qw) + qw
			# positional[p].loc[ply,'Weekly Final'] = wk_scal*positional[p].loc[ply,'Wk_FP_Pred']
			# positional[p].loc[ply,'ROS Final'] = ros_scal*positional[p].loc[ply,'ROS_FP_Pred']

			wk_scal = 1 - (positional[p].loc[ply,'Weekly Stat Score']/wkstmax)*(1-qw)
			ros_scal = 1 - (positional[p].loc[ply,'ROS Stat Score']/wkstmax)*(1-qw)

			wk_rank,wk_score = estimate_score(positional[p].loc[ply,'Avg'],positional[p].loc[ply,'Std_Dev'],wk_scal,posdatadists[pp],len(positional[p]))
			ros_rank,ros_score = estimate_score(positional[p].loc[ply,'ROS_Avg'],positional[p].loc[ply,'ROS_Std'],ros_scal,posdatadists[pp],len(positional[p]))

			positional[p].loc[ply,'Weekly Final'] = wk_score
			positional[p].loc[ply,'ROS Final'] = ros_score

			positional[p].loc[ply,'Weekly Stat Scale'] = wk_scal
			positional[p].loc[ply,'ROS Stat Scale'] = ros_scal


			# positional[p].loc[ply,'Weekly Rank Est'] = wk_rank
			# positional[p].loc[ply,'ROS Rank Est'] = ros_rank


	#
	# #################### Rosters ##############################
	#
	#
	# raw_rosters = pd.read_html(league_URL)[1:]
	# teams = ['Ryan', 'Vince', 'Nathan', 'Nick', 'Arthur', 'Jim', 'Dylan', 'Connor', 'Lucas', 'Shayne']

	if site == "yahoo":
		rosters = make_rosters_from_yahoo(league_URL,positional,player_list,teams)
	elif site == "espn":
		rosters = make_rosters_from_espn(league_URL,yourswid,yourespn_s2,teams)


	# for ros in rosters:
	# 	print(rosters[ros])
	#
	taken_players = pd.DataFrame(columns = ['Pos.', 'Player', 'FTeam'])
	for tm in rosters:
		temp_ros = pd.DataFrame(rosters[tm])
		temp_ros['FTeam'] = [tm]*len(temp_ros)
		taken_players = pd.concat([taken_players, temp_ros],sort = True)

	taken_players = taken_players[taken_players.Player != '(Empty)']
	taken_players.index = taken_players.Player

	available_players = pd.DataFrame(player_list)
	for nm in taken_players.index:
		if nm in available_players.index:
			available_players.drop(nm, inplace = True)

	available_players.sort_values('ROS_Avg', inplace = True)

	available_positional = dict()
	for posi in positional:
		available_positional[posi] = pd.DataFrame(positional[posi])
		for nm in taken_players.index:
			if nm in available_positional[posi].index:
				available_positional[posi].drop(nm, inplace = True)
		available_positional[posi].sort_values('Avg', inplace = True)


	for nm in taken_players.index:
		if " Note " in nm:
			taken_players.drop(nm,inplace = True)



	return [player_list, positional, fant_pros,matchups, snap_analysis,targets, defense_stats,kicker_stats, taken_players, available_players, available_positional,rosters,historical]


# def nchooser(n,r):
#
# 	if n>=r:
#
# 		if n >0 and r >0:
# 			nfact = prod([n-i for i in range(n)])
# 			rfact = prod([r-i for i in range(r)])
# 			nmrfact = prod([n-r-i for i in range(n-r)])
# 			ch = nfact/(rfact*nmrfact)
# 		else:
# 			ch = 1
#
# 	else:
#
# 		ch =0
#
#
# 	return ch
#
# def choose_lineup(roster, positions):
# 	'''Roster should be a dataframe of players to consider
# 	with
# 	'Avg','Std_Dev','Stat Scale','Pos.'
# 	player scores are sampled with
# 	estimate_score(Avg,Std_Dev,Stat Scale,Pos.,numtrials =1000)
# 	'''
#
# 	###we need to enumerate the possible lineups
#
# 	n_QB = sum(roster.loc[:,'Pos.'] == 'QB')
# 	n_RB = sum(roster.loc[:,'Pos.'] == 'RB')
# 	n_WR = sum(roster.loc[:,'Pos.'] == 'WR')
# 	n_TE = sum(roster.loc[:,'Pos.'] == 'TE')
# 	n_DST = sum(roster.loc[:,'Pos.'] == 'DST')
# 	n_K = sum(roster.loc[:,'Pos.'] == 'K')
#
# 	total_rosters = nchooser(n_QB,positions['QB'])*nchooser(n_RB,positions['RB'])*nchooser(n_WR,positions['WR'])*nchooser(n_TE,positions['TE'])*nchooser(n_K,positions['K'])*nchooser(n_DST,positions['DST'])*nchooser(n_RB+n_WR+n_TE - (positions['RB']+positions['WR']+positions['TE']),positions['FLEX'])*nchooser(n_QB+n_RB+n_WR+n_TE - (positions['QB'] + positions['RB']+positions['WR']+positions['TE']),positions['SUPERFLEX'])
#
# 	if total_rosters == 0:
# 		print("Not enough players to fill roster.")
# 		return None
#
# 	qbs = [(nm,[]) for nm in roster[roster.loc[:,'Pos.'] == 'QB'].index]
# 	rbs = [(nm,[]) for nm in roster[roster.loc[:,'Pos.'] == 'RB'].index]
# 	wrs = [(nm,[]) for nm in roster[roster.loc[:,'Pos.'] == 'WR'].index]
# 	tes = [(nm,[]) for nm in roster[roster.loc[:,'Pos.'] == 'TE'].index]
# 	dsts = [(nm,[]) for nm in roster[roster.loc[:,'Pos.'] == 'DST'].index]
# 	ks = [(nm,[]) for nm in roster[roster.loc[:,'Pos.'] == 'K'].index]
#
# 	qba = np.linspace(0,total_rosters,n_QB + 1)
# 	qbb = [list(range(int(qba[i]),int(qba[i+1]))) for i in range(len(qba)-1)]
# 	for i in range(len(qbs)):
# 		gbs[i][1] += qbb[i]
#
#
#
#
#
#
# 	return None





##### Management functions
def this_week(available_positional,positional,rost,positions):
	'''Decide who to start/sit this week from a roster, and identify any potential available streamers'''
	pos = [ps for ps in positions.keys() if ps != 'BENCH']
	lineup = dict()
	streamers = dict()
	for p in [ps for ps in pos if ((ps != 'SUPERFLEX') and (ps != 'FLEX'))]:
		on_ros = pd.DataFrame(rost[rost.loc[:,'Pos'] == p])

		on_ros.index = on_ros.Player
		strm = pd.DataFrame(available_positional[p][available_positional[p].Opp != ''])
		# for ind in strm.index:
		# 	strm.loc[ind,'Pos.'] = strm.loc[ind,'Pos.']
		for ply in on_ros.index:
			# on_ros.loc[ply,'Pos.'] = p
			if ply in positional[p].index:
				on_ros.loc[ply,'Avg'] = positional[p].loc[ply,'Avg']
				on_ros.loc[ply,'FP_Pred'] = positional[p].loc[ply,'Wk_FP_Pred']
				on_ros.loc[ply,'Best'] = positional[p].loc[ply,'Best']
				on_ros.loc[ply,'Worst'] = positional[p].loc[ply,'Worst']
				on_ros.loc[ply,'Std_Dev'] = positional[p].loc[ply,'Std_Dev']
				on_ros.loc[ply,'Ceiling'] = on_ros.loc[ply,'Best']*positional[p].loc[ply,'Std_Dev']
				on_ros.loc[ply,'Info'] = positional[p].loc[ply,'Info']
				if positional[p].loc[ply,'Opp'] != '':
					on_ros.loc[ply,'Opp'] = positional[p].loc[ply,'Opp']
				else:
					on_ros.loc[ply,'Opp'] = 'BYE/HURT'
				on_ros.loc[ply,'Matchup Rank'] = positional[p].loc[ply, 'Weekly Matchup Rank']

			if p not in ['K','DST']:
				on_ros.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				on_ros.loc[ply,'Snap %'] = positional[p].loc[ply,'Snap %']
				on_ros.loc[ply,'Utility %'] = positional[p].loc[ply,'Utility %']
				on_ros.loc[ply,'Use %'] = positional[p].loc[ply,'Use %']
				if p != 'QB':
					on_ros.loc[ply,'Avg Targets'] = positional[p].loc[ply,'Avg Targets']
				on_ros.loc[ply,'Stat Scale'] = positional[p].loc[ply,'Weekly Stat Scale']

			elif p == 'K':
				on_ros.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				on_ros.loc[ply,'FGA'] = positional[p].loc[ply,'FGA']
				on_ros.loc[ply,'PCT'] = positional[p].loc[ply,'PCT']
				on_ros.loc[ply,'Stat Scale'] = positional[p].loc[ply,'Weekly Stat Scale']
			elif p == 'DST':
				on_ros.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				on_ros.loc[ply,'Turnovers'] = positional[p].loc[ply,'Turnovers']
				on_ros.loc[ply,'Stat Scale'] = positional[p].loc[ply,'Weekly Stat Scale']

		if len(on_ros) >0:
			for ply in on_ros.index:
				on_ros.loc[ply,'Final'] = positional[p].loc[ply,'Weekly Final']


			on_ros.sort_values('Final', inplace = True, ascending = False, axis=0)
		lineup[p] = on_ros.copy()
		#### streamers
		for ply in strm.index:
			if ply in positional[p].index:
				strm.loc[ply,'Avg'] = positional[p].loc[ply,'Avg']
				strm.loc[ply,'FP_Pred'] =positional[p].loc[ply,'Wk_FP_Pred']
				strm.loc[ply,'Best'] = positional[p].loc[ply,'Best']
				strm.loc[ply,'Worst'] = positional[p].loc[ply,'Worst']
				strm.loc[ply,'Std_Dev'] = positional[p].loc[ply,'Std_Dev']
				strm.loc[ply,'Ceiling'] = strm.loc[ply,'Best']*positional[p].loc[ply,'Std_Dev']
				strm.loc[ply,'Info'] = positional[p].loc[ply,'Info']
				strm.loc[ply,'Opp'] = positional[p].loc[ply,'Opp']
				strm.loc[ply,'Matchup Rank'] = positional[p].loc[ply, 'Weekly Matchup Rank']

			if p not in ['K','DST']:
				strm.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				strm.loc[ply,'Snap %'] = positional[p].loc[ply,'Snap %']
				strm.loc[ply,'Utility %'] = positional[p].loc[ply,'Utility %']
				strm.loc[ply,'Use %'] = positional[p].loc[ply,'Use %']
				if p != 'QB':
					strm.loc[ply,'Avg Targets'] = positional[p].loc[ply,'Avg Targets']
				strm.loc[ply,'Stat Scale'] = positional[p].loc[ply,'Weekly Stat Scale']


			elif p == 'K':
				strm.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				strm.loc[ply,'FGA'] = positional[p].loc[ply,'FGA']
				strm.loc[ply,'PCT'] = positional[p].loc[ply,'PCT']
				strm.loc[ply,'Stat Scale'] = positional[p].loc[ply,'Weekly Stat Scale']

			elif p == 'DST':
				strm.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				strm.loc[ply,'Turnovers'] = positional[p].loc[ply,'Turnovers']
				strm.loc[ply,'Stat Scale'] = positional[p].loc[ply,'Weekly Stat Scale']

		if len(strm) >0:
			for ply in strm.index:
				strm.loc[ply,'Final'] = positional[p].loc[ply,'Weekly Final']

		strm.sort_values('Final', inplace = True, ascending = False,axis=0)
		streamers[p] = strm.copy()

	# for lp in lineup.items():
	# 	print(lp[0],lp[1].columns)


	# realpos = [p for p in positions.keys() if (p != 'FLEX') and (p != 'SUPERFLEX') and (positions[p]) and (p != 'BENCH')]
	# roster_with_info = pd.concat([lineup[pos].loc[:,['Avg','Std_Dev','Stat Scale','Pos.']] for pos in realpos],sort = True)



	lineup['FLEX'] = pd.concat([lineup['RB'],lineup['WR'],lineup['TE']], sort = True)
	lineup['FLEX'].sort_values('Final',inplace = True)
	lineup['SUPERFLEX'] = pd.concat([lineup['FLEX'],lineup['QB']],sort = True)
	lineup['SUPERFLEX'].sort_values('Final',inplace = True)

	streamers['FLEX'] = pd.concat([streamers['RB'],streamers['WR'],streamers['TE']],sort = True)
	streamers['FLEX'].sort_values('Final',inplace = True)
	streamers['SUPERFLEX'] = pd.concat([streamers['FLEX'],streamers['QB']],sort = True)
	streamers['SUPERFLEX'].sort_values('Final',inplace = True)






	starters = pd.DataFrame(columns = lineup['QB'].columns)
	for p in [ps for ps in pos if positions[ps] > 0]:
		strpo = pd.DataFrame(lineup[p])
		for pl in strpo.index:
			if pl in starters.index:
				strpo.drop(pl, inplace = True)
		strpo.sort_values('Final', inplace = True, ascending = False,axis=0)
		strpo = strpo.iloc[:Roster[p]]
		starters = pd.concat([starters,strpo], sort = True)
	starters.drop('Player', axis = 1,inplace = True)
	starters.drop('Best',axis = 1,inplace = True)
	starters.drop('Worst', axis = 1,inplace = True)
	if 'Snap %' in starters.columns:
		starters.drop('Snap %', axis = 1,inplace = True)
		starters.drop('Utility %',axis = 1, inplace = True)
		starters = starters[['Pos','Opp','Matchup Rank','Final','Avg','Ceiling','Stat Scale','FP/G','Avg Targets','Use %']]
	else:
		starters = starters[['Pos','Opp','Matchup Rank','Final','Avg','Ceiling']]
	bench = pd.DataFrame(columns = lineup['QB'].columns)
	for p in [ps for ps in pos if "FLEX" not in ps]:
		bnpo = lineup[p].copy()
		for nm in starters.index:
			if nm in bnpo.index:
				bnpo.drop(nm,inplace = True)
		bench = pd.concat([bench, bnpo], sort = True)
	# bench.drop('FTeam',axis = 1,inplace = True)
	bench.drop('Player',axis = 1, inplace = True)
	bench.drop('Best',axis = 1,inplace = True)
	bench.drop('Worst',axis = 1, inplace = True)
	if 'Snap %' in bench.columns:
		bench.drop('Snap %', axis = 1,inplace = True)
		bench.drop('Utility %',axis = 1, inplace = True)
		bench = bench[['Pos','Opp','Matchup Rank','Final','Avg','Ceiling','Stat Scale','FP/G','Avg Targets','Use %']]
	else:
		bench = bench[['Pos','Opp','Matchup Rank','Final','Avg','Ceiling']]

	for p in pos:

		streamers[p].drop('ROS_Avg', axis =1 ,inplace = True)
		streamers[p].drop('ROS_Best', axis =1 ,inplace = True)
		streamers[p].drop('ROS_Worst', axis =1 ,inplace = True)
		streamers[p].drop('ROS_Std', axis =1 ,inplace = True)
		if 'Snap %' in streamers[p].columns:
			streamers[p].drop('Snap %', axis =1 ,inplace = True)
			streamers[p].drop('Utility %', axis =1 ,inplace = True)

	strmdict = {}
	lineup = dict([(lp,lineup[lp]) for lp in lineup.keys() if len(lineup[lp]) >0])
	streamers = dict([(lp,streamers[lp]) for lp in streamers.keys() if lp in lineup.keys()])
	for p in streamers.keys():
			min_sc = min(lineup[p].loc[:,'Final'])
			strmdict[p] = streamers[p][streamers[p].loc[:,'Final']>min_sc].sort_values('Final', ascending = False)
	return[starters, bench, strmdict, lineup, streamers]

def rest_of_schedule(available_positional,positional,rost,positions):
	'''A look at the ROS'''
	pos = [ps for ps in positions.keys() if ps != 'BENCH']
	lineup = dict()
	streamers = dict()
	for p in [ps for ps in pos if ((ps != 'SUPERFLEX') and (ps != 'FLEX'))]:
		on_ros = pd.DataFrame(rost[rost.loc[:,'Pos'] == p])

		on_ros.index = on_ros.Player
		strm = pd.DataFrame(index = available_positional[p][available_positional[p].Opp != ''].index)
		# for ind in strm.index:
		# 	strm.loc[ind,'Pos.'] = strm.loc[ind,'Pos.']

		for ply in on_ros.index:
			if ply in positional[p].index:
				on_ros.loc[ply,'Avg'] = positional[p].loc[ply,'ROS_Avg']
				on_ros.loc[ply,'FP_Pred'] = positional[p].loc[ply,'ROS_FP_Pred']
				on_ros.loc[ply,'Best'] = positional[p].loc[ply,'ROS_Best']
				on_ros.loc[ply,'Worst'] = positional[p].loc[ply,'ROS_Worst']
				on_ros.loc[ply,'Std_Dev'] = positional[p].loc[ply,'ROS_Std']
				on_ros.loc[ply,'Ceiling'] = on_ros.loc[ply,'Best']*positional[p].loc[ply,'ROS_Std']
				on_ros.loc[ply,'Info'] = positional[p].loc[ply,'Info']
				on_ros.loc[ply,'Matchup Rank'] = positional[p].loc[ply, 'ROS Matchup Rank']

			if p not in ['K','DST']:
				on_ros.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				on_ros.loc[ply,'Snap %'] = positional[p].loc[ply,'Snap %']
				on_ros.loc[ply,'Utility %'] = positional[p].loc[ply,'Utility %']
				on_ros.loc[ply,'Use %'] = positional[p].loc[ply,'Use %']
				if p != 'QB':
					on_ros.loc[ply,'Avg Targets'] = positional[p].loc[ply,'Avg Targets']
				on_ros.loc[ply,'Stat Scale'] = positional[p].loc[ply,'ROS Stat Scale']

			elif p == 'K':
				on_ros.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				on_ros.loc[ply,'FGA'] = positional[p].loc[ply,'FGA']
				on_ros.loc[ply,'PCT'] = positional[p].loc[ply,'PCT']
				on_ros.loc[ply,'Stat Scale'] = positional[p].loc[ply,'ROS Stat Scale']
			elif p == 'DST':
				on_ros.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				on_ros.loc[ply,'Turnovers'] = positional[p].loc[ply,'Turnovers']
				on_ros.loc[ply,'Stat Scale'] = positional[p].loc[ply,'ROS Stat Scale']

		if len(on_ros) >0:
			for ply in on_ros.index:
				on_ros.loc[ply,'Final'] = positional[p].loc[ply,'ROS Final']


			on_ros.sort_values('Final', inplace = True, ascending = False, axis=0)
		lineup[p] = on_ros.copy()
		#### streamers
		for ply in strm.index:
			if ply in positional[p].index:
				strm.loc[ply,'Avg'] = positional[p].loc[ply,'ROS_Avg']
				strm.loc[ply,'FP_Pred'] =positional[p].loc[ply,'ROS_FP_Pred']
				strm.loc[ply,'Best'] = positional[p].loc[ply,'ROS_Best']
				strm.loc[ply,'Worst'] = positional[p].loc[ply,'ROS_Worst']
				strm.loc[ply,'Std_Dev'] = positional[p].loc[ply,'ROS_Std']
				strm.loc[ply,'Ceiling'] = strm.loc[ply,'Best']*positional[p].loc[ply,'ROS_Std']
				strm.loc[ply,'Info'] = positional[p].loc[ply,'Info']
				strm.loc[ply,'Matchup Rank'] = positional[p].loc[ply, 'ROS Matchup Rank']

			if p not in ['K','DST']:
				strm.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				strm.loc[ply,'Snap %'] = positional[p].loc[ply,'Snap %']
				strm.loc[ply,'Utility %'] = positional[p].loc[ply,'Utility %']
				strm.loc[ply,'Use %'] = positional[p].loc[ply,'Use %']
				if p != 'QB':
					strm.loc[ply,'Avg Targets'] = positional[p].loc[ply,'Avg Targets']
				strm.loc[ply,'Stat Scale'] = positional[p].loc[ply,'ROS Stat Scale']


			elif p == 'K':
				strm.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				strm.loc[ply,'FGA'] = positional[p].loc[ply,'FGA']
				strm.loc[ply,'PCT'] = positional[p].loc[ply,'PCT']
				strm.loc[ply,'Stat Scale'] = positional[p].loc[ply,'ROS Stat Scale']

			elif p == 'DST':
				strm.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
				strm.loc[ply,'Turnovers'] = positional[p].loc[ply,'Turnovers']
				strm.loc[ply,'Stat Scale'] = positional[p].loc[ply,'ROS Stat Scale']

		if len(strm) >0:
			for ply in strm.index:
				strm.loc[ply,'Final'] = positional[p].loc[ply,'ROS Final']

		strm.sort_values('Final', inplace = True, ascending = False,axis=0)
		streamers[p] = strm.copy()

	# for lp in lineup.items():
	# 	print(lp[0],lp[1].columns)


	# realpos = [p for p in positions.keys() if (p != 'FLEX') and (p != 'SUPERFLEX') and (positions[p]) and (p != 'BENCH')]
	# roster_with_info = pd.concat([lineup[pos].loc[:,['Avg','Std_Dev','Stat Scale','Pos.']] for pos in realpos],sort = True)



	lineup['FLEX'] = pd.concat([lineup['RB'],lineup['WR'],lineup['TE']], sort = True)
	lineup['FLEX'].sort_values('Final',inplace = True, ascending = False)
	lineup['SUPERFLEX'] = pd.concat([lineup['FLEX'],lineup['QB']],sort = True)
	lineup['SUPERFLEX'].sort_values('Final',inplace = True, ascending = False)

	streamers['FLEX'] = pd.concat([streamers['RB'],streamers['WR'],streamers['TE']],sort = True)
	streamers['FLEX'].sort_values('Final',inplace = True, ascending = False)
	streamers['SUPERFLEX'] = pd.concat([streamers['FLEX'],streamers['QB']],sort = True)
	streamers['SUPERFLEX'].sort_values('Final',inplace = True, ascending = False)


	strmdict = {}
	lineup = dict([(lp,lineup[lp]) for lp in lineup.keys() if len(lineup[lp]) >0])
	streamers = dict([(lp,streamers[lp]) for lp in streamers.keys() if lp in lineup.keys()])
	for p in streamers.keys():
			min_sc = min(lineup[p].loc[:,'Final'])
			strmdict[p] = streamers[p][streamers[p].loc[:,'Final']>min_sc].sort_values('Final', ascending = False)
	return[lineup, streamers, strmdict]




	#
	#
	#
	# pos = [ps for ps in positions.keys() if ps != 'BENCH']
	# lineup = dict()
	# streamers = dict()
	# for p in [ps for ps in pos if ((ps != 'SUPERFLEX') and (ps != 'FLEX'))]:
	# 	on_ros = pd.DataFrame(rost[rost.Pos == p])
	#
	# 	on_ros.index = on_ros.Player
	# 	strm = pd.DataFrame(available_positional[p][available_positional[p].Opp != ''])
	# 	for ind in strm.index:
	# 		strm.loc[ind,'Pos.'] = strm.loc[ind,'Pos.']
	# 	for ply in on_ros.index:
	# 		if ply in positional[p].index:
	# 			on_ros.loc[ply,'Avg'] = positional[p].loc[ply,'Avg']
	# 			on_ros.loc[ply,'FP_Pred'] = positional[p].loc[ply,'ROS_FP_Pred']
	# 			on_ros.loc[ply,'Best'] = positional[p].loc[ply,'Best']
	# 			on_ros.loc[ply,'Worst'] = positional[p].loc[ply,'Worst']
	# 			on_ros.loc[ply,'Ceiling'] = on_ros.loc[ply,'Best']*positional[p].loc[ply,'Std_Dev']
	# 			on_ros.loc[ply,'Info'] = positional[p].loc[ply,'Info']
	# 			if positional[p].loc[ply,'Opp'] != '':
	# 				on_ros.loc[ply,'Opp'] = positional[p].loc[ply,'Opp']
	# 			else:
	# 				on_ros.loc[ply,'Opp'] = 'BYE/HURT'
	# 			on_ros.loc[ply,'Matchup Rank'] = positional[p].loc[ply, 'ROS Matchup Rank']
	#
	# 		if p not in ['K','DST']:
	# 			on_ros.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
	# 			on_ros.loc[ply,'Snap %'] = positional[p].loc[ply,'Snap %']
	# 			on_ros.loc[ply,'Utility %'] = positional[p].loc[ply,'Utility %']
	# 			on_ros.loc[ply,'Use %'] = positional[p].loc[ply,'Use %']
	# 			if p != 'QB':
	# 				on_ros.loc[ply,'Avg Targets'] = positional[p].loc[ply,'Avg Targets']
	# 			on_ros.loc[ply,'Stat Score'] = positional[p].loc[ply,'ROS Stat Score']
	#
	#
	# 		elif p == 'K':
	# 			on_ros.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
	# 			on_ros.loc[ply,'FGA'] = positional[p].loc[ply,'FGA']
	# 			on_ros.loc[ply,'PCT'] = positional[p].loc[ply,'PCT']
	# 			on_ros.loc[ply, 'Stat Score'] = positional[p].loc[ply,'ROS Stat Score']
	#
	# 		elif p == 'DST':
	# 			on_ros.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
	# 			on_ros.loc[ply,'Turnovers'] = positional[p].loc[ply,'Turnovers']
	# 			on_ros.loc[ply,'Stat Score'] = positional[p].loc[ply,'ROS Stat Score']
	#
	# 	if len(on_ros) >0:
	# 		for ply in on_ros.index:
	# 			on_ros.loc[ply,'Final'] = positional[p].loc[ply,'ROS Final']
	#
	#
	# 		on_ros.sort_values('Final', inplace = True, ascending = False, axis=0)
	# 	lineup[p] = on_ros.copy()
	# 	#### streamers
	# 	for ply in strm.index:
	# 		pp = strm.loc[ply,'Pos.'] #in case we are in the flex position
	# 		if ply in positional[p].index:
	# 			strm.loc[ply,'Avg'] = positional[p].loc[ply,'Avg']
	# 			strm.loc[ply,'FP_Pred'] = positional[p].loc[ply,'ROS_FP_Pred']
	# 			strm.loc[ply,'Best'] = positional[p].loc[ply,'Best']
	# 			strm.loc[ply,'Worst'] = positional[p].loc[ply,'Worst']
	# 			strm.loc[ply,'Ceiling'] = strm.loc[ply,'Best']*positional[p].loc[ply,'Std_Dev']
	# 			strm.loc[ply,'Info'] = positional[p].loc[ply,'Info']
	# 			strm.loc[ply,'Opp'] = positional[p].loc[ply,'Opp']
	# 			strm.loc[ply,'Matchup Rank'] = positional[p].loc[ply, 'ROS Matchup Rank']
	#
	# 		if p not in ['K','DST']:
	# 			strm.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
	# 			strm.loc[ply,'Snap %'] = positional[p].loc[ply,'Snap %']
	# 			strm.loc[ply,'Utility %'] = positional[p].loc[ply,'Utility %']
	# 			strm.loc[ply,'Use %'] = positional[p].loc[ply,'Use %']
	# 			if p != 'QB':
	# 				strm.loc[ply,'Avg Targets'] = positional[p].loc[ply,'Avg Targets']
	# 			strm.loc[ply,'Stat Score'] = positional[p].loc[ply,'ROS Stat Score']
	#
	#
	# 		elif p == 'K':
	# 			strm.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
	# 			strm.loc[ply,'FGA'] = positional[p].loc[ply,'FGA']
	# 			strm.loc[ply,'PCT'] = positional[p].loc[ply,'PCT']
	# 			strm.loc[ply, 'Stat Score'] = positional[p].loc[ply,'ROS Stat Score']
	#
	# 		elif p == 'DST':
	# 			strm.loc[ply,'FP/G'] = positional[p].loc[ply,'FP/G']
	# 			strm.loc[ply,'Turnovers'] = positional[p].loc[ply,'Turnovers']
	# 			strm.loc[ply,'Stat Score'] = positional[p].loc[ply,'ROS Stat Score']
	#
	# 	if len(strm) >0:
	# 		for ply in strm.index:
	# 			strm.loc[ply,'Final'] = positional[p].loc[ply,'ROS Final']
	#
	# 	strm.sort_values('Final', inplace = True, ascending = False,axis=0)
	# 	streamers[p] = strm
	#
	# lineup['FLEX'] = pd.concat([lineup['RB'],lineup['WR'],lineup['TE']], sort = True)
	# lineup['FLEX'].sort_values('Final',inplace = True)
	# lineup['SUPERFLEX'] = pd.concat([lineup['FLEX'],lineup['QB']],sort = True)
	# lineup['SUPERFLEX'].sort_values('Final',inplace = True)
	#
	# streamers['FLEX'] = pd.concat([streamers['RB'],streamers['WR'],streamers['TE']],sort = True)
	# streamers['FLEX'].sort_values('Final',inplace = True)
	# streamers['SUPERFLEX'] = pd.concat([streamers['FLEX'],streamers['QB']],sort = True)
	# streamers['SUPERFLEX'].sort_values('Final',inplace = True)
	#
	# strmdict = {}
	# lineup = dict([(lp,lineup[lp]) for lp in lineup.keys() if len(lineup[lp]) >0])
	# streamers = dict([(lp,streamers[lp]) for lp in streamers.keys() if lp in lineup.keys()])
	# for p in streamers.keys():
	# 		min_sc = min(lineup[p].loc[:,'Final'])
	# 		strmdict[p] = streamers[p][streamers[p].loc[:,'Final']>min_sc].sort_values('Final', ascending = False)
	#
	# return[lineup, streamers, strmdict]



def team_score(available_positional,positional,roster,positions, add = [], drop = []):
	'''Score the team by player rank weighted by starting'''
	# weekly_team =  this_week(available_positional,positional,roster,positions)
	# ros_team = rest_of_schedule(available_positional,positional,roster,positions)
	#
	#
	# week_starters = weekly_team[0]
	# week_score = sum(week_starters.loc[:,'Final'])
	return None





def tradeit(team1, players1, team2, players2):
	score1 = team_score(tm = team1, give = players1, get = players2)
	score2 = team_score(tm = team2, give = players2, get = players1)
	return [(score1[1] - score1[0])/score1[0], (score2[1] - score2[0])/score2[0]]





def GetHistory(pos):
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

	historical_stats = {}

	for yr,url in urls.items():
		historical_stats[yr] = pd.concat([pd.read_html(url+'&cur_page='+str(p))[7] for p in range(5)])
		cols = ['Player'] + list(historical_stats[yr].iloc[1][1:].values)
		historical_stats[yr].drop([0,1],inplace = True)
		historical_stats[yr].columns = cols
		ranknms = [(int(nm.split('.')[0]),nm.split('.')[1][1:]) for nm in historical_stats[yr].iloc[:,0]]
		historical_stats[yr].loc[:,'Player'] = [rn[1] for rn in ranknms]
		historical_stats[yr].index = [rn[0] for rn in ranknms]

	tot_by_rk = []
	for his in historical_stats.values():
	    if len(his) > len(tot_by_rk):
	        tot_by_rk = tot_by_rk + [0]*(len(his)-len(tot_by_rk))
	    for i in his.index:
	        tot_by_rk[i-1] += float(his.loc[i,'FPts/G'])#/float(his.loc[1,'FPts/G'])

	avg_by_rank = np.array(tot_by_rk)/len(historical_stats)

	return historical_stats, avg_by_rank


def GetHistoryFromUSB(pos):
	years= list(range(2001,2019))

	historical_stats = {}

	for yr in years:
		historical_stats[yr] = pd.read_pickle('playerdata/YearlyFFballHistory/' + pos + '/' + str(yr))

	tot_by_rk = []
	for his in historical_stats.values():
	    if len(his) > len(tot_by_rk):
	        tot_by_rk = tot_by_rk + [0]*(len(his)-len(tot_by_rk))
	    for i in his.index:
	        tot_by_rk[i-1] += float(his.loc[i,'FPts/G'])#/float(his.loc[1,'FPts/G'])

	avg_by_rank = np.array(tot_by_rk)/len(historical_stats)

	return historical_stats, avg_by_rank


def save_histpoints(pos):
	posdat = []
	for yr in [str(y) for y in range(2001,2018)]:
	    for wk in [str(w) for w in range(1,17)]:
	        dat = pd.read_pickle('playerdata/WeeklyFFballHistory/'+pos+'/'+yr+'/'+wk)
	        for ind in dat.index:
	            if len(posdat) >= ind:
	                posdat[ind-1] += [dat.loc[ind,'FPts']]
	            else:
	                posdat += [[dat.loc[ind,'FPts']]]
	mxlen = max([len(dat) for dat in posdat])
	for ind in range(len(posdat)):
		if len(posdat[ind]) < mxlen:
			numneed = mxlen - len(posdat[ind])
			# print(posdat[ind])
			posdat[ind] += [mean(np.array(posdat[ind]).astype(float))]*numneed

	posdat = np.array(posdat)
	np.save('leagueinfo/'+pos+'distribution',posdat)


####### Data Frames Created #######
# Description - name - index - columns
#full player list - player_list - player name - Team Pos Depth Notes ROS_Avg ROS_Best ROS_Std TOS_Notes
#list of (position) [dictionary] - positional['position'] - same as above - same as above
#expert consensus rankings (weekly) from fantasy pros [dictionary] - fant_pros['position'] - int - Rank Name Opp Best Worst Avg Std Dev Notes
#list of matchups [dictionary] - matchups['position'] - player name - ECR 1 2 3 ... 17 (week numbers)
#rest of schedule rankings from fantasy pros [dictionary] - ros_rks['position'] - player name - Rank Name Bye Best Worst Avg Std Dev ADP vs ADP
#various stat dataframes - targets, snaps, etc

#fantasy rosters [dictionary] - rosters['Person'] (example rosters['']) - int - Pos Player FTeam
#players taken - taken_players - player name - Pos Player Fteam
#players available - available_players - player name - Team Pos Depth Notes ROS_Avg ROS_Best ROS_Worst ROS_Std ROS_Notes
#available by position [dictionary] - available_postional['position'] - player name - Team Pos Depth Notes FP_Notes Avg Best Worst Std_Dev Opp ROS_Avg ROS_Best ROS_Worst ROS_Std ROS_Notes
#player info (rest of season) [dictionary] - ros['position'] - player name - Team Pos Depth Notes ROS_Avg ROS_Best ROS_Worst ROS_Std ROS_Notes AvgSnaps Snap% Utility% FantPoints/Game Fant_Team
