import sound
import ui
import scene
import functools
import itertools
from scene import SpriteNode, ShapeNode, LabelNode, Action, Scene, Node, Rect, Point
from dataclasses import dataclass
from typing import ClassVar, List
import time
from functools import partial
from scene import SpriteNode, ShapeNode, LabelNode, Action, Scene, Node, Rect, Point, Texture
from urllib.request import urlopen

FPS: float = 60

DEBUG = False

#url = urlopen('https://pre00.deviantart.net/ba81/th/pre/f/2009/242/f/4/space_invaders_sprite_sheet_by_gooperblooper22.png')
with open('space_invaders.png', 'rb') as f:
    img = ui.Image.from_data(f.read())
whole_sprite = Texture(img)
taito_sprite = whole_sprite.subtexture(Rect(0.0, 0.837, 1, 0.163))
invader1 = whole_sprite.subtexture(Rect(0.0, 0.88, 0.05, 0.012))
invader2 = whole_sprite.subtexture(Rect(0.054, 0.88, 0.05, 0.012))
invader3 = whole_sprite.subtexture(Rect(0.112, 0.88, 0.05, 0.012))
invader4 = whole_sprite.subtexture(Rect(0.167, 0.88, 0.05, 0.012))
invader5 = whole_sprite.subtexture(Rect(0.232, 0.88, 0.05, 0.012))
invader6 = whole_sprite.subtexture(Rect(0.285, 0.88, 0.05, 0.012))
ufo = whole_sprite.subtexture(Rect(0.342, 0.88, 0.09, 0.012))
ship = whole_sprite.subtexture(Rect(0.445, 0.88, 0.05, 0.01))
shield1 = whole_sprite.subtexture(Rect(0.505, 0.88, 0.085, 0.019))
shield2 = whole_sprite.subtexture(Rect(0.598, 0.88, 0.085, 0.019))
shield3 = whole_sprite.subtexture(Rect(0.683, 0.88, 0.085, 0.019))
shield4 = whole_sprite.subtexture(Rect(0.77, 0.88, 0.085, 0.019))
shield5 = whole_sprite.subtexture(Rect(0.77, 0.853, 0.085, 0.019))
shield6 = whole_sprite.subtexture(Rect(0.575, 0.856, 0.085, 0.019))
beam = whole_sprite.subtexture(Rect(0.66, 0.853, 0.03, 0.019))
explosion = whole_sprite.subtexture(Rect(0.702, 0.853, 0.055, 0.016))
title = whole_sprite.subtexture(Rect(0.264, 0.913, 0.4, 0.09))

@dataclass
class GameObject(SpriteNode):
    """
    Game Object base class. / ゲームオブジェクト基本クラス
    """

    obj_id: ClassVar[int] = 0
    id: int = 0
    invisible: bool = False
    #type: str = ''

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.id = self.get_new_id()

    def collided_with(self, other) -> None:
        """
        Collision detection. / 衝突判定
        """
        name = 'collided_with_' + getattr(other, 'type', '')
        f = getattr(self, name, None)
        if f:
            f(other)

    def update(self, now) -> None:
        """
        Called on every game loop. / 毎フレームの更新
        """
        pass

    @property
    def body(self):
        """
        Get body size for collision detection. / 衝突判定用の矩形取得
        """
        return self.frame

    def draw_debug_info(self) -> None:
        """
        Draw object info for debugging. / デバッグ用の情報描画
        """
        if not DEBUG:
            return
        r = self.body
        path = ui.Path.rect(r.x, r.y, r.w, r.h)
        shape = ShapeNode(path, fill_color='clear', stroke_color='black', parent=self)
        self.add_child(shape)

        label_id = LabelNode(text=str(self.id), parent=self)
        label_coord = LabelNode(text='({},{})'.format(self.frame.x, self.frame.y), parent=self)
        self.add_child(label_id)
        self.add_child(label_coord)

    def get_new_id(self) -> int:
        GameObject.obj_id += 1
        return self.obj_id


