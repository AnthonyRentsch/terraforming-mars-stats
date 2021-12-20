import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import gspread # https://docs.gspread.org/en/latest/oauth2.html#oauth-client-id
## note: if ever need to re-create and download oauth client secret, 
## make sure to delete authorized_user.json file, which has token for login that needs to be removed ###

corp_map = {
    'Aphrodite': {'clean_name': 'Aphrodite', 'origin': 'Venus'},
    'Arcadian': {'clean_name': 'Arcadian Communities', 'origin': 'Promotional'},
    'Arcadian Communities': {'clean_name': 'Arcadian Communities', 'origin': 'Promotional'},
    'Aridor': {'clean_name': 'Aridor', 'origin': 'Colonies'},
    'ArkLight': {'clean_name': 'Arklight', 'origin':' Colonies'},
    'Arklight': {'clean_name': 'Arklight', 'origin':' Colonies'},
    'Arklight ': {'clean_name': 'Arklight', 'origin':' Colonies'},
    'Beginner': {'clean_name': 'Beginner', 'origin': 'Base'},
    'Celestic': {'clean_name': 'Celestic', 'origin': 'Venus'},
    'Solesta': {'clean_name': 'Celestic', 'origin': 'Venus'},
    'Cheng Shing Mars': {'clean_name': 'Cheung Shing Mars', 'origin': 'Prelude'},
    'Cheung Shing': {'clean_name': 'Cheung Shing Mars', 'origin': 'Prelude'},
    'Cheung Shing Mars': {'clean_name': 'Cheung Shing Mars', 'origin': 'Prelude'},
    'Credicor': {'clean_name': 'Credicor', 'origin': 'Base'},
    'Ecoline': {'clean_name': 'Ecoline', 'origin': 'Base'},
    'Ecoline ': {'clean_name': 'Ecoline', 'origin': 'Base'},
    'Factorium': {'clean_name': 'Factorum', 'origin': 'Promotional'},
    'Helion': {'clean_name': 'Helion', 'origin': 'Base'},
    'Interplanetary Cinematics': {'clean_name': 'Interplanetary Cinematics', 'origin': 'Base'},
    'Inventrix': {'clean_name': 'Inventrix', 'origin': 'Base'},
    'Inventrix ': {'clean_name': 'Inventrix', 'origin': 'Base'},
    'Lakefront': {'clean_name': 'Lakefront Resorts', 'origin': 'Turmoil'},
    'Lakefront Resorts': {'clean_name': 'Lakefront Resorts', 'origin': 'Turmoil'},
    'Manutech': {'clean_name': 'Manutech', 'origin': 'Venus'},
    'Mining Build': {'clean_name': 'Mining Guild', 'origin': 'Base'},
    'Mining Guild': {'clean_name': 'Mining Guild', 'origin': 'Base'},
    'Mons Insurance': {'clean_name': 'Mons Insurance', 'origin': 'Promotional'},
    'Morning Star': {'clean_name': 'Morning Star Inc', 'origin': 'Venus'},
    'Morning Star Inc': {'clean_name': 'Morning Star Inc', 'origin': 'Venus'},
    'Morning Star Inc.': {'clean_name': 'Morning Star Inc', 'origin': 'Venus'},
    'MSI': {'clean_name': 'Morning Star Inc', 'origin': 'Venus'},
    'Philares': {'clean_name': 'Philares', 'origin': 'Promotional'},
    'Philares ': {'clean_name': 'Philares', 'origin': 'Promotional'},
    'Phobo Log': {'clean_name': 'Phobolog', 'origin': 'Base'},
    'Phobolog': {'clean_name': 'Phobolog', 'origin': 'Base'},
    'Phobolog ': {'clean_name': 'Phobolog', 'origin': 'Base'},
    'Point Luna': {'clean_name': 'Point Luna', 'origin': 'Prelude'},
    'Point Luna ': {'clean_name': 'Point Luna', 'origin': 'Prelude'},
    'Polyphemos': {'clean_name': 'Polyphemos', 'origin': 'Colonies'},
    'Polyphemos ': {'clean_name': 'Polyphemos', 'origin': 'Colonies'},
    'Poseidon': {'clean_name': 'Poseidon', 'origin': 'Colonies'},
    'Pristar ': {'clean_name': 'Pristar', 'origin': 'Turmoil'},
    'Recyclon': {'clean_name': 'Recyclon', 'origin': 'Promotional'},
    'Recyclon ': {'clean_name': 'Recyclon', 'origin': 'Promotional'},
    'Robinson Industries': {'clean_name': 'Robinson Industries', 'origin': 'Prelude'},
    'Robinson': {'clean_name': 'Robinson Industries', 'origin': 'Prelude'},
    'Saturn': {'clean_name': 'Saturn Systems', 'origin': 'Base'},
    'Saturn ': {'clean_name': 'Saturn Systems', 'origin': 'Base'},
    'Saturn Sustems': {'clean_name': 'Saturn Systems', 'origin': 'Base'},
    'Saturn Systems': {'clean_name': 'Saturn Systems', 'origin': 'Base'},
    'Saturn systems': {'clean_name': 'Saturn Systems', 'origin': 'Base'},
    'Septen Tribus': {'clean_name': 'Septem Tribus', 'origin': 'Turmoil'},
    'Septum Tribus': {'clean_name': 'Septem Tribus', 'origin': 'Turmoil'},
    'Septem Tribus': {'clean_name': 'Septem Tribus', 'origin': 'Turmoil'},
    'Storm Craft': {'clean_name': 'Storm Craft Incorporated', 'origin': 'Colonies'},
    'Stormcraft': {'clean_name': 'Storm Craft Incorporated', 'origin': 'Colonies'},
    'Teractor': {'clean_name': 'Teractor', 'origin': 'Base'},
    'Terractor': {'clean_name': 'Teractor', 'origin': 'Base'},
    'Terra Labs': {'clean_name': 'Terralabs Research', 'origin': 'Turmoil'},
    'Terralabs': {'clean_name': 'Terralabs Research', 'origin': 'Turmoil'},
    'Terralabs ': {'clean_name': 'Terralabs Research', 'origin': 'Turmoil'},
    'Tharsis': {'clean_name': 'Tharsis Republic', 'origin': 'Base'},
    'Tharsis Republic': {'clean_name': 'Tharsis Republic', 'origin': 'Base'},
    'Thorgate': {'clean_name': 'Thorgate', 'origin': 'Base'},
    'UNMI': {'clean_name': 'United Nations Mars Initiative', 'origin': 'Base'},
    'United Nations Mars Initiative': {'clean_name': 'United Nations Mars Initiative', 'origin': 'Base'},
    'Utopia': {'clean_name': 'Utopia Invest', 'origin': 'Turmoil'},
    'Valley': {'clean_name': 'Valley Trust', 'origin': 'Prelude'},
    'Valley Trust': {'clean_name': 'Valley Trust', 'origin': 'Prelude'},
    'Viron': {'clean_name': 'Viron', 'origin': 'Venus'},
    'Vitor': {'clean_name': 'Vitor', 'origin': 'Prelude'}
}

