import os

import jsonlines
from jsonlines.jsonlines import Writer
from loguru import logger

from conversion_rate_analyzer import config
from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.utils.exceptions import SpotRateWriterError


class SpotRateWriter:
    """Class for writing conversion rates that exceed acceptance threshold percentage.
    Data will be written into a jsonline file.

    Throws:
        SpotRateWriterException:
            Attempt made to write without initializing the jsonline writer,
            or the output file has been removed before closing.
    """

    def __init__(self, path: str):
        """
        This writer appends the data to the specified output file.
        If the file does not exist, it will be created.
        The file will be flushed after each write.
        """
        self.path = path

        if not os.path.exists(self.path):
            logger.info(f"Output file ({self.path}) does not exist. Creating file.")

        self.writer: Writer = jsonlines.open(self.path, mode="a", flush=True)
        logger.info("Jsonline writer created.")

    def write(
            self,
            data: CurrencyConversionRate,
            current_avg_rate: float = None,
            pct_change: float = None
    ):
        out = data.dict()

        if config.VERBOSE:
            out["average_rate"] = current_avg_rate
            out["pct_change"] = pct_change
        else:
            del out["rate"]

        out["alert"] = "spotChange"

        self.writer.write(out)

    def close(self):
        self.writer.close()

        if not os.path.exists(self.path):
            raise SpotRateWriterError("Output file has been removed before closing.", self.path)

        logger.info(f"Jsonline writer terminated and output file closed. Saved output at {self.path}.")
