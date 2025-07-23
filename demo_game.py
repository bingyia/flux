from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, Vec4, WindowProperties
from panda3d.bullet import BulletWorld, BulletRigidBodyNode, BulletBoxShape, BulletPlaneShape


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


class MinecraftDemo(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.accept("escape", self.userExit)

        self.speed = 5
        self.sensitivity = 0.2

        self.keys = {"w": False, "a": False, "s": False, "d": False}
        for key in self.keys:
            self.accept(key, self._set_key, [key, True])
            self.accept(f"{key}-up", self._set_key, [key, False])

        self._setup_world()
        self._setup_camera()
        self.taskMgr.add(self._update, "update")

    def _set_key(self, key: str, value: bool) -> None:
        self.keys[key] = value

    def _setup_world(self) -> None:
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))

        # Ground plane
        plane_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        plane_node = BulletRigidBodyNode("ground")
        plane_node.addShape(plane_shape)
        plane_np = self.render.attachNewNode(plane_node)
        self.world.attachRigidBody(plane_node)

        ground = self.loader.loadModel("box")
        ground.setScale(10, 10, 0.1)
        ground.setColor(0.5, 0.5, 0.5, 1)
        ground.reparentTo(plane_np)

        # 25 cubes with different colors
        colors = [Vec4((i % 5) / 4, ((i // 5) % 5) / 4, (i / 24), 1) for i in range(25)]
        for i, color in enumerate(colors):
            shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
            node = BulletRigidBodyNode(f"cube{i}")
            node.setMass(1.0)
            node.addShape(shape)
            np = self.render.attachNewNode(node)
            np.setPos((i % 5) * 2 - 4, (i // 5) * 2, 1)
            self.world.attachRigidBody(node)

            model = self.loader.loadModel("box")
            model.setColor(color)
            model.reparentTo(np)

    def _setup_camera(self) -> None:
        self.camera.setPos(0, -10, 2)
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        center_x = int(self.win.getProperties().getXSize() / 2)
        center_y = int(self.win.getProperties().getYSize() / 2)
        self.win.movePointer(0, center_x, center_y)

    def _update(self, task):
        dt = globalClock.getDt()
        self.world.doPhysics(dt)

        # Mouse look
        center_x = int(self.win.getProperties().getXSize() / 2)
        center_y = int(self.win.getProperties().getYSize() / 2)
        md = self.win.getPointer(0)
        x = md.getX() - center_x
        y = md.getY() - center_y
        self.win.movePointer(0, center_x, center_y)
        self.camera.setH(self.camera.getH() - x * self.sensitivity)
        self.camera.setP(clamp(self.camera.getP() - y * self.sensitivity, -90, 90))

        # Keyboard movement
        direction = Vec3(0, 0, 0)
        if self.keys["w"]:
            direction.y += self.speed * dt
        if self.keys["s"]:
            direction.y -= self.speed * dt
        if self.keys["a"]:
            direction.x -= self.speed * dt
        if self.keys["d"]:
            direction.x += self.speed * dt
        self.camera.setPos(self.camera, direction)

        return task.cont


if __name__ == "__main__":
    MinecraftDemo().run()
