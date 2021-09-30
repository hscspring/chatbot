import os
import sqlite3
import random

from .utils import normalize_for_sql

class MultiWozDB:
    # loading databases

    domains = ['restaurant', 'hotel', 'attraction', 'train',    'taxi', 'hospital']  # , 'police']

    hotel_info = ['name', 'area', 'internet', 'parking', 'phone', 'postcode', 'pricerange', 'stars', 'takesbookings', 'type', 'address']
    train_info = ["arriveBy", "day", "departure", "destination", "duration", "leaveAt", "price", "trainID"]
    restaurant_info = ["address", "area", "food", "id", "introduction", "name", "phone", "postcode", "pricerange", "signature","type"]
    attraction_info = ["address", "area", "entrance fee", "id", "name", "openhours", "phone", "postcode", "pricerange", "type"]
    taxi_info = []
    database_keys = {
        'hotel': hotel_info,
        'train': train_info,
        'restaurant': restaurant_info,
        'attraction': attraction_info
    }

    def __init__(self, data_path):
        self.dbs = {}

        for domain in MultiWozDB.domains:
            db = os.path.join('{}/{}-dbase.db'.format(data_path, domain))
            conn = sqlite3.connect(db)
            c = conn.cursor()
            self.dbs[domain] = c

    def queryResultVenues_new(self, domain, turn, real_belief=False):
        if domain not in self.database_keys:
            return []
        
        sql_query = "select {} from {}".format(','.join(self.database_keys[domain]), domain)
        if real_belief == True:
            items = turn.items()
        else:
            items = turn['metadata'][domain]['semi'].items()

        flag = True
        for key, val in items:
            if key == 'leaveat':
                key = 'leaveAt'
            if key == 'arriveby':
                key = 'arriveBy'

            if val == "" or val == "dontcare" or val == 'not mentioned' or val == "don't care" or val == "dont care" or val == "do n't care":
                pass
            if 'book' in key:
                pass
            else:
                if flag:
                    sql_query += " where "
                    val2 = val.replace("'", "''")
                    val2 = normalize_for_sql(val2)

                    if key == 'name' and val2 in ['the cow pizza kitchen and bar',
                                                  'cow pizza kitchen and bar',
                                                  'wankworth house']:
                        continue

                    if key == 'leaveAt':
                        sql_query += r" " + key + " > " + r"'" + val2 + r"'"
                    elif key == 'arriveBy':
                        sql_query += r" " + key + " < " + r"'" + val2 + r"'"
                    else:
                        sql_query += r" " + key + "=" + r"'" + val2 + r"'"
                    flag = False
                else:
                    val2 = val.replace("'", "''")
                    val2 = normalize_for_sql(val2)

                    if key == 'name' and val2 in ['the cow pizza kitchen and bar',
                                                  'cow pizza kitchen and bar',
                                                  'wankworth house']:
                        continue


                    if key == 'leaveAt':
                        sql_query += r" and " + key + " > " + r"'" + val2 + r"'"
                    elif key == 'arriveBy':
                        sql_query += r" and " + key + " < " + r"'" + val2 + r"'"
                    else:
                        sql_query += r" and " + key + "=" + r"'" + val2 + r"'"

        try:  # "select * from attraction  where name = 'queens college'"
            results = self.dbs[domain].execute(sql_query).fetchall()
            results_dic = []
            for a in results:
                a_dic = dict.fromkeys(self.database_keys[domain])
                for k, v in zip(self.database_keys[domain], a):
                    a_dic[k] = v
                results_dic.append(a_dic)
            return results_dic
        except:
            return []


