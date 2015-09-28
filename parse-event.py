#!/usr/bin/python

import sys
from datetime import datetime
import time

'''
Sep 26 2015 20:10:14.739 [INFO] New controller ('70.194.3.148', 1131) with token Vgcz2G94tj7L (14 seconds old)
Sep 26 2015 20:10:14.739 [INFO] 1 active players
Sep 26 2015 20:10:16.731 [INFO] Controller ('70.194.3.148', 1131) selects local-roms/Pac-Man (U) [!].nes
Sep 26 2015 20:10:53.016 [INFO] Controller websocket ('70.194.3.148', 1131) closed
Sep 26 2015 20:10:53.016 [INFO] 0 active players
Sep 26 2015 20:11:18.865 [INFO] New controller ('166.170.26.8', 16679) with token Vgcz2G94tj7L (78 seconds old)
Sep 26 2015 20:11:18.865 [INFO] 1 active players
Sep 26 2015 20:11:24.098 [INFO] Controller websocket ('166.170.26.8', 16679) closed
Sep 26 2015 20:11:24.098 [INFO] 0 active players
Sep 26 2015 20:15:17.614 [INFO] New controller ('70.194.3.148', 1137) with token Vgc1BLPquUY- (17 seconds old)
Sep 26 2015 20:15:17.614 [INFO] 1 active players
Sep 26 2015 20:20:22.553 [INFO] Timing out controller ('70.194.3.148', 1137) (0 players left)
Sep 26 2015 20:20:32.558 [INFO] Timing out controller ('70.194.3.148', 1137) (0 players left)
Sep 26 2015 20:20:32.558 [WARN] Controller ('70.194.3.148', 1137) seemed to have left on its own
Sep 26 2015 20:20:33.826 [INFO] Controller websocket ('70.194.3.148', 1137) closed
Sep 26 2015 20:20:33.826 [INFO] 0 active players
'''

def get_diff_str(diff):
    diff_m = diff / 60
    diff_s = diff - (diff_m*60)
    if (diff_m < 60):
        diff_str = "%d:%02d" % (diff_m, diff_s)
    else:
        diff_str = "%d:%02d:%02d" % (diff_m/60, diff_m%60, diff_s)
    return diff_str


# msg is something like "Even took %s seconds"
def print_diff_event(msg, first_time, second_time):

    msg = str(first_time) + ' ' + msg

    diff_str = get_diff_str((second_time - first_time).seconds)
    print msg % (diff_str)


active = 0
in_menu = False
in_game = False
last_t = None
tot_played_time = 0
tot_menu_time = 0
meta_tot = 0

for line in sys.stdin.readlines():
    if '[INFO]' not in line:
        continue
    ts, event = line.split('[INFO]')

    ms = int(ts.split('.')[1])
    t = datetime.strptime(ts.split('.')[0], '%b %d %Y %H:%M:%S')

    last_active = active
    last_controller_timed_out = False

    if 'New controller' in event:
        #active += 1
        pass
    elif 'Timing out controller' in event:
        active = int(event.split(' ')[6].replace('(', ''))
        last_controller_timed_out = True
    elif 'Controller websocket' in event:
        # closed
        #active -= 1
        pass
    elif 'active players' in event:
        #print 'active players: %s' % str(event.split(' '))
        active_s = event.split(' ')[1]
        active = int(active_s)
    elif 'selects' in event:
        in_menu = False
        in_game = True
        # start in game
        in_game_start = t
        game = event.split('selects ')[1].strip()
        #print "In menu for %d seconds" % ((t-start_menu).seconds)
        print_diff_event("In menu for %s", start_menu, t)
        tot_menu_time += (t-start_menu).seconds


    if active > 0 and last_active == 0:
        # started
        in_menu = True
        start_menu = t

    if active == 0 and last_active != 0:
        # end playing game or menu
        if in_menu:
            #print 'In menu for %d seconds' % ((t - start_menu).seconds)
            print_diff_event("In menu for %s", start_menu, t)
            tot_menu_time += (t-start_menu).seconds
            in_menu = False
            in_game = False
        elif in_game:
            #print 'In game (%s) for %d seconds' % (game, (t - in_game_start).seconds)
            print_diff_event("In game (%s) for %%s" % (game), in_game_start, t)
            tot_played_time += (t-in_game_start).seconds
            in_game = False
            in_menu = False


    if last_t is not None and last_t.day != t.day:
        print '---------'
        print '%s played a total of %s (in menu for %s)' % (last_t.strftime('%Y-%m-%d'), get_diff_str(tot_played_time), get_diff_str(tot_menu_time))
        print '---------'

        meta_tot += tot_played_time
        tot_played_time = 0
        tot_menu_time = 0

    last_t = t



print '=============='
print 'played total of %s' % (get_diff_str(meta_tot))
