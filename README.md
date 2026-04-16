# info_kchb_pwd_manager

企業內部帳號密碼管理系統，用於統一管理員工在各系統的帳號與密碼配置。

## 功能說明

- **員工管理**：記錄員工基本資料、所屬單位、職稱、到職/離職日期及在職狀態
- **系統管理**：維護公司內部各系統的名稱、網址與說明
- **帳密配置**：管理員工與各系統之間的帳號密碼對應關係，支援權限取消功能
- **防呆機制**：確保每位員工在同一系統只能擁有一組帳號

## 技術架構

- **後端框架**：Django 6.0.4
- **資料庫**：PostgreSQL（psycopg2）
- **資料處理**：pandas、openpyxl（支援 Excel 匯入匯出）
- **Python**：3.x

## 資料模型

| 模型 | 說明 |
|---|---|
| `Employee` | 員工資料表 |
| `SystemApp` | 系統資料表 |
| `Account` | 帳密配置表（核心） |

## 安裝與執行

1. 建立虛擬環境
```bash
python -m venv venv
venv\Scripts\activate
```

2. 安裝套件
```bash
pip install -r requirements.txt
```

3. 執行資料庫遷移
```bash
python manage.py migrate
```

4. 啟動開發伺服器
```bash
python manage.py runserver
```

## 注意事項

- 資料庫連線設定請參考 `config/settings.py`
- 請勿將 `.env` 或含有機密資訊的設定檔上傳至版本控制
