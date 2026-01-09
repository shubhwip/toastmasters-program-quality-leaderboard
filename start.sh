#!/bin/bash
streamlit run app.py --server.port=${PORT:-8501} --server.enableCORS false
