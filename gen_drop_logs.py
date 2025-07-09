import os
import sys
import datetime
import json
import re
from netCDF4 import Dataset

import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

# Input directories
scandirname = filedialog.askdirectory(initialdir='\\\\10.10.60.240/aoc-storage/AVAPS/Data/Archive', title='INPUT SCAN DIRECTORY')
outdirname = filedialog.askdirectory(initialdir=os.getcwd(), title='OUTPUT DIRECTORY FOR MASTER CSV')

startdatetime = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

# Input date range and aircraft filter
start_date = simpledialog.askstring("INPUT", "START DATE:\nYYYYMMDD",
                                     initialvalue=datetime.datetime.utcnow().strftime("%Y") + "0101",
                                     parent=root)

end_date = simpledialog.askstring("INPUT", "END DATE:\nYYYYMMDD",
                                   initialvalue=datetime.datetime.utcnow().strftime("%Y%m%d"),
                                   parent=root)

AIRCRAFT = simpledialog.askstring("INPUT", "AIRCRAFT IDENT:\nA = ALL\nH = N42\nI = N43\nN = N49\nO = NOT H, I, OR N",
                                   initialvalue='A',
                                   parent=root).upper()

flights = {}
char = '-'
for root_dir, dirs, files in os.walk(scandirname, topdown=False):
    sys.stdout.write('\r' + char)
    if char == '-':
        char = '\\'
    elif char == '\\':
        char = '|'
    elif char == '|':
        char = '/'
    elif char == '/':
        char = '-'

    mission_folder = os.path.basename(root_dir)
    mission_folder_code = mission_folder[-2]
    if (AIRCRAFT != 'A'):
        if (AIRCRAFT == 'O'):
            if (mission_folder_code == 'H' or mission_folder_code == 'I' or mission_folder_code == 'N'):
                continue
        elif (AIRCRAFT != mission_folder_code):
            continue

    for name in sorted(files):
        # D-file processing
        if (name[0] == 'D') and (len(name) == 18):
            dateint = int(name[1:9])
            startdateint = int(start_date)
            enddateint = int(end_date)
            if (dateint < startdateint):
                continue
            if (dateint > enddateint):
                continue
            
            pattern = r'^D(\d{8})_(\d{6})\..+$'
            match = re.match(pattern, name)
            if match:
                date_part = match.group(1)  # YYYYMMDD
                time_part = match.group(2)  # HHMMSS
                launch_datetime = f"{date_part}T{time_part}"  # e.g. "20250124T134530"
            else:
                launch_datetime = None  # or handle error
            print(name)
            flid = os.path.basename(root_dir).upper()
            file_path = os.path.join(root_dir, name)
            
            # Initialize all fields
            field = ''
            data = ''
            channel = ''
            project = ''
            mission = ''
            actype = ''
            tail = ''
            launch_date = ''
            launch_time = ''
            sounding = ''
            sonde_id = ''
            sonde_type = ''
            rev = ''
            built = ''
            sens = ''
            freq = ''
            batt = ''
            firm = ''
            shut = ''
            basep = ''
            baset = ''
            baseh1 = ''
            baseh2 = ''
            dynmp = ''
            dynmt = ''
            dynmh = ''
            pltype = ''
            pltime = ''
            plpres = ''
            pltemp = ''
            pldewp = ''
            plhumi = ''
            plws = ''
            plwd = ''
            pllat = ''
            pllon = ''
            plalt = ''
            oper = ''
            comm = ''
            stdcomm = ''
            
            with open(file_path, "r") as f:
                for line in f:
                    if (line[0:7] == 'AVAPS-T') and (line[9:14] == ' COM ') and (':' in line):
                        field_data = line.split(' COM ', 1)[1].strip()
                        if ':' in field_data:
                            field, data = field_data.split(':', 1)
                            field = field.strip()
                            data = data.strip()

                            if field == 'Data Type/Data Channel':
                                channel = data.split(',')[1].strip().split('Channel ')[1]
                            elif field == 'Project Name/Mission ID':
                                project = data.split(',')[0].strip()
                                mission = data.split(',')[1].strip()
                            elif field == 'Aircraft Type/ID':
                                actype = data.split(',')[0].strip()
                                tail = data.split(',')[1].strip()
                            elif field == 'Launch Time (y,m,d,h,m,s)':
                                launch_date = data.split(',')[0].strip()
                                launch_time = data.split(',')[1].strip()
                            elif field == 'Sounding Name':
                                sounding = data
                            elif field == 'Sonde ID/Type/Rev/Built/Sensors':
                                parts = data.split(',', 4)
                                sonde_id = parts[0].strip()
                                sonde_type = parts[1].strip()
                                rev = parts[2].strip()
                                built = parts[3].strip()
                                sens = parts[4].strip()
                            elif field == 'Sonde Freq/Batt/Firmware/Shutoff':
                                freq = data.split(',')[0].strip()
                                batt = data.split(',')[1].strip()
                                firm = data.split(',')[2].strip()
                                shut = data.split(',')[3].strip()
                            elif field == 'Sonde Baseline Errors (p,t,h1,h2)':
                                basep = data.split(',')[0].strip()
                                baset = data.split(',')[1].strip()
                                baseh1 = data.split(',')[2].strip()
                                baseh2 = data.split(',')[3].strip()
                            elif field == 'Sonde Dynamic Errors  (p,t,h)':
                                dynmp = data.split(',')[0].strip()
                                dynmt = data.split(',')[1].strip()
                                dynmh = data.split(',')[2].strip()
                            elif field == 'Pre-launch Obs Data System/Time':
                                pltype = data.split(',')[0].strip()
                                pltime = data.split(',')[1].strip()
                            elif field == 'Pre-launch Obs (p,t,d,h)':
                                plpres = data.split(',')[0].strip()
                                pltemp = data.split(',')[1].strip()
                                pldewp = data.split(',')[2].strip()
                                plhumi = data.split(',')[3].strip()
                            elif field == 'Pre-launch Obs (wd,ws)':
                                plws = data.split(',')[0].strip()
                                plwd = data.split(',')[1].strip()
                            elif field == 'Pre-launch Obs (lon,lat,alt)':
                                pllon = data.split(',')[0].strip()
                                pllat = data.split(',')[1].strip()
                                plalt = data.split(',')[2].strip()
                            elif field == 'Operator Name/Comments':
                                parts = data.split(',', 1)
                                oper = parts[0].strip()
                                comm = parts[1].strip() if len(parts) > 1 else ''
                            elif field == 'Standard Comments':
                                stdcomm = data

            if not flid in flights:
                flights[flid] = {}

            # Handle potential duplicate sonde IDs (D-file vs. D-file)
            if sonde_id in flights[flid]:
                existing = flights[flid][sonde_id]
                existing_channel = int(existing.get('channel', -1))
                current_channel = int(channel)
                existing_source = existing.get('source_type', '')

                if existing_source == 'NC':
                    # D wins – rename NC
                    new_sonde_id = existing['sonde_id'] + '_' + existing['channel'] + '_dup'
                    existing['sonde_id'] = new_sonde_id
                    flights[flid][new_sonde_id] = existing
                    del flights[flid][sonde_id]
                elif existing_source == 'D':
                    if existing_channel > current_channel:
                        new_sonde_id = existing['sonde_id'] + '_' + existing['channel'] + '_dup'
                        existing['sonde_id'] = new_sonde_id
                        flights[flid][new_sonde_id] = existing
                        del flights[flid][sonde_id]
                    else:
                        sonde_id = sonde_id + '_' + channel + '_dup'

            bad_sonde_flag = ''
            if "Good Drop" not in stdcomm:
                bad_sonde_flag = 'B'

            flights[flid][sonde_id] = {
                'file': name,
                'channel': channel,
                'project': project,
                'mission': mission,
                'actype': actype,
                'tail': tail,
                'launch_date': launch_date,
                'launch_time': launch_time,
                'sounding': sounding,
                'sonde_id': sonde_id, # Use sonde_id as key
                'type': sonde_type,
                'rev': rev,
                'built': built,
                'sens': sens,
                'freq': freq,
                'batt': batt,
                'firm': firm,
                'shut': shut,
                'basep': basep,
                'baset': baset,
                'baseh1': baseh1,
                'baseh2': baseh2,
                'dynmp': dynmp,
                'dynmt': dynmt,
                'dynmh': dynmh,
                'pltype': pltype,
                'pltime': pltime,
                'plpres': plpres,
                'pltemp': pltemp,
                'pldewp': pldewp,
                'plhumi': plhumi,
                'plws': plws,
                'plwd': plwd,
                'pllat': pllat,
                'pllon': pllon,
                'plalt': plalt,
                'oper': oper,
                'comm': comm,
                'stdcomm': stdcomm,
                'source_type': 'D',
                'launch_datetime': launch_datetime,
                'accounting_code': '',
                'bad_sonde_flag': bad_sonde_flag
            }

        # NetCDF file processing
        elif name.endswith(".nc"):
            pattern = r"^([A-Za-z0-9_-]+)-([A-Za-z0-9_-]+)-([0-9]+)-?(\d{8}T\d{6})?-([A-Za-z0-9_-]+)\.nc$"
            match = re.match(pattern, name)
            if not match:
                print(f'Filename does NOT match expected pattern – skipped: {name}')
                continue

            project_name = match.group(1)
            mission_id = match.group(2)
            drop_number = match.group(3)
            filedate = match.group(4)  # Could be None
            channel = match.group(5)

            if filedate is None:
                print(f'No launch time in filename. Skipped: {name}')
                continue

            launch_date_raw = filedate[:8]  # YYYYMMDD
            launch_time_raw = filedate[9:]  # HHMMSS
            launch_datetime = filedate

            dateint = int(launch_date_raw)
            startdateint = int(start_date)
            enddateint = int(end_date)
            if (dateint < startdateint):
                continue
            if (dateint > enddateint):
                continue

            # Convert dates and times to MM/DD/YYYY HH:MM:SS (for display in CSV)
            launch_date = f"{launch_date_raw[4:6]}/{launch_date_raw[6:]}/{launch_date_raw[:4]}"
            launch_time = f"{launch_time_raw[:2]}:{launch_time_raw[2:4]}:{launch_time_raw[4:]}"

            print(name)
            flid = os.path.basename(root_dir).upper()
            file_path = os.path.join(root_dir, name)

            ncfile = None # Initialize to None
            try:
                ncfile = Dataset(file_path, 'r')

                project = project_name
                mission = mission_id
                actype = getattr(ncfile, 'DropPlatform', '')
                tail = getattr(ncfile, 'DropTailNumber', '')
                sounding = getattr(ncfile, 'ObservationNumber', '')
                sonde_id = getattr(ncfile, 'SerialNumber', '')
                sonde_type = getattr(ncfile, 'FactoryProductCode', '')
                rev = getattr(ncfile, 'FactoryRevisionCode', '')
                built = getattr(ncfile, 'ProductionDate', '')
                sens = getattr(ncfile, 'PtuSensorPartNumber', '') + ' ' + getattr(ncfile, 'GpsSensorPartNumber', '')
                freq = getattr(ncfile, 'DropFrequency', '')
                batt = getattr(ncfile, 'BatteryVoltage', '')
                firm = getattr(ncfile, 'FactorySndFirmware', '')
                shut = getattr(ncfile, 'ShutoffDuration', '')
                basep = getattr(ncfile, 'DropPressureAddition', '')
                baset = ''
                baseh1 = ''
                baseh2 = ''
                dynmp = ''
                dynmt = ''
                dynmh = ''
                pl_obs_raw = getattr(ncfile, 'DropLaunchObs', '')
                pl_obs = {}
                if pl_obs_raw:
                    try:
                        pl_obs = json.loads(pl_obs_raw)
                    except json.JSONDecodeError:
                        pl_obs = {}
                pltype = pl_obs.get('header', '')
                pltime = pl_obs.get('utc', '')
                plpres = pl_obs.get('static_pressure', '')
                pltemp = pl_obs.get('ambient_temperature', '')
                pldewp = pl_obs.get('dew_point', '')
                plhumi = pl_obs.get('humidity', '')
                plws = pl_obs.get('wind_speed', '')
                plwd = pl_obs.get('wind_direction', '')
                pllat = pl_obs.get('latitude', '')
                pllon = pl_obs.get('longitude', '')
                plalt = pl_obs.get('pressure_altitude', '')
                oper = getattr(ncfile, 'DropOperator', '')
                accounting_code = getattr(ncfile, 'AccountingCode', '')
                comm = ''
                stdcomm = getattr(ncfile, 'OperatorComments', '')
                bad_sonde_flag = ''
                if "Good Drop" not in stdcomm:
                    bad_sonde_flag = 'B'

                if not flid in flights:
                    flights[flid] = {}

                # Handle potential duplicate sonde IDs (NC-file vs. existing)
                if sonde_id in flights[flid]:
                    existing = flights[flid][sonde_id]
                    existing_channel = int(existing.get('channel', -1))
                    current_channel = int(channel)
                    existing_source = existing.get('source_type', '')

                    if existing_source == 'D':
                        # D wins – NC is renamed
                        sonde_id = sonde_id + '_' + channel + '_dup'
                    elif existing_source == 'NC':
                        if existing_channel > current_channel:
                            new_sonde_id = existing['sonde_id'] + '_' + existing['channel'] + '_dup'
                            existing['sonde_id'] = new_sonde_id
                            flights[flid][new_sonde_id] = existing
                            del flights[flid][sonde_id]
                        else:
                            sonde_id = sonde_id + '_' + channel + '_dup'

                flights[flid][sonde_id] = {
                    'file': name,
                    'channel': channel,
                    'project': project,
                    'mission': mission,
                    'actype': actype,
                    'tail': tail,
                    'launch_date': launch_date,
                    'launch_time': launch_time,
                    'sounding': sounding,
                    'sonde_id': sonde_id, # Use sonde_id as key
                    'type': sonde_type,
                    'rev': rev,
                    'built': built,
                    'sens': sens,
                    'freq': freq,
                    'batt': batt,
                    'firm': firm,
                    'shut': shut,
                    'basep': basep,
                    'baset': baset,
                    'baseh1': baseh1,
                    'baseh2': baseh2,
                    'dynmp': dynmp,
                    'dynmt': dynmt,
                    'dynmh': dynmh,
                    'pltype': pltype,
                    'pltime': pltime,
                    'plpres': plpres,
                    'pltemp': pltemp,
                    'pldewp': pldewp,
                    'plhumi': plhumi,
                    'plws': plws,
                    'plwd': plwd,
                    'pllat': pllat,
                    'pllon': pllon,
                    'plalt': plalt,
                    'oper': oper,
                    'comm': comm,
                    'stdcomm': stdcomm,
                    'source_type': 'NC',
                    'launch_datetime': launch_datetime,
                    'accounting_code': accounting_code,
                    'bad_sonde_flag': bad_sonde_flag
                }
            except Exception as e:
                print(f"Error processing NetCDF file {file_path}: {e}")
            finally:
                if ncfile:
                    ncfile.close()


