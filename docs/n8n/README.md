# n8n Workflow Catalog

Thư mục này chứa workflow mẫu cho Customer Journey platform.

## Nhóm workflow generic có sẵn

- `onboarding.json`
- `abandoned-cart.json`

Đây là các mẫu mang tính platform-level, dùng event schema chung của project.

## Nhóm workflow chính cho Bitenex

- `onboarding-first-order.json`
- `abandoned-checkout-recovery.json`
- `delivered-review-reorder.json`

Ba workflow này là phiên bản áp dụng trực tiếp cho journey chính của Bitenex:

1. Onboarding -> first order
2. Abandoned checkout recovery
3. Delivered -> review + reorder

## Cách hiểu đúng

- `customer-journey` là platform track event, resolve identity, chạy segment và automation.
- `workflow-n8n` là thư mục export riêng cho các workflow Bitenex cụ thể.
- `customer-journey/docs/n8n` là nơi nên đặt các workflow đã được “gắn ngữ cảnh” với customer-journey project.

## Mapping event đề xuất cho Bitenex

- `sign_up`
- `begin_checkout`
- `purchase_success`
- `order_delivered`
- `review_submitted`
- `reorder_started`

## Ghi chú triển khai

- Một số workflow Bitenex gọi endpoint nội bộ dạng journey status / voucher / notification.
- Các endpoint đó chưa nằm trong API contract MVP hiện tại, nên đang được xem như integration placeholders.
- Nếu muốn productionize, cần bổ sung hoặc proxy các endpoint nội bộ này từ Customer Journey API hoặc từ Bitenex core API.
