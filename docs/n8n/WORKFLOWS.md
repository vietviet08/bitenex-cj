# 🚀 Bitenex — Customer Journey Tracking & Automation Platform

> **n8n Workflow Design Document**  
> Phiên bản: 1.0 | Ngày: 2026-03-29  
> Source of Truth: bitenex-api + bitenex-user

---

## 📐 Kiến trúc tổng thể

```mermaid
graph TB
    subgraph "Bitenex Backend"
        API["FastAPI\n(bitenex-api)"]
        DB[("PostgreSQL")]
        WS["WebSocket\nRealtime"]
        API <--> DB
        API <--> WS
    end

    subgraph "n8n Automation Layer"
        WH["Webhook Triggers"]
        SCH["Scheduled Jobs"]
        LOGIC["Business Logic\n(IF / Switch / Code)"]
        WAIT["Wait / Delay Nodes"]
        WH --> LOGIC
        SCH --> LOGIC
        LOGIC --> WAIT
    end

    subgraph "Notification Channels"
        PUSH["Push Notification\n(FCM/APNs)"]
        EMAIL["Email\n(SMTP/SendGrid)"]
        SMS["SMS\n(Twilio)"]
        INAPP["In-App\n(via API)"]
    end

    subgraph "CRM / Analytics"
        SEGMENT["Customer Segments\n(Tags / Scoring)"]
        ANALYTICS["Event Tracking\n(Mixpanel / GA4)"]
        SLACK["Slack Alerts\n(Ops)"]
    end

    API --"post event webhook"--> WH
    LOGIC --> PUSH
    LOGIC --> EMAIL
    LOGIC --> SMS
    LOGIC --> API
    LOGIC --> SEGMENT
    LOGIC --> ANALYTICS
    LOGIC --> SLACK
```

---

## 🗺️ Tổng quan 8 Workflows

| # | Workflow | Trigger | Kênh | Mục tiêu |
|---|----------|---------|------|----------|
| WF-01 | Onboarding → First Order | `user.registered` | Push, Email | Chuyển đổi người dùng mới → đơn đầu tiên |
| WF-02 | Abandoned Checkout Recovery | `checkout.abandoned` | Push, Email, SMS | Thu hồi checkout bị bỏ dở |
| WF-03 | Order Lifecycle Orchestration | `order.status_changed` | Push, In-App, WebSocket | Cập nhật realtime trạng thái đơn hàng |
| WF-04 | Delivered → Review + Reorder | `order.delivered` | Push, Email | Thu thập đánh giá + kích thích reorder |
| WF-05 | Driver Dispatch SLA Monitor | `dispatch.assigned` + Cron | Slack, Push | Giám sát SLA giao hàng, cảnh báo chậm trễ |
| WF-06 | Payment Failure Recovery | `payment.failed` | Push, Email, SMS | Khôi phục thanh toán thất bại |
| WF-07 | Merchant Daily Analytics Digest | Cron 08:00 | Email, Slack | Báo cáo doanh thu hàng ngày cho merchant |
| WF-08 | Win-back Lapsed Users | Cron daily | Push, Email | Re-engage người dùng không hoạt động |

---

## WF-01: Onboarding → First Order Journey

**Mục tiêu**: Hướng dẫn người dùng mới đặt đơn hàng đầu tiên trong vòng 24 giờ.

**Trigger**: Webhook `POST /webhook/bitenex/user-registered`

```mermaid
flowchart TD
    A([🔔 Webhook\nuser.registered]) --> B[Set Variables\nuserId, email, firstName\nphone, city, platform]
    B --> C[POST /internal/events/track\nEvent: user_registered]
    C --> D[Send Welcome Email\n🎉 Chào mừng đến Bitenex!]
    D --> E[Send Welcome Push\n🍜 Khám phá món ăn yêu thích]
    E --> F[Wait 10 phút]
    F --> G{GET /internal/journeys\n/users/:id/first-order-status\nHas First Order?}
    G -- "✅ Có đơn" --> H[Track: first_order_converted\nTag User: new_converted\nEnd ✓]
    G -- "❌ Chưa có" --> I[Send Push: Welcome Nudge\n🍽️ Đặt đơn ngay - ship miễn phí!]
    I --> J[Wait 6 giờ]
    J --> K{Check First Order Again?}
    K -- "✅ Có đơn" --> L[Track: first_order_converted\nTag: converted_with_nudge\nEnd ✓]
    K -- "❌ Chưa có" --> M[POST /internal/marketing\n/issue-voucher\nVoucher: WELCOME50K]
    M --> N[Send Push + Email\n🎁 Tặng bạn voucher 50K!]
    N --> O[Wait 12 giờ]
    O --> P{Check Final?}
    P -- "✅ Có đơn" --> Q[Track: converted_with_voucher\nEnd ✓]
    P -- "❌ Không có đơn" --> R[Tag: unactivated_24h\nAdd to Segment: re-engage\nEnd ○]
```

