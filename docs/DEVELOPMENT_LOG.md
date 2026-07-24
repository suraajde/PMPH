# PMPH Development Log

## Project

PMPH - Portfolio Manager & Portfolio Health

This document records completed development milestones, verified checkpoints,
Git commits, and the exact continuation point for future development sessions.

---

## Sprint History

### Sprint 0.1.x - Project Foundation
Status: COMPLETED

- Project structure created
- Configuration management established
- SQLite connection established
- Git repository initialized
- GitHub integration established
- Initial documentation created

---

### Sprint 0.2.0 - Database Manager and Initial Tables
Status: COMPLETED

Git Commit:
8733202

- Database foundation implemented
- Initial persistent database architecture established

---

### Sprint 0.3.0 - Professional UI Navigation
Status: COMPLETED

Git Commit:
178754e

- Professional UI navigation foundation added
- Dashboard navigation
- Import Holdings navigation
- Database navigation

---

### Sprint 0.4.2 - Universal Import Framework and ProStocks Parser
Status: COMPLETED

Git Commit:
8466541

- Universal import framework established
- ProStocks holdings parser implemented
- Import architecture prepared for multiple brokers/platforms

---

### Sprint 0.4.4 - Universal Multi-File Holdings Import and Validation
Status: COMPLETED

Git Commit:
97010ce

- Universal multi-file holdings import
- Content-based Excel detection
- Holdings validation
- Multi-file processing foundation

---

### Sprint 0.5.0 - Portfolio Persistence and Holdings Synchronization
Status: COMPLETED

Git Commit:
eab1011

- Portfolio account persistence
- Holdings persistence
- Stable security identity
- FULL statement synchronization
- PARTIAL import protection
- Existing holding updates
- Sold-security removal on authoritative FULL synchronization

---

### Sprint 0.6.0 - Protected Portfolio Import, Backup and Persistence Foundation
Status: COMPLETED

Git Commit:
4a3581d

Completed capabilities:

- Universal multi-file holdings importer
- Account assignment
- FULL/PARTIAL synchronization
- Pre-import impact preview
- Verified automatic SQLite backup
- Backup failure write protection
- Protected multi-file batch import
- Persistent live portfolio database

Verified live persistence checkpoint:

- Accounts: 2
- Holdings: 4
- Working tree clean after commit and push

This commit is the stable baseline for Sprint 0.7.x development.

---

## Sprint 0.7.1 - Portfolio Read Service

Status: COMPLETED

Development branch:
sprint-0.7.1

Base commit:
4a3581d

### Implemented

Created:

- services/portfolio_read_service.py
- tests/test_portfolio_read_service.py

PortfolioReadService capabilities:

- Single account portfolio read
- All-account grouped portfolio read
- Consolidated cross-account holdings read
- ISIN-first security consolidation with symbol fallback
- Consolidated quantity
- Consolidated invested value
- Consolidated current value
- Consolidated profit/loss
- Recalculated average price
- Recalculated current price
- Recalculated profit/loss percentage
- Account participation tracking
- Portfolio-level summary

### Sprint 0.7.1 Functional Verification

PASS:

- Account-wise portfolio read
- All-account grouped portfolio read
- Consolidated holdings read
- Portfolio summary read
- Combined same-process Sprint 0.7.1 test execution
- Isolated SQLite test databases

### Live Database Verification

PortfolioReadService verified against:

data/pmph_portfolio.db

Verified result:

- Accounts: 2
- Raw holdings: 4
- Consolidated securities: 4
- Invested value: approximately 474,803.77
- Current value: approximately 504,034.60
- Profit: approximately 29,230.83
- Portfolio profit percentage: approximately 6.16%

Verified account distribution:

- Anita / Zerodha: 3 holdings
- Jaideep / ProStocks: 1 holding

Verified securities:

- GOLDBEES
- HDFCSML250
- MIDCAP
- SMALLCAP

### Regression Verification

PASS:

- Portfolio Database
- Holdings Database
- Holdings Synchronization
- Portfolio Import Service
- Protected Portfolio Batch Import
- Database Backup and Restore Safety

