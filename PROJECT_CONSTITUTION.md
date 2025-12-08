# SDD 拍賣網站 - 專案憲章（Project Constitution）

## 版本資訊
- **建立日期**：2025 年 12 月 8 日
- **版本**：1.0
- **適用範圍**：整個 SDD 拍賣網站專案

---

## I. 程式碼品質原則

### 1.1 可讀性與可維護性
- **代碼簡潔性**：每個函數應控制在 50 行以內，每行代碼字數不超過 100 字符
- **語言統一**：整個專案採用英文編寫代碼，中文限於註釋、文檔和用戶介面
- **清晰意圖**：代碼應一目瞭然，無需過度閱讀即可理解邏輯
- **註釋規範**：
  - 複雜算法必須提供說明註釋
  - 業務邏輯需要用中文註釋解釋為什麼（why），而非做什麼（what）
  - 過時代碼應及時移除，不使用註釋掩蓋

### 1.2 模組化設計
- **單一職責原則（SRP）**
  - 每個模組、類別、函數應僅有一個改變理由
  - 避免「萬能模組」或「God Class」
  - 每個文件應該代表一個單一的概念或責任
  
- **模組獨立性**
  - 模組間應通過明確的介面進行通信
  - 最小化模組間的耦合度
  - 避免循環依賴

### 1.3 DRY 原則（勿重複自己）
- **禁止重複代碼**
  - 相同或相似代碼出現 2 次以上必須進行抽象化和重構
  - 尋找共同點並提取為通用函數或類別
  
- **重構策略**
  - 定期進行代碼審查以識別重複
  - 優先使用繼承、組合、工廠模式等設計模式
  - 建立工具類（Utilities）集中管理公共邏輯

### 1.4 命名規範
- **駝峰式命名法（Camel Case）**
  - 變數和函數：小駝峰 `myVariableName`、`getUserData()`
  - 類別和接口：大駝峰 `UserService`、`IAuthRepository`
  - 常數：全大寫 `MAX_RETRY_COUNT`、`DEFAULT_TIMEOUT`
  
- **命名原則**
  - 使用有意義的單詞，避免縮寫（除了廣泛認知的如 `id`, `url`）
  - 布爾值變數應以 `is`, `has`, `can`, `should` 開頭，如 `isActive`、`hasPermission`
  - 集合變數應使用複數形式，如 `userList`、`productItems`

### 1.5 代碼風格統一
- **使用編輯器配置**：遵循專案的 `.editorconfig` 設定
- **自動格式化**：使用 Prettier、ESLint 等工具確保風格一致
- **版本控制**：所有格式化工具配置應提交至代碼庫

---

## II. 測試標準

### 2.1 單元測試（Unit Testing）
- **覆蓋範圍**
  - 核心業務邏輯必須達到 80% 以上的代碼覆蓋率
  - 每個公開函數必須有對應的單元測試
  - 邊界情況和異常處理必須被測試
  
- **測試規範**
  - 測試文件應與源文件並存，使用 `.test.js` 或 `.spec.js` 後綴
  - 使用 AAA 模式：Arrange（準備）→ Act（執行）→ Assert（驗證）
  - 每個測試只驗證一個功能點
  - 使用有意義的測試名稱，如 `shouldReturnUserWhenValidIdProvided`

### 2.2 整合測試（Integration Testing）
- **範圍**
  - 測試模組間的協作是否正常
  - 測試與外部系統（數據庫、API）的交互
  - 測試完整的業務流程
  
- **執行標準**
  - 整合測試應在隔離的測試環境中運行
  - 使用測試數據庫或 Mock 外部服務
  - 整合測試應覆蓋主要業務路徑

### 2.3 端到端測試（E2E Testing）
- **範圍**
  - 重要用戶流程（如登錄、下單、支付）必須有 E2E 測試
  - 關鍵業務功能的完整流程驗證
  
- **工具與方法**
  - 使用 Selenium、Cypress 或 Playwright 等工具
  - 測試應涵蓋不同瀏覽器和設備

### 2.4 錯誤處理流程
- **異常捕捉**
  - 所有可能拋出異常的操作必須有 try-catch 處理
  - 不允許異常信息被無聲吞沒，必須記錄到日誌
  
