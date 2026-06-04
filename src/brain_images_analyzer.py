import numpy as np


class BrainImageAnalyzer:
    """
    Analiza de forma básica una imagen cerebral en escala de grises.

    Este análisis es experimental, orientativo y no diagnóstico.
    """

    def __init__(self, brain_image, brain_mask=None):
        self.brain_image = brain_image
        self.brain_mask = brain_mask

    def analyze_dark_areas(self, threshold=50):
        """
        Calcula el porcentaje de zonas oscuras.

        Si hay una máscara cerebral, solo analiza los píxeles dentro
        de esa zona útil. Así se evita contar el fondo negro exterior.
        """

        gray_image = self.brain_image.gray_image

        if gray_image is None:
            raise ValueError("La imagen no está cargada en escala de grises.")

        if self.brain_mask is not None:
            valid_pixels_mask = self.brain_mask > 0
        else:
            valid_pixels_mask = np.ones_like(gray_image, dtype=bool)

        dark_mask = (gray_image < threshold) & valid_pixels_mask

        total_valid_pixels = np.sum(valid_pixels_mask)
        dark_pixels = np.sum(dark_mask)

        if total_valid_pixels == 0:
            raise ValueError("La máscara cerebral no contiene píxeles válidos.")

        dark_ratio = dark_pixels / total_valid_pixels
        dark_percentage = round(dark_ratio * 100, 2)

        return {
            "dark_pixels": int(dark_pixels),
            "total_pixels_analyzed": int(total_valid_pixels),
            "dark_ratio": float(dark_ratio),
            "dark_percentage": dark_percentage,
            "comment": self.generate_comment(dark_ratio)
        }

    def generate_comment(self, dark_ratio):
        """
        Genera una explicación comprensible del porcentaje de zonas oscuras.
        """

        if dark_ratio < 0.10:
            return (
                "El porcentaje de zonas oscuras dentro de la región útil es bajo. "
                "Esto significa que, según este análisis básico, la imagen no presenta "
                "una cantidad elevada de áreas oscuras internas. No se observan indicios "
                "visuales claros de aumento de espacios oscuros."
            )

        elif dark_ratio < 0.25:
            return (
                "El porcentaje de zonas oscuras dentro de la región útil es moderado. "
                "Esto puede indicar la presencia de cavidades, ventrículos, surcos o "
                "espacios hipodensos visibles. El resultado puede ser relevante, pero "
                "no permite confirmar atrofia por sí solo."
            )

        else:
            return (
                "El porcentaje de zonas oscuras dentro de la región útil es elevado. "
                "Esto podría estar relacionado con una mayor presencia de espacios "
                "hipodensos, ventrículos marcados o posible pérdida de volumen cerebral. "
                "Aun así, este análisis es orientativo y no permite establecer un diagnóstico."
            )