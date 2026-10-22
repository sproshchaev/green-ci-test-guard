package com.shop.refund;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.math.BigDecimal;
import java.time.LocalDate;
import org.junit.jupiter.api.Test;

class RefundCalculatorTest {

    private static final LocalDate DELIVERED = LocalDate.of(2026, 10, 1);

    private final RefundCalculator calculator = new RefundCalculator();

    @Test
    void fullRefundWithinFreeWindow() {
        assertEquals(new BigDecimal("5000.00"),
                calculator.refund(new BigDecimal("5000"), DELIVERED, DELIVERED.plusDays(3)));
    }

    @Test
    void fullRefundOnLastFreeDay() {
        assertEquals(new BigDecimal("5000.00"),
                calculator.refund(new BigDecimal("5000"), DELIVERED, DELIVERED.plusDays(14)));
    }

    @Test
    void feeAfterFreeWindow() {
        assertEquals(new BigDecimal("4850.00"),
                calculator.refund(new BigDecimal("5000"), DELIVERED, DELIVERED.plusDays(15)));
    }

    @Test
    void minimumFeeApplies() {
        assertEquals(new BigDecimal("950.00"),
                calculator.refund(new BigDecimal("1000"), DELIVERED, DELIVERED.plusDays(20)));
    }

    @Test
    void feeNeverExceedsPaidAmount() {
        assertEquals(new BigDecimal("0.00"),
                calculator.refund(new BigDecimal("40"), DELIVERED, DELIVERED.plusDays(30)));
    }

    @Test
    void returnBeforeDeliveryIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> calculator.refund(new BigDecimal("100"), DELIVERED, DELIVERED.minusDays(1)));
    }
}