No regression detected in the Sprint 0.6.0 protected persistence foundation.

---

## Sprint 0.7.2 - Persistent Database / Portfolio UI

Status: COMPLETED

### Implementation

- Added dedicated Portfolio sidebar navigation
- Added Portfolio routing in app.py
- Added ui/portfolio_view.py
- Connected the UI to PortfolioReadService
- Added persistent portfolio summary metrics
- Added consolidated holdings presentation
- Added account-wise holdings presentation
- Added shared numeric and currency formatting
- Corrected rupee symbol UTF-8 presentation
- Preserved a read-only portfolio UI boundary
- Added tests/test_portfolio_view.py render smoke test

### Live UI Verification

Verified against:

data/pmph_portfolio.db

Verified result:

- Accounts: 2
- Holdings: 4
- Invested value: approximately 474,803.77
- Current value: approximately 504,034.60
- Profit: approximately 29,230.83
- Portfolio return: approximately 6.16%

Verified consolidated securities:

- GOLDBEES
- HDFCSML250
- MIDCAP
- SMALLCAP

Verified account-wise presentation:

- Anita / Zerodha: 3 holdings
- Jaideep / ProStocks: 1 holding

### Regression Verification

PASS:

- Portfolio Database
- Holdings Database
- Portfolio Import Service
- Protected Portfolio Batch Import
- Portfolio UI render smoke test

No regression detected in the protected portfolio persistence/import foundation.

---

## Sprint 0.8.1 - Portfolio Dashboard Foundation

Status: COMPLETED

### Implementation

- Replaced the placeholder Dashboard with a persisted portfolio dashboard
- Reused PortfolioReadService as the dashboard read boundary
- Added current value, invested value, profit/loss, and portfolio return metrics
- Added account, holding, and consolidated-security summary metrics
- Added security-wise portfolio composition
- Added account-wise portfolio allocation
- Added asset-type summary from persisted holding metadata
- Added Altair security-allocation visualization
- Preserved read-only separation from persistence/import logic
- Added tests/test_dashboard.py Dashboard render smoke test

### Live Dashboard Verification

Verified against:

data/pmph_portfolio.db

Verified result:

- Accounts: 2
- Holdings: 4
- Consolidated securities: 4
- Invested value: approximately 474,803.77
- Current value: approximately 504,034.60
- Profit: approximately 29,230.83
- Portfolio return: approximately 6.16%

Verified reconciliation:

- Portfolio summary current value: 504,034.60
- Consolidated security total: 504,034.60
- Account-wise total: 504,034.60
- Security allocation total: 100 percent
- Account allocation total: 100 percent

Verified security allocation:

- SMALLCAP: approximately 53.48 percent
- MIDCAP: approximately 30.16 percent
- GOLDBEES: approximately 11.63 percent
- HDFCSML250: approximately 4.73 percent

Current persisted asset-type metadata:

- ETF: 100 percent

### Regression Verification

PASS:

- Portfolio Database
- Holdings Database
- Portfolio Import Service
- Protected Portfolio Batch Import
- Portfolio Read Service
- Portfolio UI render smoke test
- Dashboard UI render smoke test

No regression detected in the protected persistence, read, or persistent UI foundation.

---

## Sprint 0.8.2 - Dashboard Valuation and Data Freshness Foundation

Status: COMPLETED

### Implementation

- Added services/portfolio_status_service.py
- Added read-only PortfolioStatusService
- Added persisted holding valuation coverage measurement
- Added valued-holding count and valuation coverage percentage
- Added latest and oldest persisted record update timestamps
- Added deduplicated source-file reporting
- Added explicit market valuation freshness boundary
- Added Data & Valuation Status section to the Dashboard
- Added valuation coverage, valued holdings, source files, and market freshness metrics
- Added latest persisted record-update presentation
- Added explanatory UI notice distinguishing persisted record updates from live market-price timestamps
- Added tests/test_portfolio_status_service.py
- Kept external market-data fetching deferred to Phase 0.10.x

### Live Status Verification

Verified against:

data/pmph_portfolio.db

