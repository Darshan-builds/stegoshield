"""Quick integration test: analyze all 3 demo samples and export reports."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.analyzer import analyze_file
from core.report_generator import export_json, export_html

samples = [
    ("CLEAN IMAGE", "demo/samples/normal_clean.png"),
    ("APPENDED DATA", "demo/samples/appended_data.png"),
    ("LSB MODIFIED", "demo/samples/lsb_modified.png"),
]

for label, path in samples:
    print(f"=== {label} ===")
    try:
        result = analyze_file(path)
        risk = result.get("risk_assessment", {})
        score = risk.get("score", "N/A")
        severity = risk.get("severity", "N/A")
        print(f"  Score: {score}/100")
        print(f"  Severity: {severity}")
        contributors = risk.get("contributors", [])
        for c in contributors:
            indicator = c.get("indicator", "")
            points = c.get("points", 0)
            desc = c.get("description", "")
            print(f"    +{points} {indicator}: {desc}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    print()

# Export reports for LSB modified sample
print("=== EXPORT TEST ===")
try:
    result = analyze_file("demo/samples/lsb_modified.png")
    os.makedirs("reports", exist_ok=True)
    json_path = export_json(result, "reports/test_analysis.json")
    print(f"JSON report: {json_path}")
    html_path = export_html(result, "reports/test_analysis.html")
    print(f"HTML report: {html_path}")
    print("Export complete!")
except Exception as e:
    print(f"Export ERROR: {e}")
    import traceback
    traceback.print_exc()
