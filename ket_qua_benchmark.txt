# FixedSizeChunker Benchmark Results

- Strategy: `FixedSizeChunker(chunk_size=500, overlap=50)`
- Embedding backend: local deterministic keyword-hash embedder
- Stored chunks: 77

| # | Query | Filter | Top-1 source | Top-1 score | Top-3 sources | Top-3 relevant? | Top-1 summary |
|---|---|---|---|---:|---|---|---|
| 1 | Người mua có thể gửi yêu cầu trả hàng/hoàn tiền trong thời hạn bao lâu đối với đơn hàng thông thường? | `None` | `return-refund-request-guide.md` | 0.6999 | `return-refund-request-guide.md`, `return-refund-general-rules.md`, `return-refund-general-rules.md` | Yes | # [Trả hàng/Hoàn tiền] Hướng dẫn gửi yêu cầu Trả hàng/Hoàn tiền Khi cần yêu cầu trả hàng hoặc hoàn tiền trên Shopee, Người mua có thể gửi yêu cầu trực tiếp tại trang đơn hàng ho... |
| 2 | Nếu thanh toán bằng thẻ tín dụng hoặc thẻ ghi nợ thì tiền hoàn được gửi về đâu và mất bao lâu? | `None` | `return-refund-policy.md` | 0.4420 | `return-refund-policy.md`, `return-refund-policy.md`, `return-refund-policy.md` | Yes | trả hàng sẽ được hoàn lại cho Người mua theo Chính sách hỗ trợ phí trả hàng. - Đối với đơn hàng thanh toán bằng thẻ tín dụng hoặc thẻ ghi nợ, Shopee chỉ hỗ trợ hoàn tiền về đúng... |
| 3 | Khi đã nhận hàng nhưng hàng bị lỗi, video mở kiện hàng cần đáp ứng những yêu cầu nào? | `None` | `return-refund-evidence-guide.md` | 0.6623 | `return-refund-evidence-guide.md`, `return-refund-request-guide.md`, `return-refund-request-guide.md` | Yes | ựa trên hệ thống theo dõi đơn hàng. ## 2. Đã nhận hàng nhưng hàng có vấn đề Đối với trường hợp Người mua đã nhận hàng nhưng sản phẩm có vấn đề, chẳng hạn bị bể vỡ, sai mẫu, hàng... |
| 4 | Nếu Người mua chọn hình thức Tự sắp xếp để trả hàng thì Shopee hỗ trợ phí trả hàng như thế nào? | `None` | `return-shipping-methods-fees.md` | 0.6544 | `return-shipping-methods-fees.md`, `return-shipping-methods-fees.md`, `return-shipping-methods-fees.md` | Yes | đơn hàng hoàn trả chọn **Trả hàng tại bưu cục**, sau đó xem mục **Mã vận đơn**. ## 4. Lưu ý khi chọn hình thức Tự sắp xếp Khi chọn hình thức **Tự sắp xếp**, Người mua phải lưu l... |
| 5 | Với tài liệu có audience=seller, Người bán nên làm gì khi nhận hàng hoàn nhưng sản phẩm bị hư hỏng hoặc không đúng sản phẩm của shop? | `{'audience': 'seller'}` | `seller-warranty-policy.md` | 0.6472 | `seller-warranty-policy.md`, `seller-warranty-policy.md`, `seller-warranty-policy.md` | Yes | Người bán có thể được hỗ trợ một phần phí vận chuyển hoặc cần chịu phí theo quy định của sàn. ### 1.4. Khiếu nại hàng hoàn Nếu Người bán nhận lại hàng hoàn nhưng phát hiện sản p... |
