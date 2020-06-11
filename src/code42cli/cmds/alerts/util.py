from code42cli.compat import range

_BATCH_SIZE = 100


def get_alert_details(sdk, alert_summary_list):
    alert_ids = [alert[u"id"] for alert in alert_summary_list]
    batches = [alert_ids[i : i + _BATCH_SIZE] for i in range(0, len(alert_ids), _BATCH_SIZE)]
    results = []
    for batch in batches:
        r = sdk.alerts.get_details(batch)
        results.extend(r[u"alerts"])
    results = sorted(results, key=lambda x: x[u"createdAt"], reverse=True)
    return results