- **錯誤分類**
  - 業務錯誤（Business Exception）：用戶操作引發的預期異常
  - 系統錯誤（System Exception）：系統資源或依賴服務的異常
  - 數據錯誤（Data Exception）：數據驗證或格式錯誤
  
- **錯誤恢復**
  - 提供合理的默認值或降級方案
  - 實現重試機制（帶指數退避）適用於瞬時錯誤
  - 記錄詳細的錯誤堆棧用於調試

### 2.5 日誌記錄
- **日誌等級**
  - **ERROR**：系統發生錯誤，需要立即關注
  - **WARN**：可能的問題，需要監控
  - **INFO**：重要業務事件和流程檢查點
  - **DEBUG**：開發除錯信息，不應在生產環境記錄
  
- **日誌內容**
  - 包含時間戳、日誌等級、模組名稱
  - 敏感信息（如密碼、令牌）必須被脫敏
  - 錯誤日誌應包含完整的堆棧追蹤

---

## III. 用戶體驗一致性原則

### 3.1 可預測的行為
- **一致的交互模式**
  - 相同的操作應產生相同的結果
  - UI 元件的行為應符合用戶期待
  - 避免隱藏功能或非直觀的操作流程
  
- **狀態管理**
  - 應用狀態變化應即時反映在 UI 上
  - 避免不同頁面間的狀態不一致
  - 提供明確的狀態轉換反饋

### 3.2 清晰的錯誤訊息
- **錯誤提示設計**
  - 不允許出現技術性的堆棧跟蹤給終端用戶
  - 錯誤訊息應簡潔、友好、可操作
  - 提供具體的解決方案或下一步操作建議
  
- **訊息範例**
  - ❌ 不好：`Error: Network timeout at socket.js:123`
  - ✅ 好：`連接超時。請檢查您的網絡連接，稍後重試。`
  
- **多語言支持**
  - 所有用戶訊息應支持中英文
  - 使用 i18n 框架進行國際化
  - 確保翻譯的一致性和準確性

### 3.3 響應式設計
- **設備適配**
  - 應用應在桌面、平板、手機上正常運作
  - 重要功能應在所有設備上可用
  - 遵循移動優先（Mobile-First）的設計理念
  
- **性能指標**
  - 首屏加載時間 < 3 秒
  - 交互響應時間 < 200ms
  - 離線功能應支持基本操作

### 3.4 可訪問性（Accessibility）
- **標準遵循**
  - 遵循 WCAG 2.1 Level AA 標準
  - 支持鍵盤導航
  - 提供屏幕閱讀器支持
  
- **實現方式**
  - 使用語義化 HTML 標籤
  - 為圖片提供 alt 文本
  - 確保色彩對比度符合標準

---

## IV. 效能與穩定性要求

### 4.1 效能指標（Web Vitals）
- **Core Web Vitals**
  - LCP（Largest Contentful Paint）< 2.5 秒
  - FID（First Input Delay）< 100 毫秒
  - CLS（Cumulative Layout Shift）< 0.1
  
- **其他關鍵指標**
  - TTFB（Time to First Byte）< 600 毫秒
  - DOMContentLoaded < 1.5 秒
  - 資源加載完成 < 4 秒

### 4.2 優化策略
- **前端優化**
  - 啟用 gzip 壓縮，資源大小減少 70% 以上
  - 使用代碼分割（Code Splitting）按需加載
  - 實現圖片懶加載（Lazy Loading）
  - 最小化 CSS/JS 包體積，移除未使用代碼
  - 使用內容分發網絡（CDN）加速靜態資源
  
- **後端優化**
  - 數據庫查詢應使用索引，響應時間 < 100ms
  - 實現應用層緩存（如 Redis），降低數據庫負擔
  - 使用非同步處理（Message Queue）處理耗時任務
  - 實現 API 速率限制，防止濫用
  
- **監控與分析**
  - 使用 APM 工具（如 New Relic、Datadog）監控性能
  - 建立性能基準線，定期比較
  - 設置告警，異常情況立即通知

### 4.3 穩定性保證
- **高可用性**
  - 核心服務應有冗余部署，RTO ≤ 1 小時，RPO ≤ 5 分鐘
  - 實現自動故障轉移（Failover）
  - 定期進行災難恢復演練
  
- **可靠性**
  - 關鍵數據操作必須實現事務控制
  - 重要操作應支持冪等性（Idempotency），支持安全重試
  - 實現死信隊列機制，處理失敗消息
  