Verified result:

- Holdings: 4
- Valued holdings: 4
- Valuation coverage: 100 percent
- Persisted source files: 2
- Source files:
  - Holdings_prostocks.xlsx
  - holdings-EY0423.xlsx
- Latest persisted record update: 21 Jul 2026, approximately 04:08 PM
- Market valuation freshness: NOT_TRACKED
- Market valuation as-of timestamp: not available

Important architecture boundary:

The persisted holding update timestamp represents the time the PMPH holding
record was imported or updated. It is not treated as a live market-price
timestamp.

Because PMPH does not yet persist a true market valuation as-of timestamp,
Sprint 0.8.2 does not falsely classify valuations as fresh or stale.
Market valuation freshness remains explicitly NOT_TRACKED until the planned
Phase 0.10.x market-data architecture provides authoritative valuation timing.

### Verification

PASS:

- Holding count
- Valuation coverage
- Source-file deduplication
- Record update timestamps
- Market freshness boundary
- PortfolioStatusService isolated test
- Portfolio Import Service
- Protected Portfolio Batch Import

No regression detected in the protected portfolio persistence/import foundation.

---

## Sprint 0.8.2 - Dashboard Valuation and Data Freshness Foundation

Status: COMPLETED

### Implementation

- Added services/portfolio_status_service.py
- Added read-only PortfolioStatusService
- Added persisted holding valuation coverage measurement
- Added valued-holding count and valuation coverage percentage
- Added latest and oldest persisted record update timestamps
- Added deduplicated source-file reporting
- Added explicit market valuation freshness boundary
- Added Data & Valuation Status section to the Dashboard
- Added valuation coverage, valued holdings, source files, and market freshness metrics
- Added latest persisted record-update presentation
- Added explanatory UI notice distinguishing persisted record updates from live market-price timestamps
- Added tests/test_portfolio_status_service.py
- Kept external market-data fetching deferred to Phase 0.10.x

### Live Status Verification

Verified against:

data/pmph_portfolio.db

Verified result:

- Holdings: 4
- Valued holdings: 4
- Valuation coverage: 100 percent
- Persisted source files: 2
- Source files:
  - Holdings_prostocks.xlsx
  - holdings-EY0423.xlsx
- Latest persisted record update: 21 Jul 2026, approximately 04:08 PM
- Market valuation freshness: NOT_TRACKED
- Market valuation as-of timestamp: not available

Important architecture boundary:

The persisted holding update timestamp represents the time the PMPH holding
record was imported or updated. It is not treated as a live market-price
timestamp.

Because PMPH does not yet persist a true market valuation as-of timestamp,
Sprint 0.8.2 does not falsely classify valuations as fresh or stale.
Market valuation freshness remains explicitly NOT_TRACKED until the planned
Phase 0.10.x market-data architecture provides authoritative valuation timing.

### Verification

PASS:

- Holding count
- Valuation coverage
- Source-file deduplication
- Record update timestamps
- Market freshness boundary
- PortfolioStatusService isolated test
- Portfolio Import Service
- Protected Portfolio Batch Import

No regression detected in the protected portfolio persistence/import foundation.

---

## Sprint 0.9.1 - Portfolio Concentration Analytics Foundation

Status: COMPLETED

### Implementation

- Added services/portfolio_analytics_service.py
- Established a read-only portfolio analytics service over persisted portfolio data
- Reused PortfolioReadService as the portfolio read boundary
- Added security-position concentration analytics
- Added security ranking by current portfolio value
- Added portfolio-weight calculation for persisted security positions
- Added largest-position concentration
- Added Top-3 security concentration
- Added Herfindahl-Hirschman Index (HHI) calculation for security positions
- Added effective security-position calculation
- Added account-level concentration analytics
- Added account HHI calculation
- Added persisted asset-type concentration analytics
- Added asset-type HHI calculation
- Added consolidated concentration summary
- Added explicit analytics scope and availability boundaries
- Added tests/test_portfolio_analytics_service.py
- Integrated concentration analytics into the Dashboard
- Added security-concentration presentation
- Added account-concentration presentation
- Added portfolio-health concentration summary metrics

