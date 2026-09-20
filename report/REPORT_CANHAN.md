# Báo Cáo Cá Nhân - Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> Phần nhóm nộp chung trong `REPORT_NHOM.md`. Báo cáo này ghi phần cá nhân: hướng tiếp cận, chiến lược chunking riêng, kết quả test, dự đoán similarity và kết quả retrieval.

---

## 1. Khởi động (Warm-up) - Cá nhân

### Độ tương tự Cosine

**Độ tương tự cosine cao nghĩa là gì?**
> Hai đoạn văn bản có cosine similarity cao thường có ý nghĩa gần nhau hoặc cùng nói về một chủ đề, dù cách diễn đạt có thể khác nhau.

**Ví dụ có độ tương tự cao:**
- Câu A: Người mua có thể gửi yêu cầu trả hàng nếu sản phẩm bị lỗi.
- Câu B: Khách hàng được phép yêu cầu hoàn tiền khi hàng nhận được không hoạt động.
- Tại sao tương đồng: Cả hai câu đều nói về quyền yêu cầu xử lý khi sản phẩm có vấn đề.

**Ví dụ có độ tương tự thấp:**
- Câu A: Shopee hoàn tiền qua Ví ShopeePay trong 24 giờ.
- Câu B: Người bán cần tối ưu hình ảnh sản phẩm để tăng lượt xem.
- Tại sao khác: Hai câu nói về hai nghiệp vụ khác nhau, một câu về hoàn tiền, một câu về tối ưu bán hàng.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, tức là mức độ giống nhau về ý nghĩa, thay vì bị ảnh hưởng mạnh bởi độ lớn vector. Điều này phù hợp với text embeddings vì hai câu có thể dài ngắn khác nhau nhưng vẫn cùng ý nghĩa.

### Bài toán tính toán Chunking

**Tài liệu 10,000 ký tự, `chunk_size=500`, `overlap=50`:**
> Công thức: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23 chunks`.

**Nếu overlap tăng lên 100:**
> Công thức: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks`. Số chunk tăng vì bước nhảy giữa hai chunk nhỏ hơn. Overlap lớn hơn giúp giữ ngữ cảnh tốt hơn ở ranh giới chunk, nhưng làm tăng số lượng chunk và chi phí lưu trữ/tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach)

### Chiến lược chunking cá nhân

**Chiến lược tôi chọn:** `FixedSizeChunker`

**Tham số dự kiến:**
- `chunk_size=500`
- `overlap=50`

**Lý do chọn:**
> Tôi chọn `FixedSizeChunker` vì đây là chiến lược đơn giản, dễ kiểm soát và phù hợp để làm baseline cá nhân khi so sánh với các chiến lược khác trong nhóm. Với bộ tài liệu chính sách Shopee, các đoạn văn thường dài và chứa nhiều thông tin cụ thể như thời hạn, điều kiện, phí và phương thức xử lý; chia theo kích thước cố định giúp các chunk có độ dài ổn định để đưa vào embedding và tìm kiếm.

**Điểm mạnh:**
> Chiến lược này dễ triển khai, dễ tái lập kết quả và không phụ thuộc quá nhiều vào cấu trúc văn bản đầu vào. Overlap giúp hạn chế mất thông tin ở ranh giới giữa hai chunk.

**Điểm yếu:**
> Fixed-size chunking có thể cắt ngang câu, bảng hoặc một mục chính sách. Điều này có thể làm một số chunk thiếu mạch lạc so với các chiến lược chia theo câu hoặc chia theo heading.

### Các hàm chia nhỏ

**`SentenceChunker.chunk`:**
> Tách văn bản theo ranh giới câu bằng regex, sau đó gom một số câu liên tiếp vào cùng một chunk theo `max_sentences_per_chunk`. Cách này giúp chunk dễ đọc hơn vì ít cắt ngang câu.

**`RecursiveChunker.chunk` / `_split`:**
> Thử tách văn bản theo các separator từ lớn đến nhỏ, ví dụ đoạn, dòng, câu hoặc khoảng trắng. Nếu một đoạn vẫn quá dài, hàm tiếp tục tách đệ quy cho đến khi đạt kích thước phù hợp hoặc phải fallback sang cắt theo kích thước.

### Lớp EmbeddingStore

**`add_documents` + `search`:**
> Mỗi tài liệu được embed thành vector và lưu cùng `id`, `content`, `metadata`. Khi tìm kiếm, query cũng được embed rồi so sánh với các vector đã lưu, sau đó sắp xếp theo điểm tương đồng giảm dần.