def lexicalize_train(delex_response, db_results, turn_beliefs, turn_domain):
    if len(db_results) > 0:
        sample = random.sample(db_results, k=1)[0]
        value_count = len(db_results)
    else:
        sample = turn_beliefs[turn_domain]
        value_count = 0

    lex_response = delex_response

    if 'from [value_place] to [value_place]' in delex_response:
        departure = sample['departure']
        destination = sample['destination']
        lex_response = lex_response.replace('from [value_place] to [value_place]', 'from {} to {}'.format(departure, destination))
    if 'from [value_place] on [value_day]' in delex_response:
        departure = sample['departure']
        day = sample['day']
        lex_response = lex_response.replace('from [value_place] on [value_day]', 'from {} on {}'.format(departure, day))

    if 'from [value_place]' in delex_response:
        departure = sample['departure']
        # destination = sample['destination']
        lex_response = lex_response.replace('from [value_place]', 'from {}'.format(departure))

    if 'leaving [value_place] at [value_day]' in delex_response:
        departure = sample['departure']
        day = sample['day']
        lex_response = lex_response.replace('leaving [value_place] at [value_day]', 'leaving {} at {}'.format(departure, day))

    if 'leaving [value_place] at [value_time]' in delex_response:
        leaveat = sample['leaveAt']
        departure = sample['departure']
        lex_response = lex_response.replace('leaving [value_place] at [value_time]', 'leaving {} at {}'.format(departure, leaveat))
    if 'leaves [value_place] at [value_time]' in delex_response:
        leaveat = sample['leaveAt']
        departure = sample['departure']
        lex_response = lex_response.replace('leaves [value_place] at [value_time]', 'leaves {} at {}'.format(departure, leaveat))
    if 'leaves at [value_time]' in delex_response:
        if 'leaveAt' in sample:
            leaveat = sample['leaveAt']
            lex_response = lex_response.replace('leaves at [value_time]', 'leaves at {}'.format(leaveat))
    if 'other at [value_time]' in delex_response:
        leaveat = sample['leaveAt']
        lex_response = lex_response.replace('other at [value_time]', 'other at {}'.format(leaveat))

    if 'arrives in [value_place] at [value_time]' in delex_response:
        arriveby = sample['arriveBy']
        destination = sample['destination']
        lex_response = lex_response.replace('arrives in [value_place] at [value_time]', 'arrives in {} at {}'.format(destination, arriveby))
    if 'arrives at [value_time]' in delex_response:
        arriveby = sample['arriveBy']
        lex_response = lex_response.replace('arrives at [value_time]', 'arrives at {}'.format(arriveby))

    if '[value_count] of these' in delex_response:
        value_count = 'one'
        lex_response = lex_response.replace('[value_count] of these', value_count)
    if '[value_count] minutes' in delex_response:
        lex_response = lex_response.replace('[value_count] minutes', sample['duration'])
    if '[value_count]' in delex_response:
        value_count = str(value_count)
        lex_response = lex_response.replace('[value_count]', value_count)
    if 'leaving [value_place]' in delex_response:
        departure = sample['departure']
        lex_response = lex_response.replace('leaving [value_place]', 'leaving {}'.format(departure))
    if 'leaves [value_place]' in delex_response:
        departure = sample['departure']
        lex_response = lex_response.replace('leaves [value_place]', 'leaves {}'.format(departure))
    if 'arrives in [value_place]' in delex_response:
        destination = sample['destination']
        lex_response = lex_response.replace('arrives in [value_place]', 'arrives in {}'.format(destination))
    if '[train_id]' in delex_response:
        train_id = sample['trainID']
        lex_response = lex_response.replace('[train_id]', train_id)
    if '[value_day]' in delex_response:
        train_day = sample['day']
        lex_response = lex_response.replace('[value_day]', train_day)
    if '[value_price]' in delex_response:
        train_price = sample['price']
        lex_response = lex_response.replace('[value_price]', train_price)
    if '[train_reference]' in delex_response:
        random_number = random.randint(10000,99999)
        lex_response = lex_response.replace('[train_reference]', str(random_number))
    return lex_response


def lexicalize_hotel(delex_response, db_results, turn_beliefs, turn_domain):
    if len(db_results) > 0:
        sample = random.sample(db_results, k=1)[0]
        value_count = len(db_results)
    else:
        sample = turn_beliefs[turn_domain]
        value_count = 0

    lex_response = delex_response
    try:
        if '[hotel_name]' in delex_response:
            lex_response = lex_response.replace('[hotel_name]', sample['name'])
        if '[hotel_address]' in delex_response:
            lex_response = lex_response.replace('[hotel_address]', sample['address'])
        if '[value_area]' in delex_response:
            lex_response = lex_response.replace('[value_area]', sample['area'])
        if 'starting [value_day]' in delex_response:
            lex_response = lex_response.replace('starting [value_day]', 'starting {}'.format(turn_beliefs['book day']))
        if '[value_pricerange]' in delex_response:
            lex_response = lex_response.replace('[value_pricerange]', sample['pricerange'])
        if '[value_count] star' in delex_response:
            lex_response = lex_response.replace('[value_count] star', '{} star'.format(sample['stars']))
        if '[value_count]' in delex_response:
            lex_response = lex_response.replace('[value_count]', str(value_count))
        if '[hotel_reference]' in delex_response:
            random_number = random.randint(10000, 99999)
            lex_response = lex_response.replace('[hotel_reference]', str(random_number))
        if 'starting [value_day]' in delex_response:
            lex_response = lex_response.replace('starting [value_day]', 'starting {}'.format(turn_beliefs['book day']))
        if '[value_count] people' in delex_response:
            lex_response = lex_response.replace('[value_count] people', '{} people'.format(turn_beliefs['book people']))
        if '[value_count] nights' in delex_response:
            lex_response = lex_response.replace('[value_count] nights', '{} nights'.format(turn_beliefs['book stay']))
    except:
        pass

    return lex_response