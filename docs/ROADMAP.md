# PMPH Development Roadmap

## Project
PMPH - Portfolio Manager & Portfolio Health

## Development Rule

This roadmap is the permanent source of truth for PMPH development.

At the completion of every sprint:
1. Update this roadmap.
2. Update DEVELOPMENT_LOG.md.
3. Run relevant regression tests.
4. Commit and push the completed sprint.
5. Record the exact next sprint and objective.

---

## Completed Foundation

### Sprint 0.1.x - Project Foundation
Status: COMPLETED

- Project structure
- Configuration management
- SQLite connection
- Git repository
- GitHub integration
- Project documentation

### Sprint 0.2.0 - Database Foundation
Status: COMPLETED

- Database manager foundation
- Initial persistent tables and database structure

### Sprint 0.3.0 - Professional UI Navigation
Status: COMPLETED

- Streamlit application navigation foundation
- Dashboard, Import Holdings and Database navigation

### Sprint 0.4.2 - Universal Import Framework
Status: COMPLETED

- Universal holdings import framework
- ProStocks parser
- Content-based file handling foundation

### Sprint 0.4.4 - Universal Multi-File Import and Validation
Status: COMPLETED

- Multi-file holdings import
- Content-based Excel detection
- Holdings validation
- Import preview foundation

### Sprint 0.5.0 - Portfolio Persistence and Synchronization
Status: COMPLETED

- Persistent portfolio accounts
- Persistent holdings database
- Stable security identity
- FULL statement synchronization
- PARTIAL import protection
- Holdings update and sold-security removal rules

### Sprint 0.6.0 - Protected Portfolio Import, Backup and Persistence
Status: COMPLETED
Git Commit: 4a3581d

- Universal multi-file holdings importer
- Account assignment
- FULL/PARTIAL synchronization
- Pre-import impact preview
- Verified automatic SQLite backup
- Protected batch import
- Live portfolio persistence verified
- Verified baseline: 2 accounts / 4 holdings

---

## Current Development

### Sprint 0.7.1 - Portfolio Read Service
Status: COMPLETED

Objectives:

- Read persisted portfolio account-wise
- Read all accounts while preserving account boundaries
- Consolidate identical securities across accounts
- Use ISIN-first security identity with symbol fallback
- Calculate consolidated quantity and valuation
- Recalculate average price and profit/loss percentage correctly
- Provide portfolio-level summary totals
- Maintain read separation from import/synchronization logic
- Add isolated automated verification
- Verify against live persisted PMPH portfolio

Verified during development:

- Account-wise portfolio read
- All-account grouped portfolio read
- Consolidated holdings read
- Portfolio summary read
- Combined Sprint 0.7.1 tests
- Live database read: 2 accounts / 4 holdings / 4 consolidated securities
- Sprint 0.6.0 persistence and safety regression tests

---

## Completed Persistent UI

### Sprint 0.7.2 - Persistent Database / Portfolio UI
Status: COMPLETED

Objectives completed:

- Connected PortfolioReadService to the application UI
- Added dedicated Portfolio navigation and page routing
- Displayed persistent portfolio data from SQLite
- Added portfolio summary metrics
- Added consolidated holdings view
- Added account-wise holdings view
- Preserved account/platform ownership visibility
- Added numeric and currency presentation formatting
- Maintained a read-only UI boundary over the persistence layer
- Added Portfolio UI render smoke-test coverage

Verified during development:

- Portfolio page rendered successfully in Streamlit
- Live summary matched persisted database values
- Consolidated view displayed 4 securities
- Anita / Zerodha displayed 3 holdings
- Jaideep / ProStocks displayed 1 holding
- Rupee currency encoding corrected and verified
- Relevant persistence/import regression tests passed
- Live baseline remained 2 accounts / 4 holdings

---

## Completed Dashboard Foundation

### Sprint 0.8.1 - Portfolio Dashboard Foundation
Status: COMPLETED

Objectives completed:

- Replaced the placeholder Dashboard with persisted portfolio overview data
- Reused PortfolioReadService as the dashboard read boundary
- Added core portfolio valuation metrics
- Added account, holding, and consolidated-security summary metrics
- Added security-wise portfolio composition
- Added account-wise portfolio allocation
- Added asset-type summary from persisted holding metadata
- Added security allocation visualization
- Preserved consolidated and account ownership boundaries
- Avoided premature dependency on external market-data architecture
- Added Dashboard UI render smoke-test coverage

