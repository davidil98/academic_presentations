"""Mobject que reproduce un video dentro de una escena Manim.

Uso:
    from toolkit import VideoMobject

    video = VideoMobject("figures/mi_video.mp4", speed=1.0, loop=True)
    self.add(video)
"""

from dataclasses import dataclass

import numpy as np
from manim import *
from PIL import Image

try:
    import cv2
except ImportError:
    cv2 = None
    _CV2_MISSING_MSG = (
        "VideoMobject requiere opencv-python. "
        "Instálalo con: pip install opencv-python"
    )


@dataclass
class VideoStatus:
    time: float = 0
    videoObject: "cv2.VideoCapture | None" = None

    def __deepcopy__(self, memo):
        return self


class VideoMobject(ImageMobject):
    """ImageMobject que reproduce un video frame a frame.

    Parameters
    ----------
    filename : str
        Ruta al archivo de video.
    imageops : callable, optional
        Operación PIL.ImageOps a aplicar a cada frame.
    speed : float, optional
        Factor de velocidad (1.0 = normal, 2.0 = doble).
    loop : bool, optional
        Si True, el video reinicia al terminar.
    """

    def __init__(self, filename=None, imageops=None, speed=1.0, loop=False, **kwargs):
        if cv2 is None:
            raise ImportError(_CV2_MISSING_MSG)

        self.filename = filename
        self.imageops = imageops
        self.speed = speed
        self.loop = loop
        self._id = id(self)
        self.status = VideoStatus()
        self.status.videoObject = cv2.VideoCapture(filename)

        self.status.videoObject.set(cv2.CAP_PROP_POS_FRAMES, 1)
        ret, frame = self.status.videoObject.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            if imageops is not None:
                img = imageops(img)
        else:
            img = Image.fromarray(
                np.uint8(
                    [
                        [63, 0, 0, 0],
                        [0, 127, 0, 0],
                        [0, 0, 191, 0],
                        [0, 0, 0, 255],
                    ]
                )
            )

        super().__init__(img, **kwargs)
        if ret:
            self.add_updater(self.videoUpdater)

    def videoUpdater(self, mobj, dt):
        if dt == 0:
            return
        status = self.status
        status.time += 1000 * dt * mobj.speed
        self.status.videoObject.set(cv2.CAP_PROP_POS_MSEC, status.time)
        ret, frame = self.status.videoObject.read()
        if (not ret) and self.loop:
            status.time = 0
            self.status.videoObject.set(cv2.CAP_PROP_POS_MSEC, status.time)
            ret, frame = self.status.videoObject.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            if mobj.imageops is not None:
                img = mobj.imageops(img)
            mobj.pixel_array = change_to_rgba_array(
                np.asarray(img), mobj.pixel_array_dtype
            )
