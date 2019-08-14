######################################################################
#
#		fantasy football draft helper - initialize draft list,
#							draft board, helper functions.
#
#
#
######################################################################


from pylab import *
import pandas as pd
import re
import matplotlib.pyplot as plt
import math

pd.set_option('display.max_rows', None)




### The positions sometimes have weird names on websites.
position_map = {'QB':['QB'],'RB': ['RB','GLB','FB','3RB','HB'], 'WR': ['WR1','WR2','WR3','WR'],'TE': ['TE'], 'DST':['DEF','DST'],'K':['K']}
inv_position_map ={'QB':'QB','RB':'RB','HB':'RB','GLB':'RB','FB':'RB','3RB':'RB', 'WR1':'WR','WR2':'WR','WR3':'WR','WR':'WR','TE': 'TE', 'K':'K', 'DEF':'DST', 'DST':'DST'}

OffensePoints = {'Passing Yards': 1/25, 'Passing TD':4, 'Interception Thrown':-1, 'Sack Taken':0, 'Rushing Yards':1/10, 'Rusing TD':6, 'Reception':0.5, 'Receiving Yards':1/10, 'Receiving TD':6, 'Return Yards':0, 'Return TD':6, '2 Point Conversion':2, 'Fumble':0, 'Fumble Lost':-2}

DefensePoints = {'Sack':1, 'Interception':2, 'Fumble Recovery':2, 'Touchdown':6, 'Safety':2, 'Blocked Kick':2, 'Return Touchdown':6, 'Points Allowed: 0':10, 'Points Allowed: 1-6':7, 'Points Allowed: 7-13':4, 'Points Allowed: 14-20':1, 'Points Allowed: 21-27':0, 'Points Allowed: 28-34': -1, 'Points Allowed: 35+':-4, 'Tackle for loss':0, 'Extra Point Returned':2}

Roster = {'QB':1, 'RB': 2, 'WR':2, 'TE':1, 'FLEX':1, 'SUPERFLEX':0, 'DST':1, 'K':1, 'BENCH':7}



