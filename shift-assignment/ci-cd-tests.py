import os

from nextmv.cloud import (
    Application,
    Client,
    Comparison,
    Metric,
    MetricParams,
    MetricType,
)

metrics = [
    Metric(
        field="result.value",
        metric_type=MetricType.direct_comparison,
        params=MetricParams(operator=Comparison.less_than_or_equal_to),
        statistic="mean",
    )
]

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="shift-assignment-pyomo")
acceptance_test = app.new_acceptance_test(
    candidate_instance_id="develop",
    control_instance_id="staging",
    id=os.getenv("ACCEPTANCE_TEST_ID"),
    name=os.getenv("ACCEPTANCE_TEST_ID"),
    input_set_id=os.getenv("INPUT_SET_ID"),
)
