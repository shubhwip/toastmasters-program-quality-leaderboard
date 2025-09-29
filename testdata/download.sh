#!/bin/bash

# Usage: ./download.sh <startyear> <endyear> <district_number>
# Example: ./download.sh 2023 2024 41

set -e

startyear="$1"
endyear="$2"
district_number="$3"
report_type="$4"

if [[ -z "$startyear" || -z "$endyear" || -z "$district_number" || -z "$report_type" ]]; then
    echo "Usage: $0 <startyear> <endyear> <district_number> <report_type>"
    exit 1
fi

folder="${report_type}/${startyear}-${endyear}"
mkdir -p "$folder"

# Define quarters: month, day_of_report, date_of_report, year_of_report
quarters=(
    "09 30 09/30 $startyear"
    "12 31 12/31 $startyear"
    "03 31 03/31 $endyear"
    "06 30 06/30 $endyear"
)

for q in "${quarters[@]}"; do
    read month day_of_report date_of_report year_of_report <<< "$q"
    url="https://dashboards.toastmasters.org/${startyear}-${endyear}/export.aspx?type=CSV&report=${report_type}~${district_number}~${day_of_report}/${date_of_report}/${year_of_report}~~${startyear}-${endyear}"
    outfile="${folder}/${month}.csv"
    echo "Downloading $url -> $outfile"
    curl -sSL "$url" -o "$outfile"
done