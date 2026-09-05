import json
import os
from district_coordinates import DISTRICT_COORDS
from aggregate_stats import load_claims, load_anomalies, aggregate_by_district

def get_color(stats):
    if stats['anomalies_total'] > 0:
        risk = stats['anomalies_high'] * 3 + stats['anomalies_medium'] * 2 + stats['anomalies_low'] * 1
        risk = risk / max(stats['total_claims'], 1)
        if risk >= 0.5:
            return '#c62828'
        elif risk >= 0.2:
            return '#f9a825'
        else:
            return '#2e7d32'
    if stats['approval_rate_pct'] >= 60:
        return '#2e7d32'
    elif stats['approval_rate_pct'] >= 40:
        return '#f9a825'
    else:
        return '#c62828'

def build_marker_data(claims_path='sample_data/fra_data.json', anomalies_path='sample_data/anomalies.json'):
    claims = load_claims(claims_path)
    anomalies = load_anomalies(anomalies_path)
    stats = aggregate_by_district(claims, anomalies)
    using_real_anomalies = len(anomalies) > 0
    markers = []
    for district, (lat, lon) in DISTRICT_COORDS.items():
        d = stats.get(district)
        if not d:
            continue
        markers.append({'district': district, 'lat': lat, 'lon': lon, 'radius': 8 + d['total_claims'] / 5, 'color': get_color(d), 'total_claims': d['total_claims'], 'approved': d['approved'], 'pending': d['pending'], 'rejected': d['rejected'], 'approval_rate_pct': d['approval_rate_pct'], 'avg_processing_days': d['avg_processing_days'], 'anomalies_total': d['anomalies_total'], 'anomalies_high': d['anomalies_high'], 'anomalies_medium': d['anomalies_medium'], 'anomalies_low': d['anomalies_low']})
    return (markers, using_real_anomalies)
HTML_TEMPLATE = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8" />\n<title>FRA Monitoring Map (Madhya Pradesh)</title>\n<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />\n<style>\n  html, body {{ margin:0; padding:0; height:100%; font-family: Arial, sans-serif; }}\n  #map {{ height: 100%; width: 100%; }}\n  #title-bar {{\n    position: absolute; top: 10px; left: 50px; z-index: 1000;\n    background: white; padding: 8px 14px; border-radius: 6px;\n    box-shadow: 0 1px 4px rgba(0,0,0,0.3); font-size: 14px; max-width: 340px;\n  }}\n  #title-bar h3 {{ margin: 0 0 4px 0; font-size: 16px; }}\n  #title-bar .demo-note {{ color: #c62828; font-size: 12px; font-weight: bold; }}\n  #title-bar .source-note {{ color: #555; font-size: 11px; margin-top: 4px; }}\n  .legend {{\n    position: absolute; bottom: 20px; right: 10px; z-index: 1000;\n    background: white; padding: 8px 12px; border-radius: 6px;\n    box-shadow: 0 1px 4px rgba(0,0,0,0.3); font-size: 12px;\n  }}\n  .legend span {{ display:inline-block; width:12px; height:12px; border-radius:50%; margin-right:6px; }}\n</style>\n</head>\n<body>\n\n<div id="title-bar">\n  <h3>FRA Monitoring Map</h3>\n  Madhya Pradesh &middot; 15 districts\n  <div class="demo-note">DEMO MODE: claim data is SIMULATED</div>\n  <div class="source-note">{source_note}</div>\n</div>\n\n<div class="legend">\n  <div><span style="background:#2e7d32;"></span> Low risk</div>\n  <div><span style="background:#f9a825;"></span> Medium risk</div>\n  <div><span style="background:#c62828;"></span> High risk - needs attention</div>\n</div>\n\n<div id="map"></div>\n\n<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\n<script>\n  const markerData = {marker_json};\n\n  const map = L.map(\'map\').setView([23.0, 79.5], 7);\n\n  L.tileLayer(\'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png\', {{\n    maxZoom: 12,\n    attribution: \'&copy; OpenStreetMap contributors\'\n  }}).addTo(map);\n\n  markerData.forEach(function(d) {{\n    const popupHtml =\n      "<b>" + d.district + "</b><br>" +\n      "Total Claims: " + d.total_claims + "<br>" +\n      "Approved: " + d.approved + "<br>" +\n      "Pending: " + d.pending + "<br>" +\n      "Rejected: " + d.rejected + "<br>" +\n      "Approval Rate: " + d.approval_rate_pct + "%<br>" +\n      "Avg. Processing Time: " + (d.avg_processing_days ?? "N/A") + " days<br>" +\n      "Anomalies: " + d.anomalies_total +\n      " (H:" + d.anomalies_high + " M:" + d.anomalies_medium + " L:" + d.anomalies_low + ")";\n\n    L.circleMarker([d.lat, d.lon], {{\n      radius: d.radius,\n      color: d.color,\n      fillColor: d.color,\n      fillOpacity: 0.7,\n      weight: 2\n    }}).addTo(map)\n      .bindPopup(popupHtml)\n      .bindTooltip(d.district);\n  }});\n</script>\n\n</body>\n</html>\n'

def build_map(output_path='output/mp_fra_map.html', claims_path='sample_data/fra_data.json', anomalies_path='sample_data/anomalies.json'):
    markers, using_real_anomalies = build_marker_data(claims_path, anomalies_path)
    if using_real_anomalies:
        source_note = "Coloring based on Member 3's anomaly detection output (anomalies.json)."
    else:
        source_note = 'anomalies.json not found - falling back to approval-rate coloring.'
    html = HTML_TEMPLATE.format(marker_json=json.dumps(markers), source_note=source_note)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Map saved to {output_path}')
    print('Open it in any web browser (double-click the file) to view it.')
if __name__ == '__main__':
    build_map()