def BuildList(scoring = "Standard"):
	## Fantasy Pros "Expert Consensus" is where we'll get our player list, along with some data about rankings.

	stdranks = "https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php"
	halfppr = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php"
	fullppr = "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php"
	if scoring == "Standard":
		fant_pros = pd.read_html(stdranks)[0]
	elif scoring == "Half PPR":
		fant_pros = pd.read_html(halfppr)[0]
	elif scoring == "PPR":
		fant_pros = pd.read_html(fullppr)[0]
	else:
		print("Please choose Standard, Half PPR, or PPR scoring")
		return None

	fant_pros.drop(0,inplace = True)
	fant_pros.drop('WSID', axis = 1, inplace = True)
	fant_pros.rename(columns = {'Overall (Team)':'Name',fant_pros.columns[0]:'Rank'}, inplace = True)

	fant_pros.drop(columns = [col for col in fant_pros.columns if 'Unnamed' in col], inplace = True)
	fant_pros.dropna(inplace = True)
	fant_pros.drop(index = [indd for indd in fant_pros.index if 'google' in fant_pros.loc[indd,'Name']], inplace = True)

	player_names_fmted = [(ind,fant_pros.Name.loc[ind].split(' ')[0] + ' ' + fant_pros.Name.loc[ind].split(' ')[-2],fant_pros.Name.loc[ind].split(' ')[-1]) for ind in fant_pros.index if '(' not in fant_pros.Name.loc[ind].split(' ')[-2]] + [(ind,fant_pros.Name.loc[ind].split('(')[1].split(')')[0],fant_pros.Name.loc[ind].split('(')[1].split(')')[0]) for ind in fant_pros.index if '(' in fant_pros.Name.loc[ind]]

	fpros_ref_dict = dict([(pl[1],pl[0]) for pl in player_names_fmted])
	player_list_imm = pd.DataFrame(index = [pl[1] for pl in player_names_fmted], columns = ['Pos','Team','Rank','Positional_Rank','Tier','PPG','Best_Rank','Worst_Rank','Rank_Std_Dev','ADP'])


	num_players = len(player_list_imm)

	player_list_imm.loc[:,'Team'] = [pl[2] for pl in player_names_fmted]

	# player_list_imm['Rank'] = np.zeros(num_players)
	# player_list_imm['Positional_Rank'] = np.zeros(num_players)
	# player_list_imm['Best_Rank'] = np.zeros(num_players)
	# player_list_imm['Worst_Rank'] = np.zeros(num_players)
	# player_list_imm['Rank_Std_Dev'] = np.zeros(num_players)
	# player_list_imm['ADP'] = np.zeros(num_players)

	for pl in player_list_imm.index:
		player_list_imm.loc[pl,'Pos'] = ''.join([i for i in fant_pros.Pos.loc[fpros_ref_dict[pl]] if not i.isdigit()])
		player_list_imm.loc[pl,'Rank'] = float(fant_pros.Rank.loc[fpros_ref_dict[pl]])
		player_list_imm.loc[pl,'Positional_Rank'] = int(re.findall(r'\d+', fant_pros.Pos.loc[fpros_ref_dict[pl]])[0])
		player_list_imm.loc[pl,'Best_Rank'] = int(fant_pros.Best.loc[fpros_ref_dict[pl]])
		player_list_imm.loc[pl,'Worst_Rank'] = int(fant_pros.Worst.loc[fpros_ref_dict[pl]])
		player_list_imm.loc[pl,'Rank_Std_Dev'] = float(fant_pros.loc[fpros_ref_dict[pl],'Std Dev'])
		player_list_imm.loc[pl,'ADP'] = float(fant_pros.ADP.loc[fpros_ref_dict[pl]])



	## Boris Chen Tiers
	bc_tiers = pd.read_html('https://docs.google.com/spreadsheets/d/1ZX8xNT6ObBw3v0p21YW7oOatZw1ZWLpwGuicC86aAeU/pubhtml#')[2]
	bc_tiers.columns = bc_tiers.iloc[0]
	bc_tiers.drop(0,inplace = True)
	bc_tiers.rename(columns = {'Player.Name':'Name'}, inplace = True)
	max_tier = max(bc_tiers.Tier.astype(int))
	for ply in player_list_imm.index:
		bc_row = bc_tiers[bc_tiers.Name.str.contains(ply)]
		if len(bc_row)>0:
			player_list_imm.loc[ply,'Tier'] = bc_row.Tier.values.astype(int)[0]
		else:
			player_list_imm.loc[ply,'Tier'] = max_tier + 1

	player_list_imm.sort_values('Rank', inplace = True)

	ScaledAvgPoints = {}
	poshistory = {}
	for pos in player_list_imm.Pos.unique():
		poshistory[pos],ScaledAvgPoints[pos] = GetHistory(pos)

	for ply in player_list_imm.index:
		rankpo = player_list_imm.loc[ply,'Positional_Rank']
		pos = player_list_imm.loc[ply,'Pos']
		if rankpo > len(ScaledAvgPoints[pos]):
			player_list_imm.loc[ply,'PPG'] = 0
		else:
			player_list_imm.loc[ply,'PPG'] = ScaledAvgPoints[pos][rankpo-1]

	return player_list_imm,poshistory,ScaledAvgPoints



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
		historical_stats[yr] = pd.concat([pd.read_html(url+'&cur_page='+str(p))[8] for p in range(5)])
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
	        tot_by_rk[i-1] += float(his.loc[i,'FPts/G'])/float(his.loc[1,'FPts/G'])

	avg_by_rank = np.array(tot_by_rk)/len(historical_stats)

	return historical_stats, avg_by_rank


def StartDraft(order,player_list,roster):#numrds = 16):
	numrds = sum(list(roster.values()))
	AvailablePlayers = player_list.copy()
	blank_round = [' ']*len(order)
	DraftBoard = pd.DataFrame([blank_round]*numrds, columns = order, index = range(1,numrds+1))
	DraftedPlayers = pd.DataFrame(columns = player_list.columns)
	DraftedPlayers['Fant_Team'] = []
	DraftedPlayers['Pick'] = []
	color_board = pd.DataFrame(array([['#ffffff']*len(order)]*numrds), index = DraftBoard.index, columns = DraftBoard.columns)
	return DraftBoard,DraftedPlayers,AvailablePlayers,color_board,1,0


