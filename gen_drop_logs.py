import os
import sys
import datetime
import json
import re
from netCDF4 import Dataset

import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
#scandirname = filedialog.askdirectory(initialdir='E:/AVAPSDATA/',  title='INPUT SCAN DIRECTORY')
#scandirname = filedialog.askdirectory(initialdir='\\\\10.10.60.240/aoc-storage/SEB-Engineering/AVAPS/Mirrors',  title='INPUT SCAN DIRECTORY')
scandirname = filedialog.askdirectory(initialdir='\\\\10.10.60.240/aoc-storage/AVAPS/Data/Archive',  title='INPUT SCAN DIRECTORY')
#outdirname = filedialog.askdirectory(initialdir='d:/AVAPS/inventory/drop_logs/',  title='OUTPUT DIRECTORY')
outdirname = filedialog.askdirectory(initialdir=os.getcwd(), title='OUTPUT DIRECTORY')

startdatetime=datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

from tkinter import simpledialog
start_date = simpledialog.askstring("INPUT", "START DATE:\nYYYYMMDD",
                                initialvalue=datetime.datetime.utcnow().strftime("%Y")+"0101",
                                parent=root)

end_date = simpledialog.askstring("INPUT", "END DATE:\nYYYYMMDD",
                                initialvalue=datetime.datetime.utcnow().strftime("%Y%m%d"),
                                parent=root)

AIRCRAFT = simpledialog.askstring("INPUT", "AIRCRAFT IDENT:\nA = ALL\nH = N42\nI = N43\nN = N49\nO = NOT H, I, OR N",
                                initialvalue='A',
                                parent=root).upper()



