# -*- coding: utf-8 -*-
"""
Qrent Agent Function Calling 模块
包含房源分析、数据库查询等功能
"""

import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Any
from dotenv import find_dotenv, load_dotenv
import os

# 数据库配置
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

# 从环境变量获取数据库配置
def get_db_config():
    """获取数据库配置，优先使用单独环境变量"""
    # 优先使用单独的环境变量
    if os.getenv('DB_HOST'):
        return {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': int(os.getenv('DB_PORT', '3306'))
        }
    
    # 回退到JSON格式的DB_CONFIG
    db_config_str = os.getenv('DB_CONFIG')
    if db_config_str:
        try:
            import ast
            db_config = ast.literal_eval(db_config_str)
            return db_config
        except (ValueError, SyntaxError):
            print(f"Warning: Could not parse DB_CONFIG")
    
    # 默认配置
    return {
        'host': 'localhost',
        'database': 'property',
        'user': 'property_user',
        'password': '',
        'port': 3306
    }

DB_CONFIG = get_db_config()

# 目标分析区域
TARGET_AREAS = [
    'kingsford', 'randwick', 'kensington', 'zetland', 'waterloo',
    'eastgarden', 'mascot', 'rosebery', 'wolli-creek', 'pagewood',
    'maroubra', 'paddington', 'hillsdale', 'alexandria', 'botany'
]

