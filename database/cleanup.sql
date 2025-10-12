SELECT *
FROM public."NUTCS_RAW"
    WHERE transfer_credit NOT IN ('NO TRANSFER -', 'NO AP CREDIT -')
        AND institution_name != 'Advanced Placement (admitted FL2025 & SP2026)';