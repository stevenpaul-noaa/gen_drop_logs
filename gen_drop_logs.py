import os
import sys
import datetime
import json
import re
import threading
import tkinter as tk
from tkinter import filedialog
from netCDF4 import Dataset

# Suppress customtkinter font warning (printed to stderr)
_devnull = open(os.devnull, 'w')
_stdout, _stderr = sys.stdout, sys.stderr
sys.stdout = sys.stderr = _devnull
import customtkinter as ctk
sys.stdout, sys.stderr = _stdout, _stderr
_devnull.close()

from tkcalendar import Calendar

import configparser

# ── Theme ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SCAN_DEFAULT = r'\\10.10.60.240\aoc-storage\AVAPS\Data\Archive'
NOW          = datetime.datetime.now(datetime.timezone.utc)
CONFIG_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen_drop_logs.cfg')

AIRCRAFT_OPTIONS = {
    "A – All aircraft":         "A",
    "H – N42":                  "H",
    "I – N43":                  "I",
    "N – N49":                  "N",
    "O – Other (not H, I, N)":  "O",
}
AIRCRAFT_CODES_INV = {v: k for k, v in AIRCRAFT_OPTIONS.items()}

def load_config():
    """Return config defaults, reading from file if it exists."""
    cfg = configparser.ConfigParser()
    defaults = {
        'scan_dir':   SCAN_DEFAULT + '\\' + NOW.strftime("%Y"),
        'out_dir':    os.getcwd(),
        'last_end':   '',          # empty = first run
        'aircraft':   'A',
    }
    if os.path.exists(CONFIG_PATH):
        cfg.read(CONFIG_PATH)
        s = cfg['settings'] if 'settings' in cfg else {}
        defaults['scan_dir']  = s.get('scan_dir',  defaults['scan_dir'])
        defaults['out_dir']   = s.get('out_dir',   defaults['out_dir'])
        defaults['last_end']  = s.get('last_end',  defaults['last_end'])
        defaults['aircraft']  = s.get('aircraft',  defaults['aircraft'])
    return defaults

def save_config(scan_dir, out_dir, end_date, aircraft_code):
    """Save current run settings to config file."""
    cfg = configparser.ConfigParser()
    cfg['settings'] = {
        'scan_dir':  scan_dir,
        'out_dir':   out_dir,
        'last_end':  end_date,
        'aircraft':  aircraft_code,
    }
    with open(CONFIG_PATH, 'w') as f:
        cfg.write(f)

