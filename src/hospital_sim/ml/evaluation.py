"""
ML Evaluation utilities — comparison tables and leaderboard generation.
"""

from __future__ import annotations
from typing import Dict, Any
import pandas as pd


def build_comparison_table(metrics: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """
    Build a formatted model comparison DataFrame sorted by RMSE ascending.
    """
    rows = []
    for key, m in metrics.items():
        rows.append({
            "Model":        m.get("model", key),
            "RMSE":         m.get("rmse", 0),
            "MAE":          m.get("mae", 0),
            "R²":           m.get("r2", 0),
            "Accuracy %":   m.get("accuracy_pct", 0),
        })
    df = pd.DataFrame(rows).sort_values("RMSE").reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df


def leaderboard_html(metrics: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate an HTML leaderboard string for Streamlit rendering.
    """
    df = build_comparison_table(metrics)
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    rows_html = ""
    for _, row in df.iterrows():
        medal = medals.get(int(row["Rank"]), "")
        r2_pct = int(float(row["R²"]) * 100)
        r2_color = "#10b981" if r2_pct >= 85 else "#f59e0b" if r2_pct >= 70 else "#ef4444"
        rows_html += f"""
        <tr>
          <td style="padding:8px 12px">{medal} {row['Model']}</td>
          <td style="padding:8px 12px;font-family:monospace">{row['RMSE']:.3f}</td>
          <td style="padding:8px 12px;font-family:monospace">{row['MAE']:.3f}</td>
          <td style="padding:8px 12px">
            <span style="color:{r2_color};font-weight:700">{row['R²']:.3f}</span>
          </td>
          <td style="padding:8px 12px">{row['Accuracy %']:.1f}%</td>
        </tr>"""

    return f"""
    <table style="width:100%;border-collapse:collapse;font-size:13px">
      <thead>
        <tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0">
          <th style="text-align:left;padding:8px 12px;font-size:11px;color:#94a3b8;text-transform:uppercase">Model</th>
          <th style="text-align:left;padding:8px 12px;font-size:11px;color:#94a3b8;text-transform:uppercase">RMSE</th>
          <th style="text-align:left;padding:8px 12px;font-size:11px;color:#94a3b8;text-transform:uppercase">MAE</th>
          <th style="text-align:left;padding:8px 12px;font-size:11px;color:#94a3b8;text-transform:uppercase">R²</th>
          <th style="text-align:left;padding:8px 12px;font-size:11px;color:#94a3b8;text-transform:uppercase">Accuracy</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>"""