### Live Analytics Verification

Verified against:

data/pmph_portfolio.db

Verified security concentration:

- SMALLCAP: approximately 53.48 percent
- MIDCAP: approximately 30.16 percent
- GOLDBEES: approximately 11.63 percent
- HDFCSML250: approximately 4.73 percent
- Largest security position: approximately 53.48 percent
- Top-3 security concentration: approximately 95.27 percent
- Security HHI: approximately 0.392727
- Effective security positions: approximately 2.55

Verified account concentration:

- Anita / Zerodha: approximately 88.37 percent
- Jaideep / ProStocks: approximately 11.63 percent
- Largest account concentration: approximately 88.37 percent
- Account HHI: approximately 0.794518

Verified persisted asset-type metadata:

- Asset types represented: 1
- ETF: 100 percent
- Asset-type HHI: 1.0

### Analytics Architecture Boundary

Sprint 0.9.1 measures concentration of persisted portfolio wrapper positions,
accounts, and persisted asset-type metadata.

The effective security-position metric must not be interpreted as the number
of underlying securities held inside ETFs or mutual funds.

Underlying ETF and mutual-fund diversification is not yet available.

Fund/ETF underlying-holding overlap analysis is not yet available.

Sector-level and underlying-security diversification must remain deferred
until the required instrument-intelligence and underlying-holdings
architecture is available.

The analytics service therefore exposes explicit scope and availability
boundaries rather than inferring unsupported diversification conclusions.

### Verification

PASS:

- Empty portfolio behavior
- Security ranking
- Security weights
- Top concentration
- Security HHI
- Effective security positions
- Security analytics scope
- Account concentration
- Asset-type concentration
- Analytics availability boundaries
- Portfolio Analytics Service isolated test
- Dashboard UI render smoke test
- Live Dashboard visual verification

No regression detected in the existing dashboard and portfolio read foundation.

---
## Sprint 0.9.2 - Portfolio Allocation Diagnostics Foundation

Status: COMPLETED

### Implementation

- Extended PortfolioAnalyticsService with deterministic allocation diagnostics
- Added factual allocation observations derived only from persisted portfolio information
- Added largest-security allocation observation
- Added Top-3 security allocation observation
- Added largest-account allocation observation
- Added largest-asset-type allocation observation
- Added explicit imported-portfolio analytics scope
- Established portfolio completeness as NOT_CONFIRMED
- Established complete-portfolio analytics as NOT_AVAILABLE
- Preserved target allocation as NOT_DEFINED
- Preserved recommendation status as NOT_PROVIDED
- Preserved underlying diversification as NOT_AVAILABLE
- Preserved fund/ETF overlap as NOT_AVAILABLE
- Added tests/test_portfolio_allocation_diagnostics.py
- Added Dashboard incomplete-portfolio Analysis Scope warning
- Renamed displayed percentages to Imported Holdings Weight %
- Updated Dashboard explanatory notice to prevent complete-portfolio interpretation

### Critical Portfolio Scope Boundary

The holdings currently imported and persisted in PMPH do not represent the
complete investment portfolio.

All current security, account, and asset-type allocation or concentration
percentages therefore describe only the holdings currently imported and
persisted in PMPH.

These percentages must not be interpreted as complete-portfolio allocation,
concentration, diversification, or exposure.

Portfolio completeness remains NOT_CONFIRMED.

Sprint 0.9.2 does not define target allocation and does not produce
overweight/underweight classifications, rebalance decisions, or investment
recommendations.

Underlying ETF and mutual-fund diversification remains NOT_AVAILABLE.

Fund/ETF underlying-holding overlap remains NOT_AVAILABLE.

### Verification

PASS:

- Empty imported portfolio behavior
- Empty portfolio scope boundary
- Allocation diagnostics contract
- Allocation diagnostic values
- Imported portfolio scope
- Recommendation boundary
- Sprint 0.9.1 Portfolio Analytics Service regression
- Dashboard UI render smoke test
- Portfolio Read Service regression
- Live Dashboard visual verification
- Analysis Scope warning visibility
- Imported Holdings Weight % presentation

