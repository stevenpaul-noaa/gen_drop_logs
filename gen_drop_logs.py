import os
import sys
import datetime

import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
#scandirname = filedialog.askdirectory(initialdir='E:/AVAPSDATA/',  title='INPUT SCAN DIRECTORY')
#scandirname = filedialog.askdirectory(initialdir='\\\\10.10.60.240/aoc-storage/SEB-Engineering/AVAPS/Mirrors',  title='INPUT SCAN DIRECTORY')
scandirname = filedialog.askdirectory(initialdir='\\\\10.10.60.240/aoc-storage/AVAPS/Data/Mirrors',  title='INPUT SCAN DIRECTORY')
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
minis={}
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
      ptu=''
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
            pllat= data.split(',')[0].strip()
            pllon= data.split(',')[1].strip()
            plalt= data.split(',')[2].strip()
          elif field == 'Operator Name/Comments':
            oper= data.split(',',1)[0].strip()
            comm= data.split(',',1)[1].strip()
          elif field == 'Standard Comments':
            stdcomm=data
        #endif (line[0:7] == 'AVAPS-T') and (line[9:14] == ' COM '):
      #endfor line in f:
      f.close()

      if type == '2':
        if not flid in minis:
          minis[flid]=[name]
        else:
          minis[flid].append(name)

      if not flid in flights:
        flights[flid]={}
      
      idch=name[0:len(name)-2]
      #print('IDCH IS: '+idch)
      #print('ID IS: ' + id)
      sys.stdout.flush()
      if id in flights[flid]:
        #print(id +' is present')
        #print('curr_channel: '+channel)
        #print('id_channel: '+flights[flid][id]['channel'])
        sys.stdout.flush()
        if int(flights[flid][id]['channel']) > int(channel):
          newid=flights[flid][id]['id']+'_'+flights[flid][id]['channel']+'_dup'
          flights[flid][id]['id']=newid
          #print('new id: '+ flights[flid][id]['id'])
          flights[flid][newid]={}
          flights[flid][newid]=flights[flid].pop(id)
        else:
          id=id+'_'+channel+'_dup'
      
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

  master_file.write(outstr + '\n')


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
  for file in sorted(flight):
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
    outstr=outstr+','
    outstr=outstr+','
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
    outstr=outstr+','+flight[file]['plpres'].replace(',',' ')
    outstr=outstr+','+flight[file]['pltemp'].replace(',',' ')
    outstr=outstr+','+flight[file]['pldewp'].replace(',',' ')
    outstr=outstr+','+flight[file]['plhumi'].replace(',',' ')
    outstr=outstr+','+flight[file]['plws'].replace(',',' ')
    outstr=outstr+','+flight[file]['plwd'].replace(',',' ')
    outstr=outstr+','+flight[file]['pllat'].replace(',',' ')
    outstr=outstr+','+flight[file]['pllon'].replace(',',' ')
    outstr=outstr+','+flight[file]['plalt'].replace(',',' ')
    of.write(outstr+'\n')
    #print(outstr)

    

  #print('GENERATED : ' + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") )
  #print('--END--')
  #print('')
  print('CREATED: '+outdirname+'/'+flid+'.csv')
  of.close()
  
master_file.close()
print('CREATED: ' + master_csv_path)


        
      
print('--BEGIN-- MINI SONDE MISSIONS & DROPS')
for flid in sorted(minis):
  print(flid)
  for file in minis[flid]:
    print(file)
print('--END-- MINI SONDE MISSIONS & DROPS')

from tkinter import messagebox
messagebox.showinfo("Information","PROGRAM COMPLETE")