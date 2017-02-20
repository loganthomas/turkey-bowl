# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 17:10:41 2016

@author: loganthomas
"""

# Python 2 compatibility imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Standard Libraries


# Custom Libraries
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup


def create_member_dfs(member_list):
    '''
    Create an empty DataFrame for each member participating in draft.
    Only 9 positions are included in the draft:
    (1) QB
    (2) RB_1
    (3) RB_2
    (4) WR_1
    (5) WR_2
    (6) TE
    (7) Flex
    (8) K
    (9) Defense

    Input:
         - List of members paritipating
        
    Output:
         - Dictionary of members where key = memeber name, values = member player Dataframe
    '''
    member_dict = {}    
    for member in member_list:
        member_dict[member] = pd.DataFrame(columns=['QB','RB_1','RB_2','WR_1', 'WR_2', 'TE', 'Flex', 'K', 'Defense'],index=None).T
    return member_dict
        

def draft_player(df, pos, player):
    '''
    Creates an entry in specified DataFrame for a player that has been drafted
    Function will create a column named 'Player' and insert player on the index pos
    (i.e. index=pos, column=Player, value=player)
    
    Input:
         - DataFrame in which to enter player (member who drafted player)
         - Position of the player drafted (One of 9 positions available)
         - Player name
    
    Output:
         - Entry in specified DataFrame with column name 'Player'
    '''
    df.set_value(pos, 'Player', player)


def leader_board(member_dict):
    leader_board=[]
    for member in sorted(member_dict.keys()):
        leader_board.append([member, pd.to_numeric(member_dict.get(member)['Total_Pts'], errors = 'coerce').sum()])
    leader_board = pd.DataFrame(leader_board, columns=['member','score'])
    leader_board = leader_board.sort_values('score', ascending=False).reset_index(drop=True)
    print ('Leader: ', leader_board.loc[0,'member'])
    print ('Beating',leader_board.loc[1,'member'], 'by', leader_board.loc[0,'score'] - leader_board.loc[1,'score'])
    print (leader_board)


def collect_points(member_dict):
    '''
    Collects points of each player using espn.com and joins player points to member dictionary DataFrame
    Leader board is run to show the points of each member
    
    Notes:
         - scoringPeriodID in url is week
         - startIndex corresponds to which 50 players are gathered (0=top 50, 1=51-101, etc.) 
         - BeautifulSoup is used to parse the url
         - <tr> tag defines a row in an HTML table; a <tr> element contains one or more <td> elements
         - <td> tag defines a standard cell in an HTML table
         - Function selects all <tr> elements after the first 3 tables (player info starts with 3rd table)
         - Function then selects all text in a standard cell (<td> elements) for the player tables selected
         - Columns that are unnecessary are dropped
         - Only player name is grabbed by splitting on comma
         - Function loops through all startIndexes avaiable
         - Scores are joined to member dictionary
         - Scores are aggreagted and reported with leader_board()
    '''
    # Collect Player scores    
    for i in range(901):
        if i%50==0:
            url = str('http://games.espn.com/ffl/leaders?&scoringPeriodId=12&seasonId=2016&startIndex='+str(i))
            html = urlopen(url)
            soup = BeautifulSoup(html, "lxml")
            data_rows = soup.findAll('tr')[3:]
            player_data = [[td.getText() for td in data_rows[i].findAll('td')] for i in range(len(data_rows))]
            df = pd.DataFrame(player_data)
            df.drop([1,2,3,4,5,9,13,18,22],inplace=True,axis=1)
            column_subheaders = ['Player', 'Pass_Yds', 'Pass_TD', 'Int_Thrown', 'Rush_Att', 
                                 'Rush_Yds', 'Rush_TD', 'Receps', 'Rec_Yds', 'Rec_TD', 'Rec_Targets', 
                                 '2PC', 'Fumb_Lost', 'Return_TD', 'Total_Pts']
            df.columns = column_subheaders
            df['Player'] = [x.split(',')[0] for x in df['Player']]
            df['Player'] = df['Player'].str.replace(' D/ST D/ST', '')
            if i==0:
                all_stats=df
            else:
                all_stats = all_stats.append(df, ignore_index=True)
    
    # Append Player scores to member DataFrames          
    for member in sorted(member_dict.keys()):
        member_dict[member] = pd.merge(member_dict.get(member), all_stats, on='Player', how='left')
    
    #Aggreate and report scores
    return leader_board(member_dict)

def mock_draft():
    '''
    Creates a mock draft for testing
    '''
    member_dict = create_member_dfs(['memb1', 'memb2', 'memb3', 'memb4', 'memb5'])
    
    QBs = ['Ben Roethlisberger' ,'Marcus Mariota','Aaron Rodgers', 'Russell Wilson', 'Cam Newton']
    RB_1s = ['Ezekiel Elliott','Ryan Mathews','DeMarco Murray','LeGarrette Blount','Le'+"'"+'Veon Bell']
    RB_2s = ['Mark Ingram', 'LeSean McCoy', 'Jonathan Stewart', 'David Johnson', 'Devonta Freeman']
    WR_1s = ['Doug Baldwin','Antonio Brown','Jordy Nelson','Allen Robinson','Tyrell Williams']
    WR_2s = ['Dez Bryant','Willie Snead','Stefon Diggs','Brandin Cooks','Odell Beckham Jr.']
    TEs = ['Delanie Walker','Cameron Brate','Antonio Gates','Vernon Davis','Kyle Rudolph']
    Flexs = ['Chris Moore','Malcolm Mitchell','Kellen Winslow','Steven Jackson','Jordan Norwood']
    Ks = ['Steven Hauschka','Dustin Hopkins','Josh Scobee','Zach Hocker','Adam Vinatieri']
    Defenses = ['Buccaneers','Dolphins','Ravens','Titans','Packers']
    i=0
    
    for member in sorted(member_dict.keys()):
        draft_player(member_dict[member], 'QB', QBs[i])
        draft_player(member_dict[member], 'RB_1', RB_1s[i])
        draft_player(member_dict[member], 'RB_2', RB_2s[i])
        draft_player(member_dict[member], 'WR_1', WR_1s[i])
        draft_player(member_dict[member], 'WR_2', WR_2s[i])
        draft_player(member_dict[member], 'TE', TEs[i])
        draft_player(member_dict[member], 'Flex', Flexs[i])
        draft_player(member_dict[member], 'K', Ks[i])
        draft_player(member_dict[member], 'Defense', Defenses[i])
        i+=1
    
    collect_points(member_dict)
    return member_dict


######################### Main ##############################################

# Create Member dictioanry
member_dict = create_member_dfs(['memb1', 'memb2', 'memb3', 'memb4', 'memb5'])

# Draft Player or Defense
draft_player(member_dict['memb1'], 'QB', 'Ben Roethlisberger')

# Collect Points and report
collect_points(member_dict)



