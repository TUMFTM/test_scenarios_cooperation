import dill
import os
import numpy as np
import pandas as pd


def fill_database(scenario_database, data_path):
    """
    Created by:
    Christian Knies

    Modified by:
    -

    Description:
    Fills empty database with values from highD recording files.

    Inputs and Outputs:
    :param scenario_database: empty scenario database
    :param data_path: path to highD recording files
    :return: complete scenario database
    """
    # initialize variables
    rec_nr = 0
    recording = pd.DataFrame([])
    static_info = pd.DataFrame([])
    recording_info = pd.DataFrame([])
    lane_min_dir_1 = 100
    lane_max_dir_2 = 0
    max_x_position = 0
    min_x_position = 1000
    scenario_counter = 0
    # loop through scenario database
    for n_vehicles in scenario_database:
        for roadway in scenario_database[n_vehicles]:
            for scenario in scenario_database[n_vehicles][roadway]:
                # read recording of current scenario if not already loaded
                if scenario_database[n_vehicles][roadway][scenario]["recording_id"] != rec_nr:
                    # read files
                    rec_nr = scenario_database[n_vehicles][roadway][scenario]["recording_id"]
                    recording = pd.read_csv(data_path + "/" + '{:02}'.format(rec_nr) + "_tracks.csv")
                    static_info = pd.read_csv(data_path + "/" + '{:02}'.format(rec_nr) + "_tracksMeta.csv")
                    recording_info = pd.read_csv(data_path + "/" + '{:02}'.format(rec_nr) + "_recordingMeta.csv")
                    # find min and max lanes for transformation in each driving direction
                    lane_min_dir_1 = 100
                    lane_max_dir_2 = 0
                    max_x_position = max(recording["x"])
                    min_x_position = min(recording["x"])
                    vehicle_id_direction_1 = static_info[static_info["drivingDirection"] == 1]["id"].values
                    for vehicle_id in vehicle_id_direction_1:
                        lane_min_dir_1 = min(lane_min_dir_1, min(recording[recording["id"] == vehicle_id]["laneId"]))
                    vehicle_id_direction_2 = static_info[static_info["drivingDirection"] == 2]["id"].values
                    for vehicle_id in vehicle_id_direction_2:
                        lane_max_dir_2 = max(lane_max_dir_2, max(recording[recording["id"] == vehicle_id]["laneId"]))
                # entry lane detection
                entry_lane = len(scenario_database[n_vehicles][roadway][scenario]["roadway_model"]["entrance"])
                # extract frame and vehicle ids
                frame = scenario_database[n_vehicles][roadway][scenario]["frame"]
                id_list = scenario_database[n_vehicles][roadway][scenario]["vehicle_id"]
                # detect driving direction
                if static_info[static_info["id"] == id_list[0]]["drivingDirection"].values[0] == 1:
                    dir_correct = -1
                    direction = 1
                else:
                    dir_correct = 1
                    direction = 2
                # read scenario data of relevant vehicles from recording
                scenario_database[n_vehicles][roadway][scenario]["ttc"] = np.array(
                    [recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["ttc"].values[0] for
                     vehicle_id in
                     id_list])
                scenario_database[n_vehicles][roadway][scenario]["x_position"] = transform_x_position(np.array(
                    [recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["x"].values[0] for
                     vehicle_id in
                     id_list]), direction, min_x_position, max_x_position, entry_lane)
                scenario_database[n_vehicles][roadway][scenario]["lane_id"] = transform_lane_id(np.array(
                    [recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["laneId"].values[0] for
                     vehicle_id in
                     id_list]), direction, lane_min_dir_1, lane_max_dir_2, entry_lane)
                scenario_database[n_vehicles][roadway][scenario]["velocity"] = dir_correct * np.array(
                    [recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["xVelocity"].values[0]
                     for vehicle_id in
                     id_list])
                scenario_database[n_vehicles][roadway][scenario]["acceleration"] = dir_correct * np.array(
                    [recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["xAcceleration"].values[
                         0] for
                     vehicle_id in id_list])
                scenario_database[n_vehicles][roadway][scenario]["length"] = np.array(
                    [int(recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["width"].values[0])
                     for vehicle_id
                     in id_list])
                scenario_database[n_vehicles][roadway][scenario]["width"] = np.array(
                    [int(recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["height"].values[0])
                     for vehicle_id
                     in id_list])
                scenario_database[n_vehicles][roadway][scenario]["dhw"] = np.array(
                    [recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["dhw"].values[0] for
                     vehicle_id in
                     id_list])
                scenario_database[n_vehicles][roadway][scenario]["preceding_id"] = np.array(
                    [recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["precedingId"].values[0]
                     for vehicle_id
                     in id_list])
                scenario_database[n_vehicles][roadway][scenario]["following_id"] = np.array(
                    [recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)]["followingId"].values[0]
                     for vehicle_id
                     in id_list])
                scenario_database[n_vehicles][roadway][scenario]["preceding_velocity"] = dir_correct * np.array(
                    [recording[(recording["frame"] == frame) & (recording["id"] == vehicle_id)][
                         "precedingXVelocity"].values[0]
                     for vehicle_id in id_list])
                # read scenario data from static info
                scenario_database[n_vehicles][roadway][scenario]["max_velocity"] = np.array(
                    [static_info[static_info["id"] == vehicle_id]["maxXVelocity"].values[0] for vehicle_id in
                     id_list])
                scenario_database[n_vehicles][roadway][scenario]["class"] = np.array(
                    [static_info[static_info["id"] == vehicle_id]["class"].values[0] for vehicle_id in
                     id_list])
                # read scenario data from recording info
                scenario_database[n_vehicles][roadway][scenario]["speed_limit"] = recording_info["speedLimit"].values
                # print progress
                scenario_counter += 1
                print("Extracted scenarios: " + str(scenario_counter))
    return scenario_database


