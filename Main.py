#Libraries
import matplotlib;
from matplotlib import animation

matplotlib.use("TkAgg")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sys
import getopt

#Help page
def display_help():
    print("Command usage")
    print("-h Help")
    print("-s Static graph display")
    print("-a Animated graph display")
    print("-i Number of increments per second (default: 10000")
    print("-t Simulation time (default: 3)")


#Parameters

#Defualt values for the options
static_display = False
animated_display = False
user_increments = 10000
user_end_time = 3

args = sys.argv[1:]
options = "hsat:i:"
#Options for help, static graph display or animated display
long_options = ["Help", "Static", "Animated"]
try:

    arguments, values = getopt.getopt(args, options, long_options)
    for opt, val in arguments:
        if opt in ("-h", "--Help"):
            #Displays help page
            display_help()
            sys.exit(0)
        elif opt in ("-s", "--Static"):
            static_display = True
        elif opt in ("-a", "--Animated"):
            animated_display = True
        elif opt in ("-i", "--Increments"):
            user_increments = float(val)
        elif opt in ("-t", "--Endtime"):
            user_end_time = float(val)
except getopt.error as err:
    print(str(err))
    sys.exit(2)

#Physical Constants
G = 1.0 #For our units and simulation G will be 1



#The class for the planetary bodies. Every body that will be simulated will be one of these objects. It contains the position and velocity information.
class Body:
    #Constructor
    def __init__(self, name, mass, radius, position, velocity):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.force = np.zeros(2)

#The class for the solar system
class SolarSystem:

    #Constructor
    def __init__(self, bodies_list, time_step, end_time, method_type):
        self.bodies_list = bodies_list
        self.time = 0.0
        self.time_step = time_step
        self.end_time = end_time
        self.positions_array = None
        self.method_type = method_type


    # Finding force by looping through all other bodies (n-body simulation)
    def find_forces(self, body):
            body.force = np.zeros(2)  # Resetting force to 0 first
            for other_body in self.bodies_list:
                if body != other_body:
                    self.inverse_square_equation(body, other_body)
            return body


    # n-body euler method
    def euler_method(self):

        #Looping through each body
        for body in self.bodies_list:

            #Finding new force
            self.find_forces(body)

            #Finding new position
            body.position += self.time_step * body.velocity

            #Finding new velocity
            body.velocity += self.time_step * (1.0/body.mass) * body.force

        # Incrementing time
        self.time += self.time_step



    # n-body leapfrog method
    def leapfrog_method(self):

        # Looping through each body
        for body in self.bodies_list:

            #Finding new position
            body.position += 0.5 * self.time_step * body.velocity

        #Incrementing time
        self.time += 0.5 * self.time_step

        for body in self.bodies_list:

            # Finding new force
            self.find_forces(body)

            #Finding new velocity
            body.velocity += self.time_step * (1.0/body.mass) * body.force

            #Finding new position again
            body.position += 0.5 * self.time_step * body.velocity

        # Incrementing time again
        self.time += 0.5 * self.time_step

    #Calculates the inverse square force of one body onto another (in this case gravity)
    def inverse_square_equation(self, body, other_body):
        const = -G * body.mass * other_body.mass #Constant of the equation
        x = body.position - other_body.position #the vector x
        body.force += const * x / (np.linalg.norm(x)**3)
        return body

    #Calculates hooke's law force of one body onto another
    def hookes_law_equation(self, body, other_body):
        const = 1.0 #Sprint constant
        x = body.position - other_body.position
        body.force += const * x
        return body

    #Simulation method
    def simulate(self):
        num_bodies = len(self.bodies_list)  #Number of bodies
        iterations = int(self.end_time / self.time_step)  #Number of simulation iterations

        self.positions_array = np.zeros((iterations, num_bodies, 2)) #Array which will store the positions of each body per timestep (time, body, position x_i)

        for i in range(iterations): #Simulation loop
            if self.method_type == "euler": #Chooses simulation method
                self.euler_method()
            else:
                self.leapfrog_method()
            for b, body in enumerate(self.bodies_list): #Saves the positions of each body to numpy array
                self.positions_array[i, b] = body.position


#Plots a simple graph of the system
def plot(system):
    positions = system.positions_array
    num_bodies = positions.shape[1] #Number of bodies from the position array
    plt.figure(figsize=(12, 12))


    for i in range(num_bodies): #Plots the markers for each body with a marker equal to the planets radius (shows a trail that the planet sweeps out)
        plt.plot(positions[:, i, 0], positions[:, i, 1], 'o', label=system.bodies_list[i].name, markersize=system.bodies_list[i].radius*10)


    plt.xlim(-10,10)
    plt.ylim(-10,10)
    plt.xlabel("x position")
    plt.ylabel("y position")
    plt.title("Trajectories of bodies")
    plt.legend()
    plt.axis("equal")
    plt.grid(True)
    plt.show()

#Animates a graph of the system
def animate(system):
    positions = system.positions_array
    num_bodies = positions.shape[1] #Number of bodies from the position array

    fig, ax = plt.subplots(figsize=(12, 12)) #Creates a subplot ax
    ax.set_aspect('equal')
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Trajectories of bodies")
    ax.grid(True)


    plt.xlim(-5, 5)
    plt.ylim(-5, 5)


    points = [ax.plot([], [], 'o', label=system.bodies_list[b].name, markersize=system.bodies_list[b].radius*20)[0] for b in range(num_bodies)] # Create "empty" points for each body, with a markersize equal to the radius


    lines = [ax.plot([], [], lw=1, alpha=0.7)[0] for _ in range(num_bodies)] #Creates empty lines for each body

    #Method for what will be drawn every frame
    def update(frame):
        for b in range(num_bodies): #Loop through all bodies
            x = positions[frame, b, 0] #x position of that body at that frame
            y = positions[frame, b, 1] #y position of that body at that frame


            points[b].set_data([x], [y]) #Draw a point


            lines[b].set_data(positions[:frame, b, 0], positions[:frame, b, 1]) #Draw a line for the trail
        return points + lines

    ani = FuncAnimation(fig, update, frames=positions.shape[0], interval=(1* (10000/user_increments)) , blit=True) #Animation function from matplot lib
    plt.legend()
    plt.show()

def main():

    #Creating bodies
    sun = Body("Sun", 10000.0, 1.0, (0.0, 0.0), (0.0, 0.0))
    planet  = Body("Planet", 1.0, 0.5, (2.0, 0.0), (0.0, 50))
    moon = Body("Moon", 0.05, 0.2, planet.position + (-0.1,0.0), planet.velocity + (-1,4))
    planet2 = Body("Planet", 1.0, 0.5, (-2.0, 0.0), (0.0, -50))

    #Creating system and running the simulation
    my_system = SolarSystem(bodies_list=[sun, planet, moon, planet2], time_step=(1 / user_increments), end_time=(user_end_time / 100), method_type="leapfrog")
    my_system.simulate()

    #Plotting/animating simulation
    if (static_display == True):
        plot(my_system)
    if (animated_display == True):
        animate(my_system)



if __name__ == '__main__':
    main()