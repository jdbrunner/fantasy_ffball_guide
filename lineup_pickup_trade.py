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

# Display size
pd.set_option('display.max_colwidth', 200)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)

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

########################### Add Expert Rankings ######################################
def initialize_league(scoring):

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



	fant_pros = {}
	positional = {}
	#add rankings
	for p in fp_urls:
		# print(p,fp_urls[p])
		# num_p = len(positional[p])
		fant_pros[p] = pd.read_html(fp_urls[p])[0]
		# fant_pros[p].drop(0,inplace = True)
		fant_pros[p].drop('WSIS', axis = 1, inplace = True)
		fant_pros[p].rename(columns = {fant_pros[p].columns[1]:'Name',fant_pros[p].columns[0]:'Rank'}, inplace = True)#
		fant_pros[p].drop([col for col in fant_pros[p].columns if "Unnamed" in col], axis = 1, inplace = True)
		#
		# fant_pros[p].drop(columns = [col for col in fant_pros[p].columns if 'Unnamed' in col], inplace = True)
		fant_pros[p].dropna(inplace = True)
		fant_pros[p].drop(index = [indd for indd in fant_pros[p].index if 'google' in fant_pros[p].loc[indd,'Opp']], inplace = True)
		#
		player_names_fmted = [(ind,fant_pros[p].Name.loc[ind].split(' ')[0] + ' ' + fant_pros[p].Name.loc[ind].split(' ')[-2],fant_pros[p].Name.loc[ind].split(' ')[-1]) for ind in fant_pros[p].index if '(' not in fant_pros[p].Name.loc[ind].split(' ')[-2]] + [(ind,fant_pros[p].Name.loc[ind].split('(')[1].split(')')[0],fant_pros[p].Name.loc[ind].split('(')[1].split(')')[0]) for ind in fant_pros[p].index if '(' in fant_pros[p].Name.loc[ind]]


		fant_pros[p].loc[:,"FixedName"] = [pl[1] for pl in player_names_fmted]
		fant_pros[p].loc[:,"Team"]=[pl[2] for pl in player_names_fmted]

		positional[p] = pd.DataFrame(index = [pl[1]+" - " + pl[2] for pl in player_names_fmted])
		fant_pros[p].index = [pl[1]+" - " + pl[2] for pl in player_names_fmted]


		#
		# fant_pros[p].loc[invert([isinstance(n,str) for n in fant_pros[p].Notes]),'Notes'] = [''] * len(fant_pros[p].loc[invert([isinstance(n,str) for n in fant_pros[p].Notes]),'Notes'])
		# longest_note = max([len(note) for note in fant_pros[p].Notes[invert([isnan(ente) for ente in fant_pros[p].Notes.str.contains('')])]])
		# positional[p]['FP_Notes'] = [' '*longest_note]*num_p
		for ply in positional[p].index:
			fp_row = fant_pros[p].loc[ply]
			if len(fp_row)>0:
				positional[p].loc[ply,'Name'] = fp_row['FixedName']
				positional[p].loc[ply,'Team'] = fp_row['Team']
				positional[p].loc[ply,'Pos.'] = p
				positional[p].loc[ply,'Avg'] = float(fp_row['Avg'])#.astype(float)
				positional[p].loc[ply,'Best'] = float(fp_row['Best'])#.astype(float)
				positional[p].loc[ply,'Worst'] = float(fp_row['Worst'])#.astype(float)
				positional[p].loc[ply,'Std_Dev'] = float(fp_row['Std Dev'])#.astype(float)
				positional[p].loc[ply,'Opp'] = fp_row['Opp']
				if p != "DST":
					positional[p].loc[ply,'Info'] = "http://www.google.com/search?q="+"+".join(ply.lower().split(" "))+"+fantasy"
				else:
					positional[p].loc[ply,'Info'] = "http://www.google.com/search?q="+ply+"+defense+fantasy"



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
		matchups[p] = pd.read_html(match_urls[p])[0]
		for i in matchups[p]:
			matchups[p].loc[:,i] = matchups[p].loc[:,i].astype(str)
		matchups[p].Player = matchups[p].Player.astype(str)
		if p != 'DST':
			names = [nm.split(' ')[0] + ' '+nm.split(' ')[1] + ' - '+nm.split(' ')[-1] for nm in matchups[p].Player]
		else:
			names =  [dst_teams[nm] for nm in matchups[p].Player]
		matchups[p].index = names
		matchups[p].drop('Player',axis = 1, inplace = True)

	matchups['FLEX'] = pd.concat([matchups[p] for p in ['WR','RB','TE']])


	ros_urls = {'QB':"https://www.fantasypros.com/nfl/rankings/ros-qb.php",'RB': "https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"rb.php",'WR': "https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"wr.php",'TE': "https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"te.php",'FLEX':"https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"flex.php",'DST': "https://www.fantasypros.com/nfl/rankings/ros-dst.php",'K':"https://www.fantasypros.com/nfl/rankings/ros-k.php"}
	#
	ros_rks = {}

	for p in ros_urls:
		ros_temp = pd.read_html(ros_urls[p])[0]
		if len(ros_temp) >1:
			ros_rks[p] = ros_temp
			num_po = len(ros_rks[p])
			ros_rks[p].drop(ros_rks[p].columns[1],axis = 1, inplace = True)
			ros_rks[p].rename(columns = {ros_rks[p].columns[1]:'Name',ros_rks[p].columns[0]:'Rank'}, inplace = True)
			ros_rks[p].Name = ros_rks[p].Name.astype(str)
			ros_rks[p] = ros_rks[p][invert(ros_rks[p].Name == 'nan')]
			if p != 'DST':
				names = [nm.split(' ')[0] + ' '+nm.split(' ')[1][:-2] + ' - '+nm.split(' ')[-1] for nm in ros_rks[p].loc[:,'Name']]
			else:
				names = [nm.split(')')[1].split(' ')[0] for nm in ros_rks[p].loc[:,'Name']]
			ros_rks[p].index = names
			ros_rks[p].drop('Name', axis = 1, inplace = True)
			for nm in positional[p].index:
				if nm in ros_rks[p].index:
					ros_row = ros_rks[p].loc[nm]
					positional[p].loc[nm,'ROS_Avg'] = float(ros_row['Avg'])#.values.astype(float)
					positional[p].loc[nm,'ROS_Best'] = float(ros_row['Best'])#.values.astype(float)
					positional[p].loc[nm,'ROS_Worst'] = float(ros_row['Worst'])#.values.astype(float)
					positional[p].loc[nm,'ROS_Std'] = float(ros_row['Std Dev'])#.values.astype(float)
				else:
					positional[p].loc[nm,'ROS_Avg'] = num_po
					positional[p].loc[nm,'ROS_Best'] = num_po
					positional[p].loc[nm,'ROS_Worst'] = num_po
					positional[p].loc[nm,'ROS_Std'] = num_po


	player_list = pd.concat([positional[p] for p in positional.keys() if p != "FLEX"])


	ros_overall = pd.read_html("https://www.fantasypros.com/nfl/rankings/ros-"+url_1+"overall.php")[0]
	ros_overall.drop(ros_overall.columns[1],axis=1,inplace = True)
	ros_overall.rename(columns = {ros_overall.columns[1]:'Name',ros_overall.columns[0]:'Rank'}, inplace = True)
	ros_overall = ros_overall[invert([isnan(nm) for nm in ros_overall.Name.str.contains('')])]

	names = array([nm.split(' ')[0] + ' '+nm.split(' ')[1][:-2] + ' - '+nm.split(' ')[-1] for nm in ros_overall.loc[:,'Name']])
	defs = array(ros_overall[ros_overall.Pos.str.contains('DST')].index)
	names[defs] = [nm.split(')')[1].split(' ')[0] for nm in ros_overall.loc[defs,'Name']]
	# tms =[nm[nm.rfind(' ')+1:] if nm.rfind(' ') != -1 else nm for nm in ros_overall[ros_overall.Pos.str.contains('DST')].Name]
	# names[defs -1] = tms

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
		snap_counts[p] = pd.read_html(snap_count_urls[p])[0]
		snap_counts[p].Player = snap_counts[p].Player.astype(str)
		names = array([nm[:nm.rfind('.')-1] if nm.rfind('.')!= -1 else nm[:nm.rfind(')')+1] for nm in snap_counts[p].loc[:,'Player']])
		# names = array([nm.split(' ')[0] + ' '+nm.split(' ')[1][:-2] + ' - '+nm.split(' ')[-1] for nm in snap_counts[p].loc[:,'Player']])
		snap_counts[p].index = [names[i] + ' - ' + snap_counts[p].loc[i,'Team'] for i in range(len(names))]
		snap_counts[p].drop('Player',axis = 1, inplace = True)

	for p in snap_count_perc_urls:
		snap_count_perc[p] = pd.read_html(snap_count_perc_urls[p])[0]
		snap_count_perc[p].Player = snap_count_perc[p].Player.astype(str)
		names = array([nm[:nm.rfind('.')-1] if nm.rfind('.')!= -1 else nm[:nm.rfind(')')+1] for nm in snap_count_perc[p].loc[:,'Player']])
		# names = array([nm.split(' ')[0] + ' '+nm.split(' ')[1][:-2] + ' - '+nm.split(' ')[-1] for nm in snap_count_perc[p].loc[:,'Player']])
		snap_count_perc[p].index = [names[i] + ' - ' + snap_count_perc[p].loc[i,'Team'] for i in range(len(names))]
		snap_count_perc[p].drop('Player',axis = 1, inplace = True)
	#
	### Columns are: ['Player', 'Team', 'Games', 'Snaps', 'Snaps/Gm', 'Snap %', 'Rush %',
	##							'Tgt %', 'Touch %', 'Util %', 'Fantasy Pts', 'Pts/100 Snaps']
	# Util % is "% of snaps the player touched the ball or was targeted, includes pass attempts, rush attempts, and receptions"
	snap_analysis = dict()
	for p in snap_analysis_urls:
		snap_analysis[p] = pd.read_html(snap_analysis_urls[p])[0]
		snap_analysis[p].Player = snap_analysis[p].Player.astype(str)
		names = [nm[:nm.find(' ',nm.find(' ')+1)] if nm.find(' ',nm.find(' ')+1) != -1 else nm for nm in snap_analysis[p].Player]
		# names = [nm.split(' ')[0] + ' '+nm.split(' ')[1][:-2] + ' - '+nm.split(' ')[-1] for nm in snap_analysis[p].loc[:,'Player']]
		snap_analysis[p].index = [names[i] + ' - ' + snap_analysis[p].loc[i,'Team'] for i in range(len(names))]
		snap_analysis[p].drop('Player',axis = 1, inplace = True)

	snap_analysis['FLEX'] = pd.concat([snap_analysis[p] for p in ['WR','RB','TE']])
	#
	targets_urls = {'RB': "https://www.fantasypros.com/nfl/reports/targets/rb.php",'WR': "https://www.fantasypros.com/nfl/reports/targets/wr.php",'TE': "https://www.fantasypros.com/nfl/reports/targets/te.php"}
	### Name of player in "Player" column, targets for week N in columns "N", total in "TTL", average in "AVG"
	targets = dict()
	for p in targets_urls:
		targets[p] = pd.read_html(targets_urls[p])[0]
		targets[p].Player = targets[p].Player.astype(str)
		names = [nm[:nm.find(' ',nm.find(' ')+1)] if nm.find(' ',nm.find(' ')+1) != -1 else nm for nm in targets[p].Player]
		# names = [nm.split(' ')[0] + ' '+nm.split(' ')[1][:-2] + ' - '+nm.split(' ')[-1] for nm in targets[p].loc[:,'Player']]
		targets[p].index = [names[i] + ' - ' + targets[p].loc[i,'Team'] for i in range(len(names))]
		targets[p].drop('Player',axis = 1, inplace = True)

	targets['FLEX'] = pd.concat([targets[p] for p in ['WR','RB','TE']])

	for p in targets.keys():
		targets[p].drop_duplicates(inplace = True)

	kicker_stats = pd.read_html("https://www.fantasypros.com/nfl/stats/k.php")[0]
	kicker_names = [nm[:nm.find(' ',nm.find(' ')+1)] if nm.find(' ',nm.find(' ')+1) != -1 else nm for nm in kicker_stats.Player]
	# kicker_names = [nm.split(' ')[0] + ' '+nm.split(' ')[1][:-2] + ' - '+nm.split(' ')[-1] for nm in kicker_stats.loc[:,'Player']]
	# print(kicker_stats)
	kicker_teams = [tm[tm.find('(')+1:tm.find(')')] for tm in kicker_stats.Player]
	kicker_stats.index =  [kicker_names[i] + ' - ' + kicker_teams[i] for i in range(len(kicker_names))]
	kicker_stats['Player'] = kicker_teams
	kicker_stats.rename(columns = {'Player':'Team'}, inplace = True)

	defense_stats = pd.read_html("https://www.fantasypros.com/nfl/stats/dst.php")[0]
	# print(defense_stats.loc[:,'Player'])
	# print([nm.split('(')[1].split(')')[0] for nm in defense_stats.loc[:,'Player']])
	defense_stats.index = [nm.split('(')[1].split(')')[0] for nm in defense_stats.loc[:,'Player']]

	#
	#
	#
	# ### May try to use weather data
	# ###
	#
	# #################### Rosters ##############################
	#
	#
	raw_rosters = pd.read_html("https://football.fantasysports.yahoo.com/f1/342679/starters")[1:]
	teams = ['Ryan', 'Vince', 'Nathan', 'Nick', 'Arthur', 'Jim', 'Dylan', 'Connor', 'Lucas', 'Shayne']
	rosters = dict()
	for i in range(len(teams)):
		the_rost = raw_rosters[i].copy()
		# print(the_rost.loc[:,'Player'])
		the_rost['Pos'] = ['    ']*len(the_rost)
		for ii in the_rost.index:
			if 'DEF' in the_rost.loc[ii,'Player']:
				for tm in positional['DST']['Team']:
					if tm.lower() in str(the_rost.loc[ii,'Player']).lower():
						the_rost.loc[ii,'Player'] = positional['DST'].index[positional['DST']['Team']==tm][0]
						the_rost.loc[ii,'Pos'] = 'DST'
			else:
				for pl in player_list.index:
					if player_list.loc[pl,'Pos.'] != 'DST':
						plnm = pl.split(' - ')[0]
						pltm = pl.split(' - ')[1]
						if pltm == 'JAC':
							pltm = 'JAX'
						if plnm.split(' ')[0] in the_rost.loc[ii, 'Player'] and plnm.split(' ')[1] in the_rost.loc[ii, 'Player'] and pltm in the_rost.loc[ii, 'Player'].upper():
							the_rost.loc[ii,'Player'] = pl
							the_rost.loc[ii,'Pos'] = player_list[player_list['Pos.'] != 'FLEX'].loc[pl, 'Pos.']
		rosters[teams[i]] = the_rost

	#
	taken_players = pd.DataFrame(columns = ['Pos', 'Player', 'FTeam'])
	for tm in rosters:
		temp_ros = pd.DataFrame(rosters[tm])
		temp_ros['FTeam'] = [tm]*len(temp_ros)
		taken_players = pd.concat([taken_players, temp_ros])

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
		if "Note" in nm:
			taken_players.drop(nm,inplace = True)




	#make google search links clickable
	# player_list = player_list.style.format({'Info': make_clickable})
	# available_players = available_players.style.format({'Info': make_clickable})
	# for p in positional:
	# 	positional[p] = positional[p].style.format({'Info': make_clickable})
	# 	available_positional[p] = available_positional[p].style.format({'Info': make_clickable})

	return [player_list, positional, fant_pros,matchups, snap_analysis,targets, defense_stats,kicker_stats, taken_players, available_players, available_positional,rosters]

