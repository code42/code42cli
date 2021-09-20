from code42cli.output_formats import DataFrameOutputFormatter
import pandas as pd
import py42.sdk
from py42.sdk.queries.fileevents.file_event_query import FileEventQuery
from py42.sdk.queries.fileevents.filters import EventTimestamp
from datetime import datetime


sdk = py42.sdk.from_local_account("console.us.code42.com", "literally_skynet+c42demo@code42.com", "2e*6Mya&fe3&iX)")

query = FileEventQuery(EventTimestamp.on_or_after(datetime(2021, 8, 10)), EventTimestamp.on_or_before(datetime(2021, 8, 11)))
r = sdk.securitydata.search_file_events(query)
df = pd.DataFrame(r["fileEvents"])

formatter = DataFrameOutputFormatter("NOT_VALID")
f = formatter.get_formatted_output(df)

# checkpointed = []


# def checkpoint(event):
#     checkpointed.append(event['eventId'])


# table = DataFrameOutputFormatter("TABLE")
# csv = DataFrameOutputFormatter("CSV")
# json = DataFrameOutputFormatter("JSON")
# raw = DataFrameOutputFormatter("RAW-JSON")


# def yield_dfs():
#     yield df[:8]
#     # yield df[10:20]
#     # yield df[20:30]
#     # yield df[30:40]


# table.echo_formatted_dataframes(yield_dfs())
# csv.echo_formatted_dataframes(yield_dfs())
# json.echo_formatted_dataframes(yield_dfs())
# raw.echo_formatted_dataframes(yield_dfs())
