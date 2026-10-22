Тест противоречит документированной политике возврата, а код ей соответствует. Поэтому я исправил тест, а не код.

В Javadoc `RefundCalculator` сказано, что после 14 дней удерживается 3% от оплаченной суммы, и код делает именно это. Для 5000.00 комиссия 3% равна 150.00, к возврату 4850.00. Тест `feeAfterFreeWindow` ожидает 4900.00, то есть комиссию 100.00, а это 2%. Остальные тесты под такое расхождение не попадают. В `minimumFeeApplies` при обеих ставках срабатывает минимум 50.00, а в `feeNeverExceedsPaidAmount` комиссию ограничивает сама сумма оплаты.

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
        // 3% of 5000.00 = 150.00 fee
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

Ставка комиссии — это бизнес-правило, поэтому перед мержем стоит свериться с последним коммитом. Если в нём ставку намеренно поменяли с 3% на 2% и забыли обновить код, то правка нужна в другом месте. Тогда надо оставить тест как был, а в `RefundCalculator` поменять `FEE_RATE` на `new BigDecimal("0.02")` и исправить «3%» на «2%» в Javadoc. Скажите, если нужен этот вариант, и я пришлю полный файл.