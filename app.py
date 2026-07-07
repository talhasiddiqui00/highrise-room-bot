"""
Highrise Room Management Bot - Main Core Engine (app.py)
With Anti-Duplication Locks, Debouncing, and Initialization Guards.
"""

import os
import sys
import time
import random
import asyncio
import threading
import requests
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from json import load, dump

from highrise import BaseBot, User, Position, AnchorPosition, SessionMetadata, CurrencyItem, Item
from highrise.__main__ import main, BotDefinition

sys.stdout.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

ROOM_ID = "6a28b5b000b6151bd4c9641e"
API_TOKEN = "fd250294097b09a7fd05aa523c63b77ef0b980cc28f7f09742b22d0db30b53a0"
DATA_FILE = "./data.json"

# --- Permanent storage via GitHub Gist (survives Render redeploys/restarts) ---
# Set these in Render's Environment tab. If left blank, the bot falls back to
# local-disk-only storage (the old behavior, which resets on redeploy).
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GIST_ID = os.environ.get("GIST_ID", "").strip()
GIST_FILENAME = "data.json"

TIP_MAP = {
    "1g": "gold_bar_1", "5g": "gold_bar_5", "10g": "gold_bar_10", 
    "50g": "gold_bar_50", "100g": "gold_bar_100", "500g": "gold_bar_500",
    "1k": "gold_bar_1k", "5k": "gold_bar_5k", "10k": "gold_bar_10k"
}

# Regular tipping (!give / !giveall / auto-tips) is capped at 100g max.
TIP_ALLOWED = {"1g", "5g", "10g", "50g", "100g"}

# !withdraw accepts larger denominations, with a few common ways of writing them.
WITHDRAW_ALIASES = {
    "500": "500g", "500g": "500g",
    "1k": "1k", "1kg": "1k",
    "5k": "5k", "5kg": "5k",
    "10k": "10k", "10kg": "10k",
}



