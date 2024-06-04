# gpu_monitor
NVIDIA GPU monitoring tool based on Python and the gspread library.

![Example image](./assets/example.png)

## Last Update (June 4, 2024)
> Included an example image

> How to run

### TODO
1. Support Docker environment

## Getting Started
Before getting started, you need to obtain a Google Spreadsheet auth token (refer to the link below):

https://docs.gspread.org/en/latest/

1. Place the auth token JSON file in the topmost directory ('service_account.json').

1. Install dependencies
```sh
pip install -r requirements.txt
```

2. Modify the config.yaml file
- --`json_path`: Auth token from Google Spreadsheet API.
- --`start_cell`: Starting cell for logging GPU stats.
- --`num_gpus`: The total number of GPUs in the node
- --`sleep_time`: Sleeping time between each API call (to prevent exceeding API limits).
- --`spreadsheet_name`: Name of the spreadsheet document.
- --`worksheet_name`: Name of the worksheet (see bottom left).


3. Run the monitoring using the script below
```sh
./run.sh
```

or 

```sh
python watch.py --config_path CONFIG_PATH
```