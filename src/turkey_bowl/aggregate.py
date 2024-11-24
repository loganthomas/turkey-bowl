"""
Data aggregation functions
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from turkey_bowl import utils
from turkey_bowl.scrape import Scraper

logger = logging.getLogger(__name__)


def _get_player_pts_stat_type(player_pts: Dict[str, Any]) -> str:
    """
    Helper function to get the stat type within the pulled player
    points. Will be either 'projectedStats' or 'stats'.
    """
    unique_type = set([list(v.keys())[0] for v in player_pts.values()])

    if len(unique_type) > 1:
        raise ValueError(f'More than one unique stats type detected: {unique_type}')

    stats_type = list(unique_type)[0]

    if stats_type not in ('projectedStats', 'stats'):
        raise ValueError(
            f"Unrecognized stats type: '{stats_type}'. "
            + "Expected either 'projectedStats' or 'stats'."
        )

    return stats_type


def _unpack_player_pts(year: int, week: int, player_pts_dict: Dict[str, Any]) -> Dict[str, str]:
    """
    Helper function to unpack player points nested dictionaries.
    """
    ((_, points_dict),) = player_pts_dict.items()
    points_dict = points_dict['week'][str(year)].get(str(week))

    return points_dict


def projected_player_pts_pulled(year: int, week: int, savepath: Path) -> bool:
    """
    Helper function to check if projected points have been pulled.
    """
    if savepath.exists():
        logger.info(f'Projected player data already exists at {savepath}')
        return True

    return False


def create_player_pts_df(
    year: int, week: int, player_pts: Dict[str, Any], savepath: Optional[Path] = None
) -> pd.DataFrame:
    """
    Create a DataFrame to house all player projected and actual points.
    The ``player_pts`` argument can be ``projected_player_pts`` or
    ``actual_player_pts``.

    Actual points will need to be pulled multiple times throughout as
    more games are played/completed. Projected points should be pulled
    once and only once.
    """
    dir_config = utils.load_dir_config(year)

    # Determine projected ('projectedStats') or actual points ('stats').
    stats_type = _get_player_pts_stat_type(player_pts)

    if stats_type == 'projectedStats':
        prefix = 'PROJ_'

        # Projected points should always be saved (pulled only once)
        if savepath is None:
            raise ValueError(
                'When creating a projected player points dataframe, ``savepath`` must be specified.'
            )

    # _get_player_pts_stat_type handles check and raises error if not
    # projectedStats or stats
    else:
        prefix = 'ACTUAL_'

    index = []
    points = []

    for pid, player_pts_dict in player_pts.items():
        points_dict = _unpack_player_pts(year, week, player_pts_dict)
        index.append(pid)
        points.append(points_dict)

    player_pts_df = pd.DataFrame(points, index=index)

    # Get definition of each point attribute
    stat_ids_json_path = dir_config.stat_ids_json_path
    stat_ids_dict = utils.load_from_json(stat_ids_json_path)
    stat_defns = {k: v['name'].replace(' ', '_') for k, v in stat_ids_dict.items()}
    player_pts_df = player_pts_df.rename(columns=stat_defns)

    player_pts_df = player_pts_df.add_prefix(prefix)
    player_pts_df = player_pts_df.reset_index().rename(columns={'index': 'Player'})

    # Get definition of each player team and name based on player id
    player_ids_json_path = dir_config.player_ids_json_path
    player_ids = utils.load_from_json(player_ids_json_path)

    # It is possible that there are new players when scraping actual points
    # that don't exist in player_ids.json nor projected points; if so, report and re-pull player ids
    undocumented_players = set(player_pts_df['Player']).difference(set(player_ids))
    if undocumented_players:
        scraper = Scraper(year)

        for pid in undocumented_players:
            try:
                player_metadata = scraper._get_player_metadata(pid)
                logger.info(f"Undocumented player {pid}: {player_metadata['name']}")
                scraper._update_single_player_id(pid, player_ids)
            except Exception:
                logger.info(f'Error occured for undocumented player {pid}: {player_metadata}')
                logger.info(f'Removing {pid}...')
                player_pts_df = player_pts_df[player_pts_df['Player'] != pid]

        utils.write_to_json(json_dict=player_ids, filename=scraper.dir_config.player_ids_json_path)

    else:
        logger.info('All player ids in pulled player points exist in player_ids.json')

    team = player_pts_df['Player'].apply(lambda x: player_ids[x]['team'])
    player_pts_df.insert(1, 'Team', team)

    pos = player_pts_df['Player'].apply(lambda x: player_ids[x]['position'])
    player_pts_df.insert(2, 'PROJ_Position', pos)

    player_defns = {k: v['name'] for k, v in player_ids.items() if k != 'year'}
    name = player_pts_df['Player'].apply(lambda x: player_defns[x])
    player_pts_df['Player'] = name

    # Make pts col the fourth column for easy access
    pts_col = player_pts_df.filter(regex=f'{prefix}pts')
    pts_col_name = f'{prefix}pts'
    player_pts_df = player_pts_df.drop(pts_col_name, axis=1)
    player_pts_df.insert(3, pts_col_name, pts_col)

    # Convert all col types to non-string as strings come from scrape
    col_types = {}
    for c in player_pts_df.columns:
        if c in ('Player', 'Team', 'PROJ_Position'):
            col_types[c] = 'object'
        else:
            col_types[c] = 'float64'

    player_pts_df = player_pts_df.astype(col_types)
    player_pts_df = player_pts_df.fillna(0.0)

    # Write projected players to csv so only done once
    if stats_type == 'projectedStats':
        logger.info(f'Writing projected player stats to {savepath}...')
        player_pts_df.to_csv(savepath)

    return player_pts_df


def merge_points(
    participant_teams: Dict[str, pd.DataFrame], pts_df: pd.DataFrame, verbose: bool
) -> Dict[str, pd.DataFrame]:
    """
    Merge participant team with collected player points.

    ``pts_df`` can be projected or actual points scraped.
    """
    for participant, participant_team in participant_teams.items():
        merge_cols = ['Player', 'Team']
        if ('PROJ_Position' in participant_team) and ('PROJ_Position' in pts_df):
            merge_cols.append('PROJ_Position')
        merged = pd.merge(participant_team, pts_df, how='left', on=merge_cols)

        # Drop columns where projected or actual points are 0.0
        # Leave ACTUAL_pts in case they are all 0.0 at start
        non_zero_cols = merged.select_dtypes(include='number').sum() == 0
        cols_to_drop = [
            c
            for c in merged.select_dtypes(include='number').columns[non_zero_cols]
            if c != 'ACTUAL_pts'
        ]
        merged = merged.drop(columns=cols_to_drop)

        # Check that all players have a projected and actual score
        if verbose:
            check_mask = merged[['PROJ_pts', 'ACTUAL_pts']].isna().all(axis=1)

            if check_mask.sum() > 0:
                check_players = merged.loc[check_mask, 'Player'].tolist()
                logger.info(f'WARNING: {participant} has players with NaN values: {check_players}')

        participant_teams[participant] = merged

    return participant_teams


def sort_robust_cols(participant_teams: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Sort projected and actual columns so that they line up post merge
    """
    for participant, participant_team in participant_teams.items():
        orig_cols = list(participant_team.columns)
        new_cols = []

        for c in orig_cols:
            stripped_c = c.replace('PROJ_', '').replace('ACTUAL_', '')

            if ((f'PROJ_{stripped_c}' in orig_cols) & (f'ACTUAL_{stripped_c}' in orig_cols)) & (
                (f'PROJ_{stripped_c}' not in new_cols) & (f'ACTUAL_{stripped_c}' not in new_cols)
            ):
                new_cols.append(f'ACTUAL_{stripped_c}')
                new_cols.append(f'PROJ_{stripped_c}')
            else:
                if c not in new_cols:
                    new_cols.append(c)

        participant_teams[participant] = participant_team[new_cols]

    return participant_teams


def write_robust_participant_team_scores(
    participant_teams: Dict[str, pd.DataFrame], savepath: Path
) -> None:
    """
    Writes the total points to an excel file that can be reviewed.
    """
    logger.info(f'Writing robust player points summary to {savepath}...')

    with pd.ExcelWriter(savepath) as writer:
        for participant, participant_team in participant_teams.items():
            # Write data to sheet
            participant_team.to_excel(writer, sheet_name=participant, index=False)

            # Auto-format column lengths and center columns
            worksheet = writer.sheets[participant]
            workbook = writer.book
            center = workbook.add_format()
            center.set_align('center')
            center.set_align('vcenter')

            for i, col in enumerate(participant_team):
                series = participant_team[col]
                max_len = max(series.astype(str).map(len).max(), len(str(series.name)))

                # Add a little extra spacing
                if col in ('Position', 'Player', 'Team'):
                    worksheet.set_column(i, i, max_len + 2)
                else:
                    worksheet.set_column(i, i, max_len + 2, center)