No regression detected in the existing persisted portfolio analytics,
Dashboard, or portfolio-read foundation.

---
---

## Sprint 0.9.3 - Portfolio Health Diagnostic Framework Foundation

Status: COMPLETED

### Implementation

- Added services/portfolio_health_service.py
- Established PortfolioHealthService as a read-only health-diagnostic boundary
- Consolidated deterministic allocation observations into a structured health framework
- Reused PortfolioAnalyticsService rather than duplicating concentration calculations
- Added framework identifier PORTFOLIO_HEALTH_DIAGNOSTIC_FOUNDATION
- Established framework status as OBSERVATION_ONLY
- Added structured diagnostic observations with explicit source attribution
- Consolidated concentration metrics into the health-diagnostic contract
- Preserved imported-persisted-holdings analysis scope
- Preserved portfolio completeness as NOT_CONFIRMED
- Preserved complete-portfolio analytics as NOT_AVAILABLE
- Preserved health score as NOT_AVAILABLE
- Preserved target allocation as NOT_DEFINED
- Preserved recommendation status as NOT_PROVIDED
- Preserved underlying diversification as NOT_AVAILABLE
- Preserved fund/ETF overlap as NOT_AVAILABLE
- Preserved market-dependent analytics as NOT_AVAILABLE
- Added tests/test_portfolio_health_service.py
- Integrated the Portfolio Health Diagnostic Framework into the Dashboard
- Added framework-status presentation
- Added imported-holdings-only analysis-scope presentation
- Added portfolio-completeness presentation
- Added health-score availability presentation
- Added Current Diagnostic Observations table
- Added explicit Portfolio Health Scope warning
- Added explicit Framework Boundary notice

### Critical Architecture Boundary

Sprint 0.9.3 is an observation-only diagnostic framework.

It consolidates factual observations that can be derived from holdings currently
imported and persisted in PMPH.

The currently imported holdings do not represent a confirmed complete
investment portfolio.

The framework therefore must not interpret current observations as
complete-portfolio health conclusions.

Portfolio completeness remains NOT_CONFIRMED.

Health scoring remains NOT_AVAILABLE.

Target allocation remains NOT_DEFINED.

Investment recommendations remain NOT_PROVIDED.

Underlying ETF and mutual-fund diversification remains NOT_AVAILABLE.

Fund/ETF underlying-holding overlap remains NOT_AVAILABLE.

Market-dependent risk and performance analytics remain NOT_AVAILABLE.

Future scoring or recommendation logic must remain separate from factual
diagnostic observations until the required data and architecture exist.

### Verification

PASS:

- Empty portfolio health contract
- Empty portfolio scope boundary
- Health framework contract
- Diagnostic observations
- Concentration metrics
- Imported portfolio scope
- Scoring and recommendation boundary
- Deferred analytics boundary
- Sprint 0.9.2 Allocation Diagnostics regression
- Sprint 0.9.1 Portfolio Analytics regression
- Portfolio Read Service regression
- Dashboard UI render smoke test
- Live Dashboard visual verification
- Portfolio Health Scope warning visibility
- Diagnostic Framework metrics presentation
- Current Diagnostic Observations presentation
- Framework Boundary presentation

No regression detected in the existing persisted portfolio analytics,
allocation diagnostics, Dashboard, or portfolio-read foundation.

---

---
## Sprint 0.9.4 - Portfolio Health Diagnostic Classification Foundation

Status: COMPLETED

### Implementation