##### Management functions
def this_week(week,available_positional,positional,matchups,snap_analysis,targets,kicker_stats,defense_stats,rost,positions):#, retu = False):
	'''Decide who to start/sit this week from a roster, and identify any potential available streamers'''
	# if len(pos) == 0:
	outof = 40
	pos = [ps for ps in positions.keys() if ps != 'BENCH']
	lineup = dict()
	streamers = dict()
	score_by_rk = dict()
	for p in [ps for ps in pos if ((ps != 'SUPERFLEX') and (ps != 'FLEX'))]:
		# if p != 'FLEX':
		on_ros = pd.DataFrame(rost[rost.Pos == p])
		score_by_rk[p] = GetHistory(p)[1]
		# else:
		# 	on_ros = pd.DataFrame(rost[[r in ['RB','WR','TE'] for r in rost.Pos]])
		on_ros.index = on_ros.Player
		strm = pd.DataFrame(available_positional[p][available_positional[p].Opp != ''])
		for ind in strm.index:
			strm.loc[ind,'Pos.'] = strm.loc[ind,'Pos.']
		for ply in on_ros.index:
			pp = on_ros.loc[ply,'Pos'] #in case we are in the flex position
			if ply in positional[p].index:
				on_ros.loc[ply,'Avg'] = positional[p].loc[ply,'Avg']
				on_ros.loc[ply,'FP_Pred'] = score_by_rk[p][int(positional[p].loc[ply,'Avg'])]
				on_ros.loc[ply,'Best'] = positional[p].loc[ply,'Best']
				on_ros.loc[ply,'Worst'] = positional[p].loc[ply,'Worst']
				on_ros.loc[ply,'Ceiling'] = on_ros.loc[ply,'Best']*positional[p].loc[ply,'Std_Dev']
				if positional[p].loc[ply,'Opp'] != '':
					on_ros.loc[ply,'Opp'] = positional[p].loc[ply,'Opp']
				else:
					on_ros.loc[ply,'Opp'] = 'BYE/HURT'
			if ply in matchups[pp].index:
				mtch = matchups[pp].loc[ply,str(week)]
				if mtch != 'nan':
					if mtch != 'BYE':
						# if p == 'DST':
						# 	print(on_ros)
						if on_ros.loc[ply,'Opp'] != 'BYE/HURT':
							on_ros.loc[ply,'Matchup Rank'] = mtch.replace(on_ros.loc[ply,'Opp'], '')
						else:
							numbers = where([car.isdigit() for car in mtch])[0]
							if len(numbers)>1:
								on_ros.loc[ply,'Matchup Rank'] = mtch[numbers[0]:numbers[1]+1]
							else:
								on_ros.loc[ply,'Matchup Rank'] = mtch[numbers[0]:numbers[0]+1]
					else:
						on_ros.loc[ply,'Matchup Rank'] = 129
			else:
				on_ros.loc[ply,'Matchup Rank'] = 129
			if p not in ['K','DST']:
				if ply in snap_analysis[pp].index:
					on_ros.loc[ply,'FP/G'] = snap_analysis[pp].loc[ply,'Fantasy Pts']/snap_analysis[pp].loc[ply,'Games']
					on_ros.loc[ply,'Snap %'] = snap_analysis[pp].loc[ply,'Snap %']/100
					on_ros.loc[ply,'Utility %'] = snap_analysis[pp].loc[ply,'Util %']/100
					on_ros.loc[ply,'Use %'] = on_ros.loc[ply,'Snap %']*on_ros.loc[ply,'Utility %']
					if p != 'QB':
						if ply in targets[pp].index:
							on_ros.loc[ply,'Avg Targets'] = targets[pp].loc[ply,'AVG']
							stscr = on_ros.loc[ply,'FP/G']*on_ros.loc[ply,'Use %']*on_ros.loc[ply,'Avg Targets']*(32*3+(33-float(on_ros.loc[ply,'Matchup Rank'])))/(32*4)
					else:
						stscr = on_ros.loc[ply,'FP/G']*on_ros.loc[ply,'Use %']*(32*3+(33-float(on_ros.loc[ply,'Matchup Rank'])))/(32*4)
					on_ros.loc[ply,'Stat Score'] = stscr
				else:
					on_ros.loc[ply,'Stat Score'] = 0
			elif p == 'K':
				if ply in kicker_stats.index:
					on_ros.loc[ply,'FP/G'] = kicker_stats.loc[ply,'FPTS/G']
					on_ros.loc[ply,'FGA'] = kicker_stats.loc[ply,'FGA']
					on_ros.loc[ply,'PCT'] = kicker_stats.loc[ply,'PCT']/100
					stscr = on_ros.loc[ply,'FP/G']*on_ros.loc[ply,'FGA']*on_ros.loc[ply,'PCT']*(32*3+(33-float(on_ros.loc[ply,'Matchup Rank'])))/(32*4)
					on_ros.loc[ply, 'Stat Score'] = stscr
				else:
					on_ros.loc[ply,'Stat Score'] = 0
			elif p == 'DST':
				if ply in defense_stats.index:
					on_ros.loc[ply,'FP/G'] = defense_stats.loc[ply,'FPTS/G']
					on_ros.loc[ply,'Turnovers'] = defense_stats.loc[ply,'INT'] + defense_stats.loc[ply,'FR']
					stscr = (32+(33-float(on_ros.loc[ply,'Matchup Rank'])))/(32*2)*on_ros.loc[ply,'FP/G']
					on_ros.loc[ply,'Stat Score'] = stscr
				else:
					on_ros.loc[ply,'Stat Score'] = 0
		if len(on_ros) >0:
			srtd_by_stat_score = on_ros.sort_values('Stat Score', ascending = False).index
			for ply in on_ros.index:
				on_ros.loc[ply, 'Stat Rank'] = where(srtd_by_stat_score == ply)[0][0]
				on_ros.loc[ply, 'Final'] = on_ros.loc[ply,'FP_Pred']*((outof - on_ros.loc[ply, 'Stat Rank'])/outof)#(on_ros.loc[ply, 'Stat Rank'] + on_ros.loc[ply, 'Avg'])/2
			on_ros.sort_values('Final', inplace = True, ascending = False, axis=0)
		lineup[p] = on_ros.copy()
		#### streamers
		for ply in strm.index:
			pp = strm.loc[ply,'Pos.'] #in case we are in the flex position
			if ply in positional[p].index:
				strm.loc[ply,'Avg'] = positional[p].loc[ply,'Avg']
				strm.loc[ply,'FP_Pred'] = score_by_rk[p][int(positional[p].loc[ply,'Avg'])]
				strm.loc[ply,'Best'] = positional[p].loc[ply,'Best']
				strm.loc[ply,'Worst'] = positional[p].loc[ply,'Worst']
				strm.loc[ply,'Ceiling'] = strm.loc[ply,'Best']*positional[p].loc[ply,'Std_Dev']
				strm.loc[ply,'Opp'] = positional[p].loc[ply,'Opp']
			if ply in matchups[pp].index:
				mtch = matchups[pp].loc[ply,str(week)]
				# print(ply,pp,mtch)
				if mtch != 'nan':
					if mtch != 'BYE':
						strm.loc[ply,'Matchup Rank'] = mtch.replace(strm.loc[ply,'Opp'], '')
					else:
						strm.loc[ply,'Matchup Rank'] = 129
			if p not in ['K','DST']:
				if ply in snap_analysis[pp].index:
					strm.loc[ply,'FP/G'] = snap_analysis[pp].loc[ply,'Fantasy Pts']/snap_analysis[pp].loc[ply,'Games']
					strm.loc[ply,'Snap %'] = snap_analysis[pp].loc[ply,'Snap %']/100
					strm.loc[ply,'Utility %'] = snap_analysis[pp].loc[ply,'Util %']/100
					strm.loc[ply,'Use %'] = strm.loc[ply,'Snap %']*strm.loc[ply,'Utility %']
					if p != 'QB':
						if ply in targets[pp].index:
							strm.loc[ply,'Avg Targets'] = targets[pp].loc[ply,'AVG']
							stscr = strm.loc[ply,'FP/G']*strm.loc[ply,'Use %']*strm.loc[ply,'Avg Targets']*(32*3+(33-float(strm.loc[ply,'Matchup Rank'])))/(32*4)
					else:
						stscr = strm.loc[ply,'FP/G']*strm.loc[ply,'Use %']*(32*3+(33-float(strm.loc[ply,'Matchup Rank'])))/(32*4)
					strm.loc[ply,'Stat Score'] = stscr
				else:
					strm.loc[ply,'Stat Score'] = 0
			elif p == 'K':
				if ply in kicker_stats.index:
					strm.loc[ply,'FP/G'] = kicker_stats.loc[ply,'FPTS/G']
					strm.loc[ply,'FGA'] = kicker_stats.loc[ply,'FGA']
					strm.loc[ply,'PCT'] = kicker_stats.loc[ply,'PCT']/100
					stscr = strm.loc[ply,'FP/G']*strm.loc[ply,'FGA']*strm.loc[ply,'PCT']*(32*3+(33-float(strm.loc[ply,'Matchup Rank'])))/(32*4)
					strm.loc[ply, 'Stat Score'] = stscr
				else:
					strm.loc[ply,'Stat Score'] = 0
			elif p == 'DST':
				if ply in defense_stats.index:
					strm.loc[ply,'FP/G'] = defense_stats.loc[ply,'FPTS/G']
					strm.loc[ply,'Turnovers'] = defense_stats.loc[ply,'INT'] + defense_stats.loc[ply,'FR']
					stscr = (32+(33-float(strm.loc[ply,'Matchup Rank'])))/(32*2)*strm.loc[ply,'FP/G']
					strm.loc[ply,'Stat Score'] = stscr
				else:
					strm.loc[ply,'Stat Score'] = 0
		srtd_by_stat_score_str = strm.sort_values('Stat Score', ascending = False).index
		for ply in strm.index:
			strm.loc[ply, 'Stat Rank'] = where(srtd_by_stat_score_str == ply)[0][0]
			strm.loc[ply, 'Final'] = strm.loc[ply,'FP_Pred']*((outof - strm.loc[ply, 'Stat Rank'])/outof)#(strm.loc[ply, 'Stat Rank'] + strm.loc[ply, 'Avg'])/2
		strm.sort_values('Final', inplace = True, ascending = False,axis=0)
		streamers[p] = strm

	lineup['FLEX'] = pd.concat([lineup['RB'],lineup['WR'],lineup['TE']], sort = True)
	lineup['FLEX'].sort_values('Final',inplace = True)
	lineup['SUPERFLEX'] = pd.concat([lineup['FLEX'],lineup['QB']],sort = True)
	lineup['SUPERFLEX'].sort_values('Final',inplace = True)

	streamers['FLEX'] = pd.concat([streamers['RB'],streamers['WR'],streamers['TE']],sort = True)
	streamers['FLEX'].sort_values('Final',inplace = True)
	streamers['SUPERFLEX'] = pd.concat([streamers['FLEX'],streamers['QB']],sort = True)
	streamers['SUPERFLEX'].sort_values('Final',inplace = True)

	# if len(pos) == 6:
	starters = pd.DataFrame(columns = lineup['QB'].columns)
	for p in [ps for ps in pos if positions[ps] > 0]:
		strpo = pd.DataFrame(lineup[p])
		for pl in strpo.index:
			if pl in starters.index:
				strpo.drop(pl, inplace = True)
		strpo.sort_values('Final', inplace = True, ascending = False,axis=0)
		strpo = strpo.iloc[:Roster[p]]
		starters = pd.concat([starters,strpo], sort = True)
	# starters.drop('FTeam',axis = 1,inplace = True)
	starters.drop('Player', axis = 1,inplace = True)
	starters.drop('Best',axis = 1,inplace = True)
	starters.drop('Worst', axis = 1,inplace = True)
	if 'Snap %' in starters.columns:
		starters.drop('Snap %', axis = 1,inplace = True)
		starters.drop('Utility %',axis = 1, inplace = True)
	starters = starters[['Pos','Opp','Matchup Rank','Final','Avg','Stat Rank','Ceiling','Stat Score','FP/G','Avg Targets','Use %']]
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
	bench = bench[['Pos','Opp','Matchup Rank','Final','Avg','Stat Rank','Ceiling','Stat Score','FP/G','Avg Targets','Use %']]
	# if not retu:
	# 	print('Suggested Lineup:\n', starters)
	# 	print('Bench:\n', bench)
	for p in pos:
		# streamers[p].drop('Notes', axis =1 ,inplace = True)
		# streamers[p].drop('FP_Notes', axis =1 ,inplace = True)
		streamers[p].drop('ROS_Avg', axis =1 ,inplace = True)
		streamers[p].drop('ROS_Best', axis =1 ,inplace = True)
		streamers[p].drop('ROS_Worst', axis =1 ,inplace = True)
		streamers[p].drop('ROS_Std', axis =1 ,inplace = True)
		# streamers[p].drop('ROS_Notes', axis =1 ,inplace = True)
		if 'Snap %' in streamers[p].columns:
			streamers[p].drop('Snap %', axis =1 ,inplace = True)
			streamers[p].drop('Utility %', axis =1 ,inplace = True)
		# if not retu:
		# 	print('Possible Streamers ',p,':\n', streamers[p].iloc[:5])
	strmdict = dict([(p,streamers[p].iloc[:5]) for p in streamers.keys()])
	return[starters, bench, strmdict]

	# else:
	# 	for p in pos:
	# 		# lineup[p].drop('FTeam',axis = 1,inplace = True)
	# 		lineup[p].drop('Player',axis = 1, inplace = True)
	# 		lineup[p].drop('Best',axis = 1,inplace = True)
	# 		lineup[p].drop('Worst',axis = 1, inplace = True)
	# 		if 'Snap %' in lineup[p].columns:
	# 			lineup[p].drop('Snap %', axis = 1,inplace = True)
	# 			lineup[p].drop('Utility %',axis = 1, inplace = True)
	# 		if p in ['RB','WR','FLEX','TE']:
	# 			lineup[p] = lineup[p][['Pos','Opp','Matchup Rank','Final','Avg','Stat Rank','Ceiling','Stat Score','FP/G','Avg Targets','Use %']]
	# 		elif p == 'QB':
	# 			lineup[p] = lineup[p][['Pos','Opp','Matchup Rank','Final','Avg','Stat Rank','Ceiling','Stat Score','FP/G']]
	# 		elif p == 'K':
	# 			lineup[p] = lineup[p][['Pos','Opp','Matchup Rank','Final','Avg','Stat Rank','Ceiling','Stat Score','FP/G','FGA','PCT']]
	# 		elif p == 'DST':
	# 			lineup[p] = lineup[p][['Pos','Opp','Matchup Rank','Final','Avg','Stat Rank','Ceiling','Stat Score']]
	# 		# if not retu:
	# 		# 	print('On team: ',p,':\n', lineup[p])
	# 		#streamers[p].drop('Notes', axis =1 ,inplace = True)
	# 		#streamers[p].drop('FP_Notes', axis =1 ,inplace = True)
	# 		streamers[p].drop('ROS_Avg', axis =1 ,inplace = True)
	# 		streamers[p].drop('ROS_Best', axis =1 ,inplace = True)
	# 		streamers[p].drop('ROS_Worst', axis =1 ,inplace = True)
	# 		streamers[p].drop('ROS_Std', axis =1 ,inplace = True)
	# 		# streamers[p].drop('ROS_Notes', axis =1 ,inplace = True)
	# 		if 'Snap %' in streamers[p].columns:
	# 			streamers[p].drop('Snap %', axis =1 ,inplace = True)
	# 			streamers[p].drop('Utility %', axis =1 ,inplace = True)
	# 		# if not retu:
	# 		# 	print('Possible Streamers ',p,':\n', streamers[p].iloc[:5])
	# 	return[lineup[p], streamers[p]]


