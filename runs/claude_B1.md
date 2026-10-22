Причина в последнем рефакторинге: условие стало `days < 14`, и 14-й день перестал считаться бесплатным. По политике (в Javadoc и в тесте `fullRefundOnLastFreeDay`) он бесплатный, так что чиню код, а тест оставляю как есть. Нужно `<=`.

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
 * delivery. After that a fee of 3% of the paid amount is
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

Все 6 тестов должны пройти. На 14-й день будет полный возврат 5000.00, на 15-й день 4850.00. Остальные кейсы (минимальная комиссия и потолок по сумме оплаты) это изменение не затрагивает.