from .support import import_folder
from .enums import AnimationType, Speeds

from .type_aliases import BareVec2, Surface, Sprite


class ParticleEffect(Sprite):
    """
    Player particles
    """
    def __init__(self, pos: BareVec2, animation_type: AnimationType) -> None:
        super().__init__()
        self.frame_index: float = 0.0
        self.animation_speed: float = Speeds.PARTICLE_ANIMATION.value

        self.frame: list[Surface]
        self.frames: list[Surface] = list(
            import_folder(
                f"src/graphics/character/dust_particles/{animation_type.value}"
            )
        )
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=pos)

    def animate(self) -> None:
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift: int) -> None:
        self.animate()
        self.rect.x += x_shift