**Nodes sử dụng**:
- `Webhook` (trigger)
- `Set` (biến)
- `HTTP Request` (gọi API)
- `Send Email` (SMTP/SendGrid)
- `Wait` (delay)
- `IF` (điều kiện)
- `Code` (transform data)
- `Slack` (tracking log)

**Payload webhook mẫu**:
```json
{
  "userId": "user_abc123",
  "firstName": "Minh",
  "email": "minh@example.com",
  "phone": "+84901234567",
  "city": "HCM",
  "platform": "ios",
  "registeredAt": "2026-03-29T05:00:00Z"
}
```

---

## WF-02: Abandoned Checkout Recovery

**Mục tiêu**: Thu hồi các checkout bị bỏ dở trước khi thanh toán.

**Trigger**: Webhook `POST /webhook/bitenex/checkout-abandoned`

```mermaid
flowchart TD
    A([🔔 Webhook\ncheckout.abandoned]) --> B[Set Variables\ncustomerId, checkoutSessionId\nmerchantName, cartValue\ncurrency, deepLink]
    B --> C[Track Event:\ncheckout_abandoned]
    C --> D{Cart Value >= 100K?}
    D -- "💰 High Value" --> E[Priority Channel:\nSMS + Push + Email]
    D -- "📦 Normal" --> F[Standard Channel:\nPush + Email]
    E --> G[Wait 30 phút]
    F --> G
    G --> H{GET /internal/journeys\n/checkouts/:id/status\nConverted?}
    H -- "✅ Đã thanh toán" --> I[Track: checkout_recovered\nEnd ✓]
    H -- "❌ Chưa thanh toán" --> J[Send Recovery Push\n🛒 Giỏ hàng chờ bạn!]
    J --> K[Send Recovery Email\nHTML template with cart items]
    K --> L[Wait 2 giờ]
    L --> M{Check Again?}
    M -- "✅ Recovered" --> N[Track: recovered_with_reminder\nEnd ✓]
    M -- "❌ Still Abandoned" --> O{First Abandonment?}
    O -- "Lần đầu" --> P[Issue: BringBack Voucher 30K\n⏰ Chỉ còn 24h!]
    O -- "Đã từng bỏ" --> Q[Issue: Smaller Voucher 15K\nDrop-frequency flag]
    P --> R[Send Final Push + SMS\n🎁 Ưu đãi đặc biệt!]
    Q --> R
    R --> S[Wait 24 giờ]
    S --> T[Tag: cart_abandoned_lost\nAdd to re-engage segment\nEnd ○]
```

**Nodes sử dụng**:
- `Webhook`, `Set`, `IF`, `Switch`
- `HTTP Request` (cart status, voucher)
- `Send Email` (HTML template)
- `Twilio` (SMS)
- `Wait`
- `Merge` (kết hợp branches)

---

## WF-03: Order Lifecycle Orchestration

**Mục tiêu**: Tự động thông báo mỗi bước trong vòng đời đơn hàng, từ PENDING → DELIVERED.

**Trigger**: Webhook `POST /webhook/bitenex/order-status-changed`

```mermaid
flowchart TD
    A([🔔 Webhook\norder.status_changed]) --> B[Set Variables\norderId, userId, merchantId\ndriverId, fromStatus, toStatus\norderNumber, total]
    B --> C{Switch: toStatus}

    C -- "CONFIRMED" --> D[Push: Đơn đã xác nhận ✅\nMerchant đang chuẩn bị]
    C -- "PREPARING" --> E[Push: Nhà hàng đang nấu 🍳\nEstimated: X phút]
    C -- "READY" --> F[Push: Sẵn sàng!\nTài xế đang đến lấy 🛵]
    C -- "PICKING_UP" --> G[Push: Tài xế đã lấy hàng\nXem tracking 📍]
    C -- "DELIVERING" --> H[Push: Đang giao đến bạn!\nThời gian dự kiến: Y phút 🚀]
    C -- "DELIVERED" --> I[Push: Đã giao thành công 🎉\nChúc ngon miệng!]
    C -- "CANCELLED" --> J[Push: Đơn hàng đã hủy ❌\nHoàn tiền trong 3-5 ngày]
    C -- "REFUNDED" --> K[Push: Hoàn tiền thành công 💸\nKiểm tra ví của bạn]

    D --> L[POST /internal/notifications/in-app\nStore notification record]
    E --> L
    F --> L
    G --> L
    H --> L
    I --> M[Track: order_delivered\nUpdate user stats\nTrigger WF-04!]
    J --> N[POST /internal/notifications/in-app\nTrack: order_cancelled]
    K --> O[POST /internal/notifications/in-app\nTrack: refund_completed]
    M --> L

    L --> P[POST /internal/events/track\nEvent with status metadata]
```

