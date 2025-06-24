import os
import sys
import pandas as pd
import mysql.connector
from mysql.connector import Error
from tqdm import tqdm
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv('.env')

host = os.getenv("DB_HOST")        
user = os.getenv("DB_USER")         
password = os.getenv("MYSQL_PROPERTY_USER_PASSWORD")
database = os.getenv("DB_DATABASE") 
port = int(os.getenv("DB_PORT", 3306)) 

def format_sql_value(val):
    if val is None or pd.isna(val):
        return "NULL"
    elif isinstance(val, (int, float)):
        return str(val)
    else:
        return "'" + str(val).replace("'", "''") + "'"

def parse_address_line2(address_line2):
    parts = address_line2.split('-')
    if len(parts) >= 3:
        nsw_index = next((i for i, part in enumerate(parts) if part.lower() == 'nsw'), -1)
        if nsw_index > 0 and nsw_index < len(parts) - 1:
            name = ' '.join(parts[:nsw_index]).lower()
            state = parts[nsw_index].upper()
            postcode = int(parts[nsw_index + 1])
            return {'name': name, 'state': state, 'postcode': postcode}
    return None

def get_or_create_region(cursor, connection, region_info):
    if not region_info:
        return None
    
    select_sql = "SELECT id FROM regions WHERE name = %s AND state = %s AND postcode = %s"
    cursor.execute(select_sql, (region_info['name'], region_info['state'], region_info['postcode']))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    insert_sql = "INSERT INTO regions (name, state, postcode) VALUES (%s, %s, %s)"
    cursor.execute(insert_sql, (region_info['name'], region_info['state'], region_info['postcode']))
    connection.commit()
    return cursor.lastrowid

