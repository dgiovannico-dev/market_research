#!/usr/bin/env sh
# HTTP-probe public ATS tenants (no secrets). Prints token/status for copy into .env.
set -eu
UA="${ATS_PROBE_UA:-FMI-MarketIntel/1.0}"

probe() {
  label="$1"
  url="$2"
  code="$(curl -s -o /tmp/ats_probe_body -w "%{http_code}" -A "$UA" --max-time 20 "$url" || echo err)"
  bytes="$(wc -c < /tmp/ats_probe_body 2>/dev/null || echo 0)"
  printf "%s\t%s\t%sB\t%s\n" "$label" "$code" "$bytes" "$url"
}

echo "# Greenhouse boards-api"
for b in ${GREENHOUSE_PROBE:-airbnb stripe gitlab discord cloudflare figma twilio datadog dropbox coinbase robinhood mongodb elastic databricks okta pendo duolingo asana block anthropic scaleai brex affirm gusto pinterest reddit coursera khanacademy lyft waymo spacex janestreet instacart roblox epicgames mozilla pagerduty airtable vercel mercury thefork truelayer}; do
  probe "gh:$b" "https://boards-api.greenhouse.io/v1/boards/${b}/jobs"
done

echo "# Lever postings"
for s in ${LEVER_PROBE:-spotify palantir wealthfront}; do
  probe "lv:$s" "https://api.lever.co/v0/postings/${s}?mode=json"
done

echo "# Ashby job-board"
for a in ${ASHBY_PROBE:-notion linear vercel openai ramp cursor warp granola runway supabase mercor harvey sierra cognition perplexity midjourney snowflake replit plaid miro ashby elevenlabs temporal webflow sentry docker satispay docebo}; do
  probe "ash:$a" "https://api.ashbyhq.com/posting-api/job-board/${a}"
done

echo "# Personio search.json (public listing; no HTML scrape)"
for p in ${PERSONIO_PROBE:-1komma5grad chrono24 finanzguru tado kiwi personio-gmbh alcemy researchgate plantura}; do
  probe "pe:$p" "https://${p}.jobs.personio.de/search.json"
done

echo "# Teamtailor jobs.json (career host or custom domain)"
for h in ${TEAMTAILOR_PROBE:-polestar.teamtailor.com careers.oatly.com storytel.teamtailor.com krea.teamtailor.com hedvig.teamtailor.com doktor.teamtailor.com schibsted.teamtailor.com foodora.teamtailor.com securitas.teamtailor.com mindler.teamtailor.com}; do
  probe "tt:$h" "https://${h}/jobs.json"
done

echo "# Recruitee Careers Site offers (keyless until 2027-02-10)"
for s in ${RECRUITEE_PROBE:-jobs personio bunq adjust}; do
  probe "rt:$s" "https://${s}.recruitee.com/api/offers/"
done

echo "# Pinpoint postings.json (public; skip demo-like boards)"
for s in ${PINPOINT_PROBE:-made-tech accenture bendingspoons arm freeagent workwithus imagination confluence}; do
  probe "pp:$s" "https://${s}.pinpointhq.com/postings.json"
done

echo "# Workable careers widget (keyless; back off on 429)"
for s in ${WORKABLE_PROBE:-huggingface jasper skillshare riot}; do
  probe "wa:$s" "https://apply.workable.com/api/v1/widget/accounts/${s}?details=false"
  sleep 1
done

echo "# Workday CXS jobs (POST; tenant:wd:site — override with WORKDAY_PROBE)"
for t in ${WORKDAY_PROBE:-nvidia:wd5:NVIDIAExternalCareerSite redhat:wd5:jobs intel:wd1:External salesforce:wd12:External_Career_Site adobe:wd5:external_experienced paypal:wd1:jobs micron:wd1:External nxp:wd3:careers analogdevices:wd1:External cisco:wd5:Cisco_Careers pfizer:wd1:PfizerCareers workday:wd5:Workday autodesk:wd1:Ext tmobile:wd1:External bbva:wd3:BBVA swisscom:wd103:SwisscomExternalCareers juliusbaer:wd3:External}; do
  tenant="${t%%:*}"
  rest="${t#*:}"
  wd="${rest%%:*}"
  site="${rest#*:}"
  url="https://${tenant}.${wd}.myworkdayjobs.com/wday/cxs/${tenant}/${site}/jobs"
  code="$(curl -s -o /tmp/ats_probe_body -w "%{http_code}" -A "$UA" --max-time 20 \
    -H "Content-Type: application/json" -H "Accept: application/json" \
    -d '{"appliedFacets":{},"limit":5,"offset":0,"searchText":""}' "$url" || echo err)"
  bytes="$(wc -c < /tmp/ats_probe_body 2>/dev/null || echo 0)"
  printf "%s\t%s\t%sB\t%s\n" "wd:$t" "$code" "$bytes" "$url"
done

echo "# BambooHR careers/list (public; no -L; many DC IPs get 503 — only add 200+non-empty to BAMBOOHR_COMPANIES)"
for s in ${BAMBOOHR_PROBE:-flyio cultureamp}; do
  probe "bb:$s" "https://${s}.bamboohr.com/careers/list"
done
