import sys

from loguru import logger
from pydantic.error_wrappers import ValidationError

from conversion_rate_analyzer.config import MOVING_AVERAGE_WINDOW, PCT_CHANGE_THRESHOLD
from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.moving_average import MovingAverageQueue
from conversion_rate_analyzer.utils.reader import SpotRateReader


@logger.catch
def main():
    if len(sys.argv) < 2:
        logger.warning("Supply the input file path as an argument: python main.py input.jsonl")
        sys.exit(-1)

    input_file = sys.argv[1]
    logger.info(
        (
            "Program starting with parameters:"
            f"\n\tInput File: {input_file}"
            f"\n\tMoving Average Window Size: {MOVING_AVERAGE_WINDOW} ({MOVING_AVERAGE_WINDOW / 60:.2f} minutes)"
            f"\n\tPercent Change Threshold: {PCT_CHANGE_THRESHOLD}"
        )
    )

    queue = MovingAverageQueue()

    try:
        reader = SpotRateReader().jsonlines_reader(input_file)
        for obj in reader:
            try:
                data = CurrencyConversionRate.parse_obj(obj)
                queue.process_new_rate(data)
            except ValidationError as e:
                logger.warning(e)
    except FileNotFoundError as e:
        logger.exception(e)
        # sys.exit(-1)
        raise e


if __name__ == '__main__':
    main()