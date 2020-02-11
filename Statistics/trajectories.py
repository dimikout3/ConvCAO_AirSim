import airsim
import cv2
import os
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pickle
import scipy
import pandas as pd
import seaborn as sns
import matplotlib.image as mpimg

# older boundaries
# left, right = -114.43489074707031, 64.43489074707031
# bot, top = -64.43489074707031, 114.43489074707031

# ultrawide boundaries
# left=-180.28102687023934 right=130.28102687023934 bot=-52.64051343511967 top=102.6405134351196

DRONE2_PATH = r"E:\Users\DKoutas\ownCloudConvCao\CREST_Shared\results\IROS\2Drones"
DRONE3_PATH = r"E:\Users\DKoutas\ownCloudConvCao\CREST_Shared\results\IROS\3Drones"
DRONE4_PATH = r"E:\Users\DKoutas\ownCloudConvCao\CREST_Shared\results\IROS\GridSearch\V07"
DRONE5_PATH = r"E:\Users\DKoutas\ownCloudConvCao\CREST_Shared\results\IROS\5Drones"

PATH = DRONE4_PATH

CLUSTERS = [[40,-80], [-10,75], [0,0], [80,-50]]

if __name__ == "__main__":

    if PATH == "":
        simulation_dir = os.path.join(os.getcwd(), "..")
    else:
        simulation_dir = PATH

    directories = os.listdir(simulation_dir)
    print(f"directories {directories}")
    result_dirs = [i for i in directories if 'results_' in i]
    # for safety reasons, last simulation is usally corrupted
    # result_dirs = result_dirs[0:-2]

    data = {}
    data["Simulation"] = []
    data["Time"] = []
    data["State"] = []
    data["droneID"] = []
    data["x_val"] = []
    data["y_val"] = []

    for sim in result_dirs:

        sim_dir = os.path.join(simulation_dir, sim)
        raw_dir = os.path.join(sim_dir, "swarm_raw_output")

        directories = os.listdir(raw_dir)
        # print(f"directories {directories}")
        drone_dirs = [i for i in directories if 'Drone' in i]

        for droneID in drone_dirs:

            print(f"[INFO] simulation={sim} drone={droneID}")

            pickle_in = os.path.join(raw_dir, droneID, f"state_{droneID}.pickle")
            file = open(pickle_in, "rb")
            stateList = np.array(pickle.load(file))
            file.close()

            for time, state in enumerate(stateList):

                x_val = state[0].kinematics_estimated.position.x_val
                y_val = state[0].kinematics_estimated.position.y_val

                data["x_val"].append(x_val)
                data["y_val"].append(y_val)
                #  state = [multirotorState, cameraState]
                data["Simulation"].append(sim)
                data["Time"].append(time*3.)
                data["State"].append(state)

                data["droneID"].append(droneID)

    image_path = "scene_time_0.png"
    map_img = cv2.imread(image_path)
    map_img = cv2.cvtColor(map_img, cv2.COLOR_BGR2RGB)

    df = pd.DataFrame(data)
    # import pdb; pdb.set_trace()

    simulationList = df["Simulation"].unique().tolist()
    dronesList = df["droneID"].unique().tolist()

    for sim in simulationList:

        tempDF = df[df.Simulation == sim]
        # for drone in dronesList:
        sns.lineplot(x="y_val", y="x_val",
                     hue="droneID", data=tempDF[tempDF.Time % 5 == 0],
                     alpha=np.linspace(0,1,400), lw=0.9)

        # The extent kwarg controls the bounding box in data coordinates that the image will fill specified as (left, right, bottom, top)
        left, right = -114.43489074707031, 64.43489074707031
        bot, top = -64.43489074707031, 114.43489074707031
        plt.imshow(map_img, zorder=0, extent=[left, right, bot, top])

        # plt.show()
        plt.savefig(f"trajectories/{sim}.png",dpi=1000)
        plt.close()
