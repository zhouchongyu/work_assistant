# Work Assistant 前端

面向人力资源招聘场景的智能分析系统前端，采用Vue 3 + TypeScript + Element Plus + Vite的技术栈。

## 项目结构

```
frontend/
├── src/                       # 源代码目录
│   ├── api/                  # API客户端和服务
│   │   ├── http.ts          # HTTP请求配置
│   │   ├── modules/         # API模块 (auth, vendor, customer, supply, demand, chat)
│   │   └── index.ts         # API模块导出
│   ├── components/           # 公共组件
│   │   ├── LoadingSpinner.vue  # 加载指示器
│   │   └── CommonTable.vue     # 通用表格组件
│   ├── features/             # 功能模块 (待实现)
│   ├── plugins/              # 插件 (待实现)
│   ├── router/               # 路由配置
│   │   └── index.ts         # 路由定义和守卫
│   ├── stores/               # Pinia状态管理
│   │   ├── auth.ts          # 认证状态
│   │   ├── dict.ts          # 字典缓存
│   │   └── index.ts         # Store导出
│   ├── views/                # 页面视图
│   │   ├── Login.vue        # 登录页面
│   │   ├── Dashboard.vue    # 仪表板页面
│   │   ├── Profile.vue      # 个人资料页面
│   │   └── rk/              # 招聘管理页面
│   │       ├── SupplyList.vue
│   │       ├── SupplyCreate.vue
│   │       ├── SupplyEdit.vue
│   │       ├── DemandList.vue
│   │       ├── DemandCreate.vue
│   │       ├── DemandEdit.vue
│   │       ├── VendorList.vue
│   │       └── CustomerList.vue
│   ├── styles/               # 样式文件 (待实现)
│   ├── utils/                # 工具函数 (待实现)
│   ├── App.vue              # 主应用组件
│   └── main.ts              # 应用入口
├── public/                   # 静态资源 (待实现)
├── package.json             # 项目配置
├── vite.config.ts           # Vite配置
├── tsconfig.json            # TypeScript配置
└── README.md               # 项目说明
```

## 技术栈

- **前端框架**: Vue 3 + TypeScript + Vite
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由管理**: Vue Router
- **HTTP客户端**: Axios
- **构建工具**: Vite

## 快速启动

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

## API规范

- **请求路径**: `/api/v1/*` (通过Vite代理到后端)
- **认证**: 使用Bearer Token，存储在localStorage
- **响应格式**: `{ code: number, message: string, result: any }`
- **错误处理**: HTTP 200 + 业务错误码 或 HTTP状态码错误

## 功能模块

- **Auth**: 认证授权 (登录、登出、权限验证)
- **RK (Recruitment)**: 招聘管理
  - **Supply**: 简历管理 (上传、更新、分析)
  - **Demand**: 需求管理 (创建、更新、匹配)
  - **Vendor**: 供应商管理
  - **Customer**: 客户管理
- **Chat**: AI对话 (Dify集成)
- **Profile**: 个人中心

## 约束与规范

- 使用Vue 3 Composition API + TypeScript
- 组件命名采用PascalCase
- 文件命名采用kebab-case
- 使用Element Plus组件库保持UI一致性
- 使用Pinia进行状态管理
- 使用Vue Router进行路由管理
- API调用统一通过src/api模块
- 响应式设计，适配不同屏幕尺寸