## 调用接口API

    http://fundgz.1234567.com.cn/js/[基金代码].js

### 示例
```bash
curl -s http://fundgz.1234567.com.cn/js/513560.js \
    | awk -F, '{print $4 " | " $5}'

"dwjz":"1.2631" | "gsz":"1.2598"
```
