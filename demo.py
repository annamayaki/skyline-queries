import random
from time import process_time
import pandas as pd
import matplotlib.pyplot as plt
from sorting import iter_mergesort
from range_tree import build_bbst, skyline_query_rt
from kd_tree import build_kd_tree, skyline_query_kdt

print("Welcome!")
print("Please enter the number of dimensions (2 or 3):")
line = input()
while not line.isdigit() or (int(line) < 2 or int(line) > 3):
    print("Please enter a valid number!")
    line = input()
n_dimensions = int(line)
print("Please enter the number of points to be created.")
print("They must be at least 100 so that the graphs can be produced.")
line = input()
while (not line.isdigit()) or (int(line) < 100):
    print("Please enter a valid number!")
    line = input()
n_points = int(line)
if n_points < 1000:
    n_kd_iters = 100
    n_rng_iters = 10
else:
    n_kd_iters = 10
    n_rng_iters = 5

points = []
if n_dimensions == 2:
    for i in range(n_points):
        temp = [round(random.uniform(400, 20000), 2),
                round(random.uniform(100, 350), 2)]
        points.append(temp)
else:
    for i in range(n_points):
        temp = [round(random.uniform(400, 20000), 2),
                round(random.uniform(100, 350), 2),
                round(random.uniform(400, 20000), 2)]
        points.append(temp)

points = iter_mergesort(points)

time_acc = 0
for i in range(n_rng_iters):
    start_time = process_time()
    range_root = build_bbst(points, 0, n_dimensions)
    stop_time = process_time()
    time_acc += stop_time - start_time
    points = iter_mergesort(points)
time_vals_range = [time_acc / n_rng_iters]
range_root = build_bbst(points, 0, n_dimensions)

time_acc = 0
for i in range(n_rng_iters):
    start_time = process_time()
    range_skyline = skyline_query_rt(range_root, n_dimensions)
    stop_time = process_time()
    time_acc += stop_time - start_time
    points = iter_mergesort(points)
time_vals_range.append(time_acc / n_rng_iters)
range_skyline = skyline_query_rt(range_root, n_dimensions)

time_acc = 0
for i in range(n_kd_iters):
    start_time = process_time()
    kd_root = build_kd_tree(points, n_dimensions)
    stop_time = process_time()
    time_acc += stop_time - start_time
    points = iter_mergesort(points)
time_vals_kd = [time_acc / n_kd_iters]
kd_root = build_kd_tree(points, n_dimensions)

time_acc = 0
for i in range(n_kd_iters):
    start_time = process_time()
    kd_skyline = skyline_query_kdt(kd_root, n_dimensions)
    stop_time = process_time()
    time_acc += stop_time - start_time
time_vals_kd.append(time_acc / n_kd_iters)
kd_skyline = skyline_query_kdt(kd_root, n_dimensions)

row_labels = ['Range Tree', 'k-d Tree']
column_labels = ['Build Time (ms)', 'Skyline Query Time (ms)']
data = pd.DataFrame([time_vals_range, time_vals_kd], index=row_labels, columns=column_labels)
print(data.to_string())

points_x = [x[0] for x in points if x not in kd_skyline]
points_y = [x[1] for x in points if x not in kd_skyline]
sky_x = [x[0] for x in kd_skyline]
sky_y = [x[1] for x in kd_skyline]

if n_dimensions == 2:

    fig = plt.figure(dpi=400, edgecolor='yellow')
    plt.scatter(points_x, points_y, color="navy")
    plt.scatter(sky_x, sky_y, color="yellow")
    plt.title('2D Hotel Skyline Query')
    plt.xlabel('Distance to Beach')
    plt.ylabel('Price per Night')
    plt.show()

elif n_dimensions == 3:

    from mpl_toolkits import mplot3d

    points_z = [x[2] for x in points if x not in kd_skyline]
    sky_z = [x[2] for x in kd_skyline]
    
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter3D(points_x, points_y, points_z, c='blue')
    ax.scatter3D(sky_x, sky_y, sky_z, c='yellow')
    ax.set_title('3D Hotel Skyline Query')
    ax.set_xlabel('Distance to Beach')
    ax.set_ylabel('Price per Night')
    ax.set_zlabel('Distance to City')
    plt.show()
