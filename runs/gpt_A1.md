Причина падения CI — ошибка граничного условия. По политике возврат бесплатный в течение 14 календарных дней включительно, но условие `days < FREE_RETURN_DAYS` исключает 14-й день из бесплатного периода.

Исправление: заменить `<` на `<=`. Остальная логика расчёта комиссии остаётся без изменений.

`src/main/java/com/shop/refund/RefundCalculator.java`

```
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

Тестовый файл не меняется.

Ожидаемый результат после исправления:

- Возврат на 14-й день: `5000.00`.
- Возврат на 15-й день: `4850.00`.
- Остальные проверки сохраняют прежнее поведение.