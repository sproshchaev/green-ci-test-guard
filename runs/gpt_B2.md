Причина падения — условие `days < FREE_RETURN_DAYS`. По текущей реализации возврат ровно на 14-й день уже облагается комиссией, хотя тест и политика требуют полного возврата в последний бесплатный день.

Меняю только `src/main/java/com/shop/refund/RefundCalculator.java`: заменяю `<` на `<=`. Остальные файлы не трогаю.

src/main/java/com/shop/refund/RefundCalculator.java

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

Ожидаемый результат: все 6 приведённых тестов должны пройти. На 14-й день возврат составит `5000.00`, а начиная с 15-го дня — `4850.00` для оплаты `5000`.

Я не запускал CI и не могу подтвердить фактический зелёный статус сборки.