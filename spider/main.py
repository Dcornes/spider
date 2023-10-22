import configparser
from typing import List, Dict, KeysView


class Price:
    min_price = 0
    max_price = 0

    def __init__(self, price: float):
        self.min_price = self.max_price = price

    def update_min_max(self, price: float):
        if price > self.max_price:
            self.max_price = price
        if price < self.min_price:
            self.min_price = price

options_leg_tags = {'564',  # leg position effect
                    '600',  # leg symbol
                    '608',  # leg code
                    '609',  # leg security type
                    '611',  # leg exp
                    '612',  # strike
                    '623',  # leg ratio
                    '624',  # leg side
                    '654',  # leg refid
                    }

def valid_order_single(keys: KeysView[str]) -> bool:
    # shot at validating new order single
    # clordid, side,time,ordertype,price,acct
    return '11' in keys and '54' in keys and '60' in keys and '40' in keys and '44' in keys and '1' in keys


def print_dupes_and_prices(message_list: List[str]) -> None:
    account_map: Dict[str, Price] = {}  # store price info per account

    for line in message_list:  # loop through each message
        message_map: Dict[str, str] = {}  # for each message, store tag, value
        duped_fields = set()  # duped tags

        tag_values = line.split('|')
        for key_val in tag_values:  # loop through fields
            if key_val == '\n':
                continue

            pair = key_val.split('=')
            tag = pair[0]
            value = pair[1]

            # check for duped tags
            if tag in message_map.keys():  #
                duped_fields.add(tag)
            else:
                message_map[tag] = value

        # Check for new order singles and register price by acct if duped fields not present
        if message_map['35'] == 'D' and len(duped_fields) == 0 and valid_order_single(message_map.keys()):
            price = float(message_map['44'])
            account_id = message_map['1']

            if account_id in account_map.keys():
                account_map[account_id].update_min_max(price)
            else:
                account_map[account_id] = Price(price)

        # print if message had dupes
        if len(duped_fields) > 0:
            non_option_leg_dupes = duped_fields - options_leg_tags # dupes that arent due to repeating options legs
            print(
                f'Error: duped tags for msg seqnum: {message_map["34"]} dupe_count: {len(duped_fields)} duped_tags {duped_fields}  {"duped non-option leg tags " + str(non_option_leg_dupes) if len(non_option_leg_dupes) > 0 else ""}')

    for tag, val in account_map.items():
        print(f'account: {tag} min price: {val.min_price} max price: {val.max_price}')


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf/config.ini')
    file_path = config["directories"]["file_path"]

    # load the text lines
    file = open(file_path, 'r')
    list_lines = file.readlines()
    print_dupes_and_prices(list_lines)