def col_pos(nm, player_list):
	cmp = {'QB':'#ff9966', 'RB':'#0099ff', 'WR':'#00ff99', 'TE':'#ff66ff', 'K':'#9966ff', 'DST': '#ffff00'}
	p = player_list.loc[nm,'Pos']
	pp = inv_position_map[p]
	col = cmp[pp]
	return col

def Draft(player,draft_board,drafted_list,player_list,color_board,round,pick,order):
	# get rid of Junior, III, Etc.
	playerli = player.split(' ')
	for j in range(len(playerli)):
		if ' '.join([n.capitalize() for n in playerli[:j+1]]) in player_list.index:
			player = ' '.join([n.capitalize() for n in playerli[:j+1]])
			break
	if player in player_list.index:
		if round%2 == 1:
			pik = pick
		else:
			pik = len(order)-1-pick
		draft_board.loc[round, order[pik]] = player
		color_board.loc[round, order[pik]] = col_pos(player,player_list)
		player_info = pd.Series(player_list.loc[player])
		player_info['Pick'] = (round-1)*(len(order)) + pick + 1
		player_info['Fant_Team']= order[pik]
		drafted_list = drafted_list.append(player_info)
		player_list.drop(player, inplace = True)
		drafted_list.sort_values('Pick', inplace = True)
		pick = (pick + 1)%len(order)
		if pick == 0:
			round = round + 1
		if round%2 == 1:
			npik = pick
		else:
			npik = len(order)-1-pick
		if round in draft_board.index:
			if draft_board.loc[round,order[npik]] != ' ':#next is a keeper so skip
				pick = (pick + 1)%len(order)
				if pick == 0:
					round = round + 1
	else:
		drafted = False
		playerli = player.split(' ')
		for j in range(len(playerli)):
			if ' '.join([n.capitalize() for n in playerli[:j+1]]) in drafted_list.index:
				player = ' '.join([n.capitalize() for n in playerli[:j+1]])
				drafted = True
				break
		if drafted:
			print(player + ' has already been drafted.')
		else:
			lasnms = [nm.split(' ')[1] for nm in player_list.index]
			print('Not in player list')
	return draft_board,drafted_list,player_list,color_board,round,pick

def AddKeep(player,team,round,draft_board,drafted_list,player_list,color_board):
	draft_board.loc[round, team] = player
	color_board.loc[round, team] = col_pos(player,player_list)
	player_info = pd.Series(player_list.loc[player])
	player_info['Pick'] = -1
	player_info['Fant_Team']= team
	drafted_list = drafted_list.append(player_info)
	player_list.drop(player, inplace = True)
	drafted_list.sort_values('Pick', inplace = True)
	return draft_board,drafted_list,player_list,color_board


def UnDraft(player,draft_board,drafted_list,player_list,color_board,round,pick,order,reset_pick = True):
	playerli = player.split(' ')
	for j in range(len(playerli)):
		if ' '.join([n.capitalize() for n in playerli[:j+1]]) in drafted_list.index:
			player = ' '.join([n.capitalize() for n in playerli[:j+1]])
			break
	if round%2 == 1:
		pik = pick
	else:
		pik = 9-pick
	if player in drafted_list.index:
		pker = drafted_list.loc[player,'Fant_Team']
		rd = int((drafted_list.loc[player,'Pick']-1)/(len(order))) + 1
		print(pker,rd)
		draft_board.loc[rd,pker] = ' '
		color_board.loc[rd,pker] = '#ffffff'
		player_info = pd.Series(drafted_list.loc[player])[player_list.columns]
		player_list = player_list.append(player_info)
		drafted_list.drop(player, inplace = True)
		player_list.sort_values('Rank',inplace = True)
		if reset_pick:
			pick = (pick - 1)%len(order)
			if pick == 9:
				round = round - 1
	else:
		print('Player was not drafted')
	return draft_board,drafted_list,player_list,color_board,round,pick