- **監控告警**
  - 監控應用可用性，告警閾值 99.5% 以上
  - 監控錯誤率，告警閾值 0.1% 以上
  - 監控關鍵業務指標（如訂單成功率）

### 4.4 資安與隱私
- **數據安全**
  - 敏感數據（如密碼、支付信息）必須加密存儲
  - 傳輸層應使用 HTTPS/TLS 1.2 以上
  - 定期進行安全審計和滲透測試
  
- **用戶隱私**
  - 遵守 GDPR、隱私法規等要求
  - 收集用戶數據前必須獲得明確同意
  - 提供數據導出和刪除功能
  
- **訪問控制**
  - 實現角色型訪問控制（RBAC）
  - 重要操作需要多因素認證（MFA）
  - 定期审查和撤銷過期的訪問權限

---

## V. 技術決策治理原則

### 5.1 決策框架
當項目中出現技術爭議或需要做出重要決策時，應遵循以下流程：

```
1. 問題提出 → 2. 方案評估 → 3. 憲章對標 → 4. 集體討論 → 5. 決策記錄
```

### 5.2 評估準則
所有技術決策必須依照以下優先級進行評估：

| 優先級 | 原則 | 說明 |
|--------|------|------|
| 🔴 必須 | 與本憲章的核心原則一致 | 若違反本憲章的明確要求，不允許採納 |
| 🟡 重要 | 長期可維護性與代碼質量 | 優先選擇能提高代碼質量、便於未來維護的方案 |
| 🟢 參考 | 團隊經驗與生態成熟度 | 參考團隊熟悉度和社區支持度 |
| ⚪ 次要 | 性能與開發效率 | 在滿足上述條件下優化 |

### 5.3 爭議解決流程
1. **提出與分析**
   - 清晰闡述問題和相關背景
   - 提出至少 2 個方案並列舉各自優劣

2. **對標本憲章**
   - 逐項檢查各方案是否符合本憲章要求
   - 識別任何違反核心原則的方案，直接排除

3. **集體評審**
   - 邀請相關技術人員進行討論
   - 使用評估準則進行量化評分
   - 達成共識或按優先級多數決

4. **決策記錄**
   - 記錄最終決策、理由和評估日期
   - 存檔至專案 Wiki 或 ADR（架構決策記錄）
   - 定期審視決策的效果，必要時進行調整

### 5.4 常見爭議決策指南

| 爭議類型 | 優先考慮 | 決策原則 |
|---------|---------|---------|
| 新框架引入 | 穩定性、文檔、社區支持 | 除非能顯著提升核心指標（性能、可維護性），否則不更換 |
| 架構調整 | SRP、模組化、向後兼容 | 必須優先考慮長期可維護性 |
| 功能實現方案 | 代碼重複、測試覆蓋、性能 | 遵循 DRY 原則，優先選擇便於測試的方案 |
| 優化方向 | 實際瓶頸、成本收益比 | 基於數據驅動，優化效果 > 5% 才考慮 |

### 5.5 決策例外與升級
- **小決策**（如函數命名方式）：由相關開發者決策，在 Code Review 中反饋
- **中等決策**（如新庫的引入）：由技術負責人決策，併在團隊內溝通
- **重大決策**（如架構重構）：由項目經理與技術負責人聯合決策，報告給高層

---

## VI. 遵守與檢查

### 6.1 代碼審查（Code Review）
- 所有代碼合併至主分支前，必須至少通過 1 名審查者的審查
- 審查應對標本憲章的各項原則進行檢查
- 審查者應使用統一的反饋模板和 Checklist

### 6.2 自動化檢測
- 啟用 Linter（ESLint、Pylint 等）自動檢查代碼風格和品質
- 配置 SonarQube 或類似工具進行代碼質量分析
- 設置 CI/CD 流程，自動運行測試和檢測

### 6.3 定期審視
- **月度審視**：檢查遵守情況，識別常見違規模式
- **季度審視**：評估憲章的有效性，收集改進建議
- **年度審視**：全面評估並更新憲章，記錄版本變更

### 6.4 培訓與文檔
- 新團隊成員上手時應學習本憲章
- 定期舉辦代碼質量培訓和最佳實踐分享會
- 在項目 Wiki 中提供詳細的實施指南和代碼範例