class Weapon(GameObject):
    destintion: Point
    speed: int
    move_key: str
    
    def collided_with_enemy(self, other):
        self.invisible = True
        other.invisible = True
        self.remove_all_actions()
        other.run_action(Action.sequence(
            Action.call(lambda: Explosion(parent=self.parent, position=other.position)),
            Action.call(functools.partial(self.kill_enemy, other))))

    def kill_enemy(self, enemy):
        enemy.invisible = True
        enemy.remove_from_parent()
        self.die()

    def move(self):
        x, y = self.position
        yy = min(self.destination[1], y + self.speed)
        if yy == self.destination[1]:
            sequences = [Action.move_to(x, yy),                
                         Action.call(self.die)]
        else:
            sequences = [Action.move_to(x, yy),
                         Action.call(self.move)]
        self.run_action(Action.sequence(*sequences), 'moving')

    def die(self) -> None:
        self.invisible = True
        self.parent.player.weapon = None
        self.remove_from_parent()


@dataclass
class Player(GameObject):
    """
    Game player class. / ゲームプレイヤークラス
    """
    weapon: Weapon = None
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def body(self) -> Rect:
        r = self.frame
        return Rect(r.x, r.y, r.w - 10, r.h - 50)

    def touch_began(self, touch):
        pass
        # sound.play_effect('arcade:Coin_3')
    def touch_ended(self, touch):
        x, y = self.position
        dest = (x, self.parent.size.h)
        if self.weapon:
            return
        b = Weapon(beam, position=(x, y), x_scale=2, y_scale=2)
        b.destination = dest
        b.speed = 40
        self.parent.add_child(b)
        self.weapon = b
        b.move()

@dataclass
class Enemy(GameObject):
    """
    Enemy class. / エネミークラス
    """
    pos_base: ClassVar[Point]
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Explosion(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tex = SpriteNode(explosion, parent=self, x_scale=2, y_scale=2)
        self.run_action(Action.sequence(Action.wait(0.5), Action.remove()))


class Invader(Enemy):
    def __init__(self, *args, textures=None, **kwargs):
        super().__init__(textures[0], *args, **kwargs)
        self.textures = textures
        self.last_updated = 0
        self.type = 'enemy'

    def update(self, now):
        if now - self.last_updated > 1:
            self.texture = self.textures[int(now) % 2]
            self.last_updated = now

Invader1 = partial(Invader, textures=(invader1, invader2), x_scale=3, y_scale=3)
Invader2 = partial(Invader, textures=(invader3, invader4), x_scale=3, y_scale=3)
Invader3 = partial(Invader, textures=(invader5, invader6), x_scale=3, y_scale=3)


class Game(Scene):
    """
    Game main class. / ゲームメインクラス
    """
    def setup(self):
        self.background_color = 'black'

        self.ground = Node()
        self.add_child(self.ground)
        self.ground.position = self.size / 2
        self.ground.size = self.size
        self.ground.anchor_point = (0.5, 0.5)
        self.ground.alpha = 1.0

        self.player = Player(ship, x_scale=6, y_scale=6)
        self.player.position = (self.size.w / 20, self.size.h / 20)
        self.player.size /= 2
        self.player.draw_debug_info()
        self.add_child(self.player)
        
        enemy_pos_base = (100, self.size.h / 2)
        Enemy.pos_base = enemy_pos_base
        bx, by = enemy_pos_base
        colors = ['#f400ff', '#00c8e6', '#44ee00']
        for x in range(11):
            for y in range(10):
                n = y % 3 + 1
                cls = globals()['Invader'+str(n)]
                cls(position=(bx + 50*x, by + 50*y), parent=self, color=colors[y%len(colors)])

    def update(self):
        """
        Update game. / 毎フレームの更新処理
        """
        weapons = filter(lambda c: isinstance(c, Weapon), self.children)
        enemies = filter(lambda c: isinstance(c, Enemy), self.children)
        for obj in weapons:
            self.check_collision(obj, enemies)
        now = time.time()
        for o in self.children:
            f = getattr(o, 'update', None)
            if f:
                f(now)

    def touch_began(self, touch):
        self.player.touch_began(touch)

    def touch_moved(self, touch):
        x, y = touch.location
        self.player.run_action(Action.move_to(x, self.player.position.y))

    def touch_ended(self, touch):
        self.player.touch_ended(touch)

    def check_collision(self, obj, others):
        if not isinstance(obj, GameObject):
            return
        for other in others:
            if not isinstance(other, GameObject):
                continue
            if obj.invisible:
                return
            if other.invisible:
                continue
            if obj is other:
                continue
            if obj.frame.intersects(other.frame):
                obj.collided_with(other)


if __name__ == '__main__':
    scene.run(Game(), scene.PORTRAIT, show_fps=True, frame_interval=2)
