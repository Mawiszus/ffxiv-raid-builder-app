#!/usr/bin/env python

"""RaidBuilderGUI.py: Builds a viable Raid from a set of Players given their jobs."""

__author__ = "mawi"
__copyright__ = "Copyright 2019, Planet Earth"
__credits__ = ["mawi"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "mawi"
__status__ = "Production"

import tkinter as tk
from tkinter import ttk
from _tkinter import TclError
import itertools
import math
from random import randint

JOB_LIST = [
    "PLD", "WAR", "DRK",
    "WHM", "SCH", "AST",
    "MNK", "DRG", "NIN", "SAM",
    "BRD", "MCH",
    "BLM", "SMN", "RDM"]
TANKS = [0, 1, 2]
HEALERS = [3, 4, 5]
MEELE = [6, 7, 8, 9]
RANGED = [10, 11, 12, 13, 14]
DPS = MEELE + RANGED
ROLES = [TANKS, HEALERS, DPS]
COLORS = ["#2d3a80", "#346624", "#732828"]


def is_viable_raid(raid, n_tanks=2, n_healers=2, doubles_allowed=False):
    if n_tanks + n_healers > len(raid):
        # There is not enough people to fill in even Tanks and Healers you dummy!
        return False

    jobs = set(raid)

    if not doubles_allowed:
        if len(jobs) != len(raid):
            # There are doubles!
            return False

    curr_tanks = [k for k in raid if k in TANKS]
    if len(curr_tanks) != n_tanks:
        # Not the right amount of tanks!
        return False

    curr_heals = [k for k in raid if k in HEALERS]
    if len(curr_heals) != n_healers:
        # Not the right amount of healers!
        return False

    # All Checks passed, congratulations!
    return True


class Counter_program():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Raid Builder")
        self.window.resizable(0, 0)
        self.window.geometry("800x775")

        self.n_players = tk.IntVar()
        self.n_healers = tk.IntVar()
        self.n_tanks = tk.IntVar()
        self.n_dps = tk.IntVar()
        self.allow_doubles = tk.BooleanVar()
        self.framelist = []
        self.buttonlist = []
        self.checkvarlist = []
        self.nick_list = []
        self.max_players = 8
        self.res_raid_l_frames = []
        self.res_raid_label = []

        self.error_message = tk.StringVar()
        self.n_possible_raids = tk.IntVar()
        self.n_viable_raids = tk.IntVar()
        self.viable_raids = []
        self.curr_n_raid = tk.IntVar()
        self.res_raid = []

        self.create_widgets()

    def reset(self, *args):
        self.n_players.set(8)
        self.n_healers.set(2)
        self.n_tanks.set(2)
        self.n_dps.set(8-2-2)
        self.allow_doubles.set(False)
        for p in range(self.n_players.get()):
            self.nick_list[p].set("P " + str(p+1))
            for job in range(len(JOB_LIST)):
                self.checkvarlist[p][job].set(0)

        self.update()

    def create_widgets(self):
        # Create some room around all the internal frames
        self.window['padx'] = 5
        self.window['pady'] = 5

        s = ttk.Style()
        s.configure('Tank.TCheckbutton', background=COLORS[0], foreground="white")
        s.configure('Healer.TCheckbutton', background=COLORS[1], foreground="white")
        s.configure('DPS.TCheckbutton', background=COLORS[2], foreground="white")
        s.configure('Tank.TLabel', background=COLORS[0], foreground="white")
        s.configure('Healer.TLabel', background=COLORS[1], foreground="white")
        s.configure('DPS.TLabel', background=COLORS[2], foreground="white")
        s.configure('Tank.TLabelframe', background=COLORS[0], foreground="white")
        s.configure('Healer.TLabelframe', background=COLORS[1], foreground="white")
        s.configure('DPS.TLabelframe', background=COLORS[2], foreground="white")

        self.n_players.set(8)
        self.n_players.trace_add("write", self.pl_update)
        self.n_healers.set(2)
        self.n_healers.trace_add("write", self.he_update)
        self.n_tanks.set(2)
        self.n_tanks.trace_add("write", self.pl_update)
        self.n_dps.set(8-2-2)
        self.allow_doubles.set(False)
        self.allow_doubles.trace_add("write", self.update)

        window_frame = ttk.Frame(self.window)
        window_frame.pack(expand=False)

        settings_frame = ttk.LabelFrame(window_frame, text="Settings", relief=tk.RIDGE)
        settings_frame.grid(row=1, column=0, sticky=tk.N + tk.S, pady=5)

        # Number of:
        set_n_frame = tk.Frame(settings_frame)
        set_n_frame.grid(row=1, column=0, sticky=tk.N + tk.S, padx=2)

        # Number of Players
        n_pl_label = ttk.Label(set_n_frame, text="Players", justify=tk.CENTER)
        n_pl_label.grid(row=0, column=1, sticky=tk.N + tk.S, pady=3, padx=2)

        n_pl_spinbox = tk.Spinbox(set_n_frame, textvariable=self.n_players, width=3,
                                  from_=1, to=self.max_players, justify=tk.CENTER)
        n_pl_spinbox.grid(row=1, column=1, sticky=tk.N + tk.S, pady=5, padx=5)

        # Number of Tanks
        n_ta_label = ttk.Label(set_n_frame, text="Tanks", background="#2d3a80", foreground="white")
        n_ta_label.grid(row=0, column=2, sticky=tk.N + tk.S, pady=3, padx=2)

        n_ta_spinbox = tk.Spinbox(set_n_frame, textvariable=self.n_tanks, width=3,
                                  from_=0, to=self.max_players, justify=tk.CENTER)
        n_ta_spinbox.grid(row=1, column=2, sticky=tk.N + tk.S, pady=5, padx=5)

        # Number of Healers
        n_he_label = ttk.Label(set_n_frame, text="Healers", background="#346624", foreground="white")
        n_he_label.grid(row=0, column=3, sticky=tk.N + tk.S, pady=3, padx=2)

        n_he_spinbox = tk.Spinbox(set_n_frame, textvariable=self.n_healers, width=3,
                                  from_=0, to=self.max_players, justify=tk.CENTER)
        n_he_spinbox.grid(row=1, column=3, sticky=tk.N + tk.S, pady=5, padx=5)

        # Number of DPS
        n_he_label = ttk.Label(set_n_frame, text="DPS", background="#732828", foreground="white")
        n_he_label.grid(row=0, column=4, sticky=tk.N + tk.S, pady=3, padx=2)

        n_he_label = ttk.Label(set_n_frame, textvariable=self.n_dps)
        n_he_label.grid(row=1, column=4, sticky=tk.N + tk.S, pady=3, padx=5)

        # Allow Doubles Checkbox
        all_doub_box = ttk.Checkbutton(settings_frame, text="Allow double jobs", variable=self.allow_doubles)
        all_doub_box.grid(row=2, column=0, sticky=tk.W, padx=3, pady=1)

        # --------

        my_button = tk.Button(window_frame, text="Reset", command=self.reset)
        my_button.grid(row=3, column=0, sticky=tk.N + tk.S, pady=5, padx=5)

        # - - - - - - - - - - - - - - - - - - - - -
        player_frame = ttk.Frame(window_frame, width=500)
        player_frame.grid(row=2, column=0, sticky=tk.N + tk.S)

        # Make new lists
        self.checkvarlist = []
        self.framelist = []
        self.buttonlist = []
        self.nick_list = []
        for p in range(self.max_players):
            self.framelist.append(ttk.LabelFrame(player_frame, text="Player " + str(p+1), relief=tk.RIDGE))
            self.framelist[p].grid(row=1, column=p, sticky=tk.N + tk.S, padx=5, pady=5)
            self.buttonlist.append([])
            self.checkvarlist.append([])
            roleframelist = []
            for role in range(3):  # 0 is Tanks, 1 is Healers, 2 is DPS
                roleframelist.append(tk.Frame(self.framelist[p], background=COLORS[role]))
                roleframelist[role].grid(row=role+2, column=1,
                                         sticky=tk.N + tk.S + tk.W + tk.E, padx=3, pady=3)
                for job in ROLES[role]:
                    self.checkvarlist[p].append(tk.IntVar(value=0))
                    self.checkvarlist[p][job].trace_add("write", self.update)
                    if job in TANKS:
                        sty = 'Tank.TCheckbutton'
                    elif job in HEALERS:
                        sty = 'Healer.TCheckbutton'
                    else:
                        sty = 'DPS.TCheckbutton'

                    self.buttonlist[p].append(ttk.Checkbutton(roleframelist[role], text=JOB_LIST[job],
                                                              variable=self.checkvarlist[p][job], style=sty))
                    self.buttonlist[p][job].grid(row=job, column=1, sticky=tk.W, padx=3, pady=1)
            pl_label = ttk.Label(self.framelist[p], text="Nickname:")
            pl_label.grid(row=0, column=1, sticky=tk.W, padx=1, pady=1)
            self.nick_list.append(tk.StringVar(value="P " + str(p+1)))
            # self.nick_list[p].trace_add("write", self.redraw_res_raid())
            pl_entry = ttk.Entry(self.framelist[p], textvariable=self.nick_list[p], width=10,
                                 validate="focusout", validatecommand=self.redraw_res_raid)
            pl_entry.grid(row=1, column=1, sticky=tk.W + tk.N, padx=5, pady=5)

        # - - - - - - - - - - - - - - - - - - - - -

        self.n_possible_raids.set(0)
        self.n_viable_raids.set(0)
        self.curr_n_raid.set(0)
        self.curr_n_raid.trace_add("write", self.redraw_res_raid)

        res_frame = ttk.LabelFrame(window_frame, text="Results")
        res_frame.grid(row=4, column=0, sticky=tk.N + tk.S)

        res_num_frame = ttk.Frame(res_frame)
        res_num_frame.grid(row=1, column=0, sticky=tk.N + tk.S)

        pos_label = ttk.Label(res_num_frame, text="Possible combinations: ")
        pos_label.grid(row=0, column=0, sticky=tk.W + tk.N + tk.S, pady=3)

        n_pos_label = ttk.Label(res_num_frame, textvariable=self.n_possible_raids)
        n_pos_label.grid(row=0, column=1, sticky=tk.E + tk.N + tk.S, pady=3)

        via_label = ttk.Label(res_num_frame, text="Of which are viable: ")
        via_label.grid(row=1, column=0, sticky=tk.W + tk.N + tk.S, pady=3)

        n_via_label = ttk.Label(res_num_frame, textvariable=self.n_viable_raids)
        n_via_label.grid(row=1, column=1, sticky=tk.E + tk.N + tk.S, pady=3)

        # - - - - - - - - - - - - - - - - - - - - -

        # Show a Raid Composition
        raid_frame = ttk.LabelFrame(res_frame, text="Your Raid is:")
        raid_frame.grid(row=2, column=0, sticky=tk.N + tk.S, pady=5, padx=5)

        raid_label_frame = ttk.Frame(raid_frame)
        raid_label_frame.grid(row=1, column=0, sticky=tk.N + tk.S)

        # Make new lists
        self.res_raid_l_frames = []
        self.res_raid = []
        self.res_raid_label = []
        for p in range(self.max_players):
            self.res_raid_l_frames.append(ttk.LabelFrame(raid_label_frame, text=self.nick_list[p].get()))
            self.res_raid_l_frames[p].grid(row=1, column=p, sticky=tk.N + tk.S, padx=5, pady=5)
            self.res_raid.append(tk.StringVar(value="None"))
            self.res_raid_label.append(ttk.Label(self.res_raid_l_frames[p],
                                                 textvariable=self.res_raid[p], anchor="center"))
            self.res_raid_label[p].pack(fill="both", ipadx=1, ipady=1, padx=1, pady=1)

        # Which Raid is it?
        raid_rand_frame = ttk.Frame(raid_frame)
        raid_rand_frame.grid(row=2, column=0, sticky=tk.N + tk.S)

        r1_label = ttk.Label(raid_rand_frame, text="This is raid ")
        r1_label.grid(row=1, column=0, sticky=tk.N + tk.S, pady=3, padx=3)

        r2_spinbox = tk.Spinbox(raid_rand_frame, textvariable=self.curr_n_raid, width=8,
                                from_=1, to=math.pow(len(JOB_LIST), self.max_players), justify=tk.CENTER)
        r2_spinbox.grid(row=1, column=1, sticky=tk.N + tk.S, pady=5, padx=5)

        r3_label = ttk.Label(raid_rand_frame, text="/")
        r3_label.grid(row=1, column=2, sticky=tk.N + tk.S, pady=3, padx=1)

        r4_label = ttk.Label(raid_rand_frame, textvariable=self.n_viable_raids)
        r4_label.grid(row=1, column=3, sticky=tk.N + tk.S, pady=3, padx=3)

        # Randomize me
        r5_button = tk.Button(raid_rand_frame, text="Randomize", command=self.randomize_raid)
        r5_button.grid(row=1, column=4, sticky=tk.N + tk.S, pady=5, padx=5)

        # - - - - - - - - - - - - - -

        # set window to current size so it won't change!

    def redraw_players(self, *args):
        # Hide unused players
        for p in range(len(self.framelist)):
            if p > (self.n_players.get() - 1):
                self.framelist[p].grid_remove()
            else:
                self.framelist[p].grid()
            for job in range(len(self.buttonlist[p])):
                if p > (self.n_players.get() - 1):
                    self.buttonlist[p][job].grid_remove()
                else:
                    self.buttonlist[p][job].grid()

        for p in range(len(self.res_raid_l_frames)):
            if p > (self.n_players.get() - 1):
                self.res_raid_l_frames[p].grid_remove()
                self.res_raid_label[p].pack_forget()
            else:
                self.res_raid_l_frames[p].grid()
                self.res_raid_label[p].pack(fill="both", ipadx=1, ipady=1, padx=1, pady=1)

    def redraw_res_raid(self, *args):
        if not self.res_raid:
            # We are still in init
            self.error_message.set("init")
        else:
            if self.n_viable_raids.get() <= 0:
                self.curr_n_raid.set(0)
                for p in range(self.max_players):
                    self.res_raid[p].set("None")
                    self.res_raid_label[p].configure(style='TLabel', anchor="center")
                    self.res_raid_l_frames[p].configure(text=self.nick_list[p].get())
            else:
                try:
                    if self.curr_n_raid.get() > self.n_viable_raids.get():
                        self.curr_n_raid.set(self.n_viable_raids.get())
                    elif self.curr_n_raid.get() <= 0:
                        self.curr_n_raid.set(1)
                    for p in range(self.n_players.get()):
                        self.res_raid[p].set(JOB_LIST[self.viable_raids[self.curr_n_raid.get() - 1][p]])
                        if self.viable_raids[self.curr_n_raid.get() - 1][p] in TANKS:
                            sty1 = 'Tank.TLabel'
                        elif self.viable_raids[self.curr_n_raid.get() - 1][p] in HEALERS:
                            sty1 = 'Healer.TLabel'
                        else:
                            sty1 = 'DPS.TLabel'
                        self.res_raid_label[p].configure(style=sty1, anchor="center")
                        self.res_raid_l_frames[p].configure(text=self.nick_list[p].get())
                except TclError:
                    if self.n_viable_raids.get() <= 0:
                        self.curr_n_raid.set(0)

    def randomize_raid(self, *args):
        self.curr_n_raid.set(randint(0, self.n_viable_raids.get()))
        self.redraw_res_raid()

    def pl_update(self, *args):
        try:
            if self.n_players.get() <= 1:
                self.n_players.set(1)
            elif self.n_players.get() >= self.max_players:
                self.n_players.set(self.max_players)
        except TclError:
            self.n_players.set(1)

        try:
            if self.n_tanks.get() <= 0:
                self.n_tanks.set(0)
            elif self.n_tanks.get() >= self.n_players.get():
                self.n_tanks.set(self.n_players.get())
        except TclError:
            self.n_tanks.set(0)

        try:
            if self.n_healers.get() <= 0:
                self.n_healers.set(0)
            elif self.n_healers.get() >= (self.n_players.get() - self.n_tanks.get()):
                self.n_healers.set(self.n_players.get() - self.n_tanks.get())
        except TclError:
            self.n_healers.set(0)

        self.n_dps.set(self.n_players.get() - self.n_tanks.get() - self.n_healers.get())

        self.redraw_players()
        self.update()

    def he_update(self, *args):
        try:
            if self.n_healers.get() <= 0:
                self.n_healers.set(0)
            elif self.n_healers.get() >= self.n_players.get():
                self.n_healers.set(self.n_players.get())
        except TclError:
            self.n_healers.set(0)

        try:
            if self.n_tanks.get() <= 0:
                self.n_tanks.set(0)
            elif self.n_tanks.get() >= (self.n_players.get() - self.n_healers.get()):
                self.n_tanks.set(self.n_players.get() - self.n_healers.get())
        except TclError:
            self.n_tanks.set(0)

        self.n_dps.set(self.n_players.get() - self.n_tanks.get() - self.n_healers.get())

        self.redraw_players()
        self.update()

    def update(self, *args):
        self.calculate_raids()
        self.redraw_res_raid()

    def calculate_raids(self):
        if not self.checkvarlist:
            # We are still in init
            self.n_possible_raids.set(0)
            self.n_viable_raids.set(0)
        else:
            # Add playable jobs per player
            player_jobs = []
            for p in range(self.n_players.get()):
                player_jobs.append([])
                for job in range(len(JOB_LIST)):
                    if self.checkvarlist[p][job].get():
                        player_jobs[p].append(job)

            # Max Possible:
            comb_max = 1
            for i in range(self.n_players.get()):
                comb_max = comb_max * len(player_jobs[i])
            self.n_possible_raids.set(comb_max)

            self.viable_raids = []
            for curr_raid in itertools.product(*player_jobs):
                if is_viable_raid(curr_raid, self.n_tanks.get(), self.n_healers.get(), self.allow_doubles.get()):
                    self.viable_raids.append(curr_raid)
            self.n_viable_raids.set(len(self.viable_raids))

            if self.n_viable_raids.get() > 0:
                self.curr_n_raid.set(1)


# Create the entire GUI program
program = Counter_program()

# Start the GUI event loop
program.window.mainloop()