spreadsheets = [
    '2021 Mars',
    'September Mars',
    'August Mars',
    'July Mars',
    'June Mars',
    'May Mars',
    'March-April Mars'
]

def format_data(sheet, spreadsheet):
    '''
    General function to clean and format Terraforming Mars data.
    '''

    df_t = pd.DataFrame(sheet.get_all_records())
    df_t = df_t[~df_t['Category '].isin(['Milestones (funder):','Awards (funder):', 'Map:','Generation','Credits (tiebreaker)',''])]
    df = df_t.set_index('Category ').T

    # metadata
    date = str(sheet).split("'")[1].split('(')[0].strip()
    df['game_id_temp'] = hash(f"{str(spreadsheet)}_{str(sheet)}")
    df['date'] = pd.to_datetime(date)
    df['num_players'] = df.shape[0]
    
    if '(' in str(sheet) and ')' in str(sheet):
        board_info = str(sheet).split('(')[1].replace(')','').lower()
        if 'elys' in board_info:
            df['board'] = 'Elysium'
        elif 'hella' in board_info:
            df['board'] = 'Hellas'
        elif 'tharsis' in board_info:
            df['board'] = 'Tharsis'
        else:
            df['board'] = 'Tharsis'
        df['prelude'] = 1 if 'prelude' in board_info else 0
        df['venus'] = 1 if 'ven' in board_info or ' V ' in board_info else 0
        df['colonies'] = 1 if 'col' in board_info else 0
        df['turmoil'] = 1 if 'turmoil' in board_info else 0
        df['bgg'] = 1 if 'bgg' in board_info else 0
    else:
        df['board'] = 'Tharsis'
        df['prelude'] = 0
        df['venus'] = 0
        df['colonies'] = 0
        df['turmoil'] = 0
        df['bgg'] = 0

    # game play data
    try:
        df['corporation'] = df['Corp'].map(lambda x: corp_map[x]['clean_name'])
        award_range = df.columns[2:5]
        milestone_range = df.columns[5:8]
    except:
        df['corporation'] = 'UNKNOWN'
        award_range = df.columns[1:4]
        milestone_range = df.columns[4:7]
    try:
        df['corporation_origin'] = df['Corp'].map(lambda x: corp_map[x]['origin'])
    except:
        df['corporation_origin'] = 'UNKNOWN'
        
    df['terraform_rating'] = df['Base TR Score']
    df['num_greeneries'] = df['Greeneries']
    df['num_cities'] = df['Cities (for ref, not points)']
    df['num_greenery_adjacencies'] = df['Greeneries adj to Cities']
    df['card_points'] = df['Points from Cards:']
    df['total_points'] = df['Total']
    try:
        df['total_percent_of_points'] = df['%']
    except:
        df['total_percent_of_points'] = df['Total'] / sum(df['Total'])
    df['point_diff'] = max(df['Total']) - df['Total']
    df['place'] = df['total_points'].rank(ascending=False)

    try:
        df['num_colonies'] = df['Colonies (reference)']
    except:
        try:
            df['num_colonies'] = df['Colonies (for ref, not scoring)']
        except:
            df['num_colonies'] = 0
    df['is_winner'] = [1 if total == max(df['Total']) else 0 for total in df['Total'] ]

    for i, award_col in enumerate(award_range):
        award_num = i + 1
        award_name = award_col.split('(')[0]
        try:
            award_funder = award_col.split('(')[1].replace(')', '')
        except:
            award_funder = 'UNKNOWN'
        df[f'award_{award_num}_name'] = award_name
        df[f'award_{award_num}_funder'] = award_funder
        df[f'award_{award_num}_points'] = df[award_col]

    for i, milestone_col in enumerate(milestone_range):
        milestone_num = i + 1
        milestone_name = milestone_col.split('(')[0]
        #milestone_funder = milestone_col.split('(')[1].replace(')', '')
        df[f'milestone_{milestone_num}_name'] = milestone_name
        #df[f'milestone_{milestone_num}_funder'] = milestone_funder
        df[f'milestone_{milestone_num}_points'] = df[milestone_col]

    # keep good columns
    keep_cols = ['game_id_temp','date','num_players','board','prelude','venus','colonies','turmoil','bgg',
                 'corporation','corporation_origin','terraform_rating',
                 'num_greeneries','num_cities','num_colonies','num_greenery_adjacencies','card_points',
                 'award_1_name','award_1_funder','award_2_name','award_2_funder','award_3_name','award_3_funder',
                 'milestone_1_name','milestone_2_name','milestone_3_name',
                 'award_1_points','award_2_points','award_3_points','milestone_1_points','milestone_2_points','milestone_3_points',
                 'total_points','total_percent_of_points','point_diff','is_winner','place']

    df = df[keep_cols]
    df.reset_index(inplace=True)
    df.rename(columns={'index':'player'}, inplace = True)
    
    return df

