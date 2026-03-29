# Bitenex — n8n Customer Journey Workflows

> **Thư mục này chứa 8 workflow n8n** cho nền tảng Customer Journey Tracking & Automation của Bitenex.

---

## 📁 Cấu trúc thư mục

```
customer-journey/docs/n8n/
├── WORKFLOWS.md                          ← Tài liệu đầy đủ với Mermaid diagrams
├── README.md                             ← File này
├── WF-01-onboarding-first-order.json    ← Onboarding → Đơn đầu tiên
├── WF-02-abandoned-checkout-recovery.json ← Thu hồi checkout bỏ dở
├── WF-03-order-lifecycle-orchestration.json ← Vòng đời đơn hàng realtime
├── WF-04-delivered-review-reorder.json  ← Sau giao hàng → Đánh giá + Reorder
├── WF-05-driver-sla-monitor.json        ← Giám sát SLA giao hàng (Cron)
├── WF-06-payment-failure-recovery.json  ← Phục hồi thanh toán thất bại
├── WF-07-merchant-daily-analytics.json  ← Báo cáo doanh thu hàng ngày
└── WF-08-winback-lapsed-users.json      ← Win-back người dùng không hoạt động
```

---

## 🗺️ Tổng quan 8 workflows

| # | File | Trigger | Mục tiêu |
|---|------|---------|----------|
| WF-01 | `WF-01-onboarding-first-order.json` | Webhook `user.registered` | Chuyển đổi user mới → đơn đầu |
| WF-02 | `WF-02-abandoned-checkout-recovery.json` | Webhook `checkout.abandoned` | Thu hồi giỏ hàng bỏ dở |
| WF-03 | `WF-03-order-lifecycle-orchestration.json` | Webhook `order.status_changed` | Push notification theo từng trạng thái đơn |
| WF-04 | `WF-04-delivered-review-reorder.json` | Webhook `order.delivered` | Thu thập đánh giá + kích thích reorder |
| WF-05 | `WF-05-driver-sla-monitor.json` | Cron `*/5 * * * *` | Monitor SLA giao hàng, cảnh báo chậm |
| WF-06 | `WF-06-payment-failure-recovery.json` | Webhook `payment.failed` | Phục hồi thanh toán thất bại |
| WF-07 | `WF-07-merchant-daily-analytics.json` | Cron `0 8 * * *` | Báo cáo analytics cho từng merchant |
| WF-08 | `WF-08-winback-lapsed-users.json` | Cron `0 10 * * *` | Re-engage người dùng không hoạt động |

---

## 🚀 Cách import vào n8n

1. Mở n8n UI → **Workflows** → **Add Workflow**
2. Click **⋮** (menu) → **Import from File**
3. Chọn file JSON cần import
4. Cấu hình **Credentials** và **Environment Variables**
5. Kích hoạt workflow

### Environment Variables cần thiết

```bash
BITENEX_API_BASE_URL=https://api.bitenex.vn
BITENEX_INTERNAL_API_KEY=your-internal-key
BITENEX_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=SG.xxxxx
```

---

## 📖 Tài liệu đầy đủ

Xem **[WORKFLOWS.md](./WORKFLOWS.md)** để có:
- Sơ đồ Mermaid cho từng workflow
- Mô tả chi tiết nodes sử dụng
- Payload webhook mẫu
- Danh sách internal API endpoints cần implement
- Checklist triển khai

---

## ⚠️ Lưu ý trước khi bật Production

- [ ] Implement tất cả `/internal/...` endpoints trong bitenex-api
- [ ] Cấu hình HMAC webhook signature validation
- [ ] Review rate limit notification (max 3 push/ngày/user)
- [ ] Dedup events bằng `WebhookEvent` table
- [ ] Test từng workflow với payload thực