EMOTE_MAP = {
    1:   {"name": "rest",             "id": "sit-open",                        "duration": 17.062613},
    2:   {"name": "zombie",           "id": "idle_zombie",                      "duration": 28.754937},
    3:   {"name": "relaxed",          "id": "idle_layingdown2",                 "duration": 21.546653},
    4:   {"name": "attentive",        "id": "idle_layingdown",                  "duration": 24.585168},
    5:   {"name": "sleepy",           "id": "idle-sleep",                       "duration": 22.620446},
    6:   {"name": "poutyface",        "id": "idle-sad",                         "duration": 24.377214},
    7:   {"name": "posh",             "id": "idle-posh",                        "duration": 21.851256},
    8:   {"name": "tired",            "id": "idle-loop-tired",                  "duration": 21.959007},
    9:   {"name": "taploop",          "id": "idle-loop-tapdance",               "duration": 6.261593},
    10:  {"name": "sit",              "id": "idle-loop-sitfloor",               "duration": 22.321055},
    11:  {"name": "shy",              "id": "idle-loop-shy",                    "duration": 16.47449},
    12:  {"name": "bummed",           "id": "idle-loop-sad",                    "duration": 6.052999},
    13:  {"name": "chillin",          "id": "idle-loop-happy",                  "duration": 18.798322},
    14:  {"name": "annoyed",          "id": "idle-loop-annoyed",                "duration": 17.058522},
    15:  {"name": "aerobics",         "id": "idle-loop-aerobics",               "duration": 8.507535},
    16:  {"name": "ponder",           "id": "idle-lookup",                      "duration": 22.339865},
    17:  {"name": "heropose",         "id": "idle-hero",                        "duration": 21.877099},
    18:  {"name": "relaxing",         "id": "idle-floorsleeping2",              "duration": 17.253372},
    19:  {"name": "cozynap",          "id": "idle-floorsleeping",               "duration": 13.935264},
    20:  {"name": "enthused",         "id": "idle-enthusiastic",                "duration": 15.941537},
    21:  {"name": "feelthebeat",      "id": "idle-dance-headbobbing",           "duration": 25.367458},
    22:  {"name": "irritated",        "id": "idle-angry",                       "duration": 25.427848},
    23:  {"name": "fastsing",         "id": "emote-sicklycute-sing-fast",       "duration": 10.0},
    24:  {"name": "slowsing",         "id": "emote-sicklycute-sing-slow",       "duration": 10.0},
    25:  {"name": "yes",              "id": "emote-yes",                        "duration": 2.565001},
    26:  {"name": "ibelieveicanfly",  "id": "emote-wings",                      "duration": 13.134487},
    27:  {"name": "thewave",          "id": "emote-wave",                       "duration": 2.690873},
    28:  {"name": "think",            "id": "emote-think",                      "duration": 3.691104},
    29:  {"name": "theatrical",       "id": "emote-theatrical",                 "duration": 8.591869},
    30:  {"name": "tapdance",         "id": "emote-tapdance",                   "duration": 11.057294},
    31:  {"name": "superrun",         "id": "emote-superrun",                   "duration": 6.273226},
    32:  {"name": "superpunch",       "id": "emote-superpunch",                 "duration": 3.751054},
    33:  {"name": "sumofight",        "id": "emote-sumo",                       "duration": 10.868834},
    34:  {"name": "thumbsuck",        "id": "emote-suckthumb",                  "duration": 4.185944},
    35:  {"name": "splitsdrop",       "id": "emote-splitsdrop",                 "duration": 4.46931},
    36:  {"name": "snowballfight",    "id": "emote-snowball",                   "duration": 5.230467},
    37:  {"name": "snowangel",        "id": "emote-snowangel",                  "duration": 6.218627},
    38:  {"name": "handshake",        "id": "emote-secrethandshake",            "duration": 3.879024},
    39:  {"name": "sad",              "id": "emote-sad",                        "duration": 5.411073},
    40:  {"name": "pull",             "id": "emote-ropepull",                   "duration": 8.769656},
    41:  {"name": "roll",             "id": "emote-roll",                       "duration": 3.560517},
    42:  {"name": "rofl",             "id": "emote-rofl",                       "duration": 6.314731},
    43:  {"name": "robot",            "id": "emote-robot",                      "duration": 7.607362},
    44:  {"name": "rainbow",          "id": "emote-rainbow",                    "duration": 2.813373},
    45:  {"name": "proposing",        "id": "emote-proposing",                  "duration": 4.27888},
    46:  {"name": "peekaboo",         "id": "emote-peekaboo",                   "duration": 3.629867},
    47:  {"name": "peace",            "id": "emote-peace",                      "duration": 5.755004},
    48:  {"name": "panic",            "id": "emote-panic",                      "duration": 2.850966},
    49:  {"name": "no",               "id": "emote-no",                         "duration": 2.703034},
    50:  {"name": "ninjarun",         "id": "emote-ninjarun",                   "duration": 4.754721},
    51:  {"name": "nightfever",       "id": "emote-nightfever",                 "duration": 5.488424},
    52:  {"name": "monsterfail",      "id": "emote-monster_fail",               "duration": 4.632708},
    53:  {"name": "model",            "id": "emote-model",                      "duration": 6.490173},
    54:  {"name": "levelup",          "id": "emote-levelup",                    "duration": 6.0545},
    55:  {"name": "amused",           "id": "emote-laughing2",                  "duration": 5.056641},
    56:  {"name": "laugh",            "id": "emote-laughing",                   "duration": 2.69161},
    57:  {"name": "kiss",             "id": "emote-kiss",                       "duration": 2.387175},
    58:  {"name": "superkick",        "id": "emote-kicking",                    "duration": 4.867992},
    59:  {"name": "jump",             "id": "emote-jumpb",                      "duration": 3.584234},
    60:  {"name": "judochop",         "id": "emote-judochop",                   "duration": 2.427442},
    61:  {"name": "jetpack",          "id": "emote-jetpack",                    "duration": 16.759457},
    62:  {"name": "hugyourself",      "id": "emote-hugyourself",                "duration": 4.992751},
    63:  {"name": "sweating",         "id": "emote-hot",                        "duration": 4.353037},
    64:  {"name": "hello",            "id": "emote-hello",                      "duration": 2.734844},
    65:  {"name": "harlemshake",      "id": "emote-harlemshake",                "duration": 13.558597},
    66:  {"name": "happy",            "id": "emote-happy",                      "duration": 3.483462},
    67:  {"name": "handstand",        "id": "emote-handstand",                  "duration": 4.015678},
    68:  {"name": "greedyemote",      "id": "emote-greedy",                     "duration": 4.639828},
    69:  {"name": "moonwalk",         "id": "emote-gordonshuffle",              "duration": 8.052307},
    70:  {"name": "ghostfloat",       "id": "emote-ghost-idle",                 "duration": 19.570492},
    71:  {"name": "gangnamstyle",     "id": "emote-gangnam",                    "duration": 7.275486},
    72:  {"name": "faint",            "id": "emote-fainting",                   "duration": 18.423499},
    73:  {"name": "clumsy",           "id": "emote-fail2",                      "duration": 6.475972},
    74:  {"name": "fall",             "id": "emote-fail1",                      "duration": 5.617942},
    75:  {"name": "facepalm",         "id": "emote-exasperatedb",               "duration": 2.722748},
    76:  {"name": "exasperated",      "id": "emote-exasperated",                "duration": 2.367483},
    77:  {"name": "elbowbump",        "id": "emote-elbowbump",                  "duration": 3.799768},
    78:  {"name": "disco",            "id": "emote-disco",                      "duration": 5.366973},
    79:  {"name": "blastoff",         "id": "emote-disappear",                  "duration": 6.195985},
    80:  {"name": "faintdrop",        "id": "emote-deathdrop",                  "duration": 3.762728},
    81:  {"name": "collapse",         "id": "emote-death2",                     "duration": 4.855549},
    82:  {"name": "revival",          "id": "emote-death",                      "duration": 6.615967},
    83:  {"name": "dab",              "id": "emote-dab",                        "duration": 2.717871},
    84:  {"name": "curtsy",           "id": "emote-curtsy",                     "duration": 2.425714},
    85:  {"name": "confusion",        "id": "emote-confused",                   "duration": 8.578827},
    86:  {"name": "cold",             "id": "emote-cold",                       "duration": 3.664348},
    87:  {"name": "charging",         "id": "emote-charging",                   "duration": 8.025079},
    88:  {"name": "bunnyhop",         "id": "emote-bunnyhop",                   "duration": 12.380685},
    89:  {"name": "bow",              "id": "emote-bow",                        "duration": 3.344036},
    90:  {"name": "boo",              "id": "emote-boo",                        "duration": 4.501502},
    91:  {"name": "homerun",          "id": "emote-baseball",                   "duration": 7.254841},
    92:  {"name": "fallingapart",     "id": "emote-apart",                      "duration": 4.809542},
    93:  {"name": "thumbsup",         "id": "emoji-thumbsup",                   "duration": 2.702369},
    94:  {"name": "point",            "id": "emoji-there",                      "duration": 2.059095},
    95:  {"name": "sneeze",           "id": "emoji-sneeze",                     "duration": 2.996694},
    96:  {"name": "smirk",            "id": "emoji-smirking",                   "duration": 4.823158},
    97:  {"name": "sick",             "id": "emoji-sick",                       "duration": 5.070367},
    98:  {"name": "gasp",             "id": "emoji-scared",                     "duration": 3.008487},
    99:  {"name": "punch",            "id": "emoji-punch",                      "duration": 1.755783},
    100: {"name": "pray",             "id": "emoji-pray",                       "duration": 4.503179},
    101: {"name": "stinky",           "id": "emoji-poop",                       "duration": 4.795735},
    102: {"name": "naughty",          "id": "emoji-naughty",                    "duration": 4.277602},
    103: {"name": "mindblown",        "id": "emoji-mind-blown",                 "duration": 2.397167},
    104: {"name": "lying",            "id": "emoji-lying",                      "duration": 6.313748},
    105: {"name": "levitate",         "id": "emoji-halo",                       "duration": 5.837754},
    106: {"name": "fireballlunge",    "id": "emoji-hadoken",                    "duration": 2.723709},
    107: {"name": "giveup",           "id": "emoji-give-up",                    "duration": 5.407888},
    108: {"name": "tummyache",        "id": "emoji-gagging",                    "duration": 5.500202},
    109: {"name": "stunned",          "id": "emoji-dizzy",                      "duration": 4.053049},
    110: {"name": "sob",              "id": "emoji-crying",                     "duration": 3.696499},
    111: {"name": "clap",             "id": "emoji-clapping",                   "duration": 2.161757},
    112: {"name": "raisetheroof",     "id": "emoji-celebrate",                  "duration": 3.412258},
    113: {"name": "arrogance",        "id": "emoji-arrogance",                  "duration": 6.869441},
    114: {"name": "angry",            "id": "emoji-angry",                      "duration": 5.760023},
    115: {"name": "voguehands",       "id": "dance-voguehands",                 "duration": 9.150634},
    116: {"name": "savagedance",      "id": "dance-tiktok8",                    "duration": 10.938702},
    117: {"name": "dontstartnow",     "id": "dance-tiktok2",                    "duration": 10.392353},
    118: {"name": "smoothwalk",       "id": "dance-smoothwalk",                 "duration": 6.690023},
    119: {"name": "ringonit",         "id": "dance-singleladies",               "duration": 21.191372},
    120: {"name": "letsgoshopping",   "id": "dance-shoppingcart",               "duration": 4.316035},
    121: {"name": "russian",          "id": "dance-russian",                    "duration": 10.252905},
    122: {"name": "pennywise",        "id": "dance-pennywise",                  "duration": 1.214349},
    123: {"name": "orangejuicedance", "id": "dance-orangejustice",              "duration": 6.475263},
    124: {"name": "rockout",          "id": "dance-metal",                      "duration": 15.076377},
    125: {"name": "macarena",         "id": "dance-macarena",                   "duration": 12.214141},
    126: {"name": "handsintheair",    "id": "dance-handsup",                    "duration": 22.283413},
    127: {"name": "duckwalk",         "id": "dance-duckwalk",                   "duration": 11.748784},
    128: {"name": "kpopdance",        "id": "dance-blackpink",                  "duration": 7.150958},
    129: {"name": "pushups",          "id": "dance-aerobics",                   "duration": 8.796402},
    130: {"name": "hyped",            "id": "emote-hyped",                      "duration": 7.492423},
    131: {"name": "jinglebell",       "id": "dance-jinglebell",                 "duration": 11.0},
    132: {"name": "nervous",          "id": "idle-nervous",                     "duration": 21.714221},
    133: {"name": "toilet",           "id": "idle-toilet",                      "duration": 32.174447},
    134: {"name": "attention",        "id": "emote-attention",                  "duration": 4.401206},
    135: {"name": "astronaut",        "id": "emote-astronaut",                  "duration": 13.791175},
    136: {"name": "dancezombie",      "id": "dance-zombie",                     "duration": 12.922772},
    137: {"name": "ghost",            "id": "emoji-ghost",                      "duration": 3.472759},
    138: {"name": "hearteyes",        "id": "emote-hearteyes",                  "duration": 4.034386},
    139: {"name": "swordfight",       "id": "emote-swordfight",                 "duration": 5.914365},
    140: {"name": "timejump",         "id": "emote-timejump",                   "duration": 4.007305},
    141: {"name": "snake",            "id": "emote-snake",                      "duration": 5.262578},
    142: {"name": "heartfingers",     "id": "emote-heartfingers",               "duration": 4.001974},
    143: {"name": "heartshape",       "id": "emote-heartshape",                 "duration": 6.232394},
    144: {"name": "hug",              "id": "emote-hug",                        "duration": 3.503262},
    145: {"name": "eyeroll",          "id": "emoji-eyeroll",                    "duration": 3.020264},
    146: {"name": "embarrassed",      "id": "emote-embarrassed",                "duration": 7.414283},
    147: {"name": "float",            "id": "emote-float",                      "duration": 8.995302},
    148: {"name": "telekinesis",      "id": "emote-telekinesis",                "duration": 10.492032},
    149: {"name": "sexydance",        "id": "dance-sexy",                       "duration": 12.30883},
    150: {"name": "puppet",           "id": "emote-puppet",                     "duration": 16.325823},
    151: {"name": "fighteridle",      "id": "idle-fighter",                     "duration": 17.19123},
    152: {"name": "penguindance",     "id": "dance-pinguin",                    "duration": 11.58291},
    153: {"name": "creepypuppet",     "id": "dance-creepypuppet",               "duration": 6.416121},
    154: {"name": "sleigh",           "id": "emote-sleigh",                     "duration": 11.333165},
    155: {"name": "maniac",           "id": "emote-maniac",                     "duration": 4.906886},
    156: {"name": "energyball",       "id": "emote-energyball",                 "duration": 7.575354},
    157: {"name": "singing",          "id": "idle_singing",                     "duration": 10.260182},
    158: {"name": "frog",             "id": "emote-frog",                       "duration": 14.55257},
    159: {"name": "superpose",        "id": "emote-superpose",                  "duration": 4.530791},
    160: {"name": "cute",             "id": "emote-cute",                       "duration": 6.170464},
    161: {"name": "tiktokdance9",     "id": "dance-tiktok9",                    "duration": 11.892918},
    162: {"name": "weirddance",       "id": "dance-weird",                      "duration": 21.556237},
    163: {"name": "tiktokdance10",    "id": "dance-tiktok10",                   "duration": 8.225648},
    164: {"name": "pose7",            "id": "emote-pose7",                      "duration": 4.655283},
    165: {"name": "pose8",            "id": "emote-pose8",                      "duration": 4.808806},
    166: {"name": "casualdance",      "id": "idle-dance-casual",                "duration": 9.079756},
    167: {"name": "pose1",            "id": "emote-pose1",                      "duration": 2.825795},
    168: {"name": "pose3",            "id": "emote-pose3",                      "duration": 5.10562},
    169: {"name": "pose5",            "id": "emote-pose5",                      "duration": 4.621532},
    170: {"name": "cutey",            "id": "emote-cutey",                      "duration": 3.26032},
    171: {"name": "punkguitar",       "id": "emote-punkguitar",                 "duration": 9.365807},
    172: {"name": "zombierun",        "id": "emote-zombierun",                  "duration": 9.182984},
    173: {"name": "fashionista",      "id": "emote-fashionista",                "duration": 5.606485},
    174: {"name": "gravity",          "id": "emote-gravity",                    "duration": 8.955966},
    175: {"name": "icecreamdance",    "id": "dance-icecream",                   "duration": 14.769573},
    176: {"name": "wrongdance",       "id": "dance-wrong",                      "duration": 12.422389},
    177: {"name": "uwu",              "id": "idle-uwu",                         "duration": 24.761968},
    178: {"name": "tiktokdance4",     "id": "idle-dance-tiktok4",               "duration": 15.500708},
    179: {"name": "advancedshy",      "id": "emote-shy2",                       "duration": 4.989278},
    180: {"name": "animedance",       "id": "dance-anime",                      "duration": 8.46671},
    181: {"name": "kawaii",           "id": "dance-kawai",                      "duration": 10.290789},
    182: {"name": "scritchy",         "id": "idle-wild",                        "duration": 26.422824},
    183: {"name": "iceskating",       "id": "emote-iceskating",                 "duration": 7.299156},
    184: {"name": "surprisebig",      "id": "emote-pose6",                      "duration": 5.375124},
    185: {"name": "celebrationstep",  "id": "emote-celebrationstep",            "duration": 3.353703},
    186: {"name": "creepycute",       "id": "emote-creepycute",                 "duration": 7.902453},
    187: {"name": "frustrated",       "id": "emote-frustrated",                 "duration": 5.584622},
    188: {"name": "pose10",           "id": "emote-pose10",                     "duration": 3.989871},
    189: {"name": "sitrelaxed",       "id": "sit-relaxed",                      "duration": 29.889858},
    190: {"name": "laidback",         "id": "sit-open",                         "duration": 26.025963},
    191: {"name": "slap",             "id": "emote-slap",                       "duration": 2.724945},
    192: {"name": "boxer",            "id": "emote-boxer",                      "duration": 5.555702},
    193: {"name": "headblowup",       "id": "emote-headblowup",                 "duration": 11.667537},
    194: {"name": "tiktok7",          "id": "idle-dance-tiktok7",               "duration": 12.956484},
    195: {"name": "shrink",           "id": "emote-shrink",                     "duration": 8.738784},
    196: {"name": "ditzypose",        "id": "emote-pose9",                      "duration": 4.583117},
    197: {"name": "teleporting",      "id": "emote-teleporting",                "duration": 11.7676},
    198: {"name": "touch",            "id": "dance-touch",                      "duration": 11.7},
    199: {"name": "airguitar",        "id": "idle-guitar",                      "duration": 13.229398},
    200: {"name": "thisisforyou",     "id": "emote-gift",                       "duration": 5.8},
    201: {"name": "pushit",           "id": "dance-employee",                   "duration": 8.0},
    202: {"name": "sweetsmooch",      "id": "emote-kissing",                    "duration": 5.0},
    203: {"name": "tiktok11",         "id": "dance-tiktok11",                   "duration": 11.0},
    204: {"name": "cutesalute",       "id": "emote-cutesalute",                 "duration": 3.0},
    205: {"name": "salute",           "id": "emote-salute",                     "duration": 3.0},
    206: {"name": "tough",            "id": "idle_tough",                       "duration": 28.643417},
    207: {"name": "fail3",            "id": "emote-fail3",                      "duration": 7.062429},
    208: {"name": "confused2",        "id": "emote-confused2",                  "duration": 10.056858},
    209: {"name": "disappointed",     "id": "emote-receive-disappointed",       "duration": 7.139604},
    210: {"name": "mine",             "id": "mining-mine",                      "duration": 5.022986},
    211: {"name": "miningsuccess",    "id": "mining-success",                   "duration": 3.105142},
    212: {"name": "miningfail",       "id": "mining-fail",                      "duration": 3.411112},
    213: {"name": "fishing",          "id": "fishing-idle",                     "duration": 17.870053},
    214: {"name": "fishingcast",      "id": "fishing-cast",                     "duration": 2.820928},
    215: {"name": "fishingpull",      "id": "fishing-pull",                     "duration": 2.809936},
    216: {"name": "catch",            "id": "fishing-pull-small",               "duration": 3.669087},
    217: {"name": "hipshake",         "id": "dance-hipshake",                   "duration": 13.383699},
    218: {"name": "fruity",           "id": "dance-fruity",                     "duration": 18.25285},
    219: {"name": "cheer",            "id": "dance-cheerleader",                "duration": 17.928509},
    220: {"name": "magnetic",         "id": "dance-tiktok14",                   "duration": 11.197176},
    221: {"name": "fairytwirl",       "id": "emote-looping",                    "duration": 9.886148},
    222: {"name": "fairyfloat",       "id": "idle-floating",                    "duration": 27.596596},
    223: {"name": "karma",            "id": "dance-wild",                       "duration": 16.25053},
    224: {"name": "moonlithowl",      "id": "emote-howl",                       "duration": 8.101369},
    225: {"name": "howl",             "id": "idle-howl",                        "duration": 48.618348},
    226: {"name": "trampoline",       "id": "emote-trampoline",                 "duration": 6.105925},
    227: {"name": "launch",           "id": "emote-launch",                     "duration": 10.881689},
    228: {"name": "stargazing",       "id": "emote-stargazer",                  "duration": 7.928274},
    229: {"name": "hotcocoa",         "id": "emote-holding-hot-cocoa",          "duration": 3.873471},
    230: {"name": "mittens",          "id": "emote-mittens",                    "duration": 3.16982},
    231: {"name": "monestdance",      "id": "emote-littlemonsters-dance",       "duration": 15.0},
    232: {"name": "thinkfloating",    "id": "emote-threadexchange-floating",    "duration": 10.0},
    233: {"name": "justvibe",         "id": "emote-jewelrise-vibing",           "duration": 10.0},
    234: {"name": "groundsit",        "id": "emote-pose-sit",                   "duration": 8.97},
    235: {"name": "coolstand",        "id": "emote-pose-stand1",                "duration": 8.92},
    236: {"name": "gothpose1",        "id": "emote-pose-goth1",                 "duration": 10.0},
    237: {"name": "gothpose2",        "id": "emote-pose-goth2",                 "duration": 10.0},
    238: {"name": "gothpose3",        "id": "emote-pose-goth3",                 "duration": 10.0},
    239: {"name": "bloompose1",       "id": "emote-bloomify-pose1",             "duration": 10.0},
    240: {"name": "bloompose2",       "id": "emote-bloomify-pose2",             "duration": 10.0},
    241: {"name": "bloompose3",       "id": "emote-bloomify-pose3",             "duration": 10.0},
    242: {"name": "sugarpose1",       "id": "emote-sugarbite-pose1",            "duration": 15.0},
    243: {"name": "sugarpose2",       "id": "emote-sugarbite-pose2",            "duration": 15.0},
    244: {"name": "sugarpose3",       "id": "emote-sugarbite-pose3",            "duration": 15.0},
    245: {"name": "punkpose1",        "id": "emote-punkandlaces-pose1",         "duration": 4.0},
    246: {"name": "punkpose2",        "id": "emote-punkandlaces-pose2",         "duration": 4.0},
    247: {"name": "punkpose3",        "id": "emote-punkandlaces-pose3",         "duration": 4.0},
    248: {"name": "backoff",          "id": "emote-offdutyangels-backoff",      "duration": 6.0},
    249: {"name": "comehere",         "id": "emote-offdutyangels-comehere",     "duration": 6.0},
    250: {"name": "spiderman",        "id": "emote-spiderman",                  "duration": 10.0},
    251: {"name": "daydreaming",      "id": "emote-idle-daydreaming",           "duration": 12.0},
    252: {"name": "ragdoll",          "id": "emote-ragdoll",                    "duration": 15.0},
    253: {"name": "littlemonsters",   "id": "emote-littlemonsters-dance",       "duration": 15.0},
    254: {"name": "kawaiipose",       "id": "emote-kawaiipose",                 "duration": 10.0},
}

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/get_vips":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            vips = Bot.instance.vip_users if Bot.instance else []
            self.wfile.write(json.dumps({"vip_users": vips}).encode())
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot Engine Live")
            
    def log_message(self, format, *args):
        return

