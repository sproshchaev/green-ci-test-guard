Проблема в граничном условии: `ChronoUnit.DAYS.between(...)` возвращает `14` в последний бесплатный день, но проверка `days < FREE_RETURN_DAYS` считает бесплатными только первые 14 значений от `0` до `13`.

Чтобы тест `fullRefundOnLastFreeDay` проходил и соответствовал политике «бесплатный возврат в течение 14 календарных дней после доставки», нужно включить 14-й день в бесплатное окно: заменить `<` на `<=`.

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

Тесты менять не нужно. После изменения ожидается:

- День 14 — возврат `5000.00`.
- День 15 — возврат `4850.00`.
- Остальные проверки сохраняют прежнее поведение.

Запусти CI повторно, чтобы подтвердить зелёный пайплайн.