**`search_with_filter` + `delete_document`:**
> `search_with_filter` lọc tài liệu theo metadata trước, sau đó mới tìm kiếm trên tập đã lọc. `delete_document` xóa các record có `metadata["doc_id"]` trùng với tài liệu cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer`:**
> Agent nhận câu hỏi, truy xuất top-k chunk liên quan từ vector store, ghép các chunk này thành phần ngữ cảnh, rồi tạo prompt cho LLM. Câu trả lời cần dựa trên ngữ cảnh được truy xuất thay vì suy đoán ngoài tài liệu.

---

## 3. Hoàn thiện code (Core Implementation)

### Kết quả kiểm thử

```text
python -m pytest tests/ -v

42 passed
```

**Số lượng bài test vượt qua:** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---|---|
| 1 | Người mua cần chuẩn bị video mở kiện hàng. | Shopee yêu cầu bằng chứng rõ ràng khi khiếu nại. | cao | 0.78 | Đúng |
| 2 | Tiền hoàn qua ShopeePay trong 24 giờ. | Thẻ tín dụng có thể mất 7-14 ngày để hoàn tiền. | trung bình | 0.55 | Đúng |
| 3 | Người mua theo dõi trả hàng trong mục Thông báo. | Người bán tối ưu tiêu đề sản phẩm. | thấp | 0.12 | Đúng |
| 4 | Trả hàng tại bưu cục được miễn phí. | Đơn vị vận chuyển đến lấy hàng cũng miễn phí. | cao | 0.85 | Đúng |
| 5 | Hàng giả cần bằng chứng như QR hoặc số seri. | Thực phẩm tươi sống có thời hạn khiếu nại 24 giờ. | thấp | 0.23 | Đúng |

**Kết quả nào bất ngờ nhất?**
> Kết quả cặp 2 khá bất ngờ vì mặc dù là 2 phương thức hoàn tiền khác nhau nhưng mô hình vẫn nhận ra ngữ cảnh chung về thời gian hoàn tiền nên điểm ở mức trung bình chứ không bị quá thấp.

---

## 5. Kết quả truy xuất của tôi (Competition Results)

Tôi sử dụng chiến lược `FixedSizeChunker` với `chunk_size=500` và `overlap=50` để chia tài liệu, sau đó chạy cùng 5 câu hỏi benchmark của nhóm. Chiến lược này được dùng làm baseline cá nhân để so sánh với các thành viên dùng `SentenceChunker`, `RecursiveChunker` hoặc chunking theo heading.

Lệnh benchmark đã chạy:

```powershell
.\.venv\Scripts\python.exe bench.py
```

Kết quả chi tiết được lưu tại `report/fixed_size_benchmark_results.md`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---:|---|---|
| 1 | Người mua có thể gửi yêu cầu trả hàng/hoàn tiền trong thời hạn bao lâu đối với đơn hàng thông thường? | Top-1 lấy từ `return-refund-request-guide.md`; tài liệu chứa gold answer `return-refund-general-rules.md` xuất hiện trong top-3. | 0.6999 | Có | Đơn hàng thông thường có thời hạn gửi yêu cầu trong vòng 15 ngày kể từ khi giao hàng thành công. |
| 2 | Nếu thanh toán bằng thẻ tín dụng hoặc thẻ ghi nợ thì tiền hoàn được gửi về đâu và mất bao lâu? | Top-1 lấy từ `return-refund-policy.md`, đúng tài liệu về kênh và thời gian hoàn tiền. | 0.4420 | Có | Tiền hoàn về đúng thẻ tín dụng/ghi nợ đã dùng thanh toán, thường mất 7 - 14 ngày làm việc tùy ngân hàng. |
| 3 | Khi đã nhận hàng nhưng hàng bị lỗi, video mở kiện hàng cần đáp ứng những yêu cầu nào? | Top-1 lấy từ `return-refund-evidence-guide.md`, đúng tài liệu hướng dẫn bằng chứng. | 0.6623 | Có | Video cần quay liên tục, rõ nét, không cắt ghép, thấy mã vận đơn, 6 mặt kiện hàng và tình trạng sản phẩm. |
| 4 | Nếu Người mua chọn hình thức Tự sắp xếp để trả hàng thì Shopee hỗ trợ phí trả hàng như thế nào? | Top-1 lấy từ `return-shipping-methods-fees.md`, đúng tài liệu về phương thức gửi hàng và phí hoàn trả. | 0.6544 | Có | Người mua trả trước phí; Shopee hỗ trợ trong 3 - 5 ngày làm việc nếu đủ điều kiện, bằng hoàn phí hoặc Shopee Xu. |
| 5 | Với tài liệu có `audience=seller`, Người bán nên làm gì khi nhận hàng hoàn nhưng sản phẩm bị hư hỏng hoặc không đúng sản phẩm của shop? | Top-1 lấy từ `seller-warranty-policy.md` sau khi lọc `audience=seller`. | 0.6472 | Có | Người bán có thể khiếu nại lên Shopee và chuẩn bị bằng chứng như video mở hộp, hình ảnh, mã vận đơn. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác:**
> [Điền sau demo]

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation - tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