**Nodes sử dụng**:
- `Webhook`, `Set`, `Switch`
- `HTTP Request` (push + in-app notification)
- `Code` (format message theo status)
- `Execute Workflow` (trigger WF-04 khi DELIVERED)

**Payload webhook mẫu**:
```json
{
  "orderId": "ord_xyz789",
  "orderNumber": "BX-2026-001234",
  "userId": "user_abc123",
  "merchantId": "merchant_456",
  "driverId": "driver_789",
  "fromStatus": "PREPARING",
  "toStatus": "READY",
  "total": 185000,
  "currency": "VND",
  "merchantName": "Bún Chả 36",
  "changedAt": "2026-03-29T06:30:00Z"
}
```

---

## WF-04: Delivered → Review + Reorder

**Mục tiêu**: Sau giao hàng thành công, thu thập đánh giá (driver + food) và khuyến khích reorder.

**Trigger**: Webhook `POST /webhook/bitenex/order-delivered` hoặc Execute từ WF-03

```mermaid
flowchart TD
    A([🔔 order.delivered]) --> B[Set Variables\norderId, userId, merchantId\ndriverId, merchantName\norderTotal]
    B --> C[Wait 20 phút\n⏳ Cho user ăn xong]
    C --> D[Send Review Request Push\n⭐ Bạn cảm thấy thế nào?\nĐánh giá driver & nhà hàng]
    D --> E[Send Review Email\nHTML with star rating link]
    E --> F[Wait 24 giờ]
    F --> G{GET /internal/journeys\n/orders/:id/review-status}
    G -- "✅ Đã review" --> H{Rating >= 4 sao?}
    G -- "❌ Chưa review" --> I[Send Reminder Push\n📝 1 phút đánh giá\ntặng điểm thưởng!]
    I --> J[Wait 48 giờ]
    J --> K{Reviewed After Reminder?}
    K -- "✅ Yes" --> H
    K -- "❌ No" --> L[Mark: review_skipped\nEnd review loop]

    H -- "⭐ High Rating ≥4" --> M[Issue Premium Reorder Voucher 30K\n🎁 Cảm ơn bạn!]
    H -- "👎 Low Rating <4" --> N[Flag: negative_feedback\nAlert Ops Slack Channel\nEscalate if needed]
    N --> O[Send Empathy Email\n😔 Xin lỗi về trải nghiệm]

    M --> P[Wait 3 ngày]
    O --> P
    L --> P
    P --> Q{GET /internal/journeys\n/users/:id/reorder-status}
    Q -- "✅ Đã reorder" --> R[Track: reorder_success\nUpdate LTV score\nEnd ✓]
    Q -- "❌ Chưa reorder" --> S[Send Reorder Push\n🍜 Thêm lần nữa?\nCùng nhà hàng với ưu đãi]
    S --> T[End ○]
```

**Nodes sử dụng**:
- `Webhook`, `Set`, `Wait`, `IF`
- `HTTP Request` (review status, voucher API)
- `Send Email` (review request template)
- `Slack` (negative feedback alert)
- `Code` (calculate rating average)

---

## WF-05: Driver Dispatch & SLA Monitor

**Mục tiêu**: Giám sát thời gian giao hàng, cảnh báo chậm trễ, và tự động leo thang vấn đề.

**Trigger**: Webhook `POST /webhook/bitenex/dispatch-assigned` + Cron mỗi 5 phút

```mermaid
flowchart TD
    subgraph "Trigger 1: New Assignment"
        A([🔔 dispatch.assigned]) --> B[Store: orderId, driverId\nestimatedDeliveryTime\nassignedAt in DB/store]
    end

    subgraph "Trigger 2: SLA Monitor Cron"
        C([⏰ Cron: /5 phút]) --> D[HTTP Request:\nGET /internal/orders/active-deliveries]
        D --> E[Loop: Duyệt từng đơn đang giao]
        E --> F{Tính elapsed time\nelapsed > estimatedTime?}
        F -- "✅ Trong SLA" --> G[No action]
        F -- "⚠️ Trễ 10 phút" --> H[Push Alert Driver:\n⚡ Đẩy nhanh giao hàng!]
        F -- "🚨 Trễ 20 phút" --> I[Push Alert to Customer:\n⏳ Xin lỗi, đơn hơi trễ\nĐền bù voucher 20K]
        F -- "🔴 Trễ 30 phút" --> J[Slack #ops-alert:\nOrder over 30min SLA!\nAuto escalate]
        H --> K[Track: sla_warning_driver]
        I --> L[Issue Delay Voucher\nTrack: sla_compensation_sent]
        J --> M[Create Escalation Record\nAssign to Ops Team]
    end
```

