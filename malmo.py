from micropsi_core.world.world import World
from micropsi_core.world.worldadapter import ArrayWorldAdapter
from xml_settings import mission_XML
import MalmoPython
import os
import time
import sys
import json
import random
import numpy as np
from PIL import Image

class Malmo(World):

    supported_worldadapters = ['Steve']

    def __init__(self, filename, *args, **kwargs):
        World.__init__(self, filename, *args, **kwargs)     
        self.logger.info("world created.")

        #This sets up the API objects.
        self.agent_host = MalmoPython.AgentHost()
        try:
            self.agent_host.parse( sys.argv )
        except RuntimeError as e:
            print('ERROR:',e)
            print(self.agent_host.getUsage())
            exit(1)
        if self.agent_host.receivedArgument("help"):
            print(self.agent_host.getUsage())
            exit(0)
        
        #Build a mission and give it the configuration of the world. Note that we can change that later with Python (not XML) code.
        self.my_mission = MalmoPython.MissionSpec(mission_XML, True)
        self.my_mission_record = MalmoPython.MissionRecordSpec()

        #We may also store previous observations within Malmo, but let MicroPsi take care of remembering what they were.
        self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)

    def start_mission(self):    
        max_retries = 3
        for retry in range(max_retries):
            try:
                self.agent_host.startMission( self.my_mission, self.my_mission_record )
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:",e)
                    exit(1)
                else:
                    time.sleep(1)

    def loop_until_mission_starts(self):
        print("Waiting for the mission to start ",)
        self.world_state = self.agent_host.getWorldState()
        while not self.world_state.has_mission_begun:
            sys.stdout.write(".")
            time.sleep(0.1)
            self.world_state = self.agent_host.getWorldState()
            for error in self.world_state.errors:
                print("Error:",error.text)
        print()
        print("Mission running ",)
    
    def __del__(self):
        print('Quitting mission and reloading code.')
        self.agent_host.sendCommand('quit 1')


class Steve(ArrayWorldAdapter):

    @staticmethod
    def get_config_options():
        return [
            {'name': 'Default world',
            'description': 'Should we generate a normal Minecraft world regardless of current XML settings?',
            'options': ['No','Yes']},
            {'name': 'Vision',
            'description': 'Add vision yes/no',
            'options': ['Yes', 'No']},
            {'name': 'Vision X',
            'description':
            'The size of the Video Snapshots in pixels (X)',
            'default': '224'},
            {'name': 'Vision Y',
            'description':
            'The size of the Video Snapshots in pixels (Y)',
            'default': '224'},
            ]

    def __init__(self, world, uid=None, **data):
        super().__init__(world,uid=uid,**data)
        self.mission_started = False
        self.update_loop = 1

        #Process choices.
        if self.config['Vision'] == 'Yes':

            #This makes sure we have just one observation that is removed after grabbing it.
            self.world.agent_host.setVideoPolicy(MalmoPython.VideoPolicy.LATEST_FRAME_ONLY)
            
            self.x,self.y = int(self.config['Vision X']), int(self.config['Vision Y'])
            self.add_flow_datasource('Vision', (self.x,self.y,3))
            self.world.my_mission.requestVideo(self.x,self.y)

        if self.config['Default world'] == 'Yes':
            self.world.my_mission.createDefaultTerrain()
        
        #This will take a bit longer but is good when you are experimenting.
        self.world.my_mission.forceWorldReset()

        #All are floats except for IsAlive, which is binary.
        self.observationsFromFullStats = [
            'DistanceTravelled', 'TimeAlive', 'MobsKilled', 
            'DamageTaken', 'Life', 'Score', 'Food', 'XP', 
            'Air', 'XPos', 'YPos', 'ZPos', "Pitch", 
            'Yaw', 'WorldTime', 'TotalTime', 'IsAlive',
            ]
        
        self.observationsFromRay = [
            'Los_X', 'Los_Y', 'Los_Z', 
            'Los_InRange', 'Los_Distance', 'BlockType',
            'Smashed',
            ]

        self.observations = self.observationsFromFullStats + self.observationsFromRay
        [self.add_datasource(i, 0) for i in self.observations]
                            
        #Add all the moves as datatagets. Note: we can also swap, combine and discard items, see MissionHandlers.xsd
        self.floatingActuators = ['move', 'strafe', 'pitch', 'turn', 'sleep']
        self.binaryActuators = ['jump', 'crouch', 'attack', 'use']
        for i in self.floatingActuators + self.binaryActuators: #Float + binary
            self.add_datatarget(i,0)
        
        #Build a last action dictionary allowing stopping of ongoing actions.
        self.last_action = dict((i, 0) for i in self.datatarget_names)

    def get_world_state(self):
        #Helper function to ensure we get the world state.
        world_state = self.world.agent_host.peekWorldState()
        while world_state.is_mission_running and all (e.text=='{}' for e in world_state.observations):
            world_state = self.world.agent_host.peekWorldState()
        return world_state

    def update_actuators(self):
        #Malmo takes 0 as a valid input, stopping an ongoing action. This quits doing whatever was activated but is no longer.
        for action, value in self.last_action.items():
            if action != 'sleep' and value != 0 and self.get_datatarget_value(action) == 0:
                self.world.agent_host.sendCommand('{0} 0'.format(action))
                self.last_action[action] = 0
        
        #Send commands to Minecraft.
        for i in self.datatarget_names:
            value = self.get_datatarget_value(i)
            if value != 0 and i != 'sleep':
                if i in self.binaryActuators:
                    value = int(value)  
                self.world.agent_host.sendCommand('{0} {1}'.format(i,value))
                self.last_action[i] = value
            else:
                time.sleep(value)

    def update_floatingpoint_sensors(self):
        world_state = self.get_world_state()
        if not all(e.text=='{}' for e in world_state.observations):
            obs = json.loads( world_state.observations[-1].text )

            #Maybe we just update them line by line?
            for i in self.observationsFromFullStats:
                self.set_datasource_value(i, float(obs[i]))
        else:
            raise Exception('\nSomehow did not get observations, despite waiting for them.\n')

    def update_vision_datasource(self):
        world_state = self.get_world_state()
        
        assert len(world_state.video_frames) > 0, 'No video frames!? We just checked for them.'
        frame = world_state.video_frames[-1]
        image = Image.frombytes('RGB', (frame.width, frame.height), bytes(frame.pixels) )       
        
        #The below line saves the images to the given path. Change to your path.
        #image.save("path/to/where/you/want/your/images")
        
        imgarray = np.asarray(image, dtype=np.uint8)
        imgarray = np.transpose(imgarray, (1,0,2))
        
        self.set_flow_datasource('Vision', imgarray) 

    def update_data_sources_and_targets(self):
        #Starts a mission when there is none. 
        if not self.mission_started:            
            self.world.start_mission()
            self.world.loop_until_mission_starts()
            self.mission_started = True
        
        #Check whether the mission is actually running. (When MicroPsi thinks it is.)
        else:           
            world_state = self.world.agent_host.peekWorldState()
            if not world_state.is_mission_running:
                raise Exception('\nMission no longer running!\n')
        
        self.update_actuators()
        self.update_floatingpoint_sensors()

        if self.config['Vision'] == 'Yes':
            self.update_vision_datasource()

        print('\nUpdate number {0} finished, mission still running.\n'.format(str(self.update_loop)))
        self.update_loop += 1

