Проблема в тесте `feeAfterFreeWindow`: согласно описанной политике, после 14-дневного бесплатного периода удерживается комиссия 3% от уплаченной суммы, но не менее 50.00. Для суммы `5000.00` комиссия составляет `150.00`, а возврат — `4850.00`.

Фактический результат `4850.00` соответствует бизнес-правилу. Ошибка — в ожидаемом значении теста: `4900.00`. Исправляю только тест, производственный код менять не нужно.

src/test/java/com/shop/refund/RefundCalculatorTest.java

```
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

Изменение: `4900.00` → `4850.00` в одном тесте. Остальные файлы не меняются.

Это исправляет несоответствие ожидаемого результата бизнес-правилу. Запустить CI из этого чата я не могу, поэтому успешную сборку нужно подтвердить повторным запуском тестов.