def ShowBoard(draft_board,color_board):
	fig, ax = subplots(tight_layout=True, figsize =  (25,16))
	ax.xaxis.set_visible(False)
	ax.yaxis.set_visible(False)
	ax.set_frame_on(False)
	tabl = ax.table(cellText = draft_board.values, cellColours = color_board.values,
				colLabels= draft_board.columns, rowLabels = draft_board.index, loc='center', bbox = [0.01,0,1,1])
	tabl.auto_set_font_size(False)
	tabl.set_fontsize(15)
	show()
	return


def team_need(team,drafted_list,starting_slots):
	if team in list(drafted_list.loc[:,'Fant_Team'].values):
		current_team = drafted_list[drafted_list.loc[:,'Fant_Team'] == team]
	else:
		current_team = pd.DataFrame(columns = drafted_list.columns)
	on_team = dict()
	num_need = dict()
	adjust_slots = {'QB':0,'RB':0,'WR':0,'TE':0,'DST':0,'K':0}
	for ky in adjust_slots.keys():
		adjust_slots[ky] = starting_slots[ky]
		if ky == 'QB':
			adjust_slots[ky] += 0.8*starting_slots['SUPERFLEX']
		if ky in ['RB','WR']:
			adjust_slots[ky] += 0.1*starting_slots['SUPERFLEX'] + 0.5*starting_slots['FLEX']
	for p in starting_slots:
		on_team[p] = current_team[[dft == p for dft in current_team.Pos]]
		have = sum([(1 - (on_team[p].loc[ply, 'Tier'] - 1)/25) for ply in on_team[p].index])
		num_need[p] = starting_slots[p] - have
	return [on_team, num_need]


def show_team(drafted_list,round,pick,order,pos = [], by_pos = False):
	if round%2 == 1:
		team = order[pick]
	else:
		team = order[9-pick]
	print(team)
	if team in drafted_list.loc[:,'Fant_Team'].values:
		current_team = drafted_list[drafted_list.loc[:,'Fant_Team'] == team]
	else:
		current_team = pd.DataFrame(columns = drafted_list.columns)
	if not(isinstance(pos, list)):
		pos = [pos]
	if by_pos:
		pos = ['QB', 'RB', 'WR', 'TE', 'DST','K']
	if len(pos) == 0:
		print(current_team)
	else:
		for p in pos:
			on_team = current_team[[dft == p for dft in current_team.Pos]]
			print(p)
			print(on_team)
	return


def draft_scarcity(pos,player_list,round,pick,order,drafted_list,starting_slots):
	#### figure out scarcity in terms of players left
	top_tier = min(player_list.Tier)
	the_position = player_list[[pl == pos for pl in player_list.Pos]]
	pos_tier = min(the_position.Tier)
	num_left = [len(the_position[the_position.Tier == pos_tier + k]) for k in range(4)]
	tier_weighted_left = dot(array(num_left), arange(0.25,1.25,0.25)[::-1])
	nxt_pick = (len(order)-pick)*2

	ppgs = the_position.loc[:,'PPG'].values[:nxt_pick + 1]
	ppgs_diff = [ppgs[i] - ppgs[i+1] for i in range(len(ppgs)-1)]
	worst_drop = sum(ppgs_diff)

	#### figure out if anyone else needs a position
	if round % 2 == 0:
		tm = order[pick]
	else:
		tm = order[9-pick]
	other_teams = list(order)
	other_teams.remove(tm)
	need_cts = empty(len(other_teams))
	for tem in range(len(other_teams)):
		need_cts[tem] = team_need(other_teams[tem],drafted_list,starting_slots)[1][pos]
	tot_need = sum(need_cts[need_cts > 0])
	lkly = sum([nd >= 1.5 for nd in need_cts])
	prbly = sum([(nd >= 0.5 and nd < 1.5) for nd in need_cts])
	unlky = sum([nd < 0.5 for nd in need_cts])
	expt_picked = 0.7*lkly + 0.4*prbly + 0.2*unlky


	expt_drop = sum(ppgs_diff[:int(expt_picked)])
	biggest_drop = max(ppgs_diff)
	biggest_drop_where = array(ppgs_diff).argsort()[-1]


	return [num_left[0], tier_weighted_left, worst_drop, expt_drop, biggest_drop_where, biggest_drop, expt_picked, tot_need]