flights={}
char='-'
for root, dirs, files in os.walk(scandirname, topdown=False):
  sys.stdout.write('\r'+char)
  if char == '-':
    char = '\\'
  elif char == '\\':
    char = '|'
  elif char == '|':
    char = '/'
  elif char == '/':
    char = '-'
    
  mission_folder=os.path.basename(root)
  mission_folder_code=mission_folder[-2]
  if (AIRCRAFT != 'A'):
    if (AIRCRAFT == 'O'):
      if (mission_folder_code=='H' or mission_folder_code=='I' or mission_folder_code=='N'):
        continue
    elif ( AIRCRAFT != mission_folder_code ):
      continue
  
  #print('SCANNING: '+root)
  
  for name in sorted(files):
    if (name[0] == 'D') and (len(name) == 18):
      dateint=int(name[1:9])
      startdateint=int(start_date)
      enddateint=int(end_date)
      if (dateint < startdateint):
        continue
      if (dateint > enddateint):
        continue
      #if (name[1:5] != '2019'):
      #  continue
      pattern = r'^D(\d{8})_(\d{6})\..+$'
      match = re.match(pattern, name)
      if match:
        date_part = match.group(1)   # YYYYMMDD
        time_part = match.group(2)   # HHMMSS
        launch_datetime = f"{date_part}T{time_part}"  # e.g. "20250124T134530"
      else:
        launch_datetime = None  # or handle error
      print(name)
      flid=os.path.basename(root).upper()
      file=os.path.join(root, name)
      f=open(file,"r")

      field=''
      data=''
      channel=''
      project=''
      mission=''
      actype=''
      tail=''
      launch_date=''
      launch_time=''
      sounding=''
      id=''
      type=''
      rev=''
      built=''
      sens=''
      freq=''
      batt=''
      firm=''
      shut=''
      basep=''
      baset=''
      baseh1=''
      baseh2=''
      dynmp=''
      dynmt=''
      dynmh=''
      pltype=''
      pltime=''
      plpres=''
      pltemp=''
      pldewp=''
      plhumi=''
      plws=''
      plwd=''
      pllat=''
      pllon=''
      plalt=''
      oper=''
      comm=''
      stdcomm=''

      for line in f:
        if (line[0:7] == 'AVAPS-T') and (line[9:14] == ' COM ') and (':' in line):
          field=line.split(' COM ',1)[1].strip()
          field,data=field.split(':',1)
          
          field=field.strip()
          data=data.strip()
          if field == 'Data Type/Data Channel':
            channel= data.split(',')[1].strip().split('Channel ')[1]
          elif field == 'Project Name/Mission ID':
            project= data.split(',')[0].strip()
            mission= data.split(',')[1].strip()
          elif field == 'Aircraft Type/ID':
            actype= data.split(',')[0].strip()
            tail=   data.split(',')[1].strip()
          elif field == 'Launch Time (y,m,d,h,m,s)':
            launch_date= data.split(',')[0].strip()
            launch_time= data.split(',')[1].strip()
          elif field == 'Sounding Name':
            sounding=data
          elif field == 'Sonde ID/Type/Rev/Built/Sensors':
            id=    data.split(',',4)[0].strip()
            type=  data.split(',',4)[1].strip()
            rev=   data.split(',',4)[2].strip()
            built= data.split(',',4)[3].strip()
            sens=  data.split(',',4)[4].strip()
          elif field == 'Sonde Freq/Batt/Firmware/Shutoff':
            freq= data.split(',')[0].strip()  
            batt= data.split(',')[1].strip()  
            firm= data.split(',')[2].strip()  
            shut= data.split(',')[3].strip()  
          elif field == 'Sonde Baseline Errors (p,t,h1,h2)':
            basep=  data.split(',')[0].strip()  
            baset=  data.split(',')[1].strip()  
            baseh1= data.split(',')[2].strip()  
            baseh2= data.split(',')[3].strip()  
          elif field == 'Sonde Dynamic Errors  (p,t,h)':
            dynmp= data.split(',')[0].strip()  
            dynmt= data.split(',')[1].strip()  
            dynmh= data.split(',')[2].strip()  
          elif field == 'Pre-launch Obs Data System/Time':
            pltype= data.split(',')[0].strip()
            pltime= data.split(',')[1].strip()
          elif field == 'Pre-launch Obs (p,t,d,h)':
            plpres= data.split(',')[0].strip()
            pltemp= data.split(',')[1].strip()
            pldewp= data.split(',')[2].strip()
            plhumi= data.split(',')[3].strip()
          elif field == 'Pre-launch Obs (wd,ws)':
            plws= data.split(',')[0].strip()
            plwd= data.split(',')[1].strip()
          elif field == 'Pre-launch Obs (lon,lat,alt)':
            pllon= data.split(',')[0].strip()
            pllat= data.split(',')[1].strip()
            plalt= data.split(',')[2].strip()
          elif field == 'Operator Name/Comments':
            oper= data.split(',',1)[0].strip()
            comm= data.split(',',1)[1].strip()
          elif field == 'Standard Comments':
            stdcomm=data
        #endif (line[0:7] == 'AVAPS-T') and (line[9:14] == ' COM '):
      #endfor line in f:
      f.close()

      if not flid in flights:
        flights[flid]={}
      
      idch=name[0:len(name)-2]
      #print('IDCH IS: '+idch)
      #print('ID IS: ' + id)
      sys.stdout.flush()
      if id in flights[flid]:
        existing = flights[flid][id]
        existing_channel = int (existing.get('channel', -1))
        current_channel = int(channel)
        existing_source = existing.get('source_type', '')
        sys.stdout.flush()
        if existing_source == 'NC':
            # D wins – rename NC
            newid = existing['id'] + '_' + existing['channel'] + '_dup'
            existing['id'] = newid
            flights[flid][newid] = existing
            del flights[flid][id]
        elif existing_source == 'D':
            if existing_channel > current_channel:
                newid = existing['id'] + '_' + existing['channel'] + '_dup'
                existing['id'] = newid
                flights[flid][newid] = existing
                del flights[flid][id]
            else:
                id = id + '_' + channel + '_dup'
      
      if "Good Drop" not in stdcomm:
        bad_sonde_flag = 'B'
      
      flights[flid][id]={}
      flights[flid][id]['file']=name
      flights[flid][id]['field']=field
      flights[flid][id]['data']=data
      flights[flid][id]['channel']=channel
      flights[flid][id]['project']=project
      flights[flid][id]['mission']=mission
      flights[flid][id]['actype']=actype
      flights[flid][id]['tail']=tail
      flights[flid][id]['launch_date']=launch_date
      flights[flid][id]['launch_time']=launch_time
      flights[flid][id]['sounding']=sounding
      flights[flid][id]['id']=id
      flights[flid][id]['type']=type
      flights[flid][id]['rev']=rev
      flights[flid][id]['built']=built
      flights[flid][id]['sens']=sens
      flights[flid][id]['freq']=freq
      flights[flid][id]['batt']=batt
      flights[flid][id]['firm']=firm
      flights[flid][id]['shut']=shut
      flights[flid][id]['basep']=basep
      flights[flid][id]['baset']=baset
      flights[flid][id]['baseh1']=baseh1
      flights[flid][id]['baseh2']=baseh2
      flights[flid][id]['dynmp']=dynmp
      flights[flid][id]['dynmt']=dynmt
      flights[flid][id]['dynmh']=dynmh
      flights[flid][id]['pltype']=pltype
      flights[flid][id]['pltime']=pltime
      flights[flid][id]['plpres']=plpres
      flights[flid][id]['pltemp']=pltemp
      flights[flid][id]['pldewp']=pldewp
      flights[flid][id]['plhumi']=plhumi
      flights[flid][id]['plws']=plws
      flights[flid][id]['plwd']=plwd
      flights[flid][id]['pllat']=pllat
      flights[flid][id]['pllon']=pllon
      flights[flid][id]['plalt']=plalt
      flights[flid][id]['oper']=oper
      flights[flid][id]['comm']=comm
      flights[flid][id]['stdcomm']=stdcomm
      flights[flid][id]['source_type']='D'
      flights[flid][id]['launch_datetime']=launch_datetime
      flights[flid][id]['accounting_code']=''
      flights[flid][id]['bad_sonde_flag']=bad_sonde_flag
    elif name.endswith(".nc"):
      # new NetCDF logic
      pattern = r"^([A-Za-z0-9_-]+)-([A-Za-z0-9_-]+)-([0-9]+)-?(\d{8}T\d{6})?-([A-Za-z0-9_-]+)\.nc$"
      match = re.match(pattern, name)
      if not match:
        # Filename does NOT match expected pattern — skip it
        continue

      # Extract metadata from filename
      project_name = match.group(1)
      mission_id = match.group(2)
      drop_number = match.group(3)
      filedate = match.group(4)  # Could be None
      channel = match.group(5)

      if filedate is None:
        # No launch time in filename, skip or handle as needed
        print('No launch time in filename. Skipped')
        continue

      # Now proceed with your logic using extracted fields
      # Example: parse launch_date from filedate (YYYYMMDDTHHMMSS)
      launch_date = filedate[:8]          # YYYYMMDD
      launch_time = filedate[9:]          # HHMMSS
      launch_datetime = filedate
      
      # Check date range filtering here as in your script...
      dateint=int(launch_date)
      startdateint=int(start_date)
      enddateint=int(end_date)
      if (dateint < startdateint):
        continue
      if (dateint > enddateint):
        continue


      # Convert dates and times to MM/DD/YYYY HH:MM:SS
      if len(launch_date) == 8 and launch_date.isdigit():
        launch_date = f"{launch_date[4:6]}/{launch_date[6:]}/{launch_date[:4]}"
      if len(launch_time) == 6 and launch_time.isdigit():
        launch_time = f"{launch_time[:2]}:{launch_time[2:4]}:{launch_time[4:]}"

      # Then open the NetCDF file and extract metadata...
      print(name)
      flid=os.path.basename(root).upper()
      file=os.path.join(root, name)
      ncfile = Dataset(file, 'r')
      
      project=project_name
      mission=mission_id
      actype=getattr(ncfile,'DropPlatform','')
      tail=getattr(ncfile,'DropTailNumber','')
      sounding=getattr(ncfile,'ObservationNumber','')
      id=getattr(ncfile,'SerialNumber','')
      type=getattr(ncfile,'FactoryProductCode','')
      rev=getattr(ncfile,'FactoryRevisionCode','')
      built=getattr(ncfile,'ProductionDate','')
      sens=getattr(ncfile,'PtuSensorPartNumber','')+' '+getattr(ncfile,'GpsSensorPartNumber','')
      freq=getattr(ncfile,'DropFrequency','')
      batt=getattr(ncfile,'BatteryVoltage','')
      firm=getattr(ncfile,'FactorySndFirmware','')
      shut=getattr(ncfile,'ShutoffDuration','')
      basep=getattr(ncfile,'DropPressureAddition','')
      baset=''
      baseh1=''
      baseh2=''
      dynmp=''
      dynmt=''
      dynmh=''
      pl_obs_raw=getattr(ncfile,'DropLaunchObs','')
      if pl_obs_raw:
        try:
          pl_obs = json.loads(pl_obs_raw)
        except json.JSONDecodeError:
          pl_obs={}
      else:
        pl_obs={}
      pltype=pl_obs.get('header','')
      pltime=pl_obs.get('utc','')
      plpres=pl_obs.get('static_pressure','')
      pltemp=pl_obs.get('ambient_temperature','')
      pldewp=pl_obs.get('dew_point','')
      plhumi=pl_obs.get('humidity','')
      plws=pl_obs.get('wind_speed','')
      plwd=pl_obs.get('wind_direction','')
      pllat=pl_obs.get('latitude','')
      pllon=pl_obs.get('longitude','')
      plalt=pl_obs.get('pressure_altitude','')
      oper=getattr(ncfile,'DropOperator','')
      accounting_code=getattr(ncfile,'AccountingCode','')
      comm=''
      stdcomm=getattr(ncfile,'OperatorComments','')
      bad_sonde_flag=''
      if "Good Drop" not in stdcomm:
        bad_sonde_flag = 'B'


      # Insert into flights dict as you do for D-files...
      if not flid in flights:
        flights[flid]={}
      
      sys.stdout.flush()

      if id in flights[flid]:
        existing = flights[flid][id]
        existing_channel = int (existing.get('channel', -1))
        current_channel = int(channel)
        existing_source = existing.get('source_type', '')
        sys.stdout.flush()
        if existing_source == 'D':
            # D wins – NC is renamed
            id = id + '_' + channel + '_dup'
        elif existing_source == 'NC':
            if existing_channel > current_channel:
                newid = existing['id'] + '_' + existing['channel'] + '_dup'
                existing['id'] = newid
                flights[flid][newid] = existing
                del flights[flid][id]
            else:
                id = id + '_' + channel + '_dup'

      
      flights[flid][id]={}
      flights[flid][id]['file']=name
      flights[flid][id]['channel']=channel
      flights[flid][id]['project']=project
      flights[flid][id]['mission']=mission
      flights[flid][id]['actype']=actype
      flights[flid][id]['tail']=tail
      flights[flid][id]['launch_date']=launch_date
      flights[flid][id]['launch_time']=launch_time
      flights[flid][id]['sounding']=sounding
      flights[flid][id]['id']=id
      flights[flid][id]['type']=type
      flights[flid][id]['rev']=rev
      flights[flid][id]['built']=built
      flights[flid][id]['sens']=sens
      flights[flid][id]['freq']=freq
      flights[flid][id]['batt']=batt
      flights[flid][id]['firm']=firm
      flights[flid][id]['shut']=shut
      flights[flid][id]['basep']=basep
      flights[flid][id]['baset']=baset
      flights[flid][id]['baseh1']=baseh1
      flights[flid][id]['baseh2']=baseh2
      flights[flid][id]['dynmp']=dynmp
      flights[flid][id]['dynmt']=dynmt
      flights[flid][id]['dynmh']=dynmh
      flights[flid][id]['pltype']=pltype
      flights[flid][id]['pltime']=pltime
      flights[flid][id]['plpres']=plpres
      flights[flid][id]['pltemp']=pltemp
      flights[flid][id]['pldewp']=pldewp
      flights[flid][id]['plhumi']=plhumi
      flights[flid][id]['plws']=plws
      flights[flid][id]['plwd']=plwd
      flights[flid][id]['pllat']=pllat
      flights[flid][id]['pllon']=pllon
      flights[flid][id]['plalt']=plalt
      flights[flid][id]['oper']=oper
      flights[flid][id]['comm']=comm
      flights[flid][id]['stdcomm']=stdcomm
      flights[flid][id]['source_type']='NC'
      flights[flid][id]['launch_datetime']=launch_datetime
      flights[flid][id]['accounting_code']=accounting_code
      flights[flid][id]['bad_sonde_flag']=bad_sonde_flag