def connect_to_database():
    """连接到数据库"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def extract_suburb_from_address(address1, address2):
    """从地址中提取区域名称"""
    full_address = f"{address1 or ''} {address2 or ''}".lower()
    
    for area in TARGET_AREAS:
        if area in full_address:
            return area
        area_variants = [
            area.replace('-', ' '),
            area.replace('-', ''),
            f"{area}-nsw",
            f"{area.replace('-', ' ')}-nsw",
        ]
        
        for variant in area_variants:
            if variant in full_address:
                return area
    
    return None

def categorize_room_type(bedrooms, bathrooms):
    """根据新规则分类房型"""
    try:
        bedrooms = int(float(bedrooms or 0))
        bathrooms = int(float(bathrooms or 0))
    except:
        bedrooms = 0
        bathrooms = 0
    
    if bedrooms >= 4:
        return "4室以上"
    
    return f"{bedrooms}室{bathrooms}卫"

def analyze_area_properties_function(areas: Optional[List[str]] = None, max_price: Optional[int] = None, min_price: Optional[int] = None, room_type: Optional[str] = None) -> Dict[str, Any]:
    """
    分析指定区域的房源数据 - Function Calling版本
    
    Args:
        areas: 要分析的区域列表，默认分析所有目标区域
        max_price: 最大租金过滤
        min_price: 最小租金过滤  
        room_type: 房型过滤 (如 "2室1卫", "3室2卫")
    
    Returns:
        分析结果字典
    """
    
    # 连接数据库
    connection = connect_to_database()
    if not connection:
        return {"error": "数据库连接失败"}
    
    try:
        cursor = connection.cursor()
        
        # 构建查询条件
        conditions = ["price IS NOT NULL", "bedroom_count IS NOT NULL", "bathroom_count IS NOT NULL"]
        
        if max_price:
            conditions.append(f"price <= {max_price}")
        if min_price:
            conditions.append(f"price >= {min_price}")
        
        # 获取房源数据
        query = f"""
        SELECT 
            id, price, address, region_id,
            bedroom_count, bathroom_count, parking_count,
            property_type, description_en, description_cn
        FROM properties 
        WHERE {' AND '.join(conditions)}
        """
        
        cursor.execute(query)
        raw_results = cursor.fetchall()
        
        # 手动构建字典列表
        column_names = ['id', 'pricePerWeek', 'addressLine1', 'addressLine2', 
                       'bedroomCount', 'bathroomCount', 'parkingCount',
                       'propertyType', 'description', 'descriptionCN']
        
        all_properties = []
        for row in raw_results:
            prop_dict = dict(zip(column_names, row))
            all_properties.append(prop_dict)
        
        # 按区域分类房源
        target_areas = areas if areas else TARGET_AREAS
        area_properties = defaultdict(list)
        
        for prop in all_properties:
            address1 = prop.get('addressLine1', '') or ''
            address2 = prop.get('addressLine2', '') or ''
            
            area = extract_suburb_from_address(address1, address2)
            if area and area in target_areas:
                # 应用房型过滤
                if room_type:
                    prop_room_type = categorize_room_type(prop.get('bedroomCount'), prop.get('bathroomCount'))
                    if prop_room_type != room_type:
                        continue
                
                area_properties[area].append(prop)
        
        # 分析每个区域
        analysis_results = {}
        for area_name in target_areas:
            properties = area_properties.get(area_name, [])
            analysis = analyze_single_area(area_name, properties)
            if analysis:
                analysis_results[area_name] = analysis
        
        return {
            "success": True,
            "analysis_results": analysis_results,
            "total_areas_analyzed": len(analysis_results),
            "filters_applied": {
                "areas": target_areas,
                "max_price": max_price,
                "min_price": min_price,
                "room_type": room_type
            }
        }
        
    except Error as e:
        return {"error": f"查询数据时出错: {e}"}
    
    finally:
        if connection:
            connection.close()

def analyze_single_area(area_name: str, properties: List[Dict]) -> Optional[Dict]:
    """分析单个区域的房源数据"""
    if not properties:
        return None
    
    # 按房型分组统计
    room_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        'count': 0,
        'prices': [],
        'properties': []
    })
    
    for prop in properties:
        bedrooms = prop.get('bedroomCount') or 0
        bathrooms = prop.get('bathroomCount') or 0
        price = prop.get('pricePerWeek') or 0
        
        if price > 0:
            room_type = categorize_room_type(bedrooms, bathrooms)
            room_stats[room_type]['count'] += 1
            room_stats[room_type]['prices'].append(price)
            room_stats[room_type]['properties'].append(prop)
    
    # 计算统计数据
    area_analysis = {
        'area_name': area_name,
        'total_properties': len(properties),
        'room_types': {}
    }
    
    for room_type, stats in room_stats.items():
        if stats['count'] > 0:
            prices = sorted(stats['prices'])
            analysis = {
                'count': stats['count'],
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': round(sum(prices) / len(prices)),
                'median_price': prices[len(prices)//2] if len(prices) % 2 == 1 else round((prices[len(prices)//2-1] + prices[len(prices)//2]) / 2),
                'price_range': f"{min(prices)}–{max(prices)} AUD"
            }
            
            # 计算人均租金
            if room_type == "4室以上":
                analysis['avg_per_person'] = round(analysis['avg_price'] / 4)
            elif "室" in room_type:
                try:
                    bedrooms = int(room_type.split('室')[0])
                    if bedrooms > 0:
                        analysis['avg_per_person'] = round(analysis['avg_price'] / bedrooms)
                    else:
                        analysis['avg_per_person'] = analysis['avg_price']
                except:
                    analysis['avg_per_person'] = analysis['avg_price']
            else:
                analysis['avg_per_person'] = analysis['avg_price']
            
            area_analysis['room_types'][room_type] = analysis
    
    return area_analysis

def search_properties_by_criteria(budget_min: Optional[int] = None, budget_max: Optional[int] = None, 
                                areas: Optional[List[str]] = None, bedrooms: Optional[int] = None,
                                bathrooms: Optional[int] = None, limit: int = 10) -> Dict[str, Any]:
    """
    根据条件搜索房源 - Function Calling版本
    
    Args:
        budget_min: 最小预算 (AUD/周)
        budget_max: 最大预算 (AUD/周)
        areas: 目标区域列表
        bedrooms: 卧室数量
        bathrooms: 卫生间数量
        limit: 返回结果数量限制
    
    Returns:
        符合条件的房源列表
    """
    
    connection = connect_to_database()
    if not connection:
        return {"error": "数据库连接失败"}
    
    try:
        cursor = connection.cursor()
        
        # 构建查询条件
        conditions = ["price IS NOT NULL"]
        
        if budget_min:
            conditions.append(f"price >= {budget_min}")
        if budget_max:
            conditions.append(f"price <= {budget_max}")
        if bedrooms is not None:
            conditions.append(f"bedroom_count = {bedrooms}")
        if bathrooms is not None:
            conditions.append(f"bathroom_count = {bathrooms}")
        
        query = f"""
        SELECT 
            id, price, address, region_id,
            bedroom_count, bathroom_count, parking_count,
            property_type, description_en, description_cn
        FROM properties 
        WHERE {' AND '.join(conditions)}
        ORDER BY price ASC
        LIMIT {limit}
        """
        
        cursor.execute(query)
        raw_results = cursor.fetchall()
        
        # 手动构建字典列表
        column_names = ['id', 'pricePerWeek', 'addressLine1', 'addressLine2', 
                       'bedroomCount', 'bathroomCount', 'parkingCount',
                       'propertyType', 'description', 'descriptionCN']
        
        properties = []
        for row in raw_results:
            prop_dict = dict(zip(column_names, row))
            properties.append(prop_dict)
        
        # 如果指定了区域，进行过滤
        if areas:
            filtered_properties = []
            for prop in properties:
                address1 = prop.get('addressLine1', '') or ''
                address2 = prop.get('addressLine2', '') or ''
                area = extract_suburb_from_address(address1, address2)
                if area and area in areas:
                    prop['extracted_area'] = area
                    filtered_properties.append(prop)
            properties = filtered_properties
        
        return {
            "success": True,
            "properties": properties,
            "count": len(properties),
            "search_criteria": {
                "budget_range": f"{budget_min or 0}-{budget_max or '∞'} AUD/周",
                "areas": areas or "所有区域",
                "bedrooms": bedrooms,
                "bathrooms": bathrooms
            }
        }
        
    except Error as e:
        return {"error": f"搜索房源时出错: {e}"}
    
    finally:
        if connection:
            connection.close()

# Function Calling 配置
AVAILABLE_FUNCTIONS = {
    "analyze_area_properties": {
        "function": analyze_area_properties_function,
        "description": "分析指定区域的房源数据，包括价格统计、房型分布等",
        "parameters": {
            "type": "object",
            "properties": {
                "areas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": f"要分析的区域列表，可选区域：{', '.join(TARGET_AREAS)}"
                },
                "max_price": {
                    "type": "integer",
                    "description": "最大租金过滤 (AUD/周)"
                },
                "min_price": {
                    "type": "integer", 
                    "description": "最小租金过滤 (AUD/周)"
                },
                "room_type": {
                    "type": "string",
                    "description": "房型过滤，如 '2室1卫', '3室2卫', '4室以上'"
                }
            }
        }
    },
    
    "search_properties": {
        "function": search_properties_by_criteria,
        "description": "根据预算、区域、房型等条件搜索具体房源",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_min": {
                    "type": "integer",
                    "description": "最小预算 (AUD/周)"
                },
                "budget_max": {
                    "type": "integer", 
                    "description": "最大预算 (AUD/周)"
                },
                "areas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": f"目标区域列表，可选：{', '.join(TARGET_AREAS)}"
                },
                "bedrooms": {
                    "type": "integer",
                    "description": "卧室数量"
                },
                "bathrooms": {
                    "type": "integer",
                    "description": "卫生间数量"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果数量限制，默认10",
                    "default": 10
                }
            }
        }
    }
}