class Bot(BaseBot):
    instance = None

    def __init__(self):
        super().__init__()
        Bot.instance = self
        self.bot_id = None
        self.owner_id = None
        self.owner_username = "sadi_key"
        self.extra_owners = {}  # Users granted owner access via !giveowner (id -> username)
        self.dj_access = []  # Users granted DJ booth access via !givedj
        
        # --- LOCKS TO PREVENT DUPLICATION ---
        self.is_initialized = False 
        self.last_command_time = {} 
        self.announcement_task = None 
        # ------------------------------------

        self.tip_data = {}
        self.vip_users = []
        self.welcome_payouts = []
        self._gist_dirty = False
        self._gist_pending_data = None
        
        self.load_database_file()

        self.vip_spawn_points = [
            Position(26.75, 23.0, 23.35, facing="FrontRight"),
            Position(19.00070, 23.0, 33.99, facing="FrontRight"),
            Position(27.5, 23.0, 30.0, facing="FrontRight")
        ]
        self.ground_spawn_position = Position(27.0, 0.5, 34.0, facing="FrontRight")
        self.floor1_position = Position(26.0, 8.0, 33.0, facing="FrontRight")
        self.floor2_position = Position(26.0, 15.5, 33.0, facing="FrontRight")
        self.dj_booth_position = Position(19.0, 23.0, 39.0, facing="FrontRight")

        self.active_emote_loops = {}
        self.tip_queue = asyncio.Queue()
        self.room_stay_tracker = {}
        self.welcome_in_progress = set()  # Prevent duplicate welcome messages
        self.vip_guests = set()  # Users temporarily brought to VIP lounge via !bring

    def _gist_configured(self) -> bool:
        return bool(GITHUB_TOKEN and GIST_ID)

    def _gist_headers(self) -> dict:
        return {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }

    def fetch_gist_data(self):
        """Pull the saved JSON blob from the Gist. Returns dict or None on any failure."""
        try:
            resp = requests.get(
                f"https://api.github.com/gists/{GIST_ID}",
                headers=self._gist_headers(),
                timeout=10,
            )
            resp.raise_for_status()
            file_entry = resp.json().get("files", {}).get(GIST_FILENAME)
            if not file_entry:
                return None
            content = file_entry.get("content", "")
            if file_entry.get("truncated") and file_entry.get("raw_url"):
                raw = requests.get(file_entry["raw_url"], timeout=10)
                raw.raise_for_status()
                content = raw.text
            if not content.strip():
                return None
            return json.loads(content)
        except Exception as e:
            print(f"[GIST ERROR] Fetch failed, will fall back to local disk: {e}")
            return None

    def push_gist_data(self, data: dict) -> None:
        """Push the full data dict up to the Gist so it survives redeploys."""
        try:
            payload = {"files": {GIST_FILENAME: {"content": json.dumps(data, indent=4)}}}
            resp = requests.patch(
                f"https://api.github.com/gists/{GIST_ID}",
                headers=self._gist_headers(),
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"[GIST ERROR] Push failed (data is still safe on local disk this run): {e}")

    def load_database_file(self) -> None:
        data = None

        if self._gist_configured():
            data = self.fetch_gist_data()
            if data is not None:
                print("[MEMORY LOG] Loaded Brain from GitHub Gist (permanent storage).")

        if data is None:
            # No Gist configured, or the fetch failed - fall back to local disk.
            if not os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, "w") as file:
                        dump({"users": {}, "vip_users": [], "extra_owners": {}, "dj_access": [], "welcome_payouts": [], "bot_position": {"x": 0, "y": 0, "z": 0, "facing": "FrontRight"}}, file)
                except Exception as e:
                    print(f"[MEMORY ERROR] Initialization failed: {e}")
                    return
            try:
                with open(DATA_FILE, "r") as file:
                    data = load(file)
            except Exception as e:
                print(f"[MEMORY ERROR] Read failed: {e}")
                return

        self.tip_data = data.get("users", {})
        self.vip_users = data.get("vip_users", [])
        raw_owners = data.get("extra_owners", [])
        if isinstance(raw_owners, dict):
            self.extra_owners = raw_owners
        else:
            # Migrate from the old list-of-ids format to id->username
            self.extra_owners = {uid: self.tip_data.get(uid, {}).get("username", "Unknown") for uid in raw_owners}
        self.dj_access = data.get("dj_access", [])
        self.welcome_payouts = data.get("welcome_payouts", [])
        print(f"[MEMORY LOG] Loaded Brain. Tippers={len(self.tip_data)}, VIPs={len(self.vip_users)}, Owners={len(self.extra_owners)}")

        # Keep the local file in sync with whatever we just loaded (useful as a fallback cache).
        try:
            with open(DATA_FILE, "w") as file:
                dump(data, file, indent=4)
        except Exception as e:
            print(f"[MEMORY ERROR] Local cache write failed: {e}")

    def save_database_file(self) -> None:
        try:
            data = {}
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r") as file:
                    try:
                        data = load(file)
                    except Exception:
                        data = {}

            data["users"] = self.tip_data
            data["vip_users"] = self.vip_users
            data["extra_owners"] = self.extra_owners
            data["dj_access"] = self.dj_access
            data["welcome_payouts"] = self.welcome_payouts

            with open(DATA_FILE, "w") as file:
                dump(data, file, indent=4)

            if self._gist_configured():
                # Only push Tippers/VIPs/Owners/DJs (+ bot position) to the Gist.
                # welcome_payouts is just "every user who ever joined" and isn't
                # needed permanently - keeping it out keeps the Gist small and
                # avoids it growing unbounded over time.
                gist_payload = {
                    "users": self.tip_data,
                    "vip_users": self.vip_users,
                    "extra_owners": self.extra_owners,
                    "dj_access": self.dj_access,
                    "bot_position": data.get("bot_position", {"x": 0, "y": 0, "z": 0, "facing": "FrontRight"}),
                }
                self.queue_gist_push(gist_payload)
        except Exception as e:
            print(f"[MEMORY ERROR] Write failed: {e}")

    def queue_gist_push(self, data: dict) -> None:
        # Don't hit the GitHub API synchronously from inside event handlers -
        # that blocks the event loop and can cause the bot to miss the
        # Highrise connection's keepalive, leading to disconnects. Instead we
        # stash the latest data and let gist_sync_loop push it in a thread,
        # coalescing rapid back-to-back saves (e.g. a burst of tips) into a
        # single request instead of one per event.
        self._gist_pending_data = data
        self._gist_dirty = True

    async def gist_sync_loop(self) -> None:
        while True:
            await asyncio.sleep(5)
            if not self._gist_configured() or not self._gist_dirty:
                continue
            data_to_push = self._gist_pending_data
            self._gist_dirty = False
            try:
                await asyncio.to_thread(self.push_gist_data, data_to_push)
            except Exception as e:
                print(f"[GIST ERROR] Sync loop push failed, will retry: {e}")
                self._gist_pending_data = data_to_push
                self._gist_dirty = True

    def get_bot_position(self) -> Position:
        try:
            with open(DATA_FILE, "r") as file:
                data = load(file)
                pos_data = data.get("bot_position", {"x": 0, "y": 0, "z": 0, "facing": "FrontRight"})
                return Position(pos_data["x"], pos_data["y"], pos_data["z"], pos_data["facing"])
        except Exception:
            return Position(0, 0, 0, "FrontRight")

    async def loop_emote_handler(self, user_id: str, emote_id: str, duration: float) -> None:
        try:
            next_start = asyncio.get_running_loop().time()
            while True:
                if user_id not in self.active_emote_loops or self.active_emote_loops[user_id]["emote_id"] != emote_id:
                    break
                next_start += duration + 0.15  # small safety buffer so the next emote doesn't cut off the animation
                await self.highrise.send_emote(emote_id, user_id)
                remaining = next_start - asyncio.get_running_loop().time()
                if remaining > 0:
                    await asyncio.sleep(remaining)
                else:
                    # We've fallen behind (API/network delay) - reset the schedule instead of stacking delay
                    next_start = asyncio.get_running_loop().time()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # Connection-related failures happen in bursts during a reconnect - logging is
            # enough here. Trying to whisper the user would just fail too (same dead socket)
            # and add noise without ever reaching them.
            print(f"[EMOTE ERROR] Loop failed for user {user_id}: {e}")
        finally:
            if user_id in self.active_emote_loops and self.active_emote_loops[user_id]["emote_id"] == emote_id:
                del self.active_emote_loops[user_id]

    async def stop_user_emote(self, user_id: str) -> None:
        if user_id in self.active_emote_loops:
            task = self.active_emote_loops[user_id]["task"]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            if user_id in self.active_emote_loops:
                del self.active_emote_loops[user_id]

    async def start_emote_loop_for_user(self, user_id: str, emote_id: str, duration: float, source: str) -> None:
        # source is "personal" (the user picked it themselves) or "mass" (triggered by
        # !allemote). A personal choice always overrides a mass loop for that user, and
        # !allstop only ever cancels "mass" loops, leaving personal choices running.
        await self.stop_user_emote(user_id)
        task = asyncio.create_task(self.loop_emote_handler(user_id, emote_id, duration))
        self.active_emote_loops[user_id] = {"task": task, "emote_id": emote_id, "source": source}

    async def process_tip_queue_worker(self):
        while True:
            target_id, gold_bar_tier, username, reason, amount_label = await self.tip_queue.get()
            try:
                await self.highrise.tip_user(target_id, gold_bar_tier)
                if reason == "welcome":
                    await self.highrise.chat(f"🎉 @{username} have been tipped {amount_label} for welcome bonus!")
                elif reason == "stay_reward":
                    await self.highrise.chat(f"⏰ @{username} have been tipped {amount_label} for staying bonus!")
                elif reason == "manual_tip":
                    await self.highrise.chat(f"💰 @{username} have been tipped {amount_label}!")

                # Every tip - welcome, stay bonus, or manual - gets a visible 4-5s gap
                # so they always land one by one publicly, never in a rapid burst.
                await asyncio.sleep(random.uniform(4.0, 5.0))
            except Exception as e:
                print(f"[TIP ERROR] Failed to tip {username} ({target_id}): {e}")
                await asyncio.sleep(2.0)
            finally:
                self.tip_queue.task_done()

    async def track_user_stay_durations_loop(self):
        while True:
            await asyncio.sleep(30)
            now = time.time()
            try:
                room_users = await self.highrise.get_room_users()
                live_user_ids = {u.id for u, _ in room_users.content}
            except Exception:
                continue  # Skip this cycle if we can't confirm who's in the room

            for user_id in list(self.room_stay_tracker.keys()):
                # Safety check: if user is not in the room, remove them and skip
                if user_id not in live_user_ids:
                    del self.room_stay_tracker[user_id]
                    continue

                data = self.room_stay_tracker[user_id]
                if now >= data["next_fire_time"]:
                    data["bonus_count"] += 1
                    if data["bonus_count"] == 1:
                        # 2nd tip overall (1st was welcome) - 7 minutes after the 1st bonus
                        data["next_fire_time"] = data["join_time"] + 14 * 60
                    elif data["bonus_count"] == 2:
                        # From here on, snap to fixed wall-clock 10-minute marks
                        # (e.g. :20, :30, :40) instead of counting from this moment.
                        now_dt = datetime.fromtimestamp(now)
                        minutes_to_add = 10 - (now_dt.minute % 10)
                        next_dt = now_dt.replace(second=0, microsecond=0) + timedelta(minutes=minutes_to_add)
                        data["next_fire_time"] = next_dt.timestamp()
                    else:
                        # Already aligned to a 10-minute clock mark - just add exactly
                        # 10 minutes to stay on that same alignment (e.g. :20 -> :30 -> :40).
                        data["next_fire_time"] += 10 * 60
                    await self.tip_queue.put((user_id, "gold_bar_1", data["username"], "stay_reward", "1g"))

    async def connection_watchdog_loop(self) -> None:
        consecutive_failures = 0
        while True:
            await asyncio.sleep(45)
            try:
                await self.highrise.get_wallet()
                consecutive_failures = 0  # Connection is healthy again - reset the counter
            except Exception as e:
                if "closing transport" in str(e).lower() or "timeout" in str(e).lower():
                    consecutive_failures += 1
                    print(f"[CONNECTION WATCHDOG] Health check failed ({consecutive_failures}/3): {e}")
                    # Require 3 consecutive failures (~2+ minutes) before restarting the
                    # whole process. A single failed check is often just the SDK's own
                    # reconnect logic already in progress - killing the process on the
                    # first blip was causing unnecessary full restarts.
                    if consecutive_failures >= 3:
                        print("[CONNECTION WATCHDOG] Connection appears truly dead - restarting process.")
                        os._exit(1)

    async def anti_idle_loop(self):
        while True:
            await asyncio.sleep(300)
            try:
                pos = self.get_bot_position()
                if pos.x != 0 or pos.y != 0 or pos.z != 0:
                    await self.highrise.walk_to(Position(pos.x + 0.05, pos.y, pos.z + 0.05, pos.facing))
                    await asyncio.sleep(1)
                    await self.highrise.teleport(self.bot_id, pos)
            except Exception:
                pass

    async def bot_position_watchdog_loop(self):
        # Periodically confirms the bot is still where it was placed via !set.
        # If Highrise ever resets it back to the room's default spawn point
        # (e.g. after a reconnect glitch), this teleports it back automatically.
        while True:
            await asyncio.sleep(60)
            try:
                saved_pos = self.get_bot_position()
                if saved_pos == Position(0, 0, 0, 'FrontRight'):
                    continue  # No custom position configured yet

                room_users = await self.highrise.get_room_users()
                current_pos = None
                for u, pos in room_users.content:
                    if u.id == self.bot_id:
                        current_pos = pos
                        break

                if not isinstance(current_pos, Position):
                    continue

                drifted = (
                    abs(current_pos.x - saved_pos.x) > 1.0
                    or abs(current_pos.y - saved_pos.y) > 1.0
                    or abs(current_pos.z - saved_pos.z) > 1.0
                )
                if drifted:
                    await self.highrise.teleport(self.bot_id, saved_pos)
            except Exception:
                pass

    async def start_announcement_loop(self) -> None:
        announcements = [
            "💎 <color=#FFD700><b>TIP 500g</b></color> to the bot to unlock <color=#FF0000><b>VIP access permanently</b></color>! 👑",
            "🏢 Type <color=#FFD700><b>F1</b></color> for 1st floor, <color=#FFD700><b>F2</b></color> for 2nd floor, <color=#FFD700><b>!down</b></color> for ground floor, and <color=#FFD700><b>!vip</b></color> to teleport to the VIP lounge! 🚀",
            "🛡️ <color=#00FFFF><b>We are hiring active MODs!</b></color> Interested? DM <color=#FFD700><b>@sadi_key</b></color> 📩",
            "🎭 Type a number between <color=#FFA500><b>1</b></color> and <color=#FFA500><b>254</b></color> to perform an emote! <color=#FF0000><b>!stop</b></color> to stop the emote loop. 🕺💃"
        ]
        index = 0
        next_start = asyncio.get_running_loop().time()
        while True:
            # Drift-proof scheduling: the announcement is always attempted on
            # its own 60s clock, regardless of how long get_room_users()/chat()
            # take, so it never gets pushed back by other bot activity.
            next_start += 60.0
            try:
                room_users = await self.highrise.get_room_users()
                if room_users and len(room_users.content) > 1:
                    await self.highrise.chat(announcements[index % len(announcements)])
                    index += 1
            except Exception as e:
                print(f"[ANNOUNCEMENT ERROR] {e}")

            remaining = next_start - asyncio.get_running_loop().time()
            if remaining > 0:
                await asyncio.sleep(remaining)
            else:
                # We've fallen behind - reset the schedule instead of stacking delay
                next_start = asyncio.get_running_loop().time()

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("Management Bot Connected")
        self.bot_id = session_metadata.user_id
        self.owner_id = session_metadata.room_info.owner_id

        # Reposition the bot on every connect AND every reconnect. Highrise
        # places a rejoining bot at the room's default spawn point, so
        # without this the bot drifts back there after any disconnect.
        asyncio.create_task(self.place_bot())

        # Prevent SDK reconnects from duplicating background tasks
        if self.is_initialized:
            return
        self.is_initialized = True
        
        asyncio.create_task(self.process_tip_queue_worker())
        asyncio.create_task(self.track_user_stay_durations_loop())
        asyncio.create_task(self.connection_watchdog_loop())
        asyncio.create_task(self.anti_idle_loop())
        asyncio.create_task(self.bot_position_watchdog_loop())
        asyncio.create_task(self.gist_sync_loop())
        
        # Start announcement loop safely
        if self.announcement_task is None or self.announcement_task.done():
            self.announcement_task = asyncio.create_task(self.start_announcement_loop())

    async def place_bot(self):
        await asyncio.sleep(2.0)
        pos = self.get_bot_position()
        if pos == Position(0, 0, 0, 'FrontRight'):
            return  # No custom position saved yet - leave the bot at the room's default spawn
        for attempt in range(5):
            try:
                await self.highrise.teleport(self.bot_id, pos)
                return
            except Exception:
                await asyncio.sleep(2.0)

    async def handle_welcome_flow(self, user: User):
        if user.id in self.welcome_in_progress:
            return
        self.welcome_in_progress.add(user.id)
        await asyncio.sleep(1.0)
        try:
            await self.highrise.chat(f"👋 Welcome to the room @{user.username}! Type '!help' for information.")
        except Exception:
            pass
            
        if user.id not in self.welcome_payouts:
            self.welcome_payouts.append(user.id)
            self.save_database_file()
            await asyncio.sleep(4.0) 
            await self.tip_queue.put((user.id, "gold_bar_1", user.username, "welcome", "1g"))
        
        self.welcome_in_progress.discard(user.id)

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        if user.id == self.bot_id or "bot" in user.username.lower():
            return
        self.room_stay_tracker[user.id] = {"username": user.username, "join_time": time.time(), "bonus_count": 0, "next_fire_time": time.time() + 7 * 60}
        asyncio.create_task(self.handle_welcome_flow(user))

    async def on_user_leave(self, user: User) -> None:
        await self.stop_user_emote(user.id)
        if user.id in self.room_stay_tracker:
            del self.room_stay_tracker[user.id]
        self.vip_guests.discard(user.id)

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        if sender.id == self.bot_id:
            return
        if isinstance(tip, CurrencyItem) and receiver.id == self.bot_id:
            if sender.id not in self.tip_data:
                self.tip_data[sender.id] = {"username": sender.username, "total_tips": 0}
            self.tip_data[sender.id]['total_tips'] += tip.amount
            if tip.amount >= 500:
                if sender.id not in self.vip_users:
                    self.vip_users.append(sender.id)
                await self.highrise.chat(f"👑 VIP PROMOTION: @{sender.username} has unlocked Lifetime VIP permissions! 🎉")
            else:
                await self.highrise.chat(f"Thank you {sender.username} for tipping {tip.amount}g!")
            self.save_database_file()

    async def on_chat(self, user: User, message: str) -> None:
        await self.command_handler(user, message, "chat")

    async def on_whisper(self, user: User, message: str) -> None:
        await self.command_handler(user, message, "whisper")

    async def command_handler(self, user: User, message: str, source: str):
        # 1. Reject empty messages
        if not message or not message.strip():
            return

        clean_msg = message.lower().strip()
        
        # 2. DEBOUNCE LOCK: Prevent identical commands within 2.5 seconds
        now = time.time()
        user_history = self.last_command_time.get(user.id, {})
        last_time = user_history.get(clean_msg, 0)
        
        if now - last_time < 2.5:
            return # Block duplicate from double-firing events
            
        user_history[clean_msg] = now
        self.last_command_time[user.id] = user_history

        is_owner = (user.username.lower() == self.owner_username.lower()) or (user.id in self.extra_owners) or (user.id == self.bot_id)
        is_vip = (user.id in self.vip_users)

        # 3. Handle Emote Triggering by number
        try:
            emote_num = int(clean_msg.strip())
            if emote_num in EMOTE_MAP:
                emote = EMOTE_MAP[emote_num]
                await self.start_emote_loop_for_user(user.id, emote["id"], emote["duration"], source="personal")
                await self.highrise.send_whisper(user.id, f"🎭 Looping #{emote_num} ({emote['name']})! Type '!stop' to end.")
                return
        except ValueError:
            pass

        # 4. Standard Commands
        if clean_msg == "!help":
            help_text = "⚡ Commands: !list | !stop | !vip | !down | !bring @username | F1 | F2 | !dj | !allemote 1-254 (VIP) | !allstop (VIP)"
            if is_owner:
                help_text += " | !owner | !set | !top | !bal | !allvips | !giveall | !give | !givevip | !removevip | !giveowner | !removeowner | !allowners | !givedj | !removedj | !withdraw"
            await self.respond(user, help_text, source)
            return

        elif clean_msg == "!list":
            await self.highrise.send_whisper(user.id, "💡 Type a number (1-254) in chat to loop that emote! Type '!stop' to cancel.")
            current_msg = ""
            for num, data in EMOTE_MAP.items():
                entry = f"{num}.{data['name']}, "
                if len(current_msg) + len(entry) > 200:
                    await self.highrise.send_whisper(user.id, current_msg.rstrip(", "))
                    current_msg = entry
                else:
                    current_msg += entry
            if current_msg:
                await self.highrise.send_whisper(user.id, current_msg.rstrip(", "))
            return

        elif clean_msg == "!stop":
            await self.stop_user_emote(user.id)
            return

        elif clean_msg.startswith("!allemote ") and (is_vip or is_owner):
            try:
                emote_num = int(clean_msg.split(" ")[1].strip())
                if emote_num not in EMOTE_MAP:
                    await self.respond(user, "❌ Invalid emote number. Use a number between 1 and 254.", source)
                    return
                emote = EMOTE_MAP[emote_num]
                room_users = await self.highrise.get_room_users()
                count = 0
                for u, _ in room_users.content:
                    if u.id == self.bot_id:
                        continue
                    # Don't override someone who's already doing their own personal emote choice
                    existing = self.active_emote_loops.get(u.id)
                    if existing and existing.get("source") == "personal":
                        continue
                    await self.start_emote_loop_for_user(u.id, emote["id"], emote["duration"], source="mass")
                    count += 1
                await self.respond(user, f"🎭 Started #{emote_num} ({emote['name']}) for {count} users! Type '!allstop' to stop.", source)
            except (IndexError, ValueError):
                await self.respond(user, "❌ Invalid format. Use: !allemote 1-254", source)
            return

        elif clean_msg == "!allstop" and (is_vip or is_owner):
            stopped = 0
            for uid in list(self.active_emote_loops.keys()):
                if self.active_emote_loops[uid].get("source") == "mass":
                    await self.stop_user_emote(uid)
                    stopped += 1
            await self.respond(user, f"🛑 Stopped the group emote for {stopped} users.", source)
            return

        elif clean_msg == "!vip" and (is_vip or is_owner):
            try:
                await self.highrise.teleport(user.id, random.choice(self.vip_spawn_points))
            except Exception:
                pass
            return
            
        elif clean_msg == "!down":
            try:
                await self.highrise.teleport(user.id, self.ground_spawn_position)
                self.vip_guests.discard(user.id)  # Remove guest status after going down
            except Exception:
                pass
            return

        elif clean_msg.startswith("!bring ") and (is_vip or is_owner):
            try:
                target_name = clean_msg.split("@")[1].strip() if "@" in clean_msg else clean_msg.split(" ", 1)[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, _ in room_users.content:
                    if u.username.lower() == target_name.lower():
                        await self.highrise.teleport(u.id, random.choice(self.vip_spawn_points))
                        self.vip_guests.add(u.id)  # Grant guest access so !down works
                        await self.respond(user, f"✅ @{u.username} has been brought to the VIP lounge!", source)
                        return
                await self.respond(user, "❌ User not found in the room.", source)
            except Exception as e:
                await self.respond(user, f"❌ Error: {e}", source)
            return

        elif clean_msg == "!owner" and is_owner:
            try:
                await self.highrise.teleport(user.id, Position(26.0, 32.0, 37.0, "FrontRight"))
            except Exception:
                pass
            return

        elif clean_msg == "f1":
            try:
                await self.highrise.teleport(user.id, self.floor1_position)
            except Exception:
                pass
            return

        elif clean_msg == "f2":
            try:
                await self.highrise.teleport(user.id, self.floor2_position)
            except Exception:
                pass
            return

        elif clean_msg == "!dj" and (user.id in self.dj_access or is_owner):
            try:
                await self.highrise.teleport(user.id, self.dj_booth_position)
            except Exception:
                pass
            return

        # --- EVERYTHING BELOW THIS LINE IS OWNER ONLY ---
        if not is_owner:
            return

        if clean_msg.startswith("!giveowner ") and user.username.lower() == self.owner_username.lower():
            try:
                target_name = clean_msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, _ in room_users.content:
                    if u.username.lower() == target_name:
                        if u.id not in self.extra_owners:
                            self.extra_owners[u.id] = u.username
                            self.save_database_file()
                            await self.respond(user, f"✅ @{u.username} has been granted owner access!", source)
                        else:
                            await self.respond(user, f"⚠️ @{u.username} already has owner access.", source)
                        return
                await self.respond(user, "❌ User not found in the room.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !giveowner @username", source)
            return

        elif clean_msg.startswith("!removeowner ") and user.username.lower() == self.owner_username.lower():
            try:
                target_name = clean_msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, _ in room_users.content:
                    if u.username.lower() == target_name:
                        if u.id in self.extra_owners:
                            del self.extra_owners[u.id]
                            self.save_database_file()
                            await self.respond(user, f"🚫 @{u.username} has had their owner access revoked.", source)
                        else:
                            await self.respond(user, f"⚠️ @{u.username} does not have owner access.", source)
                        return
                await self.respond(user, "❌ User not found in the room.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !removeowner @username", source)
            return

        elif clean_msg == "!allowners":
            owner_names = [self.owner_username] + list(self.extra_owners.values())
            owners_string = ", ".join(f"@{n}" for n in owner_names)
            await self.highrise.send_whisper(user.id, f"👑 Total Owners ({len(owner_names)}): {owners_string}")
            return

        elif clean_msg.startswith("!withdraw ") and user.username.lower() == self.owner_username.lower():
            try:
                amount_str = clean_msg.split(" ")[1].strip()
                normalized = WITHDRAW_ALIASES.get(amount_str)
                if normalized and normalized in TIP_MAP:
                    await self.highrise.tip_user(user.id, TIP_MAP[normalized])
                    await self.respond(user, f"✅ Withdrew {normalized} from the bot to your account.", source)
                else:
                    await self.respond(user, "❌ Incorrect amount. Use: !withdraw 500, 1kg, 5kg, or 10kg.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !withdraw 500", source)
            return

        elif clean_msg.startswith("!givedj "):
            try:
                target_name = clean_msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, _ in room_users.content:
                    if u.username.lower() == target_name:
                        if u.id not in self.dj_access:
                            self.dj_access.append(u.id)
                            self.save_database_file()
                            await self.highrise.chat(f"🎧 @{u.username} has unlocked DJ booth access!")
                        else:
                            await self.respond(user, f"⚠️ @{u.username} already has DJ access.", source)
                        return
                await self.respond(user, "❌ User not found in the room.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !givedj @username", source)
            return

        elif clean_msg.startswith("!removedj "):
            try:
                target_name = clean_msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, _ in room_users.content:
                    if u.username.lower() == target_name:
                        if u.id in self.dj_access:
                            self.dj_access.remove(u.id)
                            self.save_database_file()
                            await self.respond(user, f"🚫 @{u.username} has had their DJ access revoked.", source)
                        else:
                            await self.respond(user, f"⚠️ @{u.username} does not have DJ access.", source)
                        return
                await self.respond(user, "❌ User not found in the room.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !removedj @username", source)
            return

        elif clean_msg.startswith("!giveall "):
            try:
                amount_str = clean_msg.split(" ")[1].strip()
                if amount_str in TIP_ALLOWED:
                    room_users = await self.highrise.get_room_users()
                    count = 0
                    for u, _ in room_users.content:
                        if u.id != self.bot_id:
                            await self.tip_queue.put((u.id, TIP_MAP[amount_str], u.username, "manual_tip", amount_str))
                            count += 1
                    await self.respond(user, f"💸 Queued {amount_str} tip to {count} users in the room!", source)
                else:
                    await self.respond(user, "❌ Incorrect command, you can tip max till 100g.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !giveall 10g", source)
            return

        elif clean_msg.startswith("!give "):
            parts = clean_msg.split()
            if len(parts) >= 3:
                target_name = parts[1].replace("@", "")
                amount_str = parts[2]
                if amount_str in TIP_ALLOWED:
                    room_users = await self.highrise.get_room_users()
                    for u, _ in room_users.content:
                        if u.username.lower() == target_name:
                            await self.tip_queue.put((u.id, TIP_MAP[amount_str], u.username, "manual_tip", amount_str))
                            await self.respond(user, f"💸 Queued {amount_str} tip to @{u.username}", source)
                            return
                    await self.respond(user, "❌ User not found in the room.", source)
                else:
                    await self.respond(user, "❌ Incorrect command, you can tip max till 100g.", source)
            else:
                await self.respond(user, "❌ Invalid format. Use: !give @username 10g", source)
            return

        elif clean_msg.startswith("!givevip "):
            try:
                target_name = clean_msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, _ in room_users.content:
                    if u.username.lower() == target_name:
                        if u.id not in self.vip_users:
                            self.vip_users.append(u.id)
                            if u.id not in self.tip_data:
                                self.tip_data[u.id] = {"username": u.username, "total_tips": 0}
                            self.save_database_file()
                            await self.respond(user, f"✅ @{u.username} has been manually granted VIP status!", source)
                        else:
                            await self.respond(user, f"⚠️ @{u.username} is already a VIP.", source)
                        return
                await self.respond(user, "❌ User not found in the room.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !givevip @username", source)
            return

        elif clean_msg.startswith("!removevip "):
            try:
                target_name = clean_msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, _ in room_users.content:
                    if u.username.lower() == target_name:
                        if u.id in self.vip_users:
                            self.vip_users.remove(u.id)
                            self.save_database_file()
                            await self.respond(user, f"🚫 @{u.username} has had their VIP status revoked.", source)
                        else:
                            await self.respond(user, f"⚠️ @{u.username} is not a VIP.", source)
                        return
                await self.respond(user, "❌ User not found in the room.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !removevip @username", source)
            return
            
        elif clean_msg == "!allvips":
            if not self.vip_users:
                await self.highrise.send_whisper(user.id, "No VIPs found in database.")
                return
                
            vip_names = []
            for v_id in self.vip_users:
                name = self.tip_data.get(v_id, {}).get("username", "Unknown User")
                vip_names.append(name)
                
            vip_string = ", ".join(vip_names)
            await self.highrise.send_whisper(user.id, f"💎 Total VIPs ({len(vip_names)}): {vip_string}")
            return

        elif clean_msg == "!set":
            try:
                room_users = await self.highrise.get_room_users()
                position = None
                for u, pos in room_users.content:
                    if u.id == user.id:
                        position = pos
                        break
                
                if isinstance(position, Position):
                    data = {}
                    if os.path.exists(DATA_FILE):
                        with open(DATA_FILE, "r") as file:
                            try: data = load(file)
                            except Exception: data = {}
                    
                    data["bot_position"] = {"x": position.x, "y": position.y, "z": position.z, "facing": position.facing}
                    with open(DATA_FILE, "w") as file:
                        dump(data, file, indent=4)
                    if self._gist_configured():
                        gist_payload = {
                            "users": self.tip_data,
                            "vip_users": self.vip_users,
                            "extra_owners": self.extra_owners,
                            "dj_access": self.dj_access,
                            "bot_position": data["bot_position"],
                        }
                        self.queue_gist_push(gist_payload)
                        
                    await self.highrise.teleport(self.bot_id, position)
                    await self.respond(user, "📍 Bot position updated successfully!", source)
            except Exception as e:
                print(f"Error handling !set: {e}")
            return

        elif clean_msg == "!top":
            sorted_tippers = sorted(self.tip_data.items(), key=lambda x: x[1]['total_tips'], reverse=True)[:10]
            formatted = [f"{i+1}. {d['username']} ({d['total_tips']}g)" for i, (_, d) in enumerate(sorted_tippers)]
            leaderboard_text = "\n".join(formatted)
            await self.respond(user, f"Top Tippers:\n{leaderboard_text}", source)
            return

        elif clean_msg == "!bal":
            try:
                wallet = await self.highrise.get_wallet()
                gold = next((currency.amount for currency in wallet.content if currency.type == 'gold'), 0)
                await self.highrise.send_whisper(user.id, f"💰 Balance: {gold}g")
            except Exception:
                pass
            return

    async def respond(self, user: User, msg: str, source: str):
        if source == "chat":
            await self.highrise.chat(msg)
        elif source == "whisper":
            await self.highrise.send_whisper(user.id, msg)

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    web_worker = threading.Thread(target=run_web_server, daemon=True)
    web_worker.start()
    asyncio.run(main([BotDefinition(Bot(), ROOM_ID, API_TOKEN)]))