**Nodes sử dụng**:
- `Webhook` (initial capture)
- `Schedule Trigger` (cron)
- `HTTP Request` (active deliveries)
- `Split In Batches` (loop orders)
- `Code` (SLA calculation)
- `IF`, `Switch` (thresholds)
- `Slack` (ops alerts)
- `Postgres` (store SLA records)

---

## WF-06: Payment Failure Recovery

**Mục tiêu**: Phục hồi thanh toán thất bại và giúp user hoàn tất đơn hàng.

**Trigger**: Webhook `POST /webhook/bitenex/payment-failed`

```mermaid
flowchart TD
    A([🔔 payment.failed]) --> B[Set Variables\npaymentId, orderId, userId\nmethod, amount, errorCode\ngateway, errorMessage]
    B --> C[Track: payment_failed\nEvent + errorCode]
    C --> D{Switch: errorCode}
    D -- "INSUFFICIENT_FUNDS" --> E[Push: Số dư không đủ 💳\nThử PTT khác nhé!]
    D -- "EXPIRED_CARD" --> F[Push: Thẻ hết hạn ⚠️\nCập nhật thẻ ngay]
    D -- "NETWORK_ERROR" --> G[Push: Lỗi kết nối 🌐\nVui lòng thử lại]
    D -- "OTHER" --> H[Push: Thanh toán thất bại\nXin thử lại]
    E --> I[Send Email: Hướng dẫn đổi PTTT\nHTTP Link to payment page]
    F --> I
    G --> I
    H --> I
    I --> J[Wait 1 giờ]
    J --> K{GET /payments/:paymentId/status\nOrder still unpaid?}
    K -- "✅ Paid" --> L[Track: payment_recovered\nEnd ✓]
    K -- "❌ Still failed" --> M{PaymentMethod = COD available?}
    M -- "Có" --> N[Offer COD Alternative\nPush + Email]
    M -- "Không" --> O[Send SMS Final Attempt\n📱 Hỗ trợ 24/7: 1800-XXXX]
    N --> P[Wait 30 phút]
    O --> P
    P --> Q{Final Check?}
    Q -- "✅ OK" --> R[Track: switched_to_cod\nEnd ✓]
    Q -- "❌ Still Fail" --> S[Cancel Order\nSend Cancellation Notification\nRefund if partially charged\nEnd ○]
```

**Nodes sử dụng**:
- `Webhook`, `Set`, `Switch`
- `HTTP Request` (payment status, cancel order)
- `Send Email`, `Twilio SMS`
- `Wait`, `IF`
- `Slack` (ops notification for failed payments)

---

## WF-07: Merchant Daily Analytics Digest

**Mục tiêu**: Gửi báo cáo doanh thu + hiệu suất hàng ngày cho từng merchant vào 8:00 sáng.

**Trigger**: Cron `0 8 * * *` (08:00 mỗi ngày)

```mermaid
flowchart TD
    A([⏰ Cron 08:00 Daily]) --> B[GET /internal/merchants/active-list]
    B --> C[Split In Batches: 10 merchants/batch]
    C --> D[Loop each Merchant]
    D --> E[GET /internal/merchants/:id/daily-stats\nParams: date=yesterday]
    E --> F[Code: Format Report\n- Total orders\n- Revenue\n- Avg rating\n- Cancelled rate\n- Top items]
    F --> G{Revenue vs Last Week?}
    G -- "📈 Tăng >10%" --> H[Add badge: 🔥 Hot Day!]
    G -- "📉 Giảm >20%" --> I[Add flag: ⚠️ Revenue Drop]
    G -- "➡️ Stable" --> J[Normal report]
    H --> K[Send Email Report\nHTML Dashboard Template]
    I --> K
    J --> K
    K --> L{Rating < 3.5 today?}
    L -- "⚠️ Low Rating" --> M[Slack #merchant-ops:\nAlert: Low rating merchant]
    L -- "✅ OK" --> N[Next Merchant]
    M --> N
    N --> O{More merchants?}
    O -- "Yes" --> D
    O -- "No" --> P[POST /internal/analytics/daily-digest-sent\nLog completion\nEnd ✓]
```

