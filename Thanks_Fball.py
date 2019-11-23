"""
Thanksgiving Football module
"""
# Standard Libraries

# Third-party libraries
import pandas as pd

# Local libraries
import utils
import draft
import api


# Set option for nice DataFrame display
pd.options.display.width = None


def merge_points(participant_teams, players_df):
    """
    Notes:
        Although the 'Bench (RB/WR)' player is reported in the
        player_stats DF, it is not used to calculate the total points for a
        given participant. It is assumed that the 'Bench (RB/WR)' player
        is listed last in the excel spreadsheet.
    """
    for participant, participant_team in participant_teams.items():
        merged = pd.merge(
            participant_team,
            players_df,
            left_on=['Player', 'Team'],
            right_on=['name', 'team']
        )

        merged = merged.drop(['name', 'team',], axis=1)
        participant_teams[participant] = merged

    return participant_teams


def create_leader_board(participant_teams):
    """
    Notes: Bench player assumed last row in excel sheet.
    Left out of calculation but still shown.
    """
    # Instantiate leader board data
    leader_board_data = {}

    for participant, participant_team in participant_teams.items():
        print(f'### {participant.upper()} stats ###\n')
        print(participant_team)
        print('\n\n\n')

        # Assumes bench is last row (shown but not included in sum)
        team_pts = participant_team[:-1]['act_pts'].sum()

        leader_board_data[participant] = team_pts

    # Create a DataFrame from point_totals
    leader_board = pd.DataFrame.from_dict(leader_board_data, orient='index', columns=['PTS'])

    # Sort the leader board on highest pts to lowest pts
    leader_board = leader_board.sort_values('PTS', ascending=False)

    # Create column to show how far ahead each participant is compared to next
    leader_board['margin'] = leader_board['PTS'].diff(-1)

    # Create column to show how far out of lead they are
    leader_board['pts_back'] = leader_board.iloc[0,0] - leader_board['PTS'].values

    # Print details on points
    print(f'\n{leader_board.index[0]} winning with {leader_board.iloc[0,0]} pts\n')
    print(leader_board)
    print('\n')

    return leader_board


def main():
    """
    TODO:
    Consider returning some of these things
    (leader_board, detailed_scores, etc.) so that entire main
    doesn't need to be run each time
    """
    # 2019 start
    # Stopped here create function to cp draft_sheet.xlsx to output_dir and add year
    # Save players (with name, id, team, pos, etc.) and points from previous week... one time cost.

    year = utils.get_current_year()

    output_dir = utils.create_output_dir(str(year))

    draft_file_path = draft.copy_draft_sheet(year, output_dir)

    # Delete me
    draft_file_path = '2019/draft_sheet_2019_test.xlsx'

    participant_teams = draft.get_draft_data(draft_file_path)

    # Create a random draft order
    draft_order = draft.make_draft_order(participant_teams)
    print(draft_order)

    nfl_start_cal_week_num = utils.get_nfl_start_week(year)
    thanksgiving_cal_week_num = utils.get_thanksgiving_week(year)

    week = utils.calculate_nfl_thanksgiving_week(nfl_start_cal_week_num, thanksgiving_cal_week_num)

    # Pull week prior to gather all players (with injury reports/projections)
    #     Need to pull prior week as current week only has player ids
    #     (this helps identify players by name) One time costly, but easy to
    #     join for updating scores later on.
    prior_act_ids_pts  = api.run_query_and_collection(year, week-1, stats_type='actual')
    prior_proj_ids_pts = api.run_query_and_collection(year, week-1, stats_type='projected')

    prior_players = api.instantiate_players(year, week-1, prior_act_ids_pts, prior_proj_ids_pts)
    prior_players_df = utils.create_players_df(prior_players)
    prior_players_df_path = utils.save_players_df(year, week-1, output_dir, prior_players_df)

    actual_url = api.create_query_url(year, week, stats_type='actual')
    actual_response = api.create_api_response(actual_url)
    actual_player_ids_pts = api.collect_player_ids_pts(actual_response)

    projected_url = api.create_query_url(year, week, stats_type='projected')
    projected_response = api.create_api_response(projected_url)
    projected_player_ids_pts = api.collect_player_ids_pts(projected_response)

    players = api.instantiate_players(year, week, actual_player_ids_pts, projected_player_ids_pts)


    # CREATE update function!!!

    # Collect player scores for given week and year
    print('\nGathering points for week {} year {} by scraping the web...'.format(week, year))
    players_df, kickers_df, defenses_df = gather_points(week, year)
    print('Successfully gathered players, kickers, and defenses points')

    # Determine participant's draft player scores
    print('\nMerging points to drafted teams...')
    detailed_pnts, pnt_totals = merge_points(participant_teams, players_df, kickers_df, defenses_df)
    print('Successfully merged points to participants drafted teams')

    # Create and print leader board
    leader_board = create_leader_board(detailed_pnts, pnt_totals)
    print('\n{} winning with {} pts\n'.format(leader_board.iloc[0,0], leader_board.iloc[0,1]))
    print(leader_board)


if __name__ == '__main__':
    main()

