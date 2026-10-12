"""Generate small, deterministic IR datasets inspired by the VoltMize workflow.

This script does not import or run the FYP.  It only creates fictional records
whose vocabulary and fields match the energy-monitoring workflow.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parent


UNSTRUCTURED_DOCUMENTS = [
    ("U01", "Compressor-1 night shift anomaly", "During the night shift Compressor-1 drew unusually high energy. Power stayed above 92 kW while production was idle. Inspect unload valve leakage and the pressure setpoint."),
    ("U02", "Boiler feed pump power factor", "Boiler feed pump MTR-21 showed low power factor of 0.68 and increased reactive power during the morning shift. Check capacitor bank and motor loading."),
    ("U03", "Packaging line normal operation", "Packaging Line-2 consumed 41 kWh during the day shift. Load followed the production schedule and no anomaly was detected."),
    ("U04", "Chiller temperature-driven load", "Cold-store Chiller-2 energy increased during a hot afternoon. Ambient temperature was 39 C and cooling production was high, so the expected-load model marked it normal."),
    ("U05", "Conveyor bearing warning", "Conveyor CV-07 current rose gradually with repeated energy spikes. Maintenance found a worn bearing creating mechanical drag and replaced it."),
    ("U06", "Air leak after production", "Compressor-2 kept cycling after the evening shift ended. Abnormal off-hours consumption was traced to a compressed-air leak near the dyeing section."),
    ("U07", "Textile loom voltage imbalance", "Loom bank LB-03 reported phase voltage imbalance and elevated current on phase B. The event caused motor heating but only a small energy increase."),
    ("U08", "Idle oven weekend waste", "Baking Oven-1 remained at standby temperature on Sunday with no production. Weekend idle consumption reached 310 kWh; shutdown scheduling was recommended."),
    ("U09", "Injection moulding heater fault", "Injection Moulder IM-04 used high power because a barrel heater thermostat failed. Energy remained elevated across three production batches."),
    ("U10", "Meter communication gap", "Main meter M-00 stopped reporting for eighteen minutes. The ingestion quality check flagged missing readings; this was a communication issue, not an energy anomaly."),
    ("U11", "Compressor pressure setpoint", "Compressor-1 total consumption increased by 18 percent after the pressure setpoint was raised for night production. Resetting pressure reduced kWh without affecting output."),
    ("U12", "Motor power factor correction", "Motor MTR-09 had low power factor and high reactive energy. After capacitor correction, current fell and monthly demand charges were reduced."),
    ("U13", "Welding peak demand", "Welding Bay-2 created a short peak-demand event when several welders started together. Staggered startup was recommended to lower the demand peak."),
    ("U14", "Cold room door loss", "Cold Room CR-1 consumed excess energy overnight because a door seal was damaged. Chiller runtime and temperature deviations confirmed the cooling loss."),
    ("U15", "Scheduled maintenance shutdown", "All production meters showed near-zero load during the planned maintenance shutdown. The calendar context explains the readings and prevents a false anomaly alert."),
]

UNSTRUCTURED_QUERIES = [
    {"id": "UQ1", "text": "compressor abnormal high energy night shift", "relevant": ["U01", "U06", "U11"]},
    {"id": "UQ2", "text": "low power factor motor reactive energy", "relevant": ["U02", "U12"]},
    {"id": "UQ3", "text": "weekend idle consumption no production", "relevant": ["U08", "U15"]},
    {"id": "UQ4", "text": "temperature cooling chiller excess energy", "relevant": ["U04", "U14"]},
    {"id": "UQ5", "text": "missing meter readings communication", "relevant": ["U10"]},
]


STRUCTURED_DOCUMENTS = [
    {"id": "S01", "equipment": "Compressor-1", "summary": "High energy during night shift", "symptoms": "power 94 kW; idle production; repeated cycling", "meter_context": "night shift; total consumption 488 kWh", "probable_cause": "unload valve leakage", "action": "inspect valve and reduce pressure setpoint"},
    {"id": "S02", "equipment": "Compressor-2", "summary": "Off-hours compressor consumption", "symptoms": "cycling after shift; falling air pressure", "meter_context": "evening shift; 166 excess kWh", "probable_cause": "compressed air leak", "action": "repair pipe near dyeing section"},
    {"id": "S03", "equipment": "Motor-MTR-21", "summary": "Low motor power factor", "symptoms": "power factor 0.68; reactive current high", "meter_context": "morning shift; reactive energy 82 kvarh", "probable_cause": "capacitor bank disconnected", "action": "reconnect capacitor bank"},
    {"id": "S04", "equipment": "Oven-1", "summary": "Weekend idle energy", "symptoms": "standby heat; no production", "meter_context": "Sunday; total consumption 310 kWh", "probable_cause": "shutdown schedule missing", "action": "apply weekend shutdown rule"},
    {"id": "S05", "equipment": "Chiller-2", "summary": "Expected hot-weather cooling load", "symptoms": "long runtime; stable temperature", "meter_context": "ambient 39 C; high production", "probable_cause": "normal weather-driven demand", "action": "no maintenance required"},
    {"id": "S06", "equipment": "Cold-Room-1", "summary": "Excess overnight cooling energy", "symptoms": "temperature drift; continuous chiller runtime", "meter_context": "night; 27 percent energy increase", "probable_cause": "damaged door seal", "action": "replace seal and verify temperature"},
    {"id": "S07", "equipment": "Main-Meter", "summary": "Missing meter readings", "symptoms": "eighteen minute data gap", "meter_context": "all phases absent; ingestion quality failed", "probable_cause": "gateway communication loss", "action": "check network and backfill readings"},
    {"id": "S08", "equipment": "Conveyor-CV07", "summary": "Rising current and energy spikes", "symptoms": "current trend rising; vibration", "meter_context": "day shift; repeated 8 kW spikes", "probable_cause": "worn conveyor bearing", "action": "replace bearing and inspect alignment"},
    {"id": "S09", "equipment": "Loom-Bank-03", "summary": "Voltage imbalance", "symptoms": "phase B current high; motor heating", "meter_context": "voltage unbalance 4.2 percent", "probable_cause": "uneven phase loading", "action": "rebalance phases"},
    {"id": "S10", "equipment": "Welding-Bay-2", "summary": "Peak demand event", "symptoms": "simultaneous welder startup", "meter_context": "peak demand 214 kW; short duration", "probable_cause": "unstaggered startup", "action": "stagger welding schedule"},
    {"id": "S11", "equipment": "Injection-Moulder-04", "summary": "Persistent heater energy anomaly", "symptoms": "barrel temperature overshoot; high power", "meter_context": "three batches; 21 percent excess energy", "probable_cause": "heater thermostat failure", "action": "replace thermostat"},
    {"id": "S12", "equipment": "Factory-Textile", "summary": "Planned shutdown low load", "symptoms": "near-zero readings across meters", "meter_context": "maintenance calendar; no production", "probable_cause": "scheduled shutdown", "action": "suppress anomaly alert"},
]

STRUCTURED_QUERIES = [
    {"id": "SQ1", "text": "night shift compressor high energy cause action", "relevant": ["S01", "S02"]},
    {"id": "SQ2", "text": "low power factor reactive motor capacitor", "relevant": ["S03"]},
    {"id": "SQ3", "text": "weekend no production shutdown consumption", "relevant": ["S04", "S12"]},
    {"id": "SQ4", "text": "temperature chiller excess energy cause", "relevant": ["S05", "S06"]},
    {"id": "SQ5", "text": "missing meter readings communication action", "relevant": ["S07"]},
]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def main() -> None:
    unstructured = [{"id": doc_id, "title": title, "text": text} for doc_id, title, text in UNSTRUCTURED_DOCUMENTS]
    write_json(ROOT / "unstructured_text" / "dataset" / "incident_reports.json", unstructured)
    write_json(ROOT / "unstructured_text" / "dataset" / "queries.json", UNSTRUCTURED_QUERIES)
    write_json(ROOT / "structured_text" / "dataset" / "diagnostic_records.json", STRUCTURED_DOCUMENTS)
    write_json(ROOT / "structured_text" / "dataset" / "queries.json", STRUCTURED_QUERIES)
    print(f"Generated {len(unstructured)} unstructured incident reports and {len(STRUCTURED_DOCUMENTS)} structured diagnostic records.")


if __name__ == "__main__":
    main()