def transform_lane_id(lane_list, direction, lane_min_dir_1, lane_max_dir_2, merge_lane):
    """
    Created by:
    Christian Knies

    Modified by:
    -

    Description:
    Transforms lane IDs from highD format (https://www.highd-dataset.com/format) to scenario database format
    (ascending from right to left, rightmost lanes: ID 1, entry lanes: ID 0).

    Inputs and Outputs:
    :param lane_list: list of lanes of all vehicles
    :param direction: driving direction of vehicles in highD recording (direction 1: right->left,
                        direction2: left->right)
    :param lane_min_dir_1: minimum lane in direction 1 in highD format
    :param lane_max_dir_2: maximum lane in direction 2 in highD format
    :param merge_lane: existence of entry lane: 0: no, 1: yes
    :return: transformed list of lanes in scenario database format
    """
    if merge_lane == 0:
        min_lane = 1
    else:
        min_lane = 0
    if direction == 1:
        lane_list_trans = lane_list - lane_min_dir_1 + min_lane
    else:
        lane_list_trans = lane_max_dir_2 - lane_list + min_lane
    return lane_list_trans


def transform_x_position(position_list, direction, min_position, max_position, merge_lane):
    """
    Created by:
    Christian Knies

    Modified by:
    -

    Description:
    Transforms x-position of vehicles from highD format (https://www.highd-dataset.com/format) to scenario database
    format (drving direction in positive x direction, last vehicle set to x=0 if scneario has no entry lane).

    Inputs and Outputs:
    :param position_list: list of x positions of vehicles
    :param direction: driving direction of vehicles in highD recording (direction 1: right->left,
                        direction2: left->right)
    :param min_position: minimum x-position in whole recording
    :param max_position: maximum x-position in whole recording
    :param merge_lane: existence of entry lane: 0: no, 1: yes
    :return: transformed list of x-positions in scenario database format
    """
    if direction == 1:
        position_list_transform = max_position - position_list
    else:
        position_list_transform = position_list - min_position
    if merge_lane == 0:
        position_list_transform = position_list_transform - min(position_list_transform)
    return position_list_transform


if __name__ == '__main__':
    # path to scenario_database and recording data
    scenario_directory = os.path.dirname(os.path.realpath(__file__))
    data_directory = os.path.dirname(scenario_directory) + "/data"
    # load scenario_database
    scenarios_empty = dill.load(open(scenario_directory + "/scenario_database_empty.pkl", "rb"))
    # read scenario data from recordings
    scenarios_filled = fill_database(scenarios_empty, data_directory)
    # safe filled database to .pkl file
    filename_outfile = 'scenario_database.pkl'
    outfile = open(filename_outfile, 'wb')
    dill.dump(scenarios_filled, outfile)