def get_school_id(cursor, school_name):
    cursor.execute("SELECT id FROM schools WHERE name = %s", (school_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def push_property_data_to_db(json_file, host, user, password, database, port):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            property_data = json.load(f)
    except FileNotFoundError:
        print(f"cannot find {json_file}")
        return
    except Exception as e:
        print(f"error: {e}")
        return

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        if not connection.is_connected():
            print("cannot connect database")
            return
        cursor = connection.cursor()
        print(f"connect{database}")

        unsw_id = get_school_id(cursor, 'UNSW')
        usyd_id = get_school_id(cursor, 'USYD')
        
        if not unsw_id or not usyd_id:
            print("cannot find school")
            return

        print("clean")
        cursor.execute("DELETE FROM property_school")
        cursor.execute("DELETE FROM properties")
        connection.commit()

        successful_inserts = 0
        sql_statements = []
        
        for i, property_item in enumerate(tqdm(property_data, desc="property")):
            try:
                region_info = parse_address_line2(property_item.get('addressLine2', ''))
                region_id = get_or_create_region(cursor, connection, region_info)
                
                if not region_id:
                    print(f"property {property_item.get('houseId')}：cannot getregion")
                    continue

                property_sql = """
                INSERT INTO properties (
                    price, address, region_id, bedroom_count, bathroom_count, 
                    parking_count, property_type, house_id, available_date,
                    keywords, average_score, description_en, description_cn,
                    url, published_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                property_values = (
                    int(property_item.get('pricePerWeek', 0)),
                    property_item.get('addressLine1', ''),
                    region_id,
                    property_item.get('bedroomCount'),
                    property_item.get('bathroomCount'),
                    property_item.get('parkingCount'),
                    int(property_item.get('propertyType', 1)),
                    int(property_item.get('houseId')),
                    property_item.get('availableDate'),
                    property_item.get('keywords'),
                    property_item.get('averageScore'),
                    property_item.get('description'),
                    property_item.get('descriptionCN'),
                    property_item.get('url'),
                    property_item.get('publishedAt')
                )

                cursor.execute(property_sql, property_values)
                property_id = cursor.lastrowid

                values_str = ', '.join(format_sql_value(x) for x in property_values)
                sql_statements.append(f"INSERT INTO properties (price, address, region_id, bedroom_count, bathroom_count, parking_count, property_type, house_id, available_date, keywords, average_score, description_en, description_cn, url, published_at) VALUES ({values_str});")

                commute_unsw = property_item.get('commuteTime_UNSW')
                commute_usyd = property_item.get('commuteTime_USYD')

                if commute_unsw is not None:
                    cursor.execute(
                        "INSERT INTO property_school (property_id, school_id, commute_time) VALUES (%s, %s, %s)",
                        (property_id, unsw_id, int(commute_unsw) if commute_unsw else None)
                    )
                    sql_statements.append(f"INSERT INTO property_school (property_id, school_id, commute_time) VALUES ({property_id}, {unsw_id}, {int(commute_unsw) if commute_unsw else 'NULL'});")

                if commute_usyd is not None:
                    cursor.execute(
                        "INSERT INTO property_school (property_id, school_id, commute_time) VALUES (%s, %s, %s)",
                        (property_id, usyd_id, int(commute_usyd) if commute_usyd else None)
                    )
                    sql_statements.append(f"INSERT INTO property_school (property_id, school_id, commute_time) VALUES ({property_id}, {usyd_id}, {int(commute_usyd) if commute_usyd else 'NULL'});")

                successful_inserts += 1

                if successful_inserts % 100 == 0:
                    connection.commit()
                    print(f"finish {successful_inserts} data")

            except Exception as e:
                print(f"property {property_item.get('houseId', 'unknown')} error: {e}")
                continue

        connection.commit()
        print(f"insert {successful_inserts} property")

        sql_file = f"property_data_{datetime.now().strftime('%y%m%d_%H%M')}.sql"
        with open(sql_file, "w", encoding="utf-8") as f:
            f.write("-- Property SQL\n")
            f.write(f"-- TIME: {datetime.now()}\n")
            f.write(f"-- NUM: {successful_inserts}\n\n")
            f.write("\n".join(sql_statements))
        print(f"SQL save to {sql_file}")

        cursor.execute("SELECT COUNT(*) FROM properties")
        property_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM property_school")
        relation_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT region_id) FROM properties")
        unique_regions = cursor.fetchone()[0]

        print(f"Properties: {property_count}")
        print(f"Property-School关系: {relation_count}")
        print(f"Regions: {unique_regions}")
                
    except Error as e:
        print(f"error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL disconnected")

def push_delta_to_remote_db(csv_file, table_name, key_column, host, user, password, database, port):
    try:
        new_df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"cannot find {csv_file}")
        return
    except Exception as e:
        print(f"error: {e}")
        return

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        if not connection.is_connected():
            print("cannot connected")
            return
        cursor = connection.cursor()
        print(f"connetced {database}")

        delete_sql = f"DELETE FROM `{table_name}`"
        cursor.execute(delete_sql)
        connection.commit()
        print(f"table `{table_name}` clean")

        columns = new_df.columns.tolist()
        placeholders = ', '.join(['%s'] * len(columns))
        col_names = ', '.join([f"`{col}`" for col in columns])
        insert_sql = f"INSERT INTO `{table_name}` ({col_names}) VALUES ({placeholders})"
        
        insert_data = []
        sql_statements = []
        for index, row in new_df.iterrows():
            row_data = [None if pd.isna(x) else x for x in row]
            insert_data.append(tuple(row_data))
            values_str = ', '.join(format_sql_value(x) for x in row_data)
            sql_statements.append(f"INSERT INTO `{table_name}` ({col_names}) VALUES ({values_str});")
        
        if insert_data:
            cursor.executemany(insert_sql, insert_data)
            connection.commit()
            print(f"insert {len(insert_data)} data")
        
        sql_file = f"delta_{datetime.now().strftime('%y%m%d')}.sql"
        with open(sql_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sql_statements))
        print(f"SQL save to {sql_file}")
                
    except Error as e:
        print(f"error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL disconnectesd")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("1. 导入property JSON数据:")
        print("   python change_to_sql.py property property_data_250623.json")
        print("2. 导入CSV数据:")
        print("   python change_to_sql.py csv <csv_file> <table_name> <key_column>")
        print()
        print("示例:")
        print("   python change_to_sql.py property property_data_250623.json")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "property":
        if len(sys.argv) < 3:
            print("错误: 请指定property数据文件")
            print("使用方法: python change_to_sql.py property property_data_250623.json")
            sys.exit(1)
        
        json_file = sys.argv[2]
        print(f"开始导入property数据从文件: {json_file}")
        push_property_data_to_db(json_file, host, user, password, database, port)
        
    elif mode == "csv":
        if len(sys.argv) < 5:
            print("错误: CSV模式需要指定文件、表名和键列")
            print("使用方法: python change_to_sql.py csv <csv_file> <table_name> <key_column>")
            sys.exit(1)
        
        csv_file = sys.argv[2]
        table_name = sys.argv[3]
        key_column = sys.argv[4]
        print(f"开始导入CSV数据从文件: {csv_file} 到表: {table_name}")
        push_delta_to_remote_db(csv_file, table_name, key_column, host, user, password, database, port)
        
    else:
        print(f"错误: 未知模式 '{mode}'")
        print("支持的模式: property, csv")
        sys.exit(1)