Verified during development:

- Dashboard rendered successfully in Streamlit
- Portfolio current value reconciled to 504,034.60
- Consolidated security total reconciled to 504,034.60
- Account-wise total reconciled to 504,034.60
- Security allocation reconciled to 100 percent
- Account allocation reconciled to 100 percent
- Live baseline remained 2 accounts / 4 holdings / 4 consolidated securities
- Relevant persistence, read, and UI regression tests passed

---

## Completed Dashboard Valuation and Data Freshness Foundation

### Sprint 0.8.2 - Dashboard Valuation and Data Freshness Foundation
Status: COMPLETED

Objectives completed:

- Added read-only PortfolioStatusService for portfolio valuation/status reporting
- Added persisted holding valuation coverage measurement
- Added valued-holding count and valuation coverage percentage
- Added persisted record update timestamp visibility
- Added source-file count and deduplicated source-file reporting
- Added dashboard Data & Valuation Status section
- Explicitly separated persisted record-update timestamps from market-price freshness
- Established market valuation freshness as NOT_TRACKED until the planned market-data architecture exists
- Avoided falsely classifying persisted valuations as fresh or stale without a true market valuation timestamp
- Preserved external market-data fetching for Phase 0.10.x
- Added isolated PortfolioStatusService test coverage

Verified during development:

- Live persisted holding count: 4
- Valuation coverage: 4 / 4 holdings
- Valuation coverage percentage: 100 percent
- Persisted source files: 2
- Latest persisted record update surfaced successfully
- Market valuation freshness correctly reported as NOT_TRACKED
- Dashboard status section rendered successfully
- Relevant persistence and import regression tests passed

---

## Current Phase

### Phase 0.9.x - Portfolio Health and Analytics Foundation
Status: IN PROGRESS

### Sprint 0.9.1 - Portfolio Concentration Analytics Foundation
Status: COMPLETED

Objectives completed:

- Established read-only PortfolioAnalyticsService
- Reused PortfolioReadService as the persisted portfolio read boundary
- Added persisted security-position concentration analysis
- Added security ranking and portfolio-weight calculations
- Added largest-position and Top-3 concentration metrics
- Added security HHI calculation
- Added effective security-position calculation
- Added account concentration and account HHI
- Added persisted asset-type concentration and asset-type HHI
- Added consolidated concentration summary
- Added explicit analytics scope and availability boundaries
- Integrated concentration analytics into the Dashboard
- Added deterministic PortfolioAnalyticsService test coverage
- Preserved the boundary with the later market-data and instrument-intelligence architecture

Verified during development:

- Largest security position: approximately 53.48 percent
- Top-3 security concentration: approximately 95.27 percent
- Security HHI: approximately 0.392727
- Effective security positions: approximately 2.55
- Largest account concentration: approximately 88.37 percent
- Account HHI: approximately 0.794518
- Persisted asset-type metadata: ETF 100 percent
- Dashboard analytics section rendered and visually verified
- Underlying ETF/fund diversification remains NOT_AVAILABLE
- Fund/ETF overlap remains NOT_AVAILABLE

Important architecture boundary:

Sprint 0.9.1 measures concentration using persisted wrapper positions,
accounts, and persisted asset-type metadata. It does not infer underlying
ETF or mutual-fund diversification, sector exposure, or fund overlap without
the required instrument-intelligence and underlying-holdings architecture.

---


## Sprint 0.9.2 - Portfolio Allocation Diagnostics Foundation

Status: COMPLETED

Objectives completed:

- Extended PortfolioAnalyticsService with deterministic allocation diagnostics
- Added factual allocation observations from persisted portfolio information
- Added largest-security allocation observation
- Added Top-3 security allocation observation
- Added largest-account allocation observation
- Added largest-asset-type allocation observation
- Established explicit imported-portfolio analytics scope
- Established portfolio completeness as NOT_CONFIRMED
- Preserved target allocation as NOT_DEFINED
- Preserved recommendation status as NOT_PROVIDED
- Preserved underlying diversification as NOT_AVAILABLE
- Preserved fund/ETF overlap as NOT_AVAILABLE
- Added dedicated allocation-diagnostics test coverage
- Added Dashboard incomplete-portfolio Analysis Scope warning
- Renamed displayed percentages to Imported Holdings Weight %
- Visually verified the Dashboard scope presentation

