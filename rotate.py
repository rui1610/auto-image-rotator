import click
import cv2
import dlib
import numpy as np
import os

from PIL import Image, ImageFile


class Rotator:
    IMAGES_DIRECTORY = "/media/1970"
    IMAGES_BROKEN_DIR = "/media/broken"

    def __init__(self, overwrite_files: bool = False):
        self.detector = dlib.get_frontal_face_detector()
        self.overwrite_files = overwrite_files

    def analyze_images(self):
        # Recursively loop through all files and subdirectories.
        # os.walk() is a recursive generator.
        # The variable "root" is dynamically updated as walk() recursively traverses directories.
        images = []
        for root_dir, sub_dir, files in os.walk(self.IMAGES_DIRECTORY):
            for file_name in files:
                if file_name.lower().endswith((".jpeg", ".jpg", ".png")):
                    file_path = str(os.path.join(root_dir, file_name))
                    if file_name[2] != "._":
                        images.append(file_path)

        # Analyze each image file path - rotating when needed.
        rotations = {}
        with click.progressbar(
            images, label=f"Analyzing {len(images)} Images..."
        ) as filepaths:
            for filepath in filepaths:
                image = self.open_image(filepath)
                if image is None:
                    continue
                rotation = self.analyze_image(image, filepath)

                if rotation:
                    rotations[filepath] = rotation

        print(f"{len(rotations)} Images Rotated")
        for filepath, rotation in rotations.items():
            print(f" - {filepath} (Rotated {rotation} Degrees)")

    def analyze_image(self, image: ImageFile, filepath: str) -> int:
        """Cycles through 4 image rotations of 90 degrees.
        Saves the image at the current rotation if faces are detected.
        """

        # Fetch the original image's EXIF data.
        # This is needed to save the image with the same EXIF data.
        # The EXIF data is not preserved when using OpenCV to save the image.
        orgInfo = image.info
        exif_data = orgInfo.get("exif")

        for cycle in range(0, 4):
            if cycle > 0:
                # Rotate the image an additional 90 degrees for each non-zero cycle.
                image = image.rotate(90, expand=True)

            image_copy = np.asarray(image)
            image_gray = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)

            faces = self.detector(image_gray, 0)
            if len(faces) == 0:
                continue

            # Save the image only if it has been rotated.
            if cycle > 0:
                self.save_image(image, filepath, exif_data)
                return cycle * 90

        return 0

    def open_image(self, filepath: str) -> ImageFile:
        """Intentionally opens an image file using Pillow.
        If opened with OpenCV, the saved image is a much larger file size than the original
        (regardless of whether saved via OpenCV or Pillow).
        """
        result = None
        try:
            result = Image.open(filepath)
            return result
        except OSError:
            # If the image is not a valid image, skip it.
            print(f"Error opening image: {filepath}")

            # move file to a different directory
            error_dir = os.path.join(self.IMAGES_BROKEN_DIR)
            if not os.path.exists(error_dir):
                os.makedirs(error_dir)
            new_filepath = os.path.join(error_dir, os.path.basename(filepath))
            os.rename(filepath, new_filepath)
            print(f"Moved invalid image to: {new_filepath}")

            return None

        return Image.open(filepath)

    def save_image(self, image: ImageFile, filepath: str, exif_data) -> bool:
        """Saves the rotated image using Pillow."""

        if not self.overwrite_files:
            filepath = filepath.replace(".", "-rotated.", 1)

        try:
            image.save(filepath, exif=exif_data)
            return True
        except:
            return False


@click.command()
@click.argument("overwrite_files", type=click.BOOL, default=True)
def cli(overwrite_files: bool = False):
    rotator = Rotator(overwrite_files)
    rotator.analyze_images()


if __name__ == "__main__":
    cli()
