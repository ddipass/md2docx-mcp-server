# 多语言代码高亮测试

本文档用于测试 MD2LaTeX 改进版的多语言代码高亮功能。

## JavaScript 代码

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
    return `Welcome, ${name}`;
}

const user = "World";
greet(user);
```

## TypeScript 代码

```typescript
interface User {
    name: string;
    age: number;
}

function createUser(name: string, age: number): User {
    return { name, age };
}

const user: User = createUser("Alice", 30);
```

## Go 代码

```go
package main

import "fmt"

func main() {
    name := "World"
    fmt.Printf("Hello, %s!\n", name)
}
```

## Rust 代码

```rust
fn main() {
    let name = "World";
    println!("Hello, {}!", name);
}

struct User {
    name: String,
    age: u32,
}
```

## Vue.js 代码

```vue
<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  }
}
</script>
```

## YAML 配置

```yaml
name: test-project
version: 1.0.0
dependencies:
  - express
  - mongoose
  - dotenv
scripts:
  start: node index.js
  test: jest
```

## JSON 数据

```json
{
  "name": "John Doe",
  "age": 30,
  "city": "New York",
  "skills": ["JavaScript", "Python", "Go"],
  "active": true
}
```

## Dockerfile

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## PowerShell 脚本

```powershell
$name = "World"
Write-Host "Hello, $name!"

Get-Process | Where-Object {$_.CPU -gt 100} | Select-Object Name, CPU
```

## Kotlin 代码

```kotlin
fun main() {
    val name = "World"
    println("Hello, $name!")
}

data class User(val name: String, val age: Int)
```

## Swift 代码

```swift
import Foundation

func greet(name: String) {
    print("Hello, \(name)!")
}

let name = "World"
greet(name: name)
```

## 测试总结

这个文档包含了多种现代编程语言的代码示例，用于验证 MD2LaTeX 改进版的语言映射功能：

- **JavaScript/TypeScript** → Java 语法高亮
- **Go/Rust** → C 语法高亮  
- **Vue.js** → HTML 语法高亮
- **YAML/JSON** → XML 语法高亮
- **Dockerfile/PowerShell** → Bash 语法高亮
- **Kotlin** → Java 语法高亮
- **Swift** → C 语法高亮

所有这些语言都应该能够正确映射并生成可编译的 LaTeX 代码。
