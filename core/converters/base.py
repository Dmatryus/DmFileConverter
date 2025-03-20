from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class Converter(ABC):
    """
    Abstract base class for file converters.

    Defines a common interface and structure for all file format converters,
    ensuring consistency across different implementations.
    """

    _supported_formats: dict[str, tuple[str]] = {"input": (), "output": ()}

    @property
    def supported_formats(self) -> dict:
        """
        Retrieve the list of supported formats for both input and output.

        Returns:
            dict: A dictionary containing 'input' and 'output' keys with respective lists of supported formats.
        """
        return self._supported_formats

    @staticmethod
    def prepare_format(source_path: str | Path, target_format: str) -> tuple[str, str]:
        """
        Extract the file format from the given source path.

        Args:
            source_path (str | Path): The path to the source file.

        Returns:
            str: The extracted file format.
        """
        source_path = Path(source_path)
        source_format = source_path.suffix[1:].lower()
        target_format = target_format.lower()
        return source_format, target_format

    @classmethod
    def validate_format(cls, source_format: str, target_format: str) -> bool:
        """
        Check if the converter supports the given source and target formats.

        Args:
            source_format (str): The source file format.
            target_format (str): The target file format.

        Returns:
            bool: True if the conversion is supported, False otherwise.
        """
        return (
            source_format in cls._supported_formats["input"]
            and target_format in cls._supported_formats["output"]
        )

    @staticmethod
    def prepare_output_path(source_path: str | Path, target_format: str) -> Path:
        """
        Prepare the output path for the converted file.

        Args:
            source_path (str | Path): Path to the source file.
            target_format (str): The target file format.

        Returns:
            Path: The prepared output path.
        """
        source_path = Path(source_path)
        return source_path.parent / f"{source_path.stem}.{target_format}"

    def convert_function(
        self, source_path: Path, output_path: Path, target_format: Optional[str] = None
    ):

        raise NotImplementedError

    def convert(self, source_path: str | Path, target_format: str) -> None:
        """
        Converts a file from one format to another.
        """

        source_format, target_format = self.prepare_format(source_path, target_format)
        if not self.validate_format(source_format, target_format):
            raise ValueError(
                f"{self.__class__.__name__} not supported conversion fron {source_format} to {target_format}. Suported formats: {self.supported_formats}"
            )

        source_path = Path(source_path)
        output_path = self.prepare_output_path(source_path, target_format)

        self.convert_function(source_path, output_path, target_format)