- Added services/portfolio_health_classification_service.py
- Added deterministic descriptive diagnostic classification architecture
- Kept factual diagnostic observations separate from classification output
- Added SECURITY_CONCENTRATION classification
- Added ACCOUNT_CONCENTRATION classification
- Added ASSET_TYPE_CONCENTRATION classification
- Preserved observed diagnostic values in classification output
- Added explicit classification dimensions
- Added classification type DESCRIPTIVE
- Added classification status DESCRIPTIVE_ONLY
- Added classification scope IMPORTED_PERSISTED_HOLDINGS
- Added deterministic diagnostic-rule provenance
- Added safe handling for unsupported or unknown observation codes
- Integrated classification output into PortfolioHealthService
- Preserved the existing observation contract
- Added separate classifications and classification_count output
- Preserved portfolio completeness as NOT_CONFIRMED
- Preserved severity classification as NOT_DEFINED
- Preserved health score as NOT_AVAILABLE
- Preserved target allocation as NOT_DEFINED
- Preserved recommendation status as NOT_PROVIDED
- Added tests/test_portfolio_health_classification_service.py
- Added tests/test_portfolio_health_classification_integration.py
- Added Diagnostic Classifications presentation to the Dashboard
- Added explicit descriptive-only classification boundary
- Added imported-holdings-only classification scope presentation
- Added explicit Severity Classification: Not Defined presentation

### Critical Architecture Boundary

Sprint 0.9.4 introduces deterministic descriptive classifications only.

Factual diagnostic observations remain separate from classification output.

Classification labels describe the type of diagnostic observation and do not
represent severity, portfolio-health scoring, target allocation, rebalance
decisions, or investment recommendations.

All classifications remain scoped only to holdings currently imported and
persisted in PMPH.

Portfolio completeness remains NOT_CONFIRMED.

Severity classification remains NOT_DEFINED.

Health scoring remains NOT_AVAILABLE.

Target allocation remains NOT_DEFINED.

Investment recommendations remain NOT_PROVIDED.

Underlying ETF and mutual-fund diversification remains NOT_AVAILABLE.

Fund/ETF underlying-holding overlap remains NOT_AVAILABLE.

Market-dependent risk and performance analytics remain NOT_AVAILABLE.

### Verification

PASS:

- Empty classification contract
- Empty classification boundary
- Deterministic classification mapping
- Classification dimensions
- Observed value preservation
- Classification scope and provenance
- Unknown observation safety
- Imported portfolio scope
- Scoring and recommendation boundary
- Observation/classification separation
- Deterministic health-framework classification integration
- Classification architecture boundary
- Sprint 0.9.3 Portfolio Health regression
- Sprint 0.9.2 Allocation Diagnostics regression
- Sprint 0.9.1 Portfolio Analytics regression
- Portfolio Read Service regression
- Dashboard UI render smoke test
- Live Dashboard visual verification
- Diagnostic Classifications presentation
- Descriptive-only classification status presentation
- Severity Classification: Not Defined presentation

No regression detected in the existing portfolio-health framework, allocation
diagnostics, persisted portfolio analytics, Dashboard, or portfolio-read
foundation.

---

## Sprint 0.9.5 - Portfolio Health Diagnostic Severity Foundation

Status: COMPLETED

### Implementation

- Added services/portfolio_health_severity_service.py
- Established a separate deterministic diagnostic-severity architecture
- Preserved factual observations as a separate layer
- Preserved descriptive classifications as a separate layer
- Added a severity-rule registry for supported diagnostic candidates
- Added explicit severity eligibility gating
- Added rule-status and eligibility-status metadata
- Added data-requirement metadata
- Added explicit limitation descriptions
- Added severity scope IMPORTED_PERSISTED_HOLDINGS
- Added severity-rule provenance
- Deferred largest-security severity pending instrument intelligence
- Deferred Top-3 security severity pending instrument and underlying-exposure context
- Deferred account-allocation severity pending an explicit account-risk model
- Deferred asset-type severity pending underlying-exposure modeling
- Prevented position-weight-only severity classification
- Integrated PortfolioHealthSeverityService into PortfolioHealthService
- Added severity_classifications output
- Added severity_classification_count output
- Added severity_status output
- Added severity_scope output
- Added severity_rule_status output
- Preserved legacy severity_classification as NOT_DEFINED
- Preserved portfolio completeness as NOT_CONFIRMED
- Preserved health score as NOT_AVAILABLE
- Preserved target allocation as NOT_DEFINED
- Preserved recommendation status as NOT_PROVIDED
- Added tests/test_portfolio_health_severity_service.py
- Added tests/test_portfolio_health_severity_integration.py
- Added Diagnostic Severity Eligibility presentation to the Dashboard
- Added Severity Status presentation
- Added Eligible Severity Outputs presentation
- Added Severity Rule Status presentation
- Added explicit no-premature-severity explanation
- Added explicit no-forced-rebalance boundary
- Added advisory and investor-profile-aware future guidance principle

