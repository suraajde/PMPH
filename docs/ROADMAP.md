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

## Next Sprint

### Sprint 0.7.2 - Persistent Database / Portfolio UI

Planned objectives:

- Connect PortfolioReadService to the application UI
- Display persistent portfolio data from SQLite
- Account-wise portfolio view
- Consolidated portfolio view
- Portfolio summary metrics
- Clear account/platform ownership visibility
- Read-only UI foundation before portfolio editing features

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
