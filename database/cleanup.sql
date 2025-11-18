SELECT
    n.*,
    i.city,
    i.state,
    i.country
FROM public."NUTCS_RAW" n
INNER JOIN institutions_detailed i
    ON n.institution_name  = i.institution_name
WHERE transfer_credit NOT IN ('NO TRANSFER -', 'NO AP CREDIT -')
    AND n.institution_name != 'Advanced Placement (admitted FL2025 & SP2026)';