Important architecture boundary:

The holdings currently imported into PMPH do not represent the complete
investment portfolio.

All current allocation and concentration percentages describe only the
holdings currently imported and persisted in PMPH. They must not be
interpreted as complete-portfolio allocation, concentration,
diversification, or exposure.

---

## Next Sprint

### Sprint 0.9.3 - Portfolio Health Diagnostic Framework Foundation

Status: COMPLETED

Objectives completed:

- Established PortfolioHealthService as a read-only health-diagnostic boundary
- Consolidated deterministic concentration and allocation observations
- Added structured diagnostic observations with explicit source attribution
- Added consolidated concentration metrics to the health framework
- Established framework status as OBSERVATION_ONLY
- Preserved imported-persisted-holdings analysis scope
- Preserved portfolio completeness as NOT_CONFIRMED
- Preserved complete-portfolio analytics as NOT_AVAILABLE
- Preserved health score as NOT_AVAILABLE
- Preserved target allocation as NOT_DEFINED
- Preserved recommendation status as NOT_PROVIDED
- Preserved underlying diversification as NOT_AVAILABLE
- Preserved fund/ETF overlap as NOT_AVAILABLE
- Preserved market-dependent analytics as NOT_AVAILABLE
- Added dedicated PortfolioHealthService test coverage
- Integrated the diagnostic framework into the Dashboard
- Added explicit Portfolio Health Scope and Framework Boundary presentation
- Visually verified the live Dashboard integration

Important architecture boundary:

Sprint 0.9.3 is observation-only.

The framework describes factual conditions derived from holdings currently
imported and persisted in PMPH. Portfolio completeness remains NOT_CONFIRMED,
so these observations must not be interpreted as complete-portfolio health
conclusions.

Health scoring, target allocation, recommendations, underlying ETF/fund
diversification, fund overlap, and market-dependent analytics remain deferred
until their required architecture and data are available.

---

## Sprint 0.9.4 - Portfolio Health Diagnostic Classification Foundation

Status: COMPLETED

Objectives completed:

- Extend the observation-only health framework with deterministic diagnostic classifications
- Keep factual observations separate from classification output
- Define explicit classification scope and provenance
- Preserve imported-persisted-holdings scope
- Preserve portfolio completeness as NOT_CONFIRMED
- Avoid complete-portfolio health conclusions
- Avoid premature health scoring
- Avoid target-allocation and rebalance recommendations
- Preserve underlying ETF/fund diversification and overlap boundaries
- Keep market-dependent risk and performance analytics aligned with the later market-data foundation
- Continue building incrementally toward a future portfolio-health scoring architecture

---
## Sprint 0.9.5 - Portfolio Health Diagnostic Severity Foundation

Status: COMPLETED

Objectives completed:

- Established PortfolioHealthSeverityService as a separate severity layer
- Preserved separation between factual observations, descriptive classifications, and severity classifications
- Added an explicit severity-rule registry for supported diagnostic candidates
- Added deterministic severity eligibility gating
- Added explicit rule, eligibility, data-requirement, limitation, scope, and provenance metadata
- Deferred severity where instrument intelligence or underlying exposure context is insufficient
- Deferred account-concentration severity until explicit account-risk semantics exist
- Prevented position weight alone from producing premature severity conclusions
- Integrated the severity contract into PortfolioHealthService
- Preserved severity classification output as empty when no rule is eligible
- Preserved portfolio completeness as NOT_CONFIRMED
- Preserved health score as NOT_AVAILABLE
- Preserved target allocation as NOT_DEFINED
- Preserved recommendation status as NOT_PROVIDED
- Added dedicated severity service and integration tests
- Added Diagnostic Severity Eligibility presentation to the Dashboard
- Added explicit eligibility-gated and no-eligible-rules presentation
- Added explicit no-forced-rebalance architecture boundary
- Established that future allocation, fund-switch, SIP-redirection, and rebalance guidance must remain advisory and investor-profile aware
- Preserved the ability for an investor to intentionally choose an aggressive portfolio allocation

