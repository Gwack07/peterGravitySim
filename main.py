import math
import turtle
import random

# time step for simulation
tick = 0.025
# gravitational constant
G = 500
# screen dimensions in pixels
screenDimensions = [800, 600]
# camera zoom scale
scale = 4
# list to store all particles
particles = []
# position when starting a drag
startPos = None
# camera offset for panning
cameraPos = [0, 0]
# determines if the user is placing a planet or a particle
isParticle = True
# position where right click drag started
rightDragStart = None
# flag to detect if right dragging occurred
rightDragged = False
# pause state of the simulation
paused = False
# bool for force colours
showForceColours = True

# setup turtle graphics screen
screen = turtle.Screen()
screen.title("gravitational particle simulator")
screen.setup(screenDimensions[0], screenDimensions[1])
screen.tracer(0)  # smoother animation
screen.bgcolor("black")
turtle.colormode(1.0) #allows for rgb for the gradients

# class for particles including gravity and movement
class Particle:
    def __init__(self, mass, sVelocity, pos):
        self.mass = mass
        self.velocity = sVelocity.copy() #starting velocity
        self.pos = pos.copy()
        self.force = [0, 0]
        self.absForce = [0, 0]

        self.particle = turtle.Turtle()
        self.particle.penup()
        self.particle.shape("circle")
        self.particle.color("red")
        self.particle.shapesize(0.5)
        self.particle.goto(scale * (self.pos[0]+cameraPos[0]), scale * (self.pos[1]+cameraPos[1]))

    def resetForce(self):
        # resets force before next update
        self.force = [0, 0]
        self.absForce = [0, 0]

    def move(self):
        # updates velocity and position based on net force
        accelX = self.force[0] / (self.mass + 1e-11)
        accelY = self.force[1] / (self.mass + 1e-11)
        self.velocity[0] += accelX * tick
        self.velocity[1] += accelY * tick
        self.pos[0] += self.velocity[0] * tick
        self.pos[1] += self.velocity[1] * tick
        self.particle.goto(scale * (self.pos[0]+cameraPos[0]), scale * (self.pos[1]+cameraPos[1]))

        if showForceColours: # toggle for colour gradients
            forceMag = self.forceMagnitude()
            self.updateColor(forceMag)
        else:
            self.particle.color("red")

    def computeGravitationalAttraction(self, p2):
        # computes gravitational attraction between two particles
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

        self.absForce[0] += math.fabs(fx)
        self.absForce[1] += math.fabs(fy)

    def forceMagnitude(self):
        return math.sqrt(self.absForce[0] ** 2 + self.absForce[1] ** 2)

    def updateColor(self, forceMag):
        # normalise force factor for colouring
        scaleFactor = 10000
        normalized = min(forceMag / scaleFactor, 1.0)
        # gradient from blue to red (high to low force)
        red = normalized
        blue = 1 - normalized
        green = 0  # optional: add green for a 3-color gradient
        self.particle.color((red, green, blue))


# subclass for creating planet objects with size and color
class Planet(Particle):
    def __init__(self, mass, sVelocity, pos, color, size):
        super().__init__(mass, sVelocity, pos)
        self.color = color
        self.size = size
        self.particle.color(self.color)
        self.particle.shapesize(self.size)
        self.originalColour = color

    def move(self):
        # updates velocity and position based on net force
        accelX = self.force[0] / (self.mass + 1e-11)
        accelY = self.force[1] / (self.mass + 1e-11)
        self.velocity[0] += accelX * tick
        self.velocity[1] += accelY * tick
        self.pos[0] += self.velocity[0] * tick
        self.pos[1] += self.velocity[1] * tick
        self.particle.goto(scale * (self.pos[0]+cameraPos[0]), scale * (self.pos[1]+cameraPos[1]))

# class for creating clickable buttons on screen
class Button:
    def __init__(self, label, x, y, width, height, callback):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.callback = callback

        # create button shape
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.penup()
        self.turtle.goto(x - width / 2, y - height / 2)
        self.turtle.color("black", "gray")
        self.turtle.begin_fill()
        for _ in range(2):
            self.turtle.forward(width)
            self.turtle.left(90)
            self.turtle.forward(height)
            self.turtle.left(90)
        self.turtle.end_fill()

        # create label
        self.text = turtle.Turtle()
        self.text.hideturtle()
        self.text.penup()
        self.text.goto(x, y - 6)
        self.text.color("white")
        self.text.write(label, align="center", font=("Arial", 10, "bold"))

        # create invisible clickable area for callback
        self.click_area = turtle.Turtle()
        self.click_area.penup()
        self.click_area.goto(x, y)
        self.click_area.shape("square")
        self.click_area.shapesize(stretch_wid=height / 20, stretch_len=width / 20)
        self.click_area.fillcolor("")
        self.click_area.color("")
        self.click_area.onclick(self.onClick)

    def onClick(self, x, y):
        # executes callback function when button clicked
        self.callback()

    def contains(self, x, y):
        # checks if a coordinate is inside the button area
        half_w = self.width / 2
        half_h = self.height / 2
        return (self.x - half_w <= x <= self.x + half_w) and (self.y - half_h <= y <= self.y + half_h)

# mouse control handlers
def onMousePress(x, y):
    global startPos
    startPos = [x / scale, y / scale]


# when the left mouse is released - it will append a particle at the end position
def onMouseRelease(x, y):
    global startPos
    if startPos is None:
        return
    end_pos = [x / scale, y / scale]
    dx = end_pos[0] - startPos[0]
    dy = end_pos[1] - startPos[1]
    try:
        particles.append(Particle(1, [dx, dy], [startPos[0] - cameraPos[0], startPos[1] - cameraPos[1]]))
    except:
        print("invalid input particle not created")
    startPos = None

# when the mouse is dragged we send the current position of the mouse to chnage the position of the origin
def onRightDrag(x, y):
    global rightDragStart, rightDragged
    rightDragStart = [x, y]
    rightDragged = False

# when the mouse is dragged we send the current position of the mouse to chnage the position of the origin
def onRightDragMotion(x, y):
    global rightDragStart, cameraPos, rightDragged
    if rightDragStart is None:
        return
    dx = x - rightDragStart[0]
    dy = y - rightDragStart[1]
    cameraPos[0] += dx / scale
    cameraPos[1] += dy / scale
    rightDragStart = [x, y]
    rightDragged = True

# called when right click
def onRightClick(x, y):
    global isParticle
    # error checking the inputs for the custom particles
    try:
        mass = float(screen.textinput("Mass", "Enter mass:"))
        vel_x = float(screen.textinput("Velocity X", "Enter initial X velocity:"))
        vel_y = float(screen.textinput("Velocity Y", "Enter initial Y velocity:"))
        # checking if particle or plannet
        if isParticle == True:
            new_particle = Particle(mass, [vel_x, vel_y], [x / scale - cameraPos[0], y / scale- cameraPos[1]])
        else:
            # if planet then there are extra options
            colour = str(screen.textinput("Colour", "Enter Colour:"))
            size = float(screen.textinput("Size", "Enter Size:"))
            new_particle = Planet(mass, [vel_x, vel_y], [x / scale - cameraPos[0], y / scale - cameraPos[1]], colour, size)
        particles.append(new_particle)
    except:
        print("invalid input particle not created")
    screen.listen()

# simulation control functions
def increaseTick():
    global tick
    tick *= 2
    print(f"tick increased to {tick}")

def decreaseTick():
    global tick
    tick *= 0.5
    print(f"tick decreased to {tick}")

def flipTick():
    global tick
    tick *= -1
    print(f"tick flipped to {tick}")

def increaseScale():
    global scale
    scale *= 2
    print(f"scale increased to {scale}")

def decreaseScale():
    global scale
    scale *= 0.5
    print(f"scale decreased to {scale}")

# produces 100 particles with random parameters
def randomParticle():
    global particles
    for i in range(0, 100):
        particles.append(Particle(random.randint(0, 100000),
                                  [random.uniform(-10000, 10000), random.uniform(-10000, 10000)],
                                  [random.uniform(-100, 100), random.uniform(-100, 100)]))

def left():
    global cameraPos, scale
    cameraPos[0] += 5 / scale

def right():
    global cameraPos, scale
    cameraPos[0] -= 5 / scale

def up():
    global cameraPos, scale
    cameraPos[1] -= 5 / scale

def down():
    global cameraPos, scale
    cameraPos[1] += 5 / scale

