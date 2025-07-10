import requests
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv('.env')

API_BASE_URL = 'https://api.transport.nsw.gov.au/v1/tp/'
API_KEY =  os.getenv('NSW_TRANSPORT_API_KEY')

HEADERS = {
    'Authorization': f'apikey {API_KEY}'
}

def address_to_coord(address):
    try:
        params = {
            'outputFormat': 'rapidJSON',
            'type_sf': 'any',
            'name_sf': address,
            'coordOutputFormat': 'EPSG:4326',
            'anyMaxSizeHitList': 1, 
        }
        response = requests.get(API_BASE_URL + 'stop_finder', headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        locations = data.get('locations', [])

        if locations:
            best_match = locations[0]
            coord = f"{best_match['coord'][1]}:{best_match['coord'][0]}:EPSG:4326"
            print(f"find address: {address} | address: {coord}")
            return coord
        else:
            print(f"can not find address: {address}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"error : {e}")
        return None

def find_shortest_travel_time(origin, destination, date=None, time_='0900'):
    try:
        if not date:
            date = (datetime.now() + timedelta(days=1)).strftime('%y%m%d')

        params = {
            'outputFormat': 'rapidJSON',
            'coordOutputFormat': 'EPSG:4326',
            'depArrMacro': 'dep',
            'itdDate': date,
            'itdTime': time_,
            'type_origin': 'coord',
            'name_origin': origin,
            'type_destination': 'coord',
            'name_destination': destination,
            'inclMOT': '1,2,3,4,5,6,7,8,9,10',
            'TfNSWTR': 'true',
        }
        response = requests.get(API_BASE_URL + 'trip', headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        journeys = data.get('journeys', [])

        if not journeys:
            print("do not find commute time。")
            return None
        all_durations = [
            sum(leg.get('duration', 0) for leg in journey.get('legs', [])) // 60
            for journey in journeys
        ]
        shortest_duration = min(all_durations)
        print(f"the commute time: {shortest_duration} min")
        return shortest_duration
    except requests.exceptions.RequestException as e:
        print(f"Trip Planner API error: {e}")
        return None


def update_commute_time(university):
    today = datetime.now().strftime('%y%m%d')
    input_file = f"{university}_rentdata_{today}.csv"
    output_file = f"{university}_rentdata_{today}.csv"

    data = pd.read_csv(input_file)

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%y%m%d')
    yesterday_file = f"{university}_rentdata_{yesterday}.csv"
    
    if 'commuteTime_UNSW' not in data.columns:
        data['commuteTime_UNSW'] = None
    if 'commuteTime_USYD' not in data.columns:
        data['commuteTime_USYD'] = None

    current_commute_col = f'commuteTime_{university}'
    
    if os.path.exists(yesterday_file):
        print(f"Found previous day's data: {yesterday_file}")
        yesterday_data = pd.read_csv(yesterday_file)
        
        if current_commute_col in yesterday_data.columns:
            if 'houseId' in data.columns and 'houseId' in yesterday_data.columns:
                yesterday_data_unique = yesterday_data.drop_duplicates(subset=['houseId'], keep='first')
                print(f"Mapping {current_commute_col} from yesterday's data using houseId")
                data[current_commute_col] = data['houseId'].map(
                    yesterday_data_unique.set_index('houseId')[current_commute_col]
                )
            elif 'addressLine1' in data.columns and 'addressLine1' in yesterday_data.columns:
                yesterday_data_unique = yesterday_data.drop_duplicates(subset=['addressLine1'], keep='first')
                print(f"Mapping {current_commute_col} from yesterday's data using addressLine1")
                data[current_commute_col] = data['addressLine1'].map(
                    yesterday_data_unique.set_index('addressLine1')[current_commute_col]
                )
            else:
                print("Warning: No matching key found for mapping yesterday's data")
        else:
            print(f"Column {current_commute_col} not found in yesterday's data")
    else:
        print(f"No previous day's data found: {yesterday_file}")

    missing_commute = data[data[current_commute_col].isna()]
    
    if len(missing_commute) == 0:
        print(f"No missing {current_commute_col} data found")
        data.to_csv(output_file, index=False)
        print(f"save data to:{output_file}")
        return

    coords = {
        'UNSW': "151.23143:-33.917129:EPSG:4326",  # UNSW Kensington
        'USYD': "151.18672:-33.888333:EPSG:4326"   # USYD
    }
    
    target_coord = coords[university]

    for index, row in tqdm(missing_commute.iterrows(), total=len(missing_commute), desc=f"Updating commute time to {university}"):
        origin_address = row['addressLine1']
        origin_coord = address_to_coord(origin_address)

        if origin_coord:
            travel_time = find_shortest_travel_time(origin_coord, target_coord, time_="0900")
            data.loc[index, current_commute_col] = travel_time if travel_time is not None else 0
            print(f"{university} commute time: {travel_time} minutes")
        else:
            data.loc[index, current_commute_col] = 0

    data.to_csv(output_file, index=False)
    print(f"save data to:{output_file}")