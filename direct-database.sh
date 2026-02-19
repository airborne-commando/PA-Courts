#!/usr/bin/env sh

printf "First name (blank to skip): "
read FIRST
printf "Last name  (blank to skip): "
read LAST
printf "Docket number (blank to skip): "
read DOCKET
printf "Case status (blank to skip): "
read STATUS
printf "Output file name (default: result.json): "
read OUT

[ -z "$OUT" ] && OUT="result.json"

# Decide searchBy in shell
if [ -n "$DOCKET" ]; then
  SEARCH_BY="DocketNumber"
else
  SEARCH_BY="ParticipantName"
fi

# Build well-formed JSON with jq
JSON=$(jq -n \
  --arg fn "$FIRST" \
  --arg ln "$LAST" \
  --arg dn "$DOCKET" \
  --arg cs "$STATUS" \
  --arg sb "$SEARCH_BY" \
  '{
    searchBy: $sb,
    participantFirstName: (if $fn == "" then null else $fn end),
    participantLastName:  (if $ln == "" then null else $ln end),
    docketNumber:         (if $dn == "" then null else $dn end),
    caseStatusName:       (if $cs == "" then null else $cs end),
    organizationName: null,
    offenseTrackingNumber: null,
    policeIncidentNumber: null,
    stateIdentificationNumber: null,
    courtName: null,
    courtOfficeName: null,
    docketTypeName: null,
    dateFiledRangeBegin: null,
    dateFiledRangeEnd: null,
    dateOfBirth: null
  }')

echo "Request JSON:"
echo "$JSON" | jq .

curl -s -X POST "https://services.pacourts.us/public/v1/cases/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$JSON" \
  | jq . > "$OUT"

echo "Saved pretty JSON response to $OUT"