def player_look(player,player_list,flx = False):
	'''get rankings, stats, and news for a player'''
	if any([player in nm for nm in player_list.index]):
		unranked = len(player_list)

		plyer_ID = player_list.index[[player in nm for nm in  Players.index]][0]

		player_series = player_list.loc[player_ID]
		pos = player_series['Pos.']
		tm = player_series.Team
		if flx:
			if plyer_ID in ros_rks['FLEX'].index:
				player_series.ROS_Avg = ros_rks['FLEX'].loc[plyer_ID,'Avg']
				player_series.ROS_Best = ros_rks['FLEX'].loc[plyer_ID,'Best']
				player_series.ROS_Worst = ros_rks['FLEX'].loc[plyer_ID,'Worst']
				player_series.ROS_Std = ros_rks['FLEX'].loc[plyer_ID,'Std Dev']
			else:
				player_series.ROS_Avg = unranked
				player_series.ROS_Best = unranked
				player_series.ROS_Worst = unranked
				player_series.ROS_Std = unranked
		else:
			if plyer_ID in ros_rks[pos].index:
				player_series.ROS_Avg = ros_rks[pos].loc[plyer_ID,'Avg']
				player_series.ROS_Best = ros_rks[pos].loc[plyer_ID,'Best']
				player_series.ROS_Worst = ros_rks[pos].loc[plyer_ID,'Worst']
				player_series.ROS_Std = ros_rks[pos].loc[plyer_ID,'Std Dev']
			else:
				player_series.ROS_Avg = unranked
				player_series.ROS_Best = unranked
				player_series.ROS_Worst = unranked
				player_series.ROS_Std = unranked
		if pos in targets:
			if plyer_ID in targets[pos].index:
				player_series['AvgTargets'] = targets[pos].loc[plyer_ID,'AVG']
		if pos in snap_analysis:
			if plyer_ID in snap_analysis[pos].index:
				player_series['AvgSnaps'] = snap_analysis[pos].loc[plyer_ID, 'Snaps/Gm']
				player_series['Snap%'] = snap_analysis[pos].loc[plyer_ID, 'Snap %']/100
				player_series['Utility%'] = snap_analysis[pos].loc[plyer_ID, 'Util %']/100
				player_series['Usage'] = player_series['Snap%']*player_series['Utility%']
				player_series['FantPoints/Game'] = snap_analysis[pos].loc[plyer_ID, 'Fantasy Pts']/snap_analysis[pos].loc[plyer_ID, 'Games']
		if plyer_ID in taken_players.index:
			player_series['Fant_Team'] = taken_players.loc[plyer_ID, 'FTeam']
		else:
			player_series['Fant_Team'] = 'Available'
		return player_series
	else:
		print('no player')
		return None

