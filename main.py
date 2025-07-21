import math
import turtle
import random

tick = 0.05
G = 1000
screenDimensions = [800, 600]
scale = 1
particles = []
start_pos = None
cameraPos = [0,0] #up down left right
isParticle = True

screen = turtle.Screen()
screen.title("Gravitational Particle Simulator")
screen.bgcolor("black")
screen.setup(width=screenDimensions[0], height=screenDimensions[1])
screen.tracer(0)

class Particle:
    def __init__(self, mass, sVelocity, pos):
        self.mass = mass
        self.velocity = sVelocity.copy()
        self.pos = pos.copy()
        self.force = [0, 0]

        self.particle = turtle.Turtle()
        self.particle.penup()
        self.particle.shape("circle")
        self.particle.color("red")
        self.particle.shapesize(0.5)
        self.particle.goto(scale * (self.pos[0]+cameraPos[0]), scale * (self.pos[1]+cameraPos[1]))

    def resetForce(self):
        self.force = [0, 0]

    def move(self):
        accelX = self.force[0] / (self.mass + 1e-11)
        accelY = self.force[1] / (self.mass + 1e-11)
        self.velocity[0] += accelX * tick
        self.velocity[1] += accelY * tick
        self.pos[0] += self.velocity[0] * tick
        self.pos[1] += self.velocity[1] * tick
        self.particle.goto(scale * (self.pos[0]+cameraPos[0]), scale * (self.pos[1]+cameraPos[0]))

    def computeGravitationalAttraction(self, p2):
        dx = p2.pos[0] - self.pos[0]
        dy = p2.pos[1] - self.pos[1]
        rSquared = dx ** 2 + dy ** 2
        if rSquared == 0:
            return
        r = math.sqrt(rSquared)
        forceMagnitude = G * self.mass * p2.mass / rSquared
        fx = forceMagnitude * dx / r
        fy = forceMagnitude * dy / r
        self.force[0] += fx
        self.force[1] += fy
        p2.force[0] -= fx
        p2.force[1] -= fy

class Planet(Particle):
    def __init__(self, mass, sVelocity, pos, color, size):
        super().__init__(mass, sVelocity, pos)
        self.color = color
        self.size = size
        self.particle.color(self.color)
        self.particle.shapesize(self.size)

def on_mouse_press(x, y):
    global start_pos
    start_pos = [x / scale, y / scale]

def on_mouse_release(x, y):
    global start_pos
    if start_pos is None:
        return
    end_pos = [x / scale, y / scale]
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    try:
        particles.append(Particle(1, [dx, dy], start_pos.copy()))
    except:
        print("Invalid input, particle not created.")
    start_pos = None

def onRightClick(x, y):
    global isParticle
    try:
        mass = float(screen.textinput("Mass", "Enter mass:"))
        vel_x = float(screen.textinput("Velocity X", "Enter initial X velocity:"))
        vel_y = float(screen.textinput("Velocity Y", "Enter initial Y velocity:"))

        if isParticle == True:
            new_particle = Particle(mass, [vel_x, vel_y], [x / scale, y / scale])
        else:
            colour = str(screen.textinput("Colour", "Enter Colour:"))
            size = float(screen.textinput("Size", "Enter Size:"))
            new_particle = Planet(mass, [vel_x, vel_y], [x / scale, y / scale],colour, size)
        particles.append(new_particle)
    except:
        print("Invalid input, particle not created.")
    screen.listen()

def increaseTick():
    global tick
    tick *= 2
    print(f"Tick increased to {tick}")

def decreaseTick():
    global tick
    tick *= 0.5
    print(f"Tick decreased to {tick}")

def flipTick():
    global tick
    tick *= -1
    print(f"Tick flipped to {tick}")

def increaseScale():
    global scale
    scale *= 2
    print(f"Scale increased to {scale}")

def decreaseScale():
    global scale
    scale *= 0.5
    print(f"Scale decreased to {scale}")

def randomParticle():
    global particles
    for i in range(0,100):
        particles.append(Particle(random.randint(0, 100000), [random.uniform(-10000, 10000),random.uniform(-10000, 10000)], [random.uniform(-100, 100),random.uniform(-100, 100)]))

def left():
    global cameraPos
    cameraPos[0] -= 1
    print(f"Camera pos left {cameraPos}")

def right():
    global cameraPos
    cameraPos[0] += 1

def up():
    global cameraPos
    cameraPos[1] += 1

def down():
    global cameraPos
    cameraPos[1] -= 1

def particlePlanetSwap():
    global isParticle
    isParticle = not isParticle

keybinds = {
    'p': increaseScale,
    'l': decreaseScale,
    'Up': increaseTick,
    'Down': decreaseTick,
    'space': flipTick,
    'r':randomParticle,
    'w':up,
    'a':left,
    'd':right,
    's':down,
    'o':particlePlanetSwap
}

def update():
    for p in particles:
        p.resetForce()

    for i in range(len(particles)):
        for j in range(i):
            particles[i].computeGravitationalAttraction(particles[j])

    for p in particles:
        p.move()

    screen.update()
    screen.ontimer(update, int(abs(tick) * 1000)) 

canvas = screen.getcanvas()
canvas.bind("<ButtonPress-1>", lambda e: on_mouse_press(
    e.x - screen.window_width() // 2,
    screen.window_height() // 2 - e.y
))
canvas.bind("<ButtonRelease-1>", lambda e: on_mouse_release(
    e.x - screen.window_width() // 2,
    screen.window_height() // 2 - e.y
))
screen.onclick(onRightClick, btn=2)

for key, func in keybinds.items():
    screen.onkey(func, key)

screen.listen()
update()
turtle.mainloop()