# ── GUI ───────────────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AVAPS Drop Log Generator")
        self.geometry("600x580")
        self.resizable(False, False)

        # ── Load config ───────────────────────────────────────────────────────
        cfg = load_config()

        # Derive start date: last_end + 1 day, or Jan 1 of current year
        if cfg['last_end']:
            try:
                last_end_dt = datetime.datetime.strptime(cfg['last_end'], "%Y%m%d")
                default_start = (last_end_dt + datetime.timedelta(days=1)).strftime("%Y%m%d")
            except ValueError:
                default_start = NOW.strftime("%Y") + "0101"
        else:
            default_start = NOW.strftime("%Y") + "0101"

        default_end      = NOW.strftime("%Y%m%d")
        default_scan     = cfg['scan_dir']
        default_out      = cfg['out_dir']
        default_aircraft = AIRCRAFT_CODES_INV.get(cfg['aircraft'], list(AIRCRAFT_OPTIONS.keys())[0])

        FONT        = "Consolas"
        FONT_LABEL  = ctk.CTkFont(family=FONT, size=11, weight="bold")
        FONT_ENTRY  = ctk.CTkFont(family=FONT, size=11)
        FONT_LOG    = ctk.CTkFont(family=FONT, size=10)
        FONT_HEADER = ctk.CTkFont(family=FONT, size=16, weight="bold")
        FONT_SUB    = ctk.CTkFont(family=FONT, size=10)
        FONT_BTN    = ctk.CTkFont(family=FONT, size=13, weight="bold")
        FONT_SMBTN  = ctk.CTkFont(family=FONT, size=11)

        C_BG        = "#0d1b2a"
        C_HEADER    = "#0a1628"
        C_BORDER    = "#1565c0"
        C_HOVER     = "#1e88e5"
        C_TEXT      = "#e0f7fa"
        C_LABEL     = "#78909c"
        C_ACCENT    = "#4fc3f7"
        C_DIM       = "#546e7a"
        C_LOG_BG    = "#060e1a"

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=C_HEADER, corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(header, text="AVAPS Drop Log Generator",
                     font=FONT_HEADER, text_color=C_ACCENT).pack(pady=(14, 2))
        ctk.CTkLabel(header, text="NOAA Aircraft Operations Center",
                     font=FONT_SUB, text_color=C_DIM).pack(pady=(0, 12))

        # ── Form ──────────────────────────────────────────────────────────────
        PAD = 24
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=PAD, pady=(16, 8))
        form.columnconfigure(1, weight=1)

        ROW_PAD = (6, 0)

        def lbl(text, row):
            ctk.CTkLabel(form, text=text, anchor="w", width=120,
                         font=FONT_LABEL, text_color=C_LABEL).grid(
                row=row, column=0, sticky="w", pady=ROW_PAD)

        def path_entry(var, row):
            e = ctk.CTkEntry(form, textvariable=var, height=34,
                             font=FONT_ENTRY, fg_color=C_BG,
                             border_color=C_BORDER, text_color=C_TEXT)
            e.grid(row=row, column=1, sticky="ew", pady=ROW_PAD, padx=(8, 0))
            return e

        # Scan directory
        lbl("Scan Directory", 0)
        self.scan_var = tk.StringVar(value=default_scan)
        scan_entry = path_entry(self.scan_var, 0)

        def pick_scan(_event=None):
            initial = self.scan_var.get().replace('/', '\\') or SCAN_DEFAULT
            d = filedialog.askdirectory(initialdir=initial)
            if d:
                self.scan_var.set(d.replace('/', '\\'))

        scan_entry.bind("<Button-1>", pick_scan)

        # Output directory — click to browse, no button
        lbl("Output Directory", 1)
        self.out_var = tk.StringVar(value=default_out)
        out_entry = path_entry(self.out_var, 1)

        def pick_out(_event=None):
            d = filedialog.askdirectory(initialdir=self.out_var.get() or os.getcwd())
            if d:
                self.out_var.set(d.replace('/', '\\'))

        out_entry.bind("<Button-1>", pick_out)

        # ── Date + Aircraft row ───────────────────────────────────────────────
        bot = ctk.CTkFrame(form, fg_color="transparent")
        bot.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        bot.columnconfigure((1, 4), weight=1)

        self.start_var = tk.StringVar(value=default_start)
        self.end_var   = tk.StringVar(value=default_end)

        def open_cal(var, title):
            try:
                current = datetime.datetime.strptime(var.get(), "%Y%m%d")
            except ValueError:
                current = NOW
            top = tk.Toplevel(self)
            top.title(title)
            top.grab_set()
            top.resizable(False, False)
            top.configure(bg=C_BG)
            cal = Calendar(top, selectmode="day",
                           year=current.year, month=current.month, day=current.day,
                           background=C_BG, foreground=C_TEXT,
                           bordercolor=C_BORDER,
                           headersbackground=C_HEADER, headersforeground=C_ACCENT,
                           selectbackground=C_BORDER, selectforeground="#ffffff",
                           normalbackground=C_BG, normalforeground=C_TEXT,
                           weekendbackground=C_BG, weekendforeground=C_TEXT,
                           othermonthbackground=C_LOG_BG, othermonthforeground=C_DIM,
                           disabledforeground=C_DIM, firstweekday="sunday",
                           font=(FONT, 10), date_pattern="yyyymmdd")
            cal.pack(padx=10, pady=10)
            ctk.CTkButton(top, text="Select", font=FONT_SMBTN,
                          fg_color=C_BORDER, hover_color=C_HOVER,
                          command=lambda: [var.set(cal.get_date()), top.destroy()]
                          ).pack(pady=(0, 10))

        # Start date
        ctk.CTkLabel(bot, text="Start Date", font=FONT_LABEL,
                     text_color=C_LABEL).grid(row=0, column=0, sticky="w", padx=(0, 6))
        ctk.CTkEntry(bot, textvariable=self.start_var, width=100, height=34,
                     font=FONT_ENTRY, fg_color=C_BG,
                     border_color=C_BORDER, text_color=C_TEXT).grid(row=0, column=1, sticky="ew")
        ctk.CTkButton(bot, text="📅", width=34, height=34,
                      fg_color=C_BORDER, hover_color=C_HOVER, font=FONT_SMBTN,
                      command=lambda: open_cal(self.start_var, "Start Date")).grid(
            row=0, column=2, padx=(4, 16))

        # End date
        ctk.CTkLabel(bot, text="End Date", font=FONT_LABEL,
                     text_color=C_LABEL).grid(row=0, column=3, sticky="w", padx=(0, 6))
        ctk.CTkEntry(bot, textvariable=self.end_var, width=100, height=34,
                     font=FONT_ENTRY, fg_color=C_BG,
                     border_color=C_BORDER, text_color=C_TEXT).grid(row=0, column=4, sticky="ew")
        ctk.CTkButton(bot, text="📅", width=34, height=34,
                      fg_color=C_BORDER, hover_color=C_HOVER, font=FONT_SMBTN,
                      command=lambda: open_cal(self.end_var, "End Date")).grid(
            row=0, column=5, padx=(4, 0))

        # Aircraft — manual dropdown to avoid arrow rendering issue
        lbl("Aircraft", 3)
        self.aircraft_display = tk.StringVar(value=default_aircraft)

        ac_frame = ctk.CTkFrame(form, fg_color=C_BG, border_color=C_BORDER,
                                border_width=2, corner_radius=6)
        ac_frame.grid(row=3, column=1, columnspan=2, sticky="ew",
                      padx=(8, 0), pady=(10, 4))
        ac_frame.columnconfigure(0, weight=1)

        ac_label = ctk.CTkLabel(ac_frame, textvariable=self.aircraft_display,
                                font=FONT_ENTRY, text_color=C_TEXT, anchor="w",
                                height=30)
        ac_label.grid(row=0, column=0, sticky="ew", padx=(8, 0), pady=2)

        ac_arrow = ctk.CTkLabel(ac_frame, text="▾", font=ctk.CTkFont(size=16),
                                text_color=C_TEXT, width=30, height=30)
        ac_arrow.grid(row=0, column=1, padx=(0, 4), pady=2)

        def show_ac_menu(_event=None):
            menu = tk.Menu(self, tearoff=0, bg=C_BG, fg=C_TEXT,
                           activebackground=C_BORDER, activeforeground=C_TEXT,
                           font=("Consolas", 11), bd=0, relief="flat")
            for display, code in AIRCRAFT_OPTIONS.items():
                menu.add_command(label=display,
                                 command=lambda d=display: self.aircraft_display.set(d))
            x = ac_frame.winfo_rootx()
            y = ac_frame.winfo_rooty() + ac_frame.winfo_height()
            menu.tk_popup(x, y)

        ac_label.bind("<Button-1>", show_ac_menu)
        ac_arrow.bind("<Button-1>", show_ac_menu)
        ac_frame.bind("<Button-1>", show_ac_menu)


        # ── Log area ──────────────────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color="#1a2a3a").pack(fill="x", padx=PAD, pady=(8, 0))

        self.log = ctk.CTkTextbox(self, font=FONT_LOG,
                                  fg_color=C_LOG_BG, text_color=C_ACCENT,
                                  border_color="#1a2a3a", border_width=1,
                                  state="disabled")
        self.log.pack(fill="both", expand=True, padx=PAD, pady=(8, 0))

        # ── Run button ────────────────────────────────────────────────────────
        self.run_btn = ctk.CTkButton(self, text="▶  Generate Logs", height=42,
                                     font=FONT_BTN, fg_color=C_BORDER,
                                     hover_color=C_HOVER, corner_radius=6,
                                     command=self.start_run)
        self.run_btn.pack(fill="x", padx=PAD, pady=12)

        self.log_line("Ready.")


    # ── Logging ───────────────────────────────────────────────────────────────
    def log_line(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.update_idletasks()

    # ── Validation ────────────────────────────────────────────────────────────
    def validate(self):
        errors = []
        if not self.scan_var.get():
            errors.append("• Scan directory is required.")
        if not self.out_var.get():
            errors.append("• Output directory is required.")
        for label, var in [("Start date", self.start_var), ("End date", self.end_var)]:
            v = var.get()
            if not re.match(r'^\d{8}$', v):
                errors.append(f"• {label} must be YYYYMMDD (8 digits).")
        if errors:
            dlg = ctk.CTkToplevel(self)
            dlg.title("Input Error")
            dlg.geometry("340x180")
            dlg.grab_set()
            ctk.CTkLabel(dlg, text="\n".join(errors),
                         text_color="#ef5350",
                         font=ctk.CTkFont(size=12),
                         justify="left").pack(padx=20, pady=20)
            ctk.CTkButton(dlg, text="OK", command=dlg.destroy).pack(pady=4)
            return False
        return True

    # ── Run ───────────────────────────────────────────────────────────────────
    def start_run(self):
        if not self.validate():
            return
        self.run_btn.configure(state="disabled", text="⏳  Running…")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        threading.Thread(target=self.run_processing, daemon=True).start()

    def run_processing(self):
        scandirname  = self.scan_var.get()
        outdirname   = self.out_var.get()
        start_date   = self.start_var.get()
        end_date     = self.end_var.get()
        AIRCRAFT     = AIRCRAFT_OPTIONS[self.aircraft_display.get()]
        startdatetime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")

        try:
            flights = {}

            for root_dir, dirs, files in os.walk(scandirname, topdown=False):
                mission_folder = os.path.basename(root_dir)
                if len(mission_folder) >= 2:
                    mission_folder_code = mission_folder[-2]
                else:
                    mission_folder_code = ''

                if AIRCRAFT != 'A':
                    if AIRCRAFT == 'O':
                        if mission_folder_code in ('H', 'I', 'N'):
                            continue
                    elif AIRCRAFT != mission_folder_code:
                        continue

                for name in sorted(files):
                    # ── D-file ────────────────────────────────────────────────
                    if name[0] == 'D' and len(name) == 18:
                        dateint = int(name[1:9])
                        if dateint < int(start_date) or dateint > int(end_date):
                            continue

                        pattern = r'^D(\d{8})_(\d{6})\..+$'
                        m = re.match(pattern, name)
                        launch_datetime = f"{m.group(1)}T{m.group(2)}" if m else None

                        self.log_line(name)
                        flid = os.path.basename(root_dir).upper()
                        file_path = os.path.join(root_dir, name)

                        (field, data, channel, project, mission, actype, tail,
                         launch_date, launch_time, sounding, sonde_id, sonde_type,
                         rev, built, sens, freq, batt, firm, shut,
                         basep, baset, baseh1, baseh2, dynmp, dynmt, dynmh,
                         pltype, pltime, plpres, pltemp, pldewp, plhumi,
                         plws, plwd, pllat, pllon, plalt, oper, comm, stdcomm) = (
                            '', '', '', '', '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '', '', '', '', '', '', '')

                        with open(file_path, "r") as f:
                            for line in f:
                                if line[0:7] == 'AVAPS-T' and line[9:14] == ' COM ' and ':' in line:
                                    field_data = line.split(' COM ', 1)[1].strip()
                                    if ':' in field_data:
                                        field, data = field_data.split(':', 1)
                                        field = field.strip()
                                        data  = data.strip()

                                        def sp(n): return data.split(',')[n].strip() if len(data.split(',')) > n else ''

                                        if field == 'Data Type/Data Channel':
                                            ch_raw = sp(1)
                                            channel = ch_raw.split('Channel ')[1] if 'Channel ' in ch_raw else ch_raw
                                        elif field == 'Project Name/Mission ID':
                                            project = sp(0)
                                            mission = sp(1)
                                        elif field == 'Aircraft Type/ID':
                                            actype = sp(0)
                                            tail   = sp(1)
                                        elif field == 'Launch Time (y,m,d,h,m,s)':
                                            launch_date = sp(0)
                                            launch_time = sp(1)
                                        elif field == 'Sounding Name':
                                            sounding = data
                                        elif field == 'Sonde ID/Type/Rev/Built/Sensors':
                                            parts = data.split(',', 4)
                                            sonde_id   = parts[0].strip() if len(parts) > 0 else ''
                                            sonde_type = parts[1].strip() if len(parts) > 1 else ''
                                            rev        = parts[2].strip() if len(parts) > 2 else ''
                                            built      = parts[3].strip() if len(parts) > 3 else ''
                                            sens       = parts[4].strip() if len(parts) > 4 else ''
                                        elif field == 'Sonde Freq/Batt/Firmware/Shutoff':
                                            freq = sp(0)
                                            batt = sp(1)
                                            firm = sp(2)
                                            shut = sp(3)
                                        elif field == 'Sonde Baseline Errors (p,t,h1,h2)':
                                            basep  = sp(0)
                                            baset  = sp(1)
                                            baseh1 = sp(2)
                                            baseh2 = sp(3)
                                        elif field == 'Sonde Dynamic Errors  (p,t,h)':
                                            dynmp = sp(0)
                                            dynmt = sp(1)
                                            dynmh = sp(2)
                                        elif field == 'Pre-launch Obs Data System/Time':
                                            pltype = sp(0)
                                            pltime = sp(1)
                                        elif field == 'Pre-launch Obs (p,t,d,h)':
                                            plpres = sp(0)
                                            pltemp = sp(1)
                                            pldewp = sp(2)
                                            plhumi = sp(3)
                                        elif field == 'Pre-launch Obs (wd,ws)':
                                            plws = sp(0)
                                            plwd = sp(1)
                                        elif field == 'Pre-launch Obs (lon,lat,alt)':
                                            pllon = sp(0)
                                            pllat = sp(1)
                                            plalt = sp(2)
                                        elif field == 'Operator Name/Comments':
                                            parts = data.split(',', 1)
                                            oper = parts[0].strip()
                                            comm = parts[1].strip() if len(parts) > 1 else ''
                                        elif field == 'Standard Comments':
                                            stdcomm = data

                        if flid not in flights:
                            flights[flid] = {}

                        if sonde_id in flights[flid]:
                            existing = flights[flid][sonde_id]
                            existing_channel = int(existing.get('channel', -1))
                            current_channel  = int(channel)
                            existing_source  = existing.get('source_type', '')

                            if existing_source == 'NC':
                                new_id = existing['sonde_id'] + '_' + existing['channel'] + '_dup'
                                existing['sonde_id'] = new_id
                                flights[flid][new_id] = existing
                                del flights[flid][sonde_id]
                            elif existing_source == 'D':
                                if existing_channel > current_channel:
                                    new_id = existing['sonde_id'] + '_' + existing['channel'] + '_dup'
                                    existing['sonde_id'] = new_id
                                    flights[flid][new_id] = existing
                                    del flights[flid][sonde_id]
                                else:
                                    sonde_id = sonde_id + '_' + channel + '_dup'

                        bad_sonde_flag = '' if "Good Drop" in stdcomm else 'B'

                        flights[flid][sonde_id] = {
                            'file': name, 'channel': channel, 'project': project,
                            'mission': mission, 'actype': actype, 'tail': tail,
                            'launch_date': launch_date, 'launch_time': launch_time,
                            'sounding': sounding, 'sonde_id': sonde_id,
                            'type': sonde_type, 'rev': rev, 'built': built, 'sens': sens,
                            'freq': freq, 'batt': batt, 'firm': firm, 'shut': shut,
                            'basep': basep, 'baset': baset, 'baseh1': baseh1, 'baseh2': baseh2,
                            'dynmp': dynmp, 'dynmt': dynmt, 'dynmh': dynmh,
                            'pltype': pltype, 'pltime': pltime, 'plpres': plpres,
                            'pltemp': pltemp, 'pldewp': pldewp, 'plhumi': plhumi,
                            'plws': plws, 'plwd': plwd, 'pllat': pllat, 'pllon': pllon,
                            'plalt': plalt, 'oper': oper, 'comm': comm, 'stdcomm': stdcomm,
                            'source_type': 'D', 'launch_datetime': launch_datetime,
                            'accounting_code': '', 'bad_sonde_flag': bad_sonde_flag,
                        }

                    # ── NetCDF ────────────────────────────────────────────────
                    elif name.endswith(".nc"):
                        pattern = r"^([A-Za-z0-9_-]+)-([^-]*)-([0-9]+)-([A-Za-z0-9_-]+)-([0-9]+)\.nc$"
                        m = re.match(pattern, name)
                        if not m:
                            self.log_line(f"SKIP (pattern mismatch): {name}")
                            continue

                        project_name = m.group(4)
                        mission_id   = m.group(1)
                        channel      = m.group(5)
                        filedate     = m.group(2)

                        launch_date_raw = launch_time_raw = launch_datetime = ""
                        dateint = 0
                        launch_date = launch_time = ""

                        if filedate:
                            launch_date_raw = filedate[:8]
                            launch_time_raw = filedate[9:]
                            launch_datetime = filedate
                            dateint     = int(launch_date_raw)
                            launch_date = f"{launch_date_raw[4:6]}/{launch_date_raw[6:]}/{launch_date_raw[:4]}"
                            launch_time = f"{launch_time_raw[:2]}:{launch_time_raw[2:4]}:{launch_time_raw[4:]}"
                        else:
                            flid_tmp  = os.path.basename(root_dir).upper()
                            fp_tmp    = os.path.join(root_dir, name)
                            ncfile_tmp = None
                            try:
                                ncfile_tmp = Dataset(fp_tmp, 'r')
                                dcd = getattr(ncfile_tmp, 'DropCreationDate', '')
                                if dcd:
                                    parsed = datetime.datetime.strptime(dcd.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                                    launch_datetime = parsed.strftime("%Y%m%d%H%M%S")
                                    launch_date_raw = parsed.strftime("%Y%m%d")
                                    dateint     = int(launch_date_raw)
                                    launch_date = parsed.strftime("%m/%d/%Y")
                                    launch_time = parsed.strftime("%H:%M:%S")
                                    self.log_line(f"DropCreationDate used for {name}")
                            except Exception as e:
                                self.log_line(f"Date fallback error {name}: {e}")
                            finally:
                                if ncfile_tmp:
                                    ncfile_tmp.close()

                        if dateint < int(start_date) or dateint > int(end_date):
                            continue

                        self.log_line(name)
                        flid      = os.path.basename(root_dir).upper()
                        file_path = os.path.join(root_dir, name)
                        ncfile    = None

                        try:
                            ncfile = Dataset(file_path, 'r')

                            project    = project_name
                            mission    = mission_id
                            actype     = getattr(ncfile, 'DropPlatform', '')
                            tail       = getattr(ncfile, 'DropTailNumber', '')
                            sounding   = getattr(ncfile, 'ObservationNumber', '')
                            sonde_id   = getattr(ncfile, 'SerialNumber', '')
                            sonde_type = getattr(ncfile, 'FactoryProductCode', '')
                            rev        = getattr(ncfile, 'FactoryRevisionCode', '')
                            built      = getattr(ncfile, 'ProductionDate', '')
                            sens       = (getattr(ncfile, 'PtuSensorPartNumber', '') + ' ' +
                                          getattr(ncfile, 'GpsSensorPartNumber', ''))
                            freq       = getattr(ncfile, 'DropFrequency', '')
                            batt       = getattr(ncfile, 'BatteryVoltage', '')
                            firm       = getattr(ncfile, 'FactorySndFirmware', '')
                            shut       = getattr(ncfile, 'ShutoffDuration', '')
                            basep      = getattr(ncfile, 'DropPressureAddition', '')
                            baset = baseh1 = baseh2 = dynmp = dynmt = dynmh = ''

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
                            plws   = pl_obs.get('wind_speed', '')
                            plwd   = pl_obs.get('wind_direction', '')
                            pllat  = pl_obs.get('latitude', '')
                            pllon  = pl_obs.get('longitude', '')
                            plalt  = pl_obs.get('pressure_altitude', '')

                            oper            = getattr(ncfile, 'DropOperator', '')
                            accounting_code = getattr(ncfile, 'AccountingCode', '')
                            comm            = ''
                            stdcomm         = getattr(ncfile, 'OperatorComments', '')
                            bad_sonde_flag  = '' if "Good Drop" in stdcomm else 'B'

                            if flid not in flights:
                                flights[flid] = {}

                            if sonde_id in flights[flid]:
                                existing = flights[flid][sonde_id]
                                existing_channel = int(existing.get('channel', -1))
                                current_channel  = int(channel)
                                existing_source  = existing.get('source_type', '')

                                if existing_source == 'D':
                                    sonde_id = sonde_id + '_' + channel + '_dup'
                                elif existing_source == 'NC':
                                    if existing_channel > current_channel:
                                        new_id = existing['sonde_id'] + '_' + existing['channel'] + '_dup'
                                        existing['sonde_id'] = new_id
                                        flights[flid][new_id] = existing
                                        del flights[flid][sonde_id]
                                    else:
                                        sonde_id = sonde_id + '_' + channel + '_dup'

                            flights[flid][sonde_id] = {
                                'file': name, 'channel': channel, 'project': project,
                                'mission': mission, 'actype': actype, 'tail': tail,
                                'launch_date': launch_date, 'launch_time': launch_time,
                                'sounding': sounding, 'sonde_id': sonde_id,
                                'type': sonde_type, 'rev': rev, 'built': built, 'sens': sens,
                                'freq': freq, 'batt': batt, 'firm': firm, 'shut': shut,
                                'basep': basep, 'baset': baset, 'baseh1': baseh1, 'baseh2': baseh2,
                                'dynmp': dynmp, 'dynmt': dynmt, 'dynmh': dynmh,
                                'pltype': pltype, 'pltime': pltime, 'plpres': plpres,
                                'pltemp': pltemp, 'pldewp': pldewp, 'plhumi': plhumi,
                                'plws': plws, 'plwd': plwd, 'pllat': pllat, 'pllon': pllon,
                                'plalt': plalt, 'oper': oper, 'comm': comm, 'stdcomm': stdcomm,
                                'source_type': 'NC', 'launch_datetime': launch_datetime,
                                'accounting_code': accounting_code, 'bad_sonde_flag': bad_sonde_flag,
                            }

                        except Exception as e:
                            self.log_line(f"ERROR {name}: {e}")
                        finally:
                            if ncfile:
                                ncfile.close()

            # ── Write outputs ─────────────────────────────────────────────────
            output_year  = datetime.datetime.strptime(start_date, "%Y%m%d").year
            year_out_dir = os.path.join(outdirname, str(output_year))
            os.makedirs(year_out_dir, exist_ok=True)

            master_csv_path   = os.path.join(year_out_dir, f'all_drops_{startdatetime}.csv')
            flid_summary_path = os.path.join(year_out_dir, f'summary_{startdatetime}.txt')

            HEADER = ('flight_id,project,launch_date,launch_time,file,count,sonde_id,'
                      'operator,account,bad,sounding_name,channel,tail_num,actype,'
                      'std_comm,comm,sonde_type,sonde_rev,sonde_built,sens,freq,batt,'
                      'firm,shut,basep,baset,baseh1,baseh2,dynmp,dynmt,dynmh,'
                      'pltype,pltime,plpres,pltemp,pldewp,plhumi,plws,plwd,pllat,pllon,plalt\n')

            with open(master_csv_path, "w") as master_file, \
                 open(flid_summary_path, "w") as flid_summary_file:

                master_file.write(HEADER)

                for flid in sorted(flights):
                    count = prev_count = 1
                    flid_summary_file.write(flid + '\n')
                    self.log_line(f'Processing FLID: {flid}')

                    flight_drops_sorted = sorted(
                        flights[flid].values(),
                        key=lambda d: (
                            d['launch_datetime'],
                            1 if d['file'].endswith('.nc') else 0
                        )
                    )

                    for drop in flight_drops_sorted:
                        sid = drop['sonde_id']
                        if sid.endswith('_dup'):
                            scount = str(prev_count) + '_dup'
                        else:
                            scount     = str(count)
                            prev_count = count
                            count     += 1

                        def c(v):
                            return str(v).replace(',', ' ').replace('none', '')

                        row = ','.join([
                            c(drop['mission']).upper(), c(drop['project']),
                            c(drop['launch_date']), c(drop['launch_time']),
                            drop['file'], scount, c(sid),
                            c(drop['oper']), c(drop['accounting_code']),
                            c(drop['bad_sonde_flag']), c(drop['sounding']),
                            c(drop['channel']), c(drop['tail']), c(drop['actype']),
                            c(drop['stdcomm']), c(drop['comm']),
                            c(drop['type']), c(drop['rev']), c(drop['built']),
                            c(drop['sens']), c(drop['freq']), c(drop['batt']),
                            c(drop['firm']), c(drop['shut']),
                            c(drop['basep']), c(drop['baset']),
                            c(drop['baseh1']), c(drop['baseh2']),
                            c(drop['dynmp']), c(drop['dynmt']), c(drop['dynmh']),
                            c(drop['pltype']), c(drop['pltime']),
                            c(drop['plpres']), c(drop['pltemp']),
                            c(drop['pldewp']), c(drop['plhumi']),
                            c(drop['plws']), c(drop['plwd']),
                            c(drop['pllat']), c(drop['pllon']), c(drop['plalt']),
                        ])
                        master_file.write(row + '\n')

            self.log_line(f'✓ CREATED: {master_csv_path}')
            self.log_line(f'✓ CREATED: {flid_summary_path}')
            self.log_line('─' * 48)
            self.log_line('COMPLETE.')

            # ── Save config ───────────────────────────────────────────────────
            save_config(
                scan_dir     = scandirname,
                out_dir      = outdirname,
                end_date     = end_date,
                aircraft_code= AIRCRAFT,
            )

            self.show_done(master_csv_path, flid_summary_path)

        except Exception as e:
            self.log_line(f'FATAL ERROR: {e}')

        finally:
            self.run_btn.configure(state="normal", text="▶  Generate Logs")

    # ── Completion dialog ─────────────────────────────────────────────────────
    def show_done(self, csv_path, txt_path):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Complete")
        dlg.geometry("400x200")
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="✓  Processing Complete",
                     font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
                     text_color="#4fc3f7").pack(pady=(20, 6))

        ctk.CTkLabel(dlg,
                     text=f"CSV:  {os.path.basename(csv_path)}\nTXT:   {os.path.basename(txt_path)}",
                     font=ctk.CTkFont(family="Consolas", size=10),
                     text_color="#90a4ae",
                     justify="left").pack(padx=20)

        ctk.CTkButton(dlg, text="OK", width=100,
                      font=ctk.CTkFont(family="Consolas", size=11),
                      fg_color="#1565c0", hover_color="#1e88e5",
                      command=dlg.destroy).pack(pady=20)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
