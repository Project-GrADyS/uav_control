# Uav_control
This is the repository for Uav_control, an API for UAV autonomous flights. The Uav_control API enables UAV movement, telemetry and basic command execution such as RTL and TAKEOFF through HTTP requests, facilitating remote controlled flights, both programmatically and manually. In addition to that, Uav_control supports protocol execution for autonomous flights, oferring the same interface as gradysim-nextgen simulator. At last but not least, Uav_control can be used for simulations based on Ardupilot's SITL. 

# Installation
## Prerequisites
Python 3.10 is required
If simulated flights are intended, installing Ardupilot's codebase is necessary. To do that follow the instructions at https://ardupilot.org/dev/docs/where-to-get-the-code.html (Don't forget to build the environment after cloning). In addition to that, following the steps for running the SITL is also required, which are stated at https://ardupilot.org/dev/docs/SITL-setup-landingpage.html
## Cloning the repository
To install Uav_control simply clone this repository.
  
  `git clone git@github.com:Project-GrADyS/uav_control.git`
## Install required packages
To install required python packages run the command bellow from the root folder of the repository:

  `pip3 install -r requirements.txt`
# Executing a Simulated flight
## Starting Uav_control
To instantiate the API, run the script `uav_api.py` through the following command:
  
  `python3 uav_api.py --simulated true`
This command initiates both the SITL, and the Uav_control API. The connection addres of the SITL instance is `127.0.0.1:17171` and the api is hosted at localhost:8000 by default but both of this parameters can be modified by arguments.

## Testing and feedback
To manually test the api access the auto-generated swagger endpoint at `http://localhost:8000/docs`. 

![image](https://github.com/user-attachments/assets/6d1f9b6c-f69c-4381-98f0-7adec7311c15)

To get visual feedback of drone position and telemetry use Mission Planner, or any other ground station software of your preference, and connect to UDP port `15630` (for wsl users this may not work, check the parameters section for uav_api.py and search for gs_connection for more).

![image](https://github.com/user-attachments/assets/b7928581-89c6-46c0-9f02-3bd8edd30570)

## Flying through scripts
One of the perks of using Uav_control is simplifying UAV flights coordinated by scripts. Here are some examples:

### Simple Takeoff and Landing
This file is located at `flight_examples/takeoff_land.py`
```python
import requests
base_url = "http://localhost:8000"

# Arming vehicle
arm_result = requests.get(f"{base_url}/command/arm")
if arm_result.status_code != 200:
    print(f"Arm command fail. status_code={arm_result.status_code}")
    exit()
print("Vehicle armed.")

# Taking off
params = {"alt": 30}
takeoff_result = requests.get(f"{base_url}/command/takeoff", params=params)
if takeoff_result.status_code != 200:
    print(f"Take off command fail. status_code={takeoff_result.status_code}")
    exit()
print("Vehicle took off")

# Landing...
land_result = requests.get(f"{base_url}/command/land")
if land_result.status_code != 200:
    print(f"Land command fail. status_code={land_result.status_code}")
    exit()
print("Vehicle landed.")
```