**Nodes sử dụng**:
- `Schedule Trigger` (cron)
- `HTTP Request` (active merchants, stats)
- `Split In Batches` (pagination)
- `Code` (report formatting, calculations)
- `IF`, `Switch` (thresholds)
- `Send Email` (HTML report)
- `Slack` (ops alerts)

---

## WF-08: Win-back Lapsed Users

**Mục tiêu**: Re-engage người dùng không hoạt động trong 7, 14, và 30 ngày.

**Trigger**: Cron `0 10 * * *` (10:00 sáng mỗi ngày)

```mermaid
flowchart TD
    A([⏰ Cron 10:00 Daily]) --> B[GET /internal/users/lapsed\nParams: segments=7d,14d,30d]
    B --> C[Split Users by Segment]

    C --> D["Segment: 7-day lapsed"]
    C --> E["Segment: 14-day lapsed"]
    C --> F["Segment: 30-day lapsed"]

    D --> G[Personalize: Fetch last order\nmerchant + items]
    G --> H[Push: Miss you! 🍜\nThử lại món yêu thích?\nVoucher 20K]
    H --> I[Track: winback_7d_sent]

    E --> J[Personalize: Fetch fav cuisine\nbrowsing history]
    J --> K[Email: Curated recommendations\n+ Voucher 35K]
    K --> L[Track: winback_14d_sent]

    F --> M[Full Win-back Campaign]
    M --> N[Push: Lâu rồi chưa gặp 💔\nBitenex nhớ bạn!]
    N --> O[Email: Premium Voucher 50K\n+ Free delivery 3 orders]
    O --> P[Wait 3 ngày]
    P --> Q{Did User Return?}
    Q -- "✅ Returned" --> R[Track: winback_success\nRemove from lapsed segment]
    Q -- "❌ Still Lapsed" --> S[Tag: churned_user\nReduce email frequency\nEnd ○]

    I --> T[Analytics: Winback Funnel]
    L --> T
    R --> T
```

**Nodes sử dụng**:
- `Schedule Trigger`
- `HTTP Request` (lapsed users, last orders, preferences)
- `Split In Batches`
- `Code` (personalization logic)
- `Send Email` (curated HTML)
- `IF`, `Switch`
- `Wait`
- `Merge`

---

## 🔧 Môi trường & Biến

### n8n Environment Variables

```bash
# Bitenex API
BITENEX_API_BASE_URL=https://api.bitenex.vn
BITENEX_INTERNAL_API_KEY=your-internal-key

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=SG.xxxx

# SMS
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_FROM_NUMBER=+1234567890

# Slack
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_OPS_CHANNEL=#bitenex-ops

# Analytics
MIXPANEL_TOKEN=xxx
```

### Internal API Endpoints (cần implement)

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/internal/journeys/users/:id/first-order-status` | GET | Kiểm tra đơn đầu tiên |
| `/internal/journeys/checkouts/:id/status` | GET | Trạng thái checkout |
| `/internal/journeys/orders/:id/review-status` | GET | Trạng thái review |
| `/internal/journeys/users/:id/reorder-status` | GET | Trạng thái reorder |
| `/internal/notifications/push` | POST | Gửi push notification |
| `/internal/notifications/in-app` | POST | Lưu in-app notification |
| `/internal/marketing/issue-voucher` | POST | Phát voucher |
| `/internal/events/track` | POST | Track analytics event |
| `/internal/orders/active-deliveries` | GET | Đơn đang giao |
| `/internal/merchants/active-list` | GET | Danh sách merchant |
| `/internal/merchants/:id/daily-stats` | GET | Stats ngày hôm qua |
| `/internal/users/lapsed` | GET | Users không hoạt động |

---

## 📋 Checklist Triển khai

- [ ] Deploy n8n instance (Docker recommended)
- [ ] Cấu hình tất cả Environment Variables
- [ ] Import 8 workflow JSON files
- [ ] Implement các internal endpoints trong bitenex-api
- [ ] Test từng webhook với payload mẫu
- [ ] Cấu hình Webhook URLs trong bitenex-api (publish events)
- [ ] Review retry policy & error handling
- [ ] Cấu hình rate limiting cho notification channels
- [ ] Dedup event mechanism (dùng `WebhookEvent` table)
- [ ] Monitoring: Set up n8n error alerts → Slack

---

## 🔒 Security Notes

- Tất cả webhook endpoints nên dùng **HMAC signature validation**
- Internal API dùng **API Key auth** (không expose public)
- n8n không lưu trữ payment data (PCI compliance)
- Rate limit notification: max 3 push/ngày/user
