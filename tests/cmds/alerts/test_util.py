import code42cli.cmds.alerts_mod.util as alert_util


ALERT_SUMMARY_LIST = [{"id": i} for i in range(20)]

ALERT_DETAIL_RESULT = [
    {"alerts_mod": [{"id": 1, "createdAt": "2020-01-17"}, {"id": 11, "createdAt": "2020-01-18"}]},
    {"alerts_mod": [{"id": 2, "createdAt": "2020-01-19"}, {"id": 12, "createdAt": "2020-01-20"}]},
    {"alerts_mod": [{"id": 3, "createdAt": "2020-01-01"}, {"id": 13, "createdAt": "2020-01-02"}]},
    {"alerts_mod": [{"id": 4, "createdAt": "2020-01-03"}, {"id": 14, "createdAt": "2020-01-04"}]},
    {"alerts_mod": [{"id": 5, "createdAt": "2020-01-05"}, {"id": 15, "createdAt": "2020-01-06"}]},
    {"alerts_mod": [{"id": 6, "createdAt": "2020-01-07"}, {"id": 16, "createdAt": "2020-01-08"}]},
    {"alerts_mod": [{"id": 7, "createdAt": "2020-01-09"}, {"id": 17, "createdAt": "2020-01-10"}]},
    {"alerts_mod": [{"id": 8, "createdAt": "2020-01-11"}, {"id": 18, "createdAt": "2020-01-12"}]},
    {"alerts_mod": [{"id": 9, "createdAt": "2020-01-13"}, {"id": 19, "createdAt": "2020-01-14"}]},
    {"alerts_mod": [{"id": 10, "createdAt": "2020-01-15"}, {"id": 20, "createdAt": "2020-01-16"}]},
]

SORTED_ALERT_DETAILS = [
    {"id": 12, "createdAt": "2020-01-20"},
    {"id": 2, "createdAt": "2020-01-19"},
    {"id": 11, "createdAt": "2020-01-18"},
    {"id": 1, "createdAt": "2020-01-17"},
    {"id": 20, "createdAt": "2020-01-16"},
    {"id": 10, "createdAt": "2020-01-15"},
    {"id": 19, "createdAt": "2020-01-14"},
    {"id": 9, "createdAt": "2020-01-13"},
    {"id": 18, "createdAt": "2020-01-12"},
    {"id": 8, "createdAt": "2020-01-11"},
    {"id": 17, "createdAt": "2020-01-10"},
    {"id": 7, "createdAt": "2020-01-09"},
    {"id": 16, "createdAt": "2020-01-08"},
    {"id": 6, "createdAt": "2020-01-07"},
    {"id": 15, "createdAt": "2020-01-06"},
    {"id": 5, "createdAt": "2020-01-05"},
    {"id": 14, "createdAt": "2020-01-04"},
    {"id": 4, "createdAt": "2020-01-03"},
    {"id": 13, "createdAt": "2020-01-02"},
    {"id": 3, "createdAt": "2020-01-01"},
]


def test_get_alert_details_batches_results_according_to_batch_size(sdk):
    alert_util._BATCH_SIZE = 2
    sdk.alerts.get_details.side_effect = ALERT_DETAIL_RESULT
    results = alert_util.get_alert_details(sdk, ALERT_SUMMARY_LIST)
    assert sdk.alerts.get_details.call_count == 10


def test_get_alert_details_sorts_results_by_date(sdk):
    alert_util._BATCH_SIZE = 2
    sdk.alerts.get_details.side_effect = ALERT_DETAIL_RESULT
    results = alert_util.get_alert_details(sdk, ALERT_SUMMARY_LIST)
    assert results == SORTED_ALERT_DETAILS