master_csv_path = os.path.join(outdirname, f'all_drops_{startdatetime}.csv')
master_file = open(master_csv_path, "w")
master_file.write('flight_id,project,launch_date,launch_time,file,count,sonde_id,operator,account,bad,sounding_name,channel,tail_num,actype,std_comm,comm,sonde_type,sonde_rev,sonde_built,sens,freq,batt,firm,shut,basep,baset,baseh1,baseh2,dynmp,dynmt,dynmh,pltype,pltime,plpres,pltemp,pldewp,plhumi,plws,plwd,pllat,pllon,plalt\n')

#run through each FLID
for flid in sorted(flights):
  project=None
  mission=None
  actype=None
  tail=None
  date=None
  count=1
  #print(flid)

  of=open(outdirname+'/summary_'+startdatetime+'.txt',"a")
  of.write(flid+'\n')
  of.close()
  
  of=open(outdirname+'/'+flid+'.csv',"w")
  
  
  prev_count=0
  of.write('flight_id,project,launch_date,launch_time,file,count,sonde_id,operator,account,bad,sounding_name,channel,tail_num,actype,std_comm,comm,sonde_type,sonde_rev,sonde_built,sens,freq,batt,firm,shut,basep,baset,baseh1,baseh2,dynmp,dynmt,dynmh,pltype,pltime,plpres,pltemp,pldewp,plhumi,plws,plwd,pllat,pllon,plalt\n')
  
  
  #loop through all sonde id for a given FLID and put in new dict
  flight={}
  for id in flights[flid]:
    flight[flights[flid][id]['file']]=flights[flid][id]
  
  #sort the new struct by filename (gets R5 channels before L5 channels)
  #and write one entry per line
  for file in sorted(
    flight, 
    key=lambda f: (
      flight[f]['launch_datetime'],
      1 if flight[f]['file'].endswith('.nc') else 0 # D-files first
      )
    ):
    if flight[file]['id'][-4:] == '_dup':
      scount=str(prev_count)+'_dup'
    else:
      scount=str(count)
      prev_count=count
      count=count + 1

    outstr=flight[file]['mission'].replace(',',' ').upper()
    outstr=outstr+','+flight[file]['project'].replace(',',' ')
    outstr=outstr+','+flight[file]['launch_date'].replace(',',' ')
    outstr=outstr+','+flight[file]['launch_time'].replace(',',' ')
    outstr=outstr+','+flight[file]['file']
    outstr=outstr+','+scount
    outstr=outstr+','+flight[file]['id'].replace(',',' ')
    outstr=outstr+','+flight[file]['oper'].replace(',',' ')
    outstr=outstr+','+flight[file]['accounting_code'].replace(',',' ') # accounting code
    outstr=outstr+','+flight[file]['bad_sonde_flag'].replace(',',' ') # bad sonde flag
    outstr=outstr+','+flight[file]['sounding'].replace(',',' ')
    outstr=outstr+','+flight[file]['channel'].replace(',',' ')
    outstr=outstr+','+flight[file]['tail'].replace(',',' ')
    outstr=outstr+','+flight[file]['actype'].replace(',',' ')
    outstr=outstr+','+flight[file]['stdcomm'].replace(',',' ').replace('none','')
    outstr=outstr+','+flight[file]['comm'].replace(',',' ').replace('none','')
    outstr=outstr+','+flight[file]['type'].replace(',',' ')
    outstr=outstr+','+flight[file]['rev'].replace(',',' ')
    outstr=outstr+','+flight[file]['built'].replace(',',' ')
    outstr=outstr+','+flight[file]['sens'].replace(',',' ')
    outstr=outstr+','+flight[file]['freq'].replace(',',' ')
    outstr=outstr+','+flight[file]['batt'].replace(',',' ')
    outstr=outstr+','+flight[file]['firm'].replace(',',' ')
    outstr=outstr+','+flight[file]['shut'].replace(',',' ')
    outstr=outstr+','+flight[file]['basep'].replace(',',' ')
    outstr=outstr+','+flight[file]['baset'].replace(',',' ')
    outstr=outstr+','+flight[file]['baseh1'].replace(',',' ')
    outstr=outstr+','+flight[file]['baseh2'].replace(',',' ')
    outstr=outstr+','+flight[file]['dynmp'].replace(',',' ')
    outstr=outstr+','+flight[file]['dynmt'].replace(',',' ')
    outstr=outstr+','+flight[file]['dynmh'].replace(',',' ')
    outstr=outstr+','+flight[file]['pltype'].replace(',',' ')
    outstr=outstr+','+flight[file]['pltime'].replace(',',' ')
    outstr=outstr+','+str(flight[file]['plpres']).replace(',',' ')
    outstr=outstr+','+str(flight[file]['pltemp']).replace(',',' ')
    outstr=outstr+','+str(flight[file]['pldewp']).replace(',',' ')
    outstr=outstr+','+str(flight[file]['plhumi']).replace(',',' ')
    outstr=outstr+','+str(flight[file]['plws']).replace(',',' ')
    outstr=outstr+','+str(flight[file]['plwd']).replace(',',' ')
    outstr=outstr+','+str(flight[file]['pllat']).replace(',',' ')
    outstr=outstr+','+str(flight[file]['pllon']).replace(',',' ')
    outstr=outstr+','+str(flight[file]['plalt']).replace(',',' ')
    of.write(outstr+'\n')
    master_file.write(outstr + '\n')
    #print(outstr)

    

  #print('GENERATED : ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") )
  #print('--END--')
  #print('')
  print('CREATED: '+outdirname+'/'+flid+'.csv')
  of.close()
  
master_file.close()
print('CREATED: ' + master_csv_path)

from tkinter import messagebox
messagebox.showinfo("Information","PROGRAM COMPLETE")
