from object_constructors import *

missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            
              <About>
                <Summary>Test world!</Summary>
              </About>
              
              <ServerSection>
                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,2*3,2;1"/>
                  <!-- <ServerQuitFromTimeUp timeLimitMs="30000"/> -->
                  <!-- <ServerQuitWhenAnyAgentFinishes/> -->
                  <DrawingDecorator>

						<!-- Walls around the experimental ground -->
						<DrawCuboid x1="-50" x2="50" z1="-50" z2="-50" y1="4" y2="7" type="obsidian"/>
						<DrawCuboid x1="-50" x2="50" z1="50" z2="50" y1="4" y2="7" type="obsidian"/>
						<DrawCuboid x1="-50" x2="-50" z1="50" z2="-50" y1="4" y2="7" type="obsidian"/>
						<DrawCuboid x1="50"  x2="50" z1="-50" z2="50" y1="4" y2="7" type="obsidian"/>
						
						<!-- Add trees -->
						''' + gen_tree(-10,10) + '''
						''' + gen_tree(10,10) + '''
						''' + gen_tree(10,-10) + '''
						''' + gen_tree(-10,-10) + '''
							
					</DrawingDecorator> 
                </ServerHandlers>
              </ServerSection>
              
              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart/>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''




















