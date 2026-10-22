Ошибка в `RefundCalculator`, а не в тесте. Javadoc прямо говорит, что 14-й день входит в бесплатное окно. `ChronoUnit.DAYS.between(1 окт, 15 окт)` возвращает 14, но условие `days < FREE_RETURN_DAYS` пропускает этот день, и с него берётся комиссия. Нужно `<=`.

src/main/java/com/shop/refund/RefundCalculator.java
```java
package com.shop.refund;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

/**
 * Calculates how much money goes back to the customer when an order is returned.
 *
 * <p>Return policy: the refund is free of charge within 14 calendar days after
 * delivery, the 14th day included. After that a fee of 3% of the paid amount is
 * kept, but not less than 50.00 and never more than the paid amount itself.
 */
public class RefundCalculator {

    static final int FREE_RETURN_DAYS = 14;
    static final BigDecimal FEE_RATE = new BigDecimal("0.03");
    static final BigDecimal MIN_FEE = new BigDecimal("50.00");

    public BigDecimal refund(BigDecimal paid, LocalDate deliveredOn, LocalDate returnedOn) {
        if (paid == null || paid.signum() < 0) {
            throw new IllegalArgumentException("paid must be non-negative");
        }
        if (returnedOn.isBefore(deliveredOn)) {
            throw new IllegalArgumentException("return before delivery");
        }
        long days = ChronoUnit.DAYS.between(deliveredOn, returnedOn);
        if (days <= FREE_RETURN_DAYS) {
            return paid.setScale(2, RoundingMode.HALF_UP);
        }
        BigDecimal fee = paid.multiply(FEE_RATE).max(MIN_FEE).min(paid);
        return paid.subtract(fee).setScale(2, RoundingMode.HALF_UP);
    }
}
```

Остальные тесты эта правка не затрагивает. На 15-й день комиссия по-прежнему составляет 150, итого 4850.00. Для 1000 срабатывает минимальная комиссия 50, итого 950.00. Для 40 комиссия ограничена суммой оплаты, итого 0.00. Значит, все 6 тестов должны пройти.