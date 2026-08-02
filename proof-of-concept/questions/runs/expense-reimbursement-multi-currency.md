# expense-reimbursement-multi-currency

Spec: Add a feature that calculates the total reimbursement amount for a batch of submitted expenses, where expenses can be in different currencies.


## Pre-registered ambiguities (ground truth)

- **[Domain Expert]** Which currency the total should be reported in.

- **[Backend Developer]** Which exchange rate to use and when it's locked in (rate at submission time, at approval time, a fixed daily rate, or live) and the rounding rule — each produces a materially different total.

- **[Release Manager]** What happens if the exchange-rate source is unavailable when the batch is calculated — fail the whole batch, fall back to a last-known rate, or exclude that expense.


## Silent baseline (no permission to ask) — verdict: unparsed


### Implementation Plan

#### Approach
To implement the feature that calculates the total reimbursement amount for a batch of submitted expenses in different currencies, we will follow these steps:

1. **Currency Conversion Service**: Integrate a currency conversion service to convert all expenses to a single base currency (e.g., USD).
2. **Expense Data Model**: Update the expense data model to include currency information.
3. **Reimbursement Calculation API**: Develop an API endpoint that calculates the total reimbursement amount.
4. **Error Handling and Edge Cases**: Implement robust error handling and consider edge cases such as invalid currency codes or conversion failures.

#### Data/API Changes

1. **Expense Data Model Update**:
   - Add a `currency` field to the `Expense` model to store the currency code (e.g., USD, EUR).
   - Ensure the `amount` field is a numeric type representing the expense amount in the specified currency.

   ```python
   class Expense(models.Model):
       amount = models.DecimalField(max_digits=10, decimal_places=2)
       currency = models.CharField(max_length=3)
       # other fields...
   ```

2. **Currency Conversion Service Integration**:
   - Use an external currency conversion API (e.g., Open Exchange Rates, CurrencyLayer) to fetch real-time exchange rates.
   - Implement a service class to handle currency conversion.

   ```python
   import requests

   class CurrencyConverter:
       API_KEY = 'your_api_key_here'
       BASE_URL = 'https://openexchangerates.org/api/latest.json'

       def convert(self, amount, from_currency, to_currency):
           response = requests.get(self.BASE_URL, params={'app_id': self.API_KEY, 'base': from_currency})
           if response.status_code != 200:
               raise Exception("Currency conversion failed")
           rates = response.json().get('rates', {})
           conversion_rate = rates.get(to_currency)
           if not conversion_rate:
               raise Exception("Invalid currency code")
           return amount * conversion_rate
   ```

3. **Reimbursement Calculation API**:
   - Develop an API endpoint that aggregates all expenses, converts them to the base currency, and calculates the total reimbursement amount.

   ```python
   from rest_framework.views import APIView
   from rest_framework.response import Response
   from rest_framework import status
   from .models import Expense
   from .currency_converter import CurrencyConverter

   class ReimbursementCalculator


## Generalist, question-enabled — verdict: asked (4 question(s))


QUESTION: How should the system handle currency conversion? Should it use real-time exchange rates or a fixed exchange rate? The answer will affect the accuracy and consistency of the reimbursement amounts.

QUESTION: What should be the process for determining the base currency for conversion? Should it be a default currency set by the system, or should it be configurable by the user or an admin? The answer will impact how the reimbursement amounts are calculated and presented.

QUESTION: How should the system handle exchange rate fluctuations? Should it recalculate the reimbursement amounts periodically, or should it lock the exchange rate at the time of submission? The answer will determine the user's perception of fairness and the system's administrative overhead.

QUESTION: What should be the rounding policy for the reimbursement amounts after conversion? Should it round to the nearest whole number, or should it allow for fractional cents? The answer will affect the precision of the financial transactions and the user's satisfaction with the system.


## Role panel, question-enabled


### Architect — verdict: proceeded (0 question(s))


PROCEEDING: I plan to calculate the total reimbursement amount by summing up the converted values of each expense to a single currency, using the current exchange rates. However, I need to know which currency to convert to and where to obtain the current exchange rates.


### Backend Developer — verdict: proceeded (0 question(s))


PROCEEDING: I plan to calculate the total reimbursement amount by summing up the amounts of the expenses in their respective currencies and then converting the total to a single currency (e.g., the company's base currency) using the latest exchange rates, which will be fetched from a reliable API.

Note: The specific currency to which the total should be converted and the source of the exchange rates need to be clarified.


### Security Reviewer — verdict: proceeded (0 question(s))


PROCEEDING: I plan to calculate the total reimbursement amount by first converting all expenses to a single currency (e.g., the company's base currency) using current exchange rates, and then summing them up. We will need to determine the source currency for each expense and the method for obtaining exchange rates (e.g., using a public API or a fixed rate list).


### Release Manager — verdict: proceeded (0 question(s))


PROCEEDING: I plan to calculate the total reimbursement amount by summing up the expenses in their original currencies and then converting the total to a single currency (e.g., the company's base currency) using the latest exchange rates. However, I will need to know the base currency and the source of the exchange rates to ensure the calculation is accurate.


### Performance Reviewer — verdict: proceeded (0 question(s))


PROCEEDING: I plan to calculate the total reimbursement amount by summing up the converted values of each expense to a single currency, using the current exchange rates. However, we need to clarify which currency to convert to and how to handle cases where exchange rates are not available or outdated.


### Domain Expert — verdict: proceeded (0 question(s))


PROCEEDING: I plan to calculate the total reimbursement amount by summing up the converted values of each expense to a single currency, using the current exchange rates. However, I will need to know which currency to convert to and how to handle expenses without valid exchange rates.
