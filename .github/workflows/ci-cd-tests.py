import json
import os

from nextmv.cloud import Application, Client, Metric

with open(f"{os.getenv('APP_DIRECTORY')}/acceptance_test_metrics.json") as f:
    metric_dicts = json.load(f)["metrics"]

metrics = [Metric.from_dict(metric_dict) for metric_dict in metric_dicts]

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id=os.getenv("APP_ID"))
acceptance_test = app.new_acceptance_test(
    candidate_instance_id=os.getenv("CANDIDATE_INSTANCE"),
    control_instance_id=os.getenv("CONTROL_INSTANCE"),
    id=os.getenv("IDENTIFIER"),
    metrics=metrics,
    name=os.getenv("IDENTIFIER"),
    input_set_id=os.getenv("INPUT_SET"),
    description=f"Automated acceptance test for identifier {os.getenv('IDENTIFIER')}",
)
print(json.dumps(acceptance_test.to_dict(), indent=2))  # Pretty print.
