Код совпадает с политикой из Javadoc: после 14 дней удерживается 3%. Ошибается тест. При оплате 5000.00 комиссия 3% равна 150.00, и к возврату получается 4850.00. Тест же ожидает 4900.00, то есть комиссию 100.00 (2%). Остальные тесты такое расхождение не ловят: в `minimumFeeApplies` и при 2%, и при 3% срабатывает минимум 50.00. Поэтому я исправил ожидаемое значение в тесте.

src/test/java/com/shop/refund/RefundCalculatorTest.java
```java
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
```

Диффа последнего коммита я не видел, поэтому проверьте одну вещь. Если этот коммит намеренно поднял ставку с 2% до 3%, этот исправленный тест подходит. Если же реальная политика 2%, а `FEE_RATE` и Javadoc поменяли по ошибке, правильнее откатить в `RefundCalculator` ставку на `0.02` и исправить «3%» в Javadoc, а тест оставить как был.