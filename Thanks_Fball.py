# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 17:10:41 2016

@author: thomlo02
"""
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

dad = pd.DataFrame(columns=['QB','RB_1','RB_2','WR_1', 'WR_2', 'TE', 'Flex', 'K', 'Defense'],index=None).T
yeager = pd.DataFrame(columns=['QB','RB_1','RB_2','WR_1', 'WR_2', 'TE', 'Flex', 'K', 'Defense'],index=None).T
logan = pd.DataFrame(columns=['QB','RB_1','RB_2','WR_1', 'WR_2', 'TE', 'Flex', 'K', 'Defense'],index=None).T
becca = pd.DataFrame(columns=['QB','RB_1','RB_2','WR_1', 'WR_2', 'TE', 'Flex', 'K', 'Defense'],index=None).T
mom = pd.DataFrame(columns=['QB','RB_1','RB_2','WR_1', 'WR_2', 'TE', 'Flex', 'K', 'Defense'],index=None).T

def draft_player(df, pos, player):
    df.set_value(pos, 'Player', player)

# Draft PLayer or Defense
draft_player(becca, 'Flex', 'Jarius Wright')


##### Pseduo Draft #########################################################################################
QBs = ['Ben Roethlisberger' ,'Marcus Mariota','Aaron Rodgers', 'Russell Wilson', 'Cam Newton']

RBs = ['Ezekiel Elliott','Ryan Mathews','DeMarco Murray','LeGarrette Blount','Le'+"'"+'Veon Bell']

WR_1s = ['Doug Baldwin','Antonio Brown','Jordy Nelson','Allen Robinson','Tyrell Williams']

WR_2s = ['Dez Bryant','Willie Snead','Stefon Diggs','Brandin Cooks','Odell Beckham Jr.']

TEs = ['Delanie Walker','Cameron Brate','Antonio Gates','Vernon Davis','Kyle Rudolph']

Flexs = ['Chris Moore','Malcolm Mitchell','Kellen Winslow','Steven Jackson','Jordan Norwood']

Ks = ['Steven Hauschka','Dustin Hopkins','Josh Scobee','Zach Hocker','Adam Vinatieri']

Defenses = ['Buccaneers','Dolphins','Ravens','Titans','Packers']

family_dic = {'dad': dad, 'logan': logan, 'yeager': yeager, 'mom': mom, 'becca': becca}
i=0
for member in sorted(family_dic.keys()):
    draft_player(family_dic[member], 'QB', QBs[i])
    draft_player(family_dic[member], 'RB', RBs[i])
    draft_player(family_dic[member], 'WR_1', WR_1s[i])
    draft_player(family_dic[member], 'WR_2', WR_2s[i])
    draft_player(family_dic[member], 'TE', TEs[i])
    draft_player(family_dic[member], 'Flex', Flexs[i])
    draft_player(family_dic[member], 'K', Ks[i])
    draft_player(family_dic[member], 'Defense', Defenses[i])
    i+=1
##################################################################################################################

##################### Refresh Stats (scoringPeriodId is Week) ##################################################
for i in range(901):
    if i%50==0:
        url = str('http://games.espn.com/ffl/leaders?&scoringPeriodId=12&seasonId=2016&startIndex='+str(i))
        html = urlopen(url)
        soup = BeautifulSoup(html, "lxml")
        column_subheaders = ['Player', 'Pass_Yds', 'Pass_TD', 'Int_Thrown', 'Rush_Att', 'Rush_Yds', 'Rush_TD', 'Receps', 'Rec_Yds', 'Rec_TD', 'Rec_Targets', '2PC', 'Fumb_Lost', 'Return_TD', 'Total_Pts']
        data_rows = soup.findAll('tr')[2:]
        player_data = [[td.getText() for td in data_rows[i].findAll('td')]for i in range(len(data_rows))]
        df = pd.DataFrame(player_data)
        df.drop([1,2,3,4,5,9,13,18,22],inplace=True,axis=1)
        df.columns = column_subheaders
        df=df[1:]
        df['Player'] = [x.split(',')[0] for x in df['Player']]
        df['Player'] = df['Player'].str.replace(' D/ST D/ST', '')
        if i==0:
            all_stats=df
        else:
            all_stats = all_stats.append(df, ignore_index=True)
    
            
family_dic = {'dad': dad, 'logan': logan, 'yeager': yeager, 'mom': mom, 'becca': becca}
for member in sorted(family_dic.keys()):
    family_dic[member] = pd.merge(family_dic.get(member), all_stats, on='Player', how='left')
leader()
################################################################################################################

def leader():
    leader_board=[]
    for member in sorted(family_dic.keys()):
        leader_board.append([member, pd.to_numeric(family_dic.get(member)['Total_Pts'], errors = 'coerce').sum()])
    leader_board = pd.DataFrame(leader_board, columns=['member','score'])
    leader_board = leader_board.sort_values('score', ascending=False).reset_index(drop=True)
    print ('Leader: ', leader_board.loc[0,'member'])
    print ('Beating',leader_board.loc[1,'member'], 'by',leader_board.loc[0,'score'] -leader_board.loc[1,'score'])
    return leader_board