### Critical Architecture Boundary

Sprint 0.9.5 establishes severity eligibility architecture without inventing
unsupported severity conclusions.

Current concentration observations cannot safely be converted into LOW,
MEDIUM, or HIGH severity labels using position weights alone.

Instrument intelligence, underlying ETF and mutual-fund exposure, and
appropriate risk semantics are required before applicable severity rules may
be enabled.

Portfolio completeness remains NOT_CONFIRMED.

Health scoring remains NOT_AVAILABLE.

Target allocation remains NOT_DEFINED.

Investment recommendations remain NOT_PROVIDED.

No forced rebalance action is produced.

Future allocation, fund-switch, SIP-redirection, replacement, and rebalance
guidance must remain advisory and investor-profile aware.

An investor may intentionally choose an aggressive portfolio allocation.
PMPH may identify risks, explain trade-offs, suggest alternatives, and present
possible switches or allocation changes, but such guidance must remain
optional decision support with supporting reasons rather than mandatory
portfolio action.

### Verification

PASS:

- Empty severity contract
- Empty severity count
- Severity eligibility gate
- No eligible severity rules
- Severity rule registry
- Eligible severity rule count
- Registered severity candidates
- Explicit rule limitations
- Severity scope and provenance
- Instrument-intelligence requirement boundary
- Underlying-exposure requirement boundary
- Account-risk-semantics requirement boundary
- No premature severity output
- Imported portfolio scope
- Portfolio completeness boundary
- Health-score boundary
- Target-allocation boundary
- Recommendation boundary
- Severity integration into PortfolioHealthService
- Observation/classification/severity separation
- Sprint 0.9.5 Severity Integration test
- Sprint 0.9.5 Severity Service test
- Sprint 0.9.4 Classification Integration regression
- Sprint 0.9.3 Portfolio Health regression
- Dashboard UI render smoke test
- Live Dashboard visual verification
- Diagnostic Severity Eligibility presentation
- Eligibility Gated presentation
- No Eligible Rules presentation
- No-forced-rebalance boundary presentation
- Advisory and investor-profile-aware guidance presentation

No regression detected in the existing portfolio-health framework,
classification architecture, allocation diagnostics, persisted portfolio
analytics, Dashboard, or portfolio-read foundation.

---

## Exact Continuation Point

Completed Sprint:

0.9.5 - Portfolio Health Diagnostic Severity Foundation

Current Phase:

Phase 0.9.x - Portfolio Health and Analytics Foundation

Next Sprint:

0.9.6 - Portfolio Health Context Requirements Foundation

Primary objective:

Define and formalize the context requirements that must be satisfied before
diagnostic severity rules may become eligible.

Sprint 0.9.6 should define instrument-intelligence, underlying-exposure, and
risk-semantics requirements without inventing unsupported severity thresholds.

It should prepare a clean architectural handoff into Phase 0.10.x Market Data
and Instrument Intelligence while preserving explicit eligibility gating.

Portfolio completeness remains NOT_CONFIRMED.

Health scoring remains NOT_AVAILABLE.

Target allocation remains NOT_DEFINED.

Investment recommendations remain NOT_PROVIDED.

Future allocation and rebalance intelligence must remain advisory and
investor-profile aware. PMPH must support intentional aggressive allocation
profiles and must not convert suggested allocation changes, fund switches,
SIP redirections, replacements, or rebalancing into forced actions.

---

## Development Continuity Rule

Future PMPH sessions must begin by checking:

1. docs/ROADMAP.md
2. docs/DEVELOPMENT_LOG.md
3. git status
4. git log -5 --oneline

Do not reconstruct completed sprint history from chat memory when these
repository records are available.
