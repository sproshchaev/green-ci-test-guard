Ошибка в коде, а не в тесте. Политика в Javadoc говорит, что возврат бесплатный в течение 14 дней после доставки, **14-й день включительно**. При возврате на 14-й день `ChronoUnit.DAYS.between` возвращает `14`. Условие `days < FREE_RETURN_DAYS` даёт `false`, и комиссия ошибочно удерживается. Нужно нестрогое сравнение `<=`.

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

Остальные тесты эта правка не затрагивает. На 3-й день по-прежнему полный возврат. На 15-й день удерживается комиссия 3%, и получается `4850.00`. На 20-й и 30-й день работают минимальная комиссия и ограничение суммой оплаты. Возврат раньше даты доставки всё так же отклоняется.