Important architecture boundary:

Sprint 0.9.5 does not assign LOW, MEDIUM, or HIGH severity merely from
persisted position weights.

Severity is permitted only where sufficient context and an explicit,
deterministic, tested rule exist.

Instrument intelligence, underlying ETF and mutual-fund exposure, and
appropriate risk semantics must exist before applicable severity rules are
enabled.

Future portfolio allocation, fund-switch, SIP-redirection, replacement, and
rebalance guidance must be decision support rather than forced action.

Investor risk profile and intentional portfolio style must be respected. An
investor may intentionally maintain an aggressive allocation. PMPH may explain
risks, alternatives, trade-offs, and possible switches, but future actions
must be presented as optional decisions with supporting reasons.

---

## Next Sprint

### Sprint 0.9.6 - Portfolio Health Context Requirements Foundation

Status: PLANNED

Planned objectives:

- Define the context required before diagnostic severity rules may become eligible
- Formalize instrument-intelligence requirements for direct securities, ETFs, mutual funds, and other supported instruments
- Formalize underlying-exposure requirements for ETF and mutual-fund diagnostics
- Define risk-semantics requirements for security, account, and asset-type severity
- Preserve explicit eligibility gating when required context is unavailable
- Avoid inventing arbitrary LOW, MEDIUM, or HIGH thresholds before supporting data and semantics exist
- Preserve imported-persisted-holdings scope and portfolio completeness as NOT_CONFIRMED
- Preserve separation between diagnostics, severity, health scoring, target allocation, and recommendations
- Prepare a clean architectural handoff into Phase 0.10.x Market Data and Instrument Intelligence
- Preserve advisory, investor-profile-aware future allocation and rebalance decision support

---
## Planned Roadmap Toward v1.0

### Phase 0.8.x - Portfolio Dashboard and Valuation

Planned direction:

- Portfolio overview dashboard
- Allocation views
- Asset/category breakdown
- Account and consolidated valuation
- Profit/loss presentation
- Portfolio composition visualization
- Data freshness and valuation status

### Phase 0.9.x - Portfolio Health and Analytics Foundation

Planned direction:

- Portfolio health framework
- Diversification analysis
- Concentration analysis
- Asset allocation analysis
- Fund/ETF overlap analysis
- Risk and drawdown analytics
- Performance analytics
- Portfolio diagnostic scoring foundation

### Phase 0.10.x - Market Data and Instrument Intelligence

Planned direction:

- Reliable market-data layer
- Mutual fund and ETF metadata
- Benchmark/index mapping
- Expense ratio and instrument attributes
- Historical price/NAV foundation
- Data refresh and caching architecture

### Phase 0.11.x - SIP and Rebalancing Intelligence

Planned direction:

- SIP master and SIP allocation views
- SIP increase/decrease analysis
- SIP redirection engine
- Rebalancing framework
- Allocation drift detection
- Replacement decision foundation

### Phase 0.12.x - Portfolio Recommendation Engine

Planned direction:

- Rule-based recommendation foundation
- Portfolio health driven recommendations
- Hold / increase / reduce / replace decision support
- Recommendation reasons and evidence
- Guardrails against unnecessary portfolio churn
- AI-assisted recommendation layer only after deterministic analytics are stable

### Phase 0.13.x - Reporting, Reliability and Application Hardening

Planned direction:

- Portfolio reports
- Export capability
- Settings and configuration
- Error handling and recovery
- Database maintenance and restore workflow
- UI consistency
- Performance optimization
- Packaging and deployment preparation

### Version 1.0 - Stable PMPH Release

Target:

- Stable portfolio import and persistence
- Persistent portfolio UI
- Reliable valuation and analytics
- Portfolio health diagnostics
- SIP and rebalancing intelligence
- Explainable recommendation engine
- Reporting and recovery
- Tested stable release

---

## Architectural Principle

PMPH development follows this sequence:

Reliable Data
-> Safe Persistence
-> Read Layer
-> Persistent UI
-> Valuation
-> Analytics
-> Portfolio Health
-> Rebalancing Intelligence
-> Explainable Recommendations
-> Stable Release

AI recommendations must not be built before the underlying portfolio data,
valuation, analytics and deterministic decision rules are reliable.
