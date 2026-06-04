import os
import cv2


class BrainImage:
    """
    Representa una imagen cerebral cargada en el sistema.

    Esta clase se encarga de:
    - Validar que la imagen existe.
    - Comprobar que el formato es compatible.
    - Cargar la imagen original.
    - Convertirla a escala de grises.
    - Guardar información básica de la imagen.
    """

    ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]

    def __init__(self, image_path):
        self.image_path = image_path
        self.original_image = None
        self.gray_image = None
        self.width = None
        self.height = None
        self.channels = None

    def validate_path(self):
        """
        Comprueba que la ruta de la imagen existe.
        """
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"No se encontró la imagen: {self.image_path}")

    def validate_extension(self):
        """
        Comprueba que la imagen tiene una extensión permitida.
        """
        _, extension = os.path.splitext(self.image_path)
        extension = extension.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Formato no permitido: {extension}. "
                f"Formatos permitidos: {self.ALLOWED_EXTENSIONS}"
            )

    def load_image(self):
        """
        Carga la imagen original usando OpenCV.
        """
        self.original_image = cv2.imread(self.image_path)

        if self.original_image is None:
            raise ValueError("No se pudo cargar la imagen. Puede estar dañada o no ser válida.")

        self.height, self.width = self.original_image.shape[:2]

        if len(self.original_image.shape) == 3:
            self.channels = self.original_image.shape[2]
        else:
            self.channels = 1

    def convert_to_gray(self):
        """
        Convierte la imagen original a escala de grises.
        """
        if self.original_image is None:
            raise ValueError("Primero debes cargar la imagen antes de convertirla.")

        self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)

    def load(self):
        """
        Método principal para validar, cargar y convertir la imagen.
        """
        self.validate_path()
        self.validate_extension()
        self.load_image()
        self.convert_to_gray()

    def get_info(self):
        """
        Devuelve información básica de la imagen.
        """
        if self.original_image is None:
            raise ValueError("La imagen todavía no ha sido cargada.")

        return {
            "path": self.image_path,
            "width": self.width,
            "height": self.height,
            "channels": self.channels,
            "format": os.path.splitext(self.image_path)[1].lower()
        }