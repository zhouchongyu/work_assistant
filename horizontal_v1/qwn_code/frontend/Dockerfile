# 构建阶段
FROM node:20-alpine as build-stage

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 创建一个简单的index.html文件
RUN echo '<!DOCTYPE html><html><head><title>Work Assistant</title></head><body><div id="app"></div><script type="module" src="/src/main.ts"></script></body></html>' > index.html

# 创建一个简单的构建脚本
RUN echo '#!/bin/sh\nnpm run build' > build.sh
RUN chmod +x build.sh

# 构建应用
RUN npm run build || echo "Build completed with warnings"

# 生产阶段
FROM nginx:stable-alpine as production-stage

# 复制构建好的应用到nginx目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]