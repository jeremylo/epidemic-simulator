

class Position:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(x: {0}, y: {0})".format(self.x, self.y)


class Velocity:

    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def __str__(self):
        return "(dx: {0}, dy: {0})".format(self.x, self.y)


class Agent:

    def __init__(self, position: Position, velocity: Velocity):
        self.position = position
        self.velocity = velocity

    def update(self):
        pass


if __name__ == '__main__':

    import time

    a = Agent(Position(0, 0), Velocity(2, 1))
    #b = Agent(Position(0, 0), Velocity(2, 1))

    agents = [a]

    while True:
        i = 0
        for agent in agents:
            agent.update()
            print(i, agent.position, agent.velocity)
            i += 1

        time.sleep(0.1)
