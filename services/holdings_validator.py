from dataclasses import dataclass, field
from typing import List

from models.portfolio import PortfolioHolding


@dataclass
class HoldingValidationResult:
    holding: PortfolioHolding

    is_valid: bool = False
    confidence: str = "LOW"

    checks_passed: int = 0
    checks_failed: int = 0

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )


class HoldingsValidator:
    """
    Universal financial validation engine.

    This validator does not depend on any broker.

    It checks whether extracted holdings are internally
    consistent before PMPH allows them to move toward
    portfolio preview or database import.
    """

    VALUE_TOLERANCE_PERCENT = 1.0

    ABSOLUTE_VALUE_TOLERANCE = 2.0

    PERCENT_TOLERANCE = 0.15

    # =====================================================
    # PUBLIC METHODS
    # =====================================================

    def validate_holdings(
        self,
        holdings
    ):

        results = []

        for holding in holdings:

            result = self.validate_holding(
                holding
            )

            results.append(
                result
            )

        return results

    def validate_holding(
        self,
        holding
    ):

        result = HoldingValidationResult(
            holding=holding
        )

        # ---------------------------------------------
        # Identity validation
        # ---------------------------------------------

        self._check_identity(
            holding,
            result
        )

        # ---------------------------------------------
        # Quantity validation
        # ---------------------------------------------

        self._check_quantity(
            holding,
            result
        )

        # ---------------------------------------------
        # Invested value relationship
        # ---------------------------------------------

        self._check_invested_value(
            holding,
            result
        )

        # ---------------------------------------------
        # Current value relationship
        # ---------------------------------------------

        self._check_current_value(
            holding,
            result
        )

        # ---------------------------------------------
        # Profit / Loss relationship
        # ---------------------------------------------

        self._check_profit_loss(
            holding,
            result
        )

        # ---------------------------------------------
        # Profit / Loss percentage
        # ---------------------------------------------

        self._check_profit_loss_percent(
            holding,
            result
        )

        # ---------------------------------------------
        # Final confidence
        # ---------------------------------------------

        self._assign_confidence(
            result
        )

        return result

    # =====================================================
    # VALIDATION CHECKS
    # =====================================================

    def _check_identity(
        self,
        holding,
        result
    ):

        if any(
            [
                holding.symbol,
                holding.name,
                holding.isin,
            ]
        ):

            result.checks_passed += 1

        else:

            result.checks_failed += 1

            result.errors.append(
                "Holding has no symbol, name, or ISIN."
            )

    def _check_quantity(
        self,
        holding,
        result
    ):

        if holding.quantity > 0:

            result.checks_passed += 1

        else:

            result.checks_failed += 1

            result.errors.append(
                "Quantity is zero or negative."
            )

    def _check_invested_value(
        self,
        holding,
        result
    ):

        if (
            holding.quantity <= 0
            or holding.average_price <= 0
            or holding.invested_value <= 0
        ):

            result.warnings.append(
                "Invested-value relationship "
                "could not be fully validated."
            )

            return

        expected = (
            holding.quantity
            * holding.average_price
        )

        if self._values_match(
            expected,
            holding.invested_value
        ):

            result.checks_passed += 1

        else:

            result.checks_failed += 1

            result.errors.append(
                "Quantity × Average Price does not "
                "match Invested Value."
            )

    def _check_current_value(
        self,
        holding,
        result
    ):

        if (
            holding.quantity <= 0
            or holding.current_price <= 0
            or holding.current_value <= 0
        ):

            result.warnings.append(
                "Current-value relationship "
                "could not be fully validated."
            )

            return

        expected = (
            holding.quantity
            * holding.current_price
        )

        if self._values_match(
            expected,
            holding.current_value
        ):

            result.checks_passed += 1

        else:

            result.checks_failed += 1

            result.errors.append(
                "Quantity × Current Price does not "
                "match Current Value."
            )

    def _check_profit_loss(
        self,
        holding,
        result
    ):

        if (
            holding.current_value == 0
            and holding.invested_value == 0
        ):

            result.warnings.append(
                "Profit/Loss relationship "
                "could not be validated."
            )

            return

        expected = (
            holding.current_value
            - holding.invested_value
        )

        if self._values_match(
            expected,
            holding.profit_loss
        ):

            result.checks_passed += 1

        else:

            result.checks_failed += 1

            result.errors.append(
                "Current Value − Invested Value "
                "does not match Profit/Loss."
            )

    def _check_profit_loss_percent(
        self,
        holding,
        result
    ):

        if holding.invested_value <= 0:

            result.warnings.append(
                "Profit/Loss percentage "
                "could not be validated."
            )

            return

        expected = (
            holding.profit_loss
            / holding.invested_value
            * 100
        )

        difference = abs(
            expected
            - holding.profit_loss_percent
        )

        if (
            difference
            <= self.PERCENT_TOLERANCE
        ):

            result.checks_passed += 1

        else:

            result.checks_failed += 1

            result.errors.append(
                "Profit/Loss percentage does not "
                "match the calculated return."
            )

    # =====================================================
    # VALUE COMPARISON
    # =====================================================

    def _values_match(
        self,
        expected,
        actual
    ):

        difference = abs(
            expected
            - actual
        )

        if (
            difference
            <= self.ABSOLUTE_VALUE_TOLERANCE
        ):

            return True

        base = max(
            abs(expected),
            abs(actual),
            1.0
        )

        difference_percent = (
            difference
            / base
            * 100
        )

        return (
            difference_percent
            <= self.VALUE_TOLERANCE_PERCENT
        )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def _assign_confidence(
        self,
        result
    ):

        if result.errors:

            result.is_valid = False

            result.confidence = "LOW"

            return

        if (
            result.checks_passed >= 5
        ):

            result.is_valid = True

            result.confidence = "HIGH"

            return

        if (
            result.checks_passed >= 3
        ):

            result.is_valid = True

            result.confidence = "MEDIUM"

            return

        result.is_valid = False

        result.confidence = "LOW"