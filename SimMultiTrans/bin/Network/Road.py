
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import bin.Network.leave_loop as leave_loop

import numpy as np

from ctypes import *
import os
import logging

class Road(object):
    '''
    Use Road class to simulate the behaviors of passengers and vehicles on a road\\
    methods:\\
        arrive(v): a vehicle arrived\\
        leave(v): all vehicles completing this trip will leave\\
    '''
    def __init__(self, ori, dest, dist=0, time=0):
        self.ori = ori
        self.dest = dest
        self.dist = dist
        self.time = 0
        self.triptime = time
        
        # self.vehicle = []
        self.vehicle = {}

        self.v_count = {}
        self.v_reb_count = {}
        
        self.v_total_time = {}
        self.v_reb_time = {}
        self.flow = {}
        self.rebflow = {}
        self.history_flow = []
        self.history_rebflow = []

    def arrive(self, v):
        '''
        A vehicle arrived on the road
        '''
        time = self.triptime
        if time == 0 or not v.onroad:
            time = int(self.dist/v.get_velocity('m/s'))
        leave_time = self.time + time

        # self.vehicle.append( (v, leave_time) )
        if leave_time not in self.vehicle:
            self.vehicle[leave_time] = [v]
        else:
            self.vehicle[leave_time].append(v)
        # self.flow += 1
        if v.mode in self.flow:
            self.flow[v.mode] += 1
        else:
            self.flow[v.mode] = 1

        if v.get_occupiedseats()==0:
            if v.mode in self.rebflow:
                self.rebflow[v.mode] += 1
            else:
                self.rebflow[v.mode] = 1

        if v.mode != 'walk':
            logging.info(f'Time {self.time}: Vel {v.id} arrive at road ({self.ori},{self.dest})')


        if v.mode in self.v_count:
            self.v_count[v.mode] += 1
            self.v_total_time[v.mode] += time

            if v.mode in self.v_reb_count and v.reb == 'active' and v.get_occupiedseats() == 0:
                self.v_reb_count[v.mode] += 1
                self.v_reb_time[v.mode] += time
        else:
            self.v_count[v.mode] = 1
            self.v_total_time[v.mode] = time

        if v.mode not in self.v_reb_count and v.reb == 'active' and v.get_occupiedseats() == 0:
            self.v_reb_count[v.mode] = 1
            self.v_reb_time[v.mode] = time


    def leave(self, g):
        '''
        All vehicles finishing their trips leave the road
        '''
        ''''''
        if self.time in self.vehicle:
            leave_vehicle = self.vehicle[self.time]

            for v in leave_vehicle:
                # self.vehicle.remove( (v, leave_time) )
                self.flow[v.mode] -= 1
                
                if v.get_occupiedseats() == 0:
                    self.rebflow[v.mode] -= 1

                if v.mode != 'walk':
                    logging.info(f'Time {self.time}: Vel {v.id} leave road ({self.ori},{self.dest})')
                g.graph_top[self.dest]['node'].vehicle_arrive(v)

            # self.flow -= len( self.vehicle[self.time] )
            del self.vehicle[self.time]
        
        # record flow at each time
        self.history_flow.append( sum([self.flow[mode] for mode in self.flow]) )
        self.history_rebflow.append( sum([self.rebflow[mode] for mode in self.rebflow]) )
        '''
        if self.time in self.vehicle:
            leave_vehicle = self.vehicle[self.time]
            leave_loop.leave_loop(g, self.dest, leave_vehicle)

            self.flow -= len( leave_vehicle )
            del self.vehicle[self.time]
        '''
        '''
        leave_vehicle = []
        for (v, leave_time) in self.vehicle:
            # (v, leave_time) = self.vehicle[v_index]
            if leave_time == self.time:
                leave_vehicle.append( (v, leave_time) )

        for (v, leave_time) in leave_vehicle:
            self.vehicle.remove( (v, leave_time) )
            if v.mode != 'walk':
                logging.info(f'Time {self.time}: Vel {v.id} leave road ({self.ori},{self.dest})')
            g.graph_top[self.dest]['node'].vehicle_arrive(v)
        '''

    def passengers_clear(self):
        '''
        on_road_p = 0
        for (v, leave_time) in self.vehicle:
            if v.mode != 'walk':
                on_road_p += 1
        return on_road_p
        '''
        on_road_p = 0
        for t in self.vehicle:
            on_road_p += len(self.vehicle[t])
        return on_road_p

    def get_flow(self, mode):        
        # return len(self.vehicle)
        # return len( [v for (v,t) in self.vehicle if v.mode == mode] )
        # return self.flow
        if mode not in self.flow:
            self.flow[mode] = 0
        return self.flow[mode]

    def get_total_trip(self, mode):
        return 0 if (mode not in self.v_count) else self.v_count[mode]
    
    def get_total_reb_trip(self, mode):
        return 0 if (mode not in self.v_reb_count) else self.v_reb_count[mode]

    def get_total_time(self, mode):
        # return 0 if (mode not in self.v_count) else self.triptime*self.v_count[mode]
        return 0 if (mode not in self.v_total_time) else self.v_total_time[mode]
    
    def get_total_reb_time(self, mode):
        # return 0 if (mode not in self.v_reb_count) else self.triptime*self.v_reb_count[mode]
        return 0 if (mode not in self.v_reb_time) else self.v_reb_time[mode]

    def get_total_distance(self, mode):
        return 0 if (mode not in self.v_count) else self.dist*self.v_count[mode]
    
    def get_total_reb_distance(self, mode):
        return 0 if (mode not in self.v_reb_count) else self.dist*self.v_reb_count[mode]