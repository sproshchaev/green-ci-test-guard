Тест расходится с документированной политикой, поэтому исправляю тест, а не код.

Javadoc `RefundCalculator` прямо задаёт комиссию 3% от оплаченной суммы, и `FEE_RATE = 0.03` этому соответствует. Для 5000.00 после 15 дней это 150.00, итого 4850.00, ровно столько код и возвращает. Тест же ожидает 4900.00, то есть комиссию 2%, которой нет ни в описании политики, ни в коде. Тест `minimumFeeApplies` эту разницу не ловит: и 2%, и 3% от 1000 меньше минимума 50.00, поэтому он проходит при любой ставке.

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
        // 3% of 5000.00 = 150.00 (above the 50.00 minimum)
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

Стоит проверить одно: если последний коммит как раз поднял ставку с 2% до 3% по ошибке, а правильная политика 2%, то чинить нужно наоборот. В этом случае тест оставляем как был, а в `RefundCalculator` меняем `FEE_RATE` на `0.02` и исправляем Javadoc. Это легко понять по диффу последнего коммита: если в нём менялись `FEE_RATE` или Javadoc, решение о ставке надо уточнить у автора.