---

## VII. 版本歷史

| 版本 | 日期 | 變更說明 |
|------|------|---------|
| 1.0 | 2025-12-08 | 初版發佈 |

---

## 附錄 A：好代碼範例

### ✅ 變數命名
```javascript
// 好的命名
const userList = [];
const isActive = true;
const MAX_RETRY_COUNT = 3;
const getUserData = async () => {};

// 不好的命名
const ul = [];
const active = true;
const max_retry = 3;
const get_user_data = async () => {};
```

### ✅ 單一職責原則
```javascript
// 好的設計：每個類負責一個職責
class UserRepository {
  async fetchUser(id) { /* 數據庫查詢 */ }
}

class UserValidator {
  validateEmail(email) { /* 驗證邏輯 */ }
}

class UserService {
  constructor(repo, validator) {
    this.repo = repo;
    this.validator = validator;
  }
  async registerUser(userData) { /* 調度 */ }
}

// 不好的設計：God Class
class UserManager {
  async fetchUser(id) { }
  validateEmail(email) { }
  registerUser(userData) { }
  sendEmail(email) { }
  logActivity(activity) { }
  // ... 20 多個其他方法
}
```

### ✅ DRY 原則
```javascript
// 好的做法：提取共同邏輯
class BaseValidator {
  validate(data, schema) {
    if (!data) throw new Error('Data is required');
    return this.validateSchema(data, schema);
  }
}

class UserValidator extends BaseValidator {
  validateEmail(email) {
    return this.validate(email, emailSchema);
  }
}

// 不好的做法：代碼重複
class UserValidator {
  validateEmail(email) {
    if (!email) throw new Error('Email is required');
    // 驗證邏輯
  }
  
  validatePhone(phone) {
    if (!phone) throw new Error('Phone is required');
    // 驗證邏輯（重複了）
  }
}
```

### ✅ 錯誤處理
```javascript
// 好的錯誤處理
async function processPayment(orderId) {
  try {
    const order = await orderService.getOrder(orderId);
    const result = await paymentGateway.charge(order.amount);
    return result;
  } catch (error) {
    logger.error('Payment failed', { 
      orderId, 
      errorCode: error.code,
      timestamp: new Date() 
    });
    
    if (error.code === 'TIMEOUT') {
      throw new BusinessException('支付超時，請稍後重試');
    }
    throw new SystemException('支付系統異常，請聯繫管理員');
  }
}

// 不好的做法
function processPayment(orderId) {
  const result = paymentGateway.charge(order.amount); // 沒有處理異常
  return result;
}
```

### ✅ 測試範例
```javascript
// 好的單元測試：使用 AAA 模式
describe('UserService.registerUser', () => {
  it('shouldReturnUserWhenValidDataProvided', async () => {
    // Arrange - 準備
    const userData = {
      email: 'user@example.com',
      password: 'SecurePassword123'
    };
    const mockRepo = createMockRepository();
    const service = new UserService(mockRepo);
    
    // Act - 執行
    const result = await service.registerUser(userData);
    
    // Assert - 驗證
    expect(result).toBeDefined();
    expect(result.id).toBeTruthy();
    expect(mockRepo.save).toHaveBeenCalledWith(expect.objectContaining({
      email: userData.email
    }));
  });
});
```

---

## 附錄 B：技術決策記錄（ADR）模板

```markdown
# ADR-001: [決策標題]

## 狀態
已決策 / 待決策 / 已修訂

## 背景
[描述問題的背景和上下文]

## 評估的方案
### 方案 A：[名稱]
- 優點：...
- 缺點：...

### 方案 B：[名稱]
- 優點：...
- 缺點：...

## 決策
選擇**方案 A**

## 對標本憲章
- 可讀性：✅ / ❌
- 單一職責：✅ / ❌
- 可測試性：✅ / ❌
- 性能：✅ / ❌

## 理由
[詳細說明決策的理由]

## 影響
- 代碼層面：...
- 性能層面：...
- 運維層面：...

## 決策日期
2025-12-08

## 評審人
- [姓名]
- [姓名]
```

---

**本憲章是整個 SDD 拍賣網站專案的指導原則。所有團隊成員在技術決策和代碼實現時應遵守本憲章的各項要求。如有疑問或改進建議，請聯繫項目技術負責人。**
