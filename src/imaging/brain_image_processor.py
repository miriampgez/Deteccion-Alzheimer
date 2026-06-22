import cv2
import numpy as np
from collections import deque


class BrainImagePreprocessor:
    """
    Preprocesa una imagen cerebral para eliminar el fondo negro exterior
    sin eliminar zonas oscuras internas del cerebro.

    La idea principal es:
    - detectar el fondo negro conectado con los bordes de la imagen
    - eliminar solo ese fondo exterior
    - conservar zonas negras internas, porque pueden ser importantes
    """

    def __init__(self, brain_image):
        self.brain_image = brain_image
        self.gray_image = brain_image.gray_image
        self.background_mask = None
        self.brain_mask = None
        self.cleaned_image = None

    def create_external_background_mask(self, black_threshold=10):
        """
        Detecta el fondo negro exterior conectado con los bordes de la imagen.

        black_threshold:
        - Los píxeles con intensidad <= black_threshold se consideran casi negros.
        - Pero solo se eliminan si están conectados con el borde exterior.
        """

        if self.gray_image is None:
            raise ValueError("La imagen debe estar cargada en escala de grises.")

        height, width = self.gray_image.shape

        # Píxeles casi negros
        black_pixels = self.gray_image <= black_threshold

        # Máscara del fondo exterior
        background_mask = np.zeros_like(self.gray_image, dtype=np.uint8)

        visited = np.zeros_like(self.gray_image, dtype=bool)
        queue = deque()

        # Añadir píxeles negros de los bordes a la cola
        for x in range(width):
            if black_pixels[0, x]:
                queue.append((0, x))
                visited[0, x] = True

            if black_pixels[height - 1, x]:
                queue.append((height - 1, x))
                visited[height - 1, x] = True

        for y in range(height):
            if black_pixels[y, 0]:
                queue.append((y, 0))
                visited[y, 0] = True

            if black_pixels[y, width - 1]:
                queue.append((y, width - 1))
                visited[y, width - 1] = True

        # Flood fill: expandirse solo por píxeles negros conectados al borde
        while queue:
            y, x = queue.popleft()
            background_mask[y, x] = 255

            neighbors = [
                (y - 1, x),
                (y + 1, x),
                (y, x - 1),
                (y, x + 1)
            ]

            for ny, nx in neighbors:
                if 0 <= ny < height and 0 <= nx < width:
                    if not visited[ny, nx] and black_pixels[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((ny, nx))

        self.background_mask = background_mask
        return self.background_mask

    def create_brain_mask(self, black_threshold=10):
        """
        Crea la máscara de zona útil eliminando solo el fondo exterior.

        La zona útil será todo lo que NO sea fondo negro conectado al borde.
        """

        if self.background_mask is None:
            self.create_external_background_mask(black_threshold)

        # Invertimos la máscara:
        # fondo exterior = 255
        # zona útil = 0
        # Queremos lo contrario
        brain_mask = cv2.bitwise_not(self.background_mask)

        # Limpieza ligera para suavizar bordes
        kernel = np.ones((3, 3), np.uint8)

        brain_mask = cv2.morphologyEx(
            brain_mask,
            cv2.MORPH_CLOSE,
            kernel
        )

        self.brain_mask = brain_mask
        return self.brain_mask

    def apply_mask(self):
        """
        Aplica la máscara sobre la imagen original en gris.

        El fondo exterior se elimina, pero las zonas oscuras internas se conservan.
        """

        if self.brain_mask is None:
            self.create_brain_mask()

        self.cleaned_image = cv2.bitwise_and(
            self.gray_image,
            self.gray_image,
            mask=self.brain_mask
        )

        return self.cleaned_image

    def preprocess(self, black_threshold=10):
        """
        Ejecuta todo el preprocesado.
        """

        self.create_external_background_mask(black_threshold)
        self.create_brain_mask(black_threshold)
        self.apply_mask()

        return {
            "background_mask": self.background_mask,
            "brain_mask": self.brain_mask,
            "cleaned_image": self.cleaned_image
        }