# PocketLedger API

PocketLedger 是一个基于 FastAPI 的个人记账后端系统，支持用户认证、分类管理、收支流水和统计汇总。

## 功能

- 用户注册
- 用户登录并返回 JWT
- 当前用户信息查询
- 收入和支出分类管理
- 收支流水增删改查
- 收入、支出和余额统计
- 多用户数据隔离
- SQLite 数据库持久化
- Docker 和 Docker Compose 部署

## 本地运行

请先安装 Python 3.12 或更高版本，并在项目根目录执行以下命令。项目命令统一使用 `.venv` 虚拟环境，避免调用系统 Python。

进入项目目录：

```powershell
cd D:\another
```

创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

启动服务：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

打开接口文档：

```text
http://127.0.0.1:8000/docs
```

## 测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

当前测试结果：

```text
52 passed
```

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/auth/register` | 用户注册 |
| POST | `/auth/login` | 用户登录 |
| GET | `/users/me` | 查询当前用户 |
| GET | `/categories` | 查询分类 |
| POST | `/categories` | 创建分类 |
| PATCH | `/categories/{category_id}` | 修改分类 |
| DELETE | `/categories/{category_id}` | 删除分类 |
| GET | `/transactions` | 查询流水 |
| POST | `/transactions` | 创建流水 |
| PATCH | `/transactions/{transaction_id}` | 修改流水 |
| DELETE | `/transactions/{transaction_id}` | 删除流水 |
| GET | `/summary` | 查询统计汇总 |
| GET | `/health` | 健康检查 |

## Docker Compose

如果没有Docker Compose请先安装并启动Docker Compose。
启动：

```powershell
docker compose up --build
```

启动后打开：

```text
http://127.0.0.1:8000/docs
```

停止：

```powershell
docker compose down
```

数据库数据保存在 Docker 卷 `pocket_ledger_data` 中。

## 数据库

默认使用项目根目录下的 SQLite 数据库：

```text
pocket_ledger.db
```

Docker 环境使用：

```text
/app/data/pocket_ledger.db
```

## 认证

除 `/auth/register`、`/auth/login` 和 `/health` 外，大多数接口都需要 JWT。

在 Swagger 中点击 `Authorize`，使用：

```text
username: user@example.com
password: strong-password
```