def make_ros_list(pos):
	ply_dict = dict()
	if pos != 'FLEX':
		for ply in positional[pos].index:
			ply_dict[ply] = player_look(ply)
	else:
		for ply in positional[pos].index:
			ply_dict[ply] = player_look(ply, flx = True)
	ply_df = pd.DataFrame.from_dict(ply_dict, orient = 'index')
	ply_df.sort_values('ROS_Avg', inplace = True)
	return(ply_df)


def team_score(tm, give = [], get = []):
	'''Score the team by player rank weighted by starting'''
	ros = dict()
	for p in positional:
		ros[p] = make_ros_list(p)
	if not isinstance(give, list):
		give = [give]
	if not isinstance(get, list):
		get = [get]
	the_ros = rosters[tm]
	starters, bench = this_week(rost = the_ros, retu = True)[:2]
	roscores = []
	for pos in ros:
		starts = starters[starters.Pos == pos].index
		start_rks = ros[pos].loc[starts]
		benchers = bench[bench.Pos == pos].index
		bench_rks = ros[pos].loc[benchers]
		starter_avg = mean(start_rks.ROS_Avg.astype(float))/len(ros[pos])
		bench_avg = mean(bench_rks.ROS_Avg.astype(float))/len(ros[pos])
		if isnan(bench_avg):
			bench_avg = 0
		scr = 0.75*starter_avg + 0.25*bench_avg
		roscores = roscores + [scr]
	if len(get) != 0 or len(give) != 0:
		newros = the_ros[[j not in give for j in the_ros.Player]]
		for pl in get:
			newp = pd.DataFrame([[player_list.loc[pl,'Pos.'], pl, tm]], columns = ['Pos','Player','FTeam'])
			newros = newros.append(newp, ignore_index = True)
		hypscores = []
		nwstarters, nwbench = this_week(rost = newros, retu = True)[:2]
		for pos in ros:
			nwstarts = nwstarters[nwstarters.Pos == pos].index
			nwstart_rks = ros[pos].loc[nwstarts]
			nwbenchers = nwbench[nwbench.Pos == pos].index
			nwbench_rks = ros[pos].loc[nwbenchers]
			nwstarter_avg = mean(nwstart_rks.ROS_Avg.astype(float))/len(ros[pos])
			nwbench_avg = mean(nwbench_rks.ROS_Avg.astype(float))/len(ros[pos])
			if isnan(nwbench_avg):
				nwbench_avg = 0
			hypscr = 0.75*nwstarter_avg + 0.25*nwbench_avg
			hypscores = hypscores + [hypscr]
	if len(get) != 0 or len(give) != 0:
		return [sum(1-array(roscores)), sum(1-array(hypscores))]
	else:
		return sum(array(roscores))

def tradeit(team1, players1, team2, players2):
	score1 = team_score(tm = team1, give = players1, get = players2)
	score2 = team_score(tm = team2, give = players2, get = players1)
	return [(score1[1] - score1[0])/score1[0], (score2[1] - score2[0])/score2[0]]

def who_to_drop(ros):
	'''Find the least valuable player on your team'''
	final_score= pd.DataFrame(columns = ['Team After Dropping'])
	for plyr in ros.Player:
		final_score.loc[plyr] = team_score(give = [plyr])[1]
	return final_score.sort_values('Team After Dropping')

def posit_sit(pos, team, ret = True):
	[on_roster,stream] = this_week(pos = [pos], rost = rosters[team], retu = True)
	availab = ros[pos][ros[pos].Fant_Team == 'Available']
	rost_ros = ros[pos].loc[on_roster.index]
	if ret:
		return [on_roster,stream,rost_ros,availab]
	else:
		print('------------THIS WEEK -----------','\n', on_roster,'\n',stream[:5])
		print('------------REST OF YEAR--------------','\n', rost_ros,'\n', availab[:10])
		return None



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


# start,sit,stream = this_week(retu = True)
# start
# sit
# stream[0]
# stream[1]
# stream[2]
# stream[3]
# stream[4]
# stream[5]
#
# rbs = posit_sit('RB')
# rbs[2]
# rbs[3]
# def rest_of_season(pos = [], players = []):
# 	'''Rest of season ranker of available players & on roster, OR list of players (for trade comparisons)'''
#
# def find_breakout():
# 	'''Identify players that could be breaking out - recent
# 		increase in production, number of targets, number of touches, etc'''
#
# def stream_d():
# 	'''Figure out which defense to stream this week, (gives some small weight to upcoming schedule'''
#
# def check_trade(give, get):
# 	'''Assess a potential trade'''
#
# def find_trade(pos = []):
# 	'''identify good (realistic) trades'''
#
#