# increasing and decreasing the gravity constant
def increaseG():
    global G
    G *= 2
    print(f"G increased to {G}")

def decreaseG():
    global G
    G *= 0.5
    print(f"G decreased to {G}")

def togglePause():
    global paused
    paused = not paused
    print("paused" if paused else "resumed")

def resetSimulation():
    global particles
    for p in particles:
        p.particle.hideturtle()
    particles = []
    print("simulation reset")

def particlePlanetSwap():
    global isParticle
    isParticle = not isParticle

def toggleColour():
    global showForceColours
    showForceColours = not showForceColours
    print("show force colours toggled")

# event to screen coordinate conversion
def canvasWorldCoords(event):
    x = event.x - screen.window_width() // 2
    y = screen.window_height() // 2 - event.y
    return x, y

# event binding handlers - functions that might need to be triigered under certain conditions
def handleMousePress(event):
    x, y = canvasWorldCoords(event)
    onMousePress(x, y)

def handleMouseRelease(event):
    x, y = canvasWorldCoords(event)
    for button in buttons:
        if button.contains(x, y):
            return
    onMouseRelease(x, y)

def handleRightClick(event):
    global rightDragged
    if rightDragged:
        return
    x, y = canvasWorldCoords(event)
    onRightClick(x, y)

def handleRightDragStart(event):
    x, y = canvasWorldCoords(event)
    onRightDrag(x, y)

def handleRightDragMotion(event):
    x, y = canvasWorldCoords(event)
    onRightDragMotion(x, y)

# keybinds for interaction
keybinds = {
    'p': increaseScale,
    'l': decreaseScale,
    'Up': increaseTick,
    'Down': decreaseTick,
    'space': flipTick,
    'r': randomParticle,
    'w': up,
    'a': left,
    'd': right,
    's': down,
    'o': particlePlanetSwap,
    'x': togglePause,
    'z': resetSimulation,
    'k': increaseG,
    'm' : decreaseG,
    'j': toggleColour,
}

# onscreen buttons for actions
buttons = [
    Button("Scale + (p)", 300, 250, 100, 40, increaseScale),
    Button("Scale - (l)", 300, 200, 100, 40, decreaseScale),
    Button("Tick + (up arrow)", 300, 150, 100, 40, increaseTick),
    Button("Tick - (up arrow)", 300, 100, 100, 40, decreaseTick),
    Button("Flip Tick (space)", 300, 50, 100, 40, flipTick),
    Button("Random (random)", 300, 0, 100, 40, randomParticle),
    Button("w", -300, 100, 40, 40, up),
    Button("s", -300, 0, 40, 40, down),
    Button("a", -350, 50, 40, 40, left),
    Button("d", -250, 50, 40, 40, right),
    Button("Toggle P/P (o)", 300, -50, 100, 40, particlePlanetSwap),
    Button("Pause (x)", 300, -100, 100, 40, togglePause),
    Button("Reset (z)", 300, -150, 100, 40, resetSimulation),
    Button("increase G (k)", 300, -200, 100, 40, increaseG),
    Button("decrease G (m)", 300, -250, 100, 40, decreaseG),
]

# main update loop - main logic for the update loop
def update():
    if not paused:
        for p in particles:
            p.resetForce()
        for i in range(len(particles)):
            for j in range(i):
                particles[i].computeGravitationalAttraction(particles[j])
        for p in particles:
            p.move()
    screen.update()
    screen.ontimer(update, int(abs(tick) * 1000))

# setup canvas event bindings
canvas = screen.getcanvas()
canvas.bind("<ButtonPress-1>", handleMousePress)
canvas.bind("<ButtonRelease-1>", handleMouseRelease)
canvas.bind("<ButtonRelease-2>", handleRightClick)
canvas.bind("<ButtonPress-2>", handleRightDragStart)
canvas.bind("<B2-Motion>", handleRightDragMotion)
canvas.bind("<Control-ButtonRelease-1>", handleRightClick)
canvas.bind("<Control-ButtonPress-1>", handleRightDragStart)
canvas.bind("<Control-B1-Motion>", handleRightDragMotion)

# setup key events
for key, func in keybinds.items():
    screen.onkey(func, key)

screen.listen()
update()
turtle.mainloop()