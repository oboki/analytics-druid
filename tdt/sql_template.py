get_columns = """\
SELECT COLUMN_NAME
     , DATA_TYPE
  FROM ALL_TAB_COLUMNS
 WHERE TABLE_NAME = UPPER('{}')
   AND OWNER = 'EDWADM'
 ORDER BY COLUMN_ID
"""

format_columns = """\
SELECT REPLACE(
         LISTAGG(COLUMN_NAME, ',') WITHIN GROUP (ORDER BY COLUMN_ID),
         ',', ','||CHR(10)||CHR(13)
       ) AS Q
  FROM (SELECT CASE WHEN SUBSTR(DATA_TYPE, 1, 9) = 'TIMESTAMP' THEN 'TO_CHAR('||COLUMN_NAME||',''YYYY-MM-DD HH24:MI:SS'')'
                                                               ELSE COLUMN_NAME
               END AS COLUMN_NAME
             , COLUMN_ID
          FROM ALL_TAB_COLUMNS
         WHERE TABLE_NAME = UPPER('{}') AND OWNER = 'EDWADM'
       ) a
"""

gen_extract_sql = """\
SELECT {}
  FROM {}
 WHERE {} = '{}'
"""