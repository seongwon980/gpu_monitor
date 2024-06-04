import os
import requests
import argparse
import gspread
import time
import datetime
import yaml
import pytz
import re

def split_alpha_numeric(s):
    match = re.match(r"([a-zA-Z]+)([0-9]+)", s)
    if match:
        return match.groups()
    return None

def get_gpus_info(num_gpus):
    result_str = os.popen('nvidia-smi | grep MiB').read()

    lines = result_str.split('\n')[:num_gpus]
    usage_list = []
    max_list = []
    temperature_list = []
    user_list = []
    
    pattern = r'\b(\d+)MiB'
    for line in lines:
        matches = re.findall(pattern, line)
        if len(matches) == 2:
            usage_list.append(f"{matches[0]}MiB")
            max_list.append(f"{matches[1]}MiB")
    
    gpu_num = len(usage_list)
    
    params = {}
    params['gpu_num'] = gpu_num

    # Aggregate results
    results_list = []
    for i in range(gpu_num):
        results_dict = {}
        results_dict['usage'] = usage_list[i]
        results_dict['max'] = max_list[i]
        results_list.append(results_dict)

    return results_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PyTorch GPU USAGE')
    parser.add_argument('-c', '--config_path', default='./config.yaml')
    args = parser.parse_args()

    with open(args.config_path, 'r') as f:
        config = yaml.safe_load(f)

    spreadsheet_name = config['spreadsheet_name']
    worksheet_name = config['worksheet_name']
    start_cell = config['start_cell']
    num_gpus = config['num_gpus']
    local_timezone = config['timezone']

    # Get consecutive list of each cells
    cell_alphabet, cell_number = split_alpha_numeric(start_cell)
    cell_alphabet_list = [chr(i + ord(cell_alphabet)) for i in range(num_gpus)]
    cell_list = [char + cell_number for char in cell_alphabet_list]
    last_update_cell = chr(num_gpus + ord(cell_alphabet)) + cell_number
    
    while True:
        try:
            # Get nvidia-smi results
            results_list = get_gpus_info(num_gpus)

            # Postprocess to update sheet
            usage_list = [gpu['usage'][:-3] for gpu in results_list]
            max_list = [gpu['max'][:-3] for gpu in results_list]
            visualize_list = [f"{usage}/{_max}" for usage, _max in zip(usage_list, max_list)]
            in_usage_list = [(int(usage) > 500) for usage in usage_list]
            
            local_time = datetime.datetime.now(pytz.timezone(local_timezone))
            
            # Open and update sheet
            gc = gspread.service_account(config['json_path'])
            sh = gc.open(spreadsheet_name).worksheet(worksheet_name)

            for gpu_num, current_usage in enumerate(visualize_list):
                cell_num = cell_list[gpu_num]
                sh.update(cell_num, [[current_usage]])

                if in_usage_list[gpu_num]:
                    sh.format(cell_num, {
                        "backgroundColor": {
                        "red": 1.0,
                        "green": 0.588,
                        "blue": 0.0
                        },
                        "horizontalAlignment": "CENTER",
                    })
                else:
                    sh.format(cell_num, {
                        "backgroundColor": {
                        "red": 0.0,
                        "green": 0.984,
                        "blue": 0.0
                        },
                        "horizontalAlignment": "CENTER",
                    })

            # Update the last-update time
            current_time = local_time.strftime('%H:%M')
            sh.update(last_update_cell, [[current_time]])
            time.sleep(config['sleep_time'])
            
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(300)
