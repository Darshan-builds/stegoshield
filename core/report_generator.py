import json
import os
import datetime
from typing import Dict, Any, List

def generate_report_filename(analysis: Dict[str, Any], extension: str) -> str:
    """Generates a standard timestamped filename."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    base_name = os.path.basename(analysis.get('file_path', 'unknown_file'))
    return f"analysis_{base_name}_{timestamp}.{extension}"

def export_json(analysis: Dict[str, Any], output_path: str) -> str:
    """Exports the full analysis dictionary to a pretty-printed JSON file."""
    # Ensure metadata exists
    if 'generated_at' not in analysis:
        analysis['generated_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if 'disclaimer' not in analysis:
        analysis['disclaimer'] = "This assessment does NOT prove malware presence. It identifies potential indicators only."

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
        
    return output_path

def export_html(analysis: Dict[str, Any], output_path: str) -> str:
    """Exports a professional, offline, styled HTML report."""
    
    risk = analysis.get('risk_assessment', {})
    score = risk.get('score', 0)
    severity = risk.get('severity', 'UNKNOWN')
    color = risk.get('severity_color', 'gray')
    action = risk.get('recommended_action', 'N/A')
    
    findings_html = ""
    for c in risk.get('contributors', []):
        findings_html += f"<li><strong>{c['indicator']}</strong> (+{c['points']} pts): {c['description']}</li>"
    if not findings_html:
        findings_html = "<li>No significant risk indicators identified.</li>"
        
    file_path = analysis.get('file_path', 'Unknown')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StegoShield Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: auto;
            background-color: #1e1e1e;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        h1, h2, h3 {{ color: #ffffff; border-bottom: 1px solid #333; padding-bottom: 5px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
        .risk-badge {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            background-color: {color};
        }}
        .section {{ margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid #333; }}
        th {{ background-color: #2c2c2c; }}
        .disclaimer {{
            background-color: #2c2c2c;
            border-left: 5px solid #ff9800;
            padding: 15px;
            margin-top: 40px;
            font-style: italic;
        }}
        .findings-list {{ background-color: #252525; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>StegoShield Analysis Report</h1>
                <p>Target: <strong>{os.path.basename(file_path)}</strong></p>
                <p>Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            <div>
                <div class="risk-badge" style="background-color: {color};">{severity} ({score}/100)</div>
            </div>
        </div>

        <div class="section">
            <h2>File Information</h2>
            <table>
                <tr><th>Full Path</th><td>{file_path}</td></tr>
            </table>
        </div>

        <div class="section">
            <h2>Risk Score & Interpretation</h2>
            <p>{risk.get('explanation', 'No explanation provided.')}</p>
            <h3>Recommended Action</h3>
            <p><strong>{action}</strong></p>
        </div>

        <div class="section">
            <h2>Key Risk Findings</h2>
            <ul class="findings-list">
                {findings_html}
            </ul>
        </div>
        
        <div class="disclaimer">
            <strong>Disclaimer:</strong> This assessment does NOT prove malware presence. 
            It identifies potential indicators only. Do not execute or run files outside of a sandbox environment.
        </div>
    </div>
</body>
</html>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    return output_path

def list_reports(reports_dir: str) -> List[str]:
    """Lists all available analysis reports in a directory."""
    if not os.path.exists(reports_dir):
        return []
    return [os.path.join(reports_dir, f) for f in os.listdir(reports_dir) if f.endswith('.json') or f.endswith('.html')]

def load_report(report_path: str) -> Dict[str, Any]:
    """Loads a JSON report."""
    if not os.path.exists(report_path) or not report_path.endswith('.json'):
        raise ValueError("Invalid report file path.")
        
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)