if __name__ == '__main__':
    gc = gspread.oauth()

    df_dict = {}
    i = 0

    for spreadsheet in spreadsheets:
        if i > 0:
            time.sleep(60) # avoid API request limit
        sh = gc.open(spreadsheet)
        running = True
        j = 0
        
        while running:
            try:
                sheet = sh.get_worksheet(j)
                if 'Round Robin - 10 Matches' not in str(sheet)\
                and '2020-07-25 (Mini-Golf)' not in str(sheet)\
                and 'Copy of 2020-07-25 (Mini-Golf)' not in str(sheet)\
                and '2020-08-?? (Mini-Golf)' not in str(sheet):
                    df_dict[i] = format_data(sheet, spreadsheet)
                    j += 1
                    i += 1
                else:
                    j += 1
            except gspread.exceptions.APIError:
                time.sleep(60) # handle API limit for March-April Mars sheet, which is larger than the others
            except:
                running = False
        print(f"Loop done for {spreadsheet}")

full_df = pd.concat(df_dict.values())

# create better game id
unique_sorted_game_id_temp = pd.Series([x for _,x in sorted(zip(full_df.date, full_df.game_id_temp))]).unique()
new_game_id_map = {game_id_temp: i+1 for i, game_id_temp in enumerate(unique_sorted_game_id_temp)}
full_df['game_id'] = full_df['game_id_temp'].map(new_game_id_map)
full_df.drop('game_id_temp', axis=1, inplace=True)
full_df = full_df[['game_id','date','player','num_players','board','prelude','venus','colonies','turmoil','bgg',
                 'corporation','corporation_origin','terraform_rating',
                 'num_greeneries','num_cities','num_colonies','num_greenery_adjacencies','card_points',
                 'award_1_name','award_1_funder','award_2_name','award_2_funder','award_3_name','award_3_funder',
                 'milestone_1_name','milestone_2_name','milestone_3_name',
                 'award_1_points','award_2_points','award_3_points','milestone_1_points','milestone_2_points','milestone_3_points',
                 'total_points','total_percent_of_points','point_diff','is_winner','place']]

full_df.to_csv('../terraforming-mars-stats.csv', index=False)