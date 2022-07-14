from app.domain.payment_schema import TokenConversionRates


class TokenConversionRatesRepository:
    def fetch_by_unit(self, from_unit, to_unit, now):
        return TokenConversionRates.select(
            TokenConversionRates.conversion_rate, TokenConversionRates.id).where(
            (TokenConversionRates.conversion_from_unit == from_unit)
            & (TokenConversionRates.conversion_to_unit == to_unit)
            & (TokenConversionRates.validity_start <= now)
            & (TokenConversionRates.validity_end > now)
        ).get()
