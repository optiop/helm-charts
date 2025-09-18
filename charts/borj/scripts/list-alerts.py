import os
import yaml
from tabulate import tabulate

domain = "https://grafana-nv.redcapcloud.com"
base_path = "../nphase-global"


def extract_alerts_from_file(file_path, source_dir):
  alerts_data = []
  try:
    with open(file_path, 'r') as f:
      content = yaml.safe_load(f)

      if not content or 'groups' not in content:
        return alerts_data

      for group in content['groups']:
        group_name = group.get('name', 'N/A')
        for rule in group.get('rules', []):
          if 'alert' in rule:
            alert_name = rule.get('alert', 'N/A')
            annotations = rule.get('annotations', {})
            alerts_data.append([
              source_dir,
              group_name,
              alert_name,
              annotations
            ])
  except Exception as e:
    print(f"Error reading {file_path}: {e}")
  return alerts_data

def list_all_alerts(directories):
  table = []
  for directory in directories:
    if not os.path.exists(directory):
      print(f"Directory not found: {directory}")
      continue
    for file in os.listdir(directory):
      if file.endswith(".yaml") or file.endswith(".yml"):
        full_path = os.path.join(directory, file)
        table.extend(extract_alerts_from_file(full_path, os.path.basename(directory)))
  return table

if __name__ == "__main__":
  base_path = base_path
  alert_dirs = [
    os.path.join(base_path, "mimir-rules"),
    os.path.join(base_path, "loki-rules"),
  ]

  alerts_table = list_all_alerts(alert_dirs)

  if alerts_table:
    headers = ["Source", "Group", "Alert Name", "Runbook"]
    with open("alerts.md", "w") as f:
      f.write("| " + " | ".join(headers) + " |\n")
      f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
      for row in alerts_table:
        source, group, alert_name, annotations = row

        dashboard_path = annotations.get("__dashboardUid__")
        if dashboard_path:
          full_url = f"{domain}/d/{dashboard_path}"
          alert_cell = f"[{alert_name}]({full_url})"
        else:
          alert_cell = alert_name

        runbook = annotations.get("runbook_url", "-")
        clean_row = [source, group, alert_cell, runbook]
        clean_row = [str(cell).replace("\n", "<br>").replace("|", "\\|") for cell in clean_row]
        f.write("| " + " | ".join(clean_row) + " |\n")
  else:
    print("No alerts found.")