####### Data Frames Created #######
# Description - name - index - columns
#full player list - player_list - player name - Team Pos Depth Notes ROS_Avg ROS_Best ROS_Std TOS_Notes
#list of (position) [dictionary] - positional['position'] - same as above - same as above
#expert consensus rankings (weekly) from fantasy pros [dictionary] - fant_pros['position'] - int - Rank Name Opp Best Worst Avg Std Dev Notes
#list of matchups [dictionary] - matchups['position'] - player name - ECR 1 2 3 ... 17 (week numbers)
#rest of schedule rankings from fantasy pros [dictionary] - ros_rks['position'] - player name - Rank Name Bye Best Worst Avg Std Dev ADP vs ADP
#various stat dataframes - targets, snaps, etc

#fantasy rosters [dictionary] - rosters['Person'] (example rosters['Jim']) - int - Pos Player FTeam
#players taken - taken_players - player name - Pos Player Fteam
#players available - available_players - player name - Team Pos Depth Notes ROS_Avg ROS_Best ROS_Worst ROS_Std ROS_Notes
#available by position [dictionary] - available_postional['position'] - player name - Team Pos Depth Notes FP_Notes Avg Best Worst Std_Dev Opp ROS_Avg ROS_Best ROS_Worst ROS_Std ROS_Notes
#player info (rest of season) [dictionary] - ros['position'] - player name - Team Pos Depth Notes ROS_Avg ROS_Best ROS_Worst ROS_Std ROS_Notes AvgSnaps Snap% Utility% FantPoints/Game Fant_Team
