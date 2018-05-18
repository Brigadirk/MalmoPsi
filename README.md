# MalmoPsi 

Interface between the MicroPsi Cognitive Architecture and the Malmo API for Minecraft

### Prerequisites

MicroPsi: https://github.com/joschabach/micropsi2
Malmo: https://github.com/Microsoft/malmo

## Getting Started

Put files in micropsi_code in home directory, name the folder 'malmo' for example.

In terminal type 'export MALMO_XSD_PATH=/path/to/Malmo/Schemas'
Launch the Malmo server
Launch MicroPsi

You should now be able to select the Malmo world in the MicroPsi GUI. 
Some options are available, such as whether you want to use video information, and whether you want to load a default Minecraft world.

After setting up this world you may create an agent and start a mission through the MicroPsi GUI.

Through actuator nodes, agents can send actions to the Minecraft world, and through sensor nodes, the agents can receive information from the Minecraft world. Currently, there are no sensors that check for items in the inventory. If you want to add this functionality I would refer you to the Malmo documentation. To set up proper node nets, I would refer you to the MicroPsi documentation.

In the xml_settings file, you may change the XML file that sets up the experimental world. Currently this is a world with a fence around it and a few trees in there. The trees are spawned with Python code in the object_constructors file, to which you may add additional object constructors that you can use to add to the world.

Note: it is important to keep <MissionQuitCommmands/> part of the XML, as this allows resetting a mission from the MicroPsi shell without running into a used server.


## Acknowledgments

* MicroPsi industries: http://www.micropsi-industries.com/ 
* Microsoft Malmo: https://github.com/Microsoft/malmo

