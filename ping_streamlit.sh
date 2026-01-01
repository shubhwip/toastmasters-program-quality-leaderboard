#!/bin/bash
curl -s -o /dev/null -w "%{http_code}\n" https://toastmasters-district-91-program-quality-leaderboard.streamlit.app/ >> /Users/shubhamjain/ping_log.txt
