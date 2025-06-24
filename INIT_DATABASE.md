# QRent 数据库初始化指南

## 概述

本文档描述了如何使用创建的脚本来初始化QRent应用的基础数据。

## 创建的文件

### 1. 种子脚本 (`packages/shared/prisma/seed.ts`)
- 初始化Schools表：UNSW (id: 1), USYD (id: 2)
- 从property_data_250623.json提取并初始化Regions表
- 包含完整的错误处理和进度显示

### 2. 自动化脚本 (`scripts/init-db.sh`)
- 一键完成整个数据库初始化流程
- 包括启动数据库、推送schema、生成客户端、运行种子

### 3. 说明文档 (`packages/shared/README_SEED.md`)
- 详细的使用说明和故障排除指南

## 快速开始

### 方法1：使用自动化脚本（推荐）

```bash
# 在项目根目录
pnpm init-db
```

或者直接运行：
```bash
./scripts/init-db.sh
```

### 方法2：手动步骤

```bash
# 1. 启动数据库
docker-compose up -d db

# 2. 等待数据库启动
sleep 10

# 3. 推送schema
cd packages/shared
pnpm db:push

# 4. 生成客户端
pnpm db:generate

# 5. 运行种子
pnpm db:seed
```

## 数据结构

### Schools 表
- 固定两个学校，ID为1和2
- 支持后续扩展

### Regions 表  
- 从property_data中自动提取100个唯一区域
- 包含区域名、州和邮编信息
- 按字母顺序排序，ID从1开始

## 特性

✅ **智能地址解析**：正确处理复杂地址格式如 "bardwell-valley-nsw-2207"
✅ **数据去重**：自动去除重复区域
✅ **ID重置**：每次运行都从1开始重新编号
✅ **进度显示**：实时显示数据插入进度
✅ **错误处理**：完整的错误处理和回滚机制
✅ **类型安全**：使用TypeScript确保类型安全

## 故障排除

**数据库连接失败**: 确保Docker已启动且数据库服务正在运行
**文件路径错误**: 确保在正确目录运行命令
**权限错误**: 确保脚本有执行权限 (`chmod +x scripts/init-db.sh`)

## 使用后验证

### 方法1：使用命令行快速验证
```bash
# 查看数据数量
docker-compose exec db mysql -u root -p1234 -e "USE qrent; SELECT COUNT(*) as schools FROM schools; SELECT COUNT(*) as regions FROM regions;"

# 查看schools表数据
docker-compose exec db mysql -u root -p1234 -e "USE qrent; SELECT * FROM schools;"

# 查看regions表前10条数据
docker-compose exec db mysql -u root -p1234 -e "USE qrent; SELECT * FROM regions LIMIT 10;"
```

### 方法2：进入MySQL客户端查看
```bash
# 进入MySQL客户端
docker-compose exec db mysql -u root -p1234 qrent

# 然后在MySQL中运行SQL命令（注意：不要输入中文）
SELECT COUNT(*) FROM schools;    -- 应该返回 2
SELECT COUNT(*) FROM regions;    -- 应该返回 100
SELECT * FROM schools ORDER BY id;
SELECT * FROM regions ORDER BY name LIMIT 10;

# 退出MySQL
exit
```

### ✅ 期望的验证结果

**Schools表**:
```
+----+------+
| id | name |
+----+------+
|  1 | UNSW |
|  2 | USYD |
+----+------+
```

**Regions表（前5条）**:
```
+----+------------+-------+----------+
| id | name       | state | postcode |
+----+------------+-------+----------+
|  1 | abbotsford | NSW   |     2046 |
|  2 | alexandria | NSW   |     2015 |
|  3 | allawah    | NSW   |     2218 |
|  4 | annandale  | NSW   |     2038 |
|  5 | arncliffe  | NSW   |     2205 |
+----+------------+-------+----------+
```

## 🚀 完整运行流程总结

### 一键运行（推荐）
```bash
# 1. 确保在项目根目录
cd /Users/zach/rent/qrent

# 2. 启动数据库
docker-compose up -d db

# 3. 运行数据库初始化（包含schema推送和种子数据）
cd packages/shared && DATABASE_URL="mysql://root:1234@localhost:3306/qrent" npx tsx prisma/seed.ts

# 4. 验证结果
cd /Users/zach/rent/qrent && docker-compose exec db mysql -u root -p1234 -e "USE qrent; SELECT * FROM schools; SELECT COUNT(*) FROM regions;"
```

### 常见问题解决

**问题1**: `zsh: command not found: SELECT`
- **原因**: 在终端中直接输入SQL命令
- **解决**: 使用 `docker-compose exec db mysql...` 或先进入MySQL客户端

**问题2**: `Can't reach database server at db:3306`
- **原因**: 使用了Docker内部网络地址
- **解决**: 使用 `DATABASE_URL="mysql://root:1234@localhost:3306/qrent"`

**问题3**: 表结构存在但没有数据
- **原因**: 只推送了schema，没有运行seed
- **解决**: 运行 `DATABASE_URL="mysql://root:1234@localhost:3306/qrent" npx tsx prisma/seed.ts`

## 🎉 成功标志

当您看到以下输出时，说明初始化成功：
- Schools表有2条记录（UNSW, USYD）
- Regions表有100条记录
- 所有ID从1开始按顺序排列
- Regions按字母顺序排序
