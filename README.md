# Test scenarios for cooperative behavior planning on highways

## Introduction
  
This repository contains a script to extract test scenarios for cooperative behavior planning from the highD (https://www.highd-dataset.com/) dataset. The selection process according to which the scenarios have been chosen is described in our paper "Data-Driven Test Scenario Generation for Cooperative Maneuver Planning on Highways" (free full text: https://www.mdpi.com/2076-3417/10/22/8154). Please note that this script does not perform all the simulations described, but only contains the result of the simulations in the form of a scenario catalog.  Since the used highD dataset is only accessible after permission, the scenario catalog cannot be shared directly. Instead, we provide a Python tool that extracts the scenarios of the test catalog by their recording- and vehicle IDs, provided there is access to the root dataset.

## Format description

The scenario catalog is structured as follows:
- number of vehicles in scenario (4 and 3 vehicles)
    - roadway model (2 lanes, 3 lanes, 3 lanes with entry lane)
        - scenario number
            - vehicle positions [position_vehicle_1, position_vehicle_2, ...]
            - vehicle velocities  [velocity_vehicle_1, velocity_vehicle_2, ...]
            - vehicle lanes   [lane_vehicle_1, lane_vehicle_2, ...]
            - ...

The roadway model is structured into sections (n lanes with a sufficient length of 4000m) and highway entrances (lane 0, start x=0m, end x=250m). The lane numbers in the scenario catalog are denoted in ascending order from right to left. The ID of the rightmost lane on roadways without entry lane is set to 1, entry lanes have the ID 0. The x-position ascends in driving direction (reference point rear end of vehicles) and is set to 0 for the last vehicle on roadways without entry lanes. On roadways with an entry lane, where the distance of the vehicles to the lane end is important, the x-positions are not shifted.

![Definition of roadway.](/images/roadway_definition.png "Definition of roadway.")

## List of components
- `scenario_database_empty.pkl`: Pickle file of scenario database without specific scenario data (positions, velocities, lanes).
- `fill_database.py`: Script to extract specific scenario data from highD dataset. Outputs scenario database file with scenario data
- `scenario_database.pkl`: Scenario database file with scenario data.

## Requirements
All required python modules are listed in the `requirements.txt`file in this repo. They can be installed automatically with `pip3 install -r /path/to/requirements.txt`.

Furthermore you need the highD dataset to extract the scenarios. It can be downloaded after successful application on https://www.highd-dataset.com/.

  
## Running the code
- `Step 1`: Clone the repo.
- `Step 2`: Unzip the scenario_database_empty.zip file
- `Step 3`: Copy the files `scenario_database_empty.pkl` and `fill_database.py` to the src folder of your highD dataset (...\Python\src).
- `Step 4`: Run the `fill_database.py` file. The complete scenario catalog `scenario_database.pkl` will be generated (overall 2255 scenarios, approx. 5 minutes).

## License
This project is licensed under the LGPL License - see the LICENSE file for details
 
 
## References
The scenario catalog was generated according to the approach presented in:

Data-Driven Test Scenario Generation for Cooperative Maneuver Planning on Highways
by Christian Knies and Frank Diermeyer
DOI: 10.3390/app10228154
Free full text available: https://www.mdpi.com/2076-3417/10/22/8154

If you find our work useful in your research, please consider citing:

```
@article{Knies2020,
  doi = {10.3390/app10228154},
  url = {https://doi.org/10.3390/app10228154},
  year = {2020},
  month = nov,
  publisher = {{MDPI} {AG}},
  volume = {10},
  number = {22},
  pages = {8154},
  author = {Christian Knies and Frank Diermeyer},
  title = {Data-Driven Test Scenario Generation for Cooperative Maneuver Planning on Highways},
  journal = {Applied Sciences}
}
```
