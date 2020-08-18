from code42cli.output_formats import output_format
from code42cli.output_formats import OutputFormat
from code42cli.output_formats import to_dynamic_csv


def extraction_output_format(_, __, value):
    if value == OutputFormat.CSV:
        return to_dynamic_csv
    return output_format(_, __, value)
