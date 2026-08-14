# PocketLedger API

PocketLedger 是一个基于 FastAPI 的个人记账后端系统，提供用户认证、分类管理、收支流水和统计汇总功能。

## 功能

- 用户注册、OAuth2 登录和 JWT 认证
- 收入、支出分类管理
- 收支流水增删改查
- 收入、支出和余额统计
- 多用户数据隔离
- SQLite 数据持久化
- pytest 自动化测试
- Docker Compose 容器化配置

## 一、从 GitHub 获取项目

### 前置环境

本地运行需要：

- Git
- Python 3.12 或更高版本

检查安装结果：

```powershell
git --version
python --version
```

克隆仓库并进入项目目录：

```powershell
git clone https://github.com/konijiwas/pocket-ledger-api.git
cd pocket-ledger-api
```

如果仓库是 Private，当前 GitHub 账号必须拥有访问权限。

## 二、Windows 本地运行（推荐开发使用）

以下命令都需要在项目根目录执行。

### 1. 创建虚拟环境

```powershell
python -m venv .venv
```

### 2. 安装依赖

使用项目虚拟环境中的 Python，避免误用系统 Python：

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. 启动服务

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

启动成功后打开：

- Swagger 接口文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>

健康检查预期返回：

```json
{
  "status": "ok",
  "environment": "development"
}
```

### 4. 首次使用

项目默认使用 SQLite。首次启动时，如果根目录没有 `pocket_ledger.db`，应用会自动创建数据库和数据表。

建议在 Swagger 中按以下顺序体验：

1. 执行 `POST /auth/register` 注册用户。
2. 点击右上角 `Authorize`，使用注册邮箱和密码登录。
3. 执行 `POST /categories` 创建收入或支出分类。
4. 执行 `POST /transactions` 创建流水。
5. 执行 `GET /summary` 查看统计结果。

项目不会预置账号或示例数据。

### 5. 运行测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

当前验证结果：

```text
52 passed, 1 warning
```

### 6. 停止服务

在运行 Uvicorn 的终端中按：

```text
Ctrl + C
```

## 三、Linux 和 macOS 本地运行

```bash
git clone https://github.com/konijiwas/pocket-ledger-api.git
cd pocket-ledger-api
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m uvicorn app.main:app --reload
```

运行测试：

```bash
./.venv/bin/python -m pytest -q
```

## 四、Docker Compose 运行

Docker 方式不需要手动创建 Python 虚拟环境，但需要提前安装并启动 Docker Desktop。

检查 Docker：

```powershell
docker --version
docker compose version
```

在项目根目录启动：

```powershell
docker compose up --build
```

启动成功后打开：

<http://127.0.0.1:8000/docs>

停止容器：

```powershell
docker compose down
```

Docker Compose 使用 `pocket_ledger_data` 数据卷保存 SQLite 数据。删除容器不会自动删除该数据卷。

> 如果提示无法识别 `docker`，说明 Docker Desktop 未安装、未启动，或者安装后尚未重新打开终端。

## 五、主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/auth/register` | 用户注册 |
| POST | `/auth/login` | 用户登录并返回 JWT |
| GET | `/users/me` | 查询当前用户 |
| GET | `/categories` | 查询分类 |
| POST | `/categories` | 创建分类 |
| PATCH | `/categories/{category_id}` | 修改分类 |
| DELETE | `/categories/{category_id}` | 删除分类 |
| GET | `/transactions` | 查询流水 |
| POST | `/transactions` | 创建流水 |
| PATCH | `/transactions/{transaction_id}` | 修改流水 |
| DELETE | `/transactions/{transaction_id}` | 删除流水 |
| GET | `/summary` | 查询收入、支出和余额 |
| GET | `/health` | 健康检查 |

## 六、项目结构

```text
app/
├── main.py                    # FastAPI 应用入口和路由注册
├── api/
│   ├── deps.py                # JWT 认证依赖
│   └── routes/                # 认证、用户、分类、流水和统计接口
├── core/                      # 配置、密码哈希和 JWT
├── db/                        # 数据库连接和 ORM 基类
├── models/                    # SQLAlchemy 数据模型
└── schemas/                   # Pydantic 请求和响应模型
tests/                         # 自动化测试
Dockerfile                     # Docker 镜像配置
docker-compose.yml             # Docker Compose 配置
requirements.txt               # Python 依赖
```

## 七、数据库与环境配置

本地默认数据库：

```text
sqlite:///./pocket_ledger.db
```

可以在项目根目录创建 `.env` 覆盖配置：

```text
APP_ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./pocket_ledger.db
JWT_SECRET_KEY=请替换为随机且足够长的密钥
```

不要将真实 `.env`、JWT 密钥或本地数据库提交到 GitHub。项目的 `.gitignore` 已忽略这些文件。

## 八、常见问题

### `No module named uvicorn`

通常是使用了系统 Python，或依赖尚未安装。请执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 端口 8000 已被占用

先在旧服务器终端按 `Ctrl + C`，或者换端口启动：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

然后访问：

<http://127.0.0.1:8001/docs>

### PowerShell 禁止运行激活脚本

本 README 使用 `.venv\Scripts\python.exe` 的完整路径，不要求运行 `Activate.ps1`，通常不会受到虚拟环境激活脚本策略的影响。

## 九、技术栈

- Python 3.12+
- FastAPI / Uvicorn
- SQLAlchemy 2.0
- Pydantic / Pydantic Settings
- OAuth2 / JWT
- pwdlib / Argon2
- SQLite
- pytest
- Docker Compose
