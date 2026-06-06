# 数据库持久化系统

## 概述

为家电超市管理系统实现了完整的数据库持久化解决方案，确保所有数据修改都能被正确保存，并在应用重启后保持数据完整性。

## 功能特性

### 1. 自动数据保存
- **防抖保存机制**: 使用 500ms 延迟的防抖策略，避免频繁写入
- **页面卸载强制保存**: 在 `beforeunload` 事件中强制保存所有未保存的更改
- **实时持久化**: 所有数据修改立即写入 localStorage

### 2. 数据完整性保障
- **自动备份**: 数据库初始化前自动创建备份
- **损坏恢复**: 如果数据库损坏，自动从备份恢复
- **结构验证**: 确保所有表结构完整
- **大小警告**: 数据接近 localStorage 限制 (5MB) 时发出警告

### 3. 版本管理
- **数据库版本**: 支持数据库版本管理和升级
- **向后兼容**: 旧版本数据库自动升级到新版本
- **结构迁移**: 确保数据结构完整性

### 4. 高级功能
- **数据导出**: 支持将完整数据库导出为 JSON 文件
- **数据导入**: 支持从 JSON 文件导入数据
- **手动备份**: 用户可以随时创建备份
- **备份恢复**: 从历史备份恢复数据
- **数据库重置**: 重置到初始状态

### 5. 多标签页同步
- **Storage 事件监听**: 监听其他标签页的数据库更新
- **跨标签页同步**: 所有标签页数据保持一致

### 6. 完整的错误处理
- **操作重试**: 失败操作的重试机制
- **友好提示**: 用户友好的错误信息
- **日志记录**: 详细的错误日志

## API 接口

### 基础操作
```javascript
import {
  getDB,           // 获取完整数据库
  saveDB,          // 同步保存数据库
  saveDBAsync,     // 异步防抖保存
  getTable,        // 获取指定表
  saveTable,       // 同步保存表
  saveTableAsync,  // 异步保存表
  updateRecord,    // 更新单条记录
  addRecord,       // 添加记录
  deleteRecord     // 删除记录
} from '../utils/database.js';
```

### 高级操作
```javascript
import {
  initDB,          // 初始化数据库
  createBackup,    // 创建备份
  restoreFromBackup, // 从备份恢复
  exportDatabase,  // 导出数据库
  importDatabase,  // 导入数据库
  clearDatabase,   // 重置数据库
  getDatabaseStatus // 获取数据库状态
} from '../utils/database.js';
```

## 数据表

系统包含以下数据表：
- `users` - 用户账户
- `customers` - 客户信息
- `products` - 商品信息
- `suppliers` - 供应商信息
- `sales_orders` - 销售订单
- `sales_order_items` - 销售订单明细
- `purchase_orders` - 采购订单
- `purchase_order_items` - 采购订单明细
- `inventory_logs` - 库存变更日志
- `financial_records` - 财务记录
- `product_edit_logs` - 商品编辑日志
- `operation_logs` - 系统操作日志

## 数据库管理页面

### 功能
1. **状态展示**: 显示数据库版本、大小、各表记录数
2. **备份管理**: 创建和恢复备份
3. **数据导入/导出**: 数据迁移功能
4. **数据库重置**: 重置到初始状态
5. **操作日志**: 查看系统操作历史

### 访问权限
仅管理员用户可访问数据库管理页面 (`/database`)

## 使用示例

### 创建订单后自动保存
```javascript
// 在 mockApi.js 中，所有操作已自动持久化
const newOrder = { order_id: 'SO-001', ... };
saveTable('sales_orders', [...orders, newOrder]);
```

### 从备份恢复
```javascript
await ElMessageBox.confirm('确定要恢复吗？');
await restoreFromBackup();
```

### 导出数据
```javascript
const data = exportDatabase();
// 下载为 JSON 文件
```

## 数据安全

1. **备份机制**: 自动和手动备份双重保障
2. **导入验证**: 导入前验证数据格式
3. **权限控制**: 敏感操作仅管理员可执行
4. **二次确认**: 危险操作需要用户确认

## 性能优化

1. **防抖保存**: 减少频繁的 localStorage 写入
2. **按需加载**: 只在需要时读取数据
3. **增量更新**: 支持单条记录更新

## 浏览器兼容性

- Chrome (推荐)
- Firefox
- Safari
- Edge

所有主流现代浏览器都支持 localStorage API。
