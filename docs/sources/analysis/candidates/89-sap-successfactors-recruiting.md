# SAP SuccessFactors Recruiting (catalog_id=89)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | D |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | enterprise |
| connector_key | — |

## Official / docs
- Official: https://www.sap.com/products/hcm/recruiting.html
- Developer: SAP OData / Recruiting APIs on customer tenant (API Business Hub).
- Terms: each customer issues OAuth/API credentials; not a public job board.

## Access path (for future connector)
- Preferred: OData job requisition endpoints on `{tenant}.successfactors.com` with customer consent.
- Auth: OAuth2 client credentials or SAML bearer per tenant admin.
- Pagination: OData `$skip`/`$top`.

## Geo / role fit
- Enterprise employers only; tenant-scoped.
- Fit for FMI Demand Compass: **No** for global crawl — customer-specific integration only.

## Gaps / next step
- Document only for optional single-tenant deployments; not catalog-wide ACTIVE without tenant keys.
