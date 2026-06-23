#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=src

echo ""
echo " ╔══════════════════════════════════════╗"
echo " ║  MedCommand Hospital Operations v2.0 ║"
echo " ╚══════════════════════════════════════╝"
echo ""
echo " Starting dashboard → http://localhost:8501"
echo ""
streamlit run app.py