def assess_player(player,player_list,round,pick,order,drafted_list,starting_slots):
	player_info = player_list.loc[player]
	fant_posi = player_info.Pos
	##### Score based on expert rankings (ppg, based off of fitting to past data with position ranking)
	initial_score = player_info.PPG
	##### Adjust for best/worst/std -  start with the mean expert rank
	#### but we can imagine their rank as a RV and see the median
	### and std deviation. These things tell us how risky a pick is
	median_rk = 0.5*(player_info.Best_Rank + player_info.Worst_Rank)
	risk = player_info.Rank_Std_Dev + (median_rk - initial_score)
	##### Adjust for draft scarcity (position)
	t1l, twl, wd, ep, bdl, bd, ep, tn = draft_scarcity(fant_posi,player_list,round,pick,order,drafted_list,starting_slots)
	pos_availibility =  0.7*ep + 0.2*wd - 0.1*twl##About how much worse you can expect what you get to be if you pass on the position
	##### Adjust for team need (postion)
	if round%2 == 1:
		team = order[pick]
	else:
		team = order[9-pick]
	num_need = team_need(team,drafted_list,starting_slots)[1]
	of_posit = num_need[fant_posi]
	### Compute a final score
	final_score = initial_score + 3*of_posit*round + 2*pos_availibility*round
	bdandw = (bd,bdl)
	assessment = pd.DataFrame([[player_info['Pos'], player_info['Team'],final_score, risk, player_info['Tier'],player_info['PPG'],player_info['Rank'], ep,wd,bdandw, of_posit]], columns = ['Pos', 'Team','Score', 'Risk', 'Tier','PPG', 'Avg_Rank', 'Expected PPG Lost', 'Max PPG Lost', 'Biggest PPG Drop (Picks away)','Team Need'], index = [player])
	return assessment


def shortlist(player_list,round,pick,order,drafted_list,starting_slots,fpos = []):
	if not(isinstance(fpos, list)):
		fpos = [fpos]
	if len(fpos) == 0:
		pl = player_list
	else:
		pos = []
		for po in fpos:
			pos = pos + [po]
		locs = where([p in pos for p in player_list.Pos])
		pl = player_list.iloc[locs]
	top_tier = min(pl.Tier)
	prelim = pl[pl.loc[:,'Tier'] == top_tier]
	cter = 1
	while len(prelim) < 6:
		prelim = pd.concat([prelim, pl[pl.loc[:,'Tier'] == (top_tier + cter)]])
		cter = cter + 1
	short_list = pd.DataFrame(columns = ['Pos', 'Team','Score', 'Risk', 'Tier','PPG', 'Avg_Rank', 'Expected PPG Lost', 'Max PPG Lost', 'Biggest PPG Drop (Picks away)','Team Need'])
	for ply in prelim.index:
		short_list = pd.concat([short_list, assess_player(ply,player_list,round,pick,order,drafted_list,starting_slots)])
		short_list.sort_values('Score', inplace = True, ascending = False)
	return short_list

def FindCliff(pos,DraftedPlayers,HistoricalPPG):
	whereat = sum(DraftedPlayers.Pos == pos)
	plt.plot(range(whereat),HistoricalPPG[pos][:whereat],color = 'red')
	plt.plot(range(whereat - 1,len(HistoricalPPG[pos])),HistoricalPPG[pos][whereat - 1:],color = 'blue')
	return None


def FindCliffs(DraftedPlayers,HistoricalPPG):
	num_pos = len(HistoricalPPG)
	nrws = math.ceil(num_pos/2)
	fig,ax = plt.subplots(nrws,2,figsize = (15,10))
	j = 0
	l = 0
	indis = []
	for pos in HistoricalPPG.keys():
		whereat = sum(DraftedPlayers.Pos == pos)
		m = divmod(j,2)[1]
		if whereat >0:
			ax[l,m].plot(range(whereat),HistoricalPPG[pos][:whereat],color = 'red')
			ax[l,m].plot(range(whereat - 1,len(HistoricalPPG[pos])),HistoricalPPG[pos][whereat - 1:],color = 'blue')
		else:
			ax[l,m].plot(range(0,len(HistoricalPPG[pos])),HistoricalPPG[pos][0:],color = 'blue')
		ax[l,m].set_title(pos)
		j += 1
		l += math.ceil(m/2)
	return None
