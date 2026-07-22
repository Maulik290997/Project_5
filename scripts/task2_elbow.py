import sys, json
sys.path.insert(0, "src")
import numpy as np
from tellco.modeling import elbow_method

Xs = np.load("data/engagement_Xs.npy")
elbow = elbow_method(Xs, range(1, 9), random_state=42)
with open("data/task2_elbow.json", "w") as f:
    json.dump([(int(k), float(v)) for k, v in elbow], f)
print(elbow)
print("ELBOW DONE")
