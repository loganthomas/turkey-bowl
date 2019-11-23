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
            right_on=['name', 'team'],
            how='left',
        )

        merged = merged.drop(['name', 'team',], axis=1)
        participant_teams[participant] = merged

        # Defensive programming (ignore bench player in case written in as NONE in .xlsx)
        if sum(pd.isna(merged[:-1]['id'])) > 0:
            print(f"WARNING!! {participant}'s merge has missing player ids")

    return participant_teams


def update_pts(year, week, participant_teams, stats_type):
    # Pull ids and points from API
    player_ids_pts = api.run_query_and_collection(year, week, stats_type)

    # Make correct labels
    if stats_type == 'actual':
        stats_label = 'stats'
        col_label   = 'act_pts'
    else:
        stats_label = 'projectedStats'
        col_label   = 'proj_pts'

    for participant, participant_team in participant_teams.items():

        updated_pts = []
        for pid in participant_team['id']:
            try:
                pid = round(pid)
            except (ValueError, TypeError):
                pid = pid

            # Look up points (not an API call)
            pts = api.get_player_pts(year, week, player_ids_pts, str(pid), stats_label)

            updated_pts.append(pts)

        participant_team[col_label] = updated_pts

    return participant_teams


def create_leader_board(participant_teams):
    """
    Notes: Bench player assumed last row in excel sheet.
    Left out of calculation but still shown.
    """
    # Instantiate leader board data
    leader_board_data = {}

    for participant, participant_team in participant_teams.items():
        print(f'\n### {participant.upper()} stats ###\n')
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


def update_act_pts_and_show_leader(year, week, participant_teams):
    # Update actual points to current week
    #    Currently week prior actual points or last time called actual points.
    #    First time this is called should result in all act_pts being 0.0.
    participant_teams = update_pts(
        year              = year,
        week              = week,
        participant_teams = participant_teams,
        stats_type         ='actual'
    )

    # Create and print leader board
    leader_board = create_leader_board(participant_teams)

    return participant_teams, leader_board


def main(d=1, i=1, u=1):
    """
    d (bool 0 or 1): whether to run draft stuff
    i (bool 0 or 1): whether to run instantiation stuff
    u (bool 0 or 1): whether to run update stuff

    TODO:
        - Consider better main function without d,i,u (hacky for now)
        - Consider making a draft class so isn't call each time?
        - Consider making a leader board class with an updated method?
    """
    year = utils.get_current_year()

    output_dir = utils.create_output_dir(str(year))

    draft_file_path = draft.copy_draft_sheet(year, output_dir)

    # Delete me
    draft_file_path = '2019/draft_sheet_2019_test.xlsx'

    participant_teams = draft.get_draft_data(draft_file_path)

    # Only run draft stuff
    if d:
        # Create a random draft order
        draft_order_path, draft_order = draft.make_draft_order(year, output_dir, participant_teams)

    # Only run instantiation stuff
    if i:
        nfl_start_cal_week_num = utils.get_nfl_start_week(year)
        thanksgiving_cal_week_num = utils.get_thanksgiving_week(year)

        week = utils.calculate_nfl_thanksgiving_week(
            nfl_start_cal_week_num,
            thanksgiving_cal_week_num,
        )

        # TODO: add check to see if the prior_players_df exists, load if it does
        # TODO: add a try except so data isn't lost if a time out occurs during the API pull

        # Pull week prior to gather all players (with injury reports/projections)
        #     Need to pull prior week as current week only has player ids
        #     (this helps identify players by name) One time costly, but easy to
        #     join for updating scores later on.
        prior_act_ids_pts  = api.run_query_and_collection(year, week - 1, stats_type='actual')
        prior_proj_ids_pts = api.run_query_and_collection(year, week - 1, stats_type='projected')

        prior_players = api.instantiate_players(year, week-1, prior_act_ids_pts, prior_proj_ids_pts)
        prior_players_df = utils.create_players_df(prior_players)
        prior_players_df_path = utils.save_players_df(year, week - 1, output_dir, prior_players_df)
        print(f'Saved prior week ({week-1}) player data to {prior_players_df_path}')

        participant_teams = merge_points(participant_teams, prior_players_df)

        # Update projected points to current week (currently week prior projections)
        participant_teams = update_pts(
            year              = year,
            week              = week,
            participant_teams = participant_teams,
            stats_type        = 'projected'
        )

        return participant_teams

    # Only run update stuff
    if u:
        # Can call this multiple times when launched from IPython console
        participant_teams, leader_board = update_act_pts_and_show_leader(
            year,
            week,
            participant_teams
        )

        leader_board.to_csv(output_dir.joinpath(f'{year}_leader_board.csv'))

        return participant_teams, leader_board

