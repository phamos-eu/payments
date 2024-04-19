SELECT
  tBT.*
FROM
  `tabBank Transaction` AS tBT
WHERE
  -- Check "Bank Account" iban does not exist
  NOT EXISTS (
    SELECT
      1
    FROM
      `tabBank Account` AS tBA
    WHERE
      tBA.iban = tBT.bank_party_iban
  )

  AND tBT.docstatus != 2
  AND tBT.bank_party_iban IS NOT NULL
  GROUP BY
  -- Remove duplicate entires
  tBT.bank_party_iban
