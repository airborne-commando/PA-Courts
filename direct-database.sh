#!/usr/bin/env sh

printf "First name (blank to skip): "
read FIRST
printf "Last name  (blank to skip): "
read LAST
printf "Docket number (blank to skip): "
read DOCKET
printf "Case status (blank to skip): "
read STATUS
printf "Organization name (blank to skip): "
read ORG
printf "Offense tracking # (blank to skip): "
read OTN
printf "Police incident # (blank to skip): "
read PIN
printf "State ID # (blank to skip): "
read SID
printf "Court name (blank to skip): "
read COURT
printf "Court office (blank to skip): "
read OFFICE
printf "Docket type (blank to skip): "
read DTYPE
printf "Date filed begin (YYYY-MM-DD): "
read DATE_BEGIN
printf "Date filed end (YYYY-MM-DD): "
read DATE_END
printf "Date of birth (YYYY-MM-DD): "
read DOB
printf "Output file name (default: result.json): "
read OUT

[ -z "$OUT" ] && OUT="result.json"

# Decide searchBy based on input priority
if [ -n "$DOCKET" ]; then
  SEARCH_BY="DocketNumber"
elif [ -n "$FIRST" ] || [ -n "$LAST" ]; then
  SEARCH_BY="ParticipantName"
else
  SEARCH_BY="All"
fi

# Build complete JSON with all fields
JSON=$(jq -n \
  --arg fn "$FIRST" \
  --arg ln "$LAST" \
  --arg dn "$DOCKET" \
  --arg cs "$STATUS" \
  --arg org "$ORG" \
  --arg otn "$OTN" \
  --arg pin "$PIN" \
  --arg sid "$SID" \
  --arg court "$COURT" \
  --arg office "$OFFICE" \
  --arg dtype "$DTYPE" \
  --arg datebegin "$DATE_BEGIN" \
  --arg dateend "$DATE_END" \
  --arg dob "$DOB" \
  --arg sb "$SEARCH_BY" \
  '{
    searchBy: $sb,
    participantFirstName: (if $fn == "" then null else $fn end),
    participantLastName:  (if $ln == "" then null else $ln end),
    docketNumber:         (if $dn == "" then null else $dn end),
    caseStatusName:       (if $cs == "" then null else $cs end),
    organizationName:     (if $org == "" then null else $org end),
    offenseTrackingNumber:(if $otn == "" then null else $otn end),
    policeIncidentNumber: (if $pin == "" then null else $pin end),
    stateIdentificationNumber:(if $sid == "" then null else $sid end),
    courtName:            (if $court == "" then null else $court end),
    courtOfficeName:      (if $office == "" then null else $office end),
    docketTypeName:       (if $dtype == "" then null else $dtype end),
    dateFiledRangeBegin:  (if $datebegin == "" then null else $datebegin end),
    dateFiledRangeEnd:    (if $dateend == "" then null else $dateend end),
    dateOfBirth:          (if $dob == "" then null else $dob end)
  }')

echo "Request JSON:"
echo "$JSON" | jq .
echo

# Save COMPLETE search response
curl -s -X POST "https://services.pacourts.us/public/v1/cases/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$JSON" \
  | jq . > "$OUT"

echo "✅ Saved COMPLETE search response to: $OUT"
echo

# Extract and fetch full details for each case (FIXED IFS syntax)
echo "🔍 Fetching full details for each case..."
DETAILED_OUT="detailed_$OUT"
> "$DETAILED_OUT"  # Create/empty detailed file

if jq -e '.results' "$OUT" >/dev/null 2>&1; then
  jq -r '.results[]? | select(.href != null) | "\(.docketNumber):\(.href)"' "$OUT" | while IFS=: read -r docket href; do
    echo "  Getting $docket..."
    curl -s "$href" | jq --arg docket "$docket" '{docketNumber: $docket, fullDetails: .}' >> "$DETAILED_OUT"
  done
else
  echo "  No results found or no href links available"
fi

echo "✅ Saved detailed case files to: $DETAILED_OUT"
echo

echo "📋 Available search options from response:"
echo "Case Status Options:"
jq -r '.caseStatusNameOptions[] // empty' "$OUT" 2>/dev/null || echo "  None"
echo
echo "Court Options:"
jq -r '.courtNameOptions[] // empty' "$OUT" 2>/dev/null || echo "  None"
echo
echo "Court Office Options:"
jq -r '.courtOfficeNameOptions[] // empty' "$OUT" 2>/dev/null || echo "  None"
echo
echo "Docket Type Options:"
jq -r '.docketTypeNameOptions[] // empty' "$OUT" 2>/dev/null || echo "  None"
echo

echo "📊 Found $(jq '.maxIndex // 0' "$OUT" 2>/dev/null || echo 0) total cases"
echo "First 3 results:"
jq '.results[:3] | {docketNumber, shortCaption, statusName, courtOffice: .courtOffice.displayName, filingDate} // empty' "$OUT" 2>/dev/null || echo "No results"
