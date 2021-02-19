#!/sw/airflow/opt/python/airflow-env/bin/python

import sys
import os
import cx_Oracle
from contextlib import closing
from airflow.hooks.oracle_hook import OracleHook

import sql_template

batch_size = 10000
table_name = sys.argv[1]
base_column = sys.argv[2]
base_value = sys.argv[3]

def write_batch(table_name,
                rcnt,
                l
               ):
  if not os.path.exists('.tmp'):
    os.makedirs('.tmp')

  with open('.tmp/{}_{}.dat'.format(table_name,str(rcnt)),'wt') as f:
    f.write("\n".join(l)+"\n")


def get_columns(table_name,
                cur
               ):
  cur.execute(
    sql_template.get_columns.format(table_name)
  )
  rs = cur.fetchall()
  #for row in rs:
  #  print(row[0],row[1])

  return [r[0] for r in rs]


def format_columns(table_name, cur):
  cur.execute(
    sql_template.format_columns.format(table_name)
  )
  rs = cur.fetchall()

  return rs[0][0]


def merge_files(table_name, base_value):
  os.system("""\
       cat .tmp/{table_name}_*.dat > {table_name}.dat \
    && rm .tmp/{table_name}_*.dat \
    && gzip {table_name}.dat \
    && mv {table_name}.dat.gz {table_name}-{base_value}.json.gz
  """.format(
    table_name=table_name,
    base_value=base_value
  ))


def main():
  hook = OracleHook(
    oracle_conn_id='oracle_default'
  )
  with closing(hook.get_conn()) as conn:
    with closing(conn.cursor()) as cur:
      columns = get_columns(table_name, cur)
      formatted_columns = format_columns(table_name, cur)
      
      rcnt = 0
      l = []
      
      cur.execute(
        sql_template.gen_extract_sql.format(
          formatted_columns,
          table_name,
          base_column,
          base_value
        )
      )

      for row in cur.fetchall():
        rcnt = rcnt + 1
      
        r = []
        for i in range(len(columns)):
          r.append('''"{}":"{}"'''.format(columns[i], row[i])) if isinstance(row[i], str) else r.append('''"{}":{}'''.format(columns[i], row[i])) 
      
        l.append('{'+','.join(r)+'}')
      
        if rcnt % batch_size == 0:
          write_batch(table_name,rcnt,l)
          l = [] 
      
      if len(l) != 0: # final batch
        write_batch(table_name,rcnt,l)
  
  merge_files(table_name, base_value)


if __name__ == '__main__':
  main()