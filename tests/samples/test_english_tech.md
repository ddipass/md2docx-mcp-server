# Technical Documentation Test

## Overview
This document tests MD2LaTeX functionality with English technical content.

## Code Examples

### Python Code
```python
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return [x * 2 for x in self.data]
```

### JavaScript Code
```javascript
const fetchData = async (url) => {
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
    }
};
```

## Mathematical Formulas

### Algorithm Complexity
- Time Complexity: $O(n \log n)$
- Space Complexity: $O(n)$

### Statistical Formulas
Standard deviation:
$$
\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2}
$$

## System Architecture

### Components
1. **Frontend Layer**
   - React.js components
   - State management with Redux
   
2. **Backend Layer**
   - Node.js server
   - Express.js framework
   
3. **Database Layer**
   - MongoDB for document storage
   - Redis for caching

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Retrieve all users |
| POST | `/api/users` | Create new user |
| PUT | `/api/users/:id` | Update user |
| DELETE | `/api/users/:id` | Delete user |

## Performance Metrics

> **Note**: All benchmarks were conducted on a MacBook Pro M1 with 16GB RAM.

- Response time: < 100ms
- Throughput: 1000 requests/second
- Memory usage: < 512MB

## Conclusion

The MD2LaTeX tool effectively handles technical documentation with code blocks, formulas, and structured content.