# Determine the output year directory
output_year = datetime.datetime.strptime(start_date, "%Y%m%d").year
year_out_dir = os.path.join(outdirname, str(output_year))

# Create the year directory if it doesn't exist
os.makedirs(year_out_dir, exist_ok=True)

# Path for the master CSV
master_csv_path = os.path.join(year_out_dir, f'all_drops_{startdatetime}.csv')
master_file = open(master_csv_path, "w")
master_file.write('flight_id,project,launch_date,launch_time,file,count,sonde_id,operator,account,bad,sounding_name,channel,tail_num,actype,std_comm,comm,sonde_type,sonde_rev,sonde_built,sens,freq,batt,firm,shut,basep,baset,baseh1,baseh2,dynmp,dynmt,dynmh,pltype,pltime,plpres,pltemp,pldewp,plhumi,plws,plwd,pllat,pllon,plalt\n')

# Path for the FLID summary text file
flid_summary_path = os.path.join(year_out_dir, f'summary_{startdatetime}.txt')
flid_summary_file = open(flid_summary_path, "w")


# Iterate through each FLID to process and write to the master CSV and summary file
for flid in sorted(flights):
    count = 1
    prev_count = 0

    # Write FLID to the summary file
    flid_summary_file.write(flid + '\n')
    print(f'Processing FLID: {flid}') # Added for better console feedback

    # Create a temporary list of drops for the current flight, sorted for output
    flight_drops_sorted = sorted(
        flights[flid].values(),
        key=lambda drop: (
            drop['launch_datetime'],
            1 if drop['file'].endswith('.nc') else 0  # D-files first
        )
    )

    for drop_data in flight_drops_sorted:
        # Use a temporary sonde_id variable for output formatting
        current_sonde_id = drop_data['sonde_id']

        if current_sonde_id.endswith('_dup'):
            scount = str(prev_count) + '_dup'
        else:
            scount = str(count)
            prev_count = count
            count = count + 1

        outstr = drop_data['mission'].replace(',', ' ').upper()
        outstr += ',' + drop_data['project'].replace(',', ' ')
        outstr += ',' + drop_data['launch_date'].replace(',', ' ')
        outstr += ',' + drop_data['launch_time'].replace(',', ' ')
        outstr += ',' + drop_data['file']
        outstr += ',' + scount
        outstr += ',' + current_sonde_id.replace(',', ' ') # Use the potentially modified sonde_id
        outstr += ',' + drop_data['oper'].replace(',', ' ')
        outstr += ',' + drop_data['accounting_code'].replace(',', ' ')
        outstr += ',' + drop_data['bad_sonde_flag'].replace(',', ' ')
        outstr += ',' + drop_data['sounding'].replace(',', ' ')
        outstr += ',' + drop_data['channel'].replace(',', ' ')
        outstr += ',' + drop_data['tail'].replace(',', ' ')
        outstr += ',' + drop_data['actype'].replace(',', ' ')
        outstr += ',' + drop_data['stdcomm'].replace(',', ' ').replace('none', '')
        outstr += ',' + drop_data['comm'].replace(',', ' ').replace('none', '')
        outstr += ',' + drop_data['type'].replace(',', ' ')
        outstr += ',' + drop_data['rev'].replace(',', ' ')
        outstr += ',' + drop_data['built'].replace(',', ' ')
        outstr += ',' + drop_data['sens'].replace(',', ' ')
        outstr += ',' + drop_data['freq'].replace(',', ' ')
        outstr += ',' + drop_data['batt'].replace(',', ' ')
        outstr += ',' + drop_data['firm'].replace(',', ' ')
        outstr += ',' + drop_data['shut'].replace(',', ' ')
        outstr += ',' + drop_data['basep'].replace(',', ' ')
        outstr += ',' + drop_data['baset'].replace(',', ' ')
        outstr += ',' + drop_data['baseh1'].replace(',', ' ')
        outstr += ',' + drop_data['baseh2'].replace(',', ' ')
        outstr += ',' + drop_data['dynmp'].replace(',', ' ')
        outstr += ',' + drop_data['dynmt'].replace(',', ' ')
        outstr += ',' + drop_data['dynmh'].replace(',', ' ')
        outstr += ',' + drop_data['pltype'].replace(',', ' ')
        outstr += ',' + drop_data['pltime'].replace(',', ' ')
        outstr += ',' + str(drop_data['plpres']).replace(',', ' ')
        outstr += ',' + str(drop_data['pltemp']).replace(',', ' ')
        outstr += ',' + str(drop_data['pldewp']).replace(',', ' ')
        outstr += ',' + str(drop_data['plhumi']).replace(',', ' ')
        outstr += ',' + str(drop_data['plws']).replace(',', ' ')
        outstr += ',' + str(drop_data['plwd']).replace(',', ' ')
        outstr += ',' + str(drop_data['pllat']).replace(',', ' ')
        outstr += ',' + str(drop_data['pllon']).replace(',', ' ')
        outstr += ',' + str(drop_data['plalt']).replace(',', ' ')
        master_file.write(outstr + '\n')

master_file.close()
flid_summary_file.close() # Close the summary file

print('CREATED: ' + master_csv_path)
print('CREATED: ' + flid_summary_path)

messagebox.showinfo("Information", "PROGRAM COMPLETE")
