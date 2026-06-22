TELEGRAM CHATBOT – 204PROD. MEDIA AGENCY
## 1. TỔNG QUAN DỰ ÁN
* **Tên dự án:** Hybrid Telegram Chatbot cho 204prod.
* **Đối tượng phục vụ:** 204prod. Media Agency (Đoàn làm phim, đội ngũ sản xuất media hiện trường).
* **Mục đích cốt lõi:** Tối ưu hóa và tổng hợp chi phí vận hành trực ca/theo dự án sản xuất truyền thông một cách tức thời. Giúp nhân viên hiện trường (set quay) dễ dàng báo cáo chi phí, hệ thống tự động cộng dồn và quản lý doanh thu/chi phí theo thời gian thực mà không làm gián đoạn tiến độ công việc.

---

## 2. KIẾN TRÚC KỸ THUẬT & HẠ TẦNG (TECHNICAL ARCHITECTURE)
Hệ thống được thiết kế theo mô hình **Hybrid (Sử dụng Logic Code thông thường kết hợp AI)**, tối ưu hóa hạ tầng Serverless/Cloud Container để tiết kiệm chi phí và đảm bảo hiệu năng.

### Khắc phục giới hạn hạ tầng Deployment:
* **Không dùng Long Polling:** Hủy bỏ hoàn toàn cơ chế chạy nền liên tục (`Background Worker` với vòng lặp vô tận) nhằm tránh lỗi ngắt kết nối hoặc lỗi crash khi deploy trên các nền tảng Cloud App (PaaS).
* **Webhook + FastAPI:** Hệ thống chuyển sang cơ chế Webhook. Sử dụng framework **FastAPI (Python)** để expose một cổng công khai (port), đăng ký URL này với Telegram API. Mỗi khi có tin nhắn mới, Telegram sẽ kích hoạt một request HTTP POST trực tiếp đến hệ thống.
* **Cơ chế "Keep-alive" chống ngủ đông:** Cấu hình dịch vụ giám sát bên thứ ba (ví dụ: UptimeRobot) thực hiện gửi request ping tự động đến endpoint API của FastAPI với tần suất **10 phút/lần**. Giải pháp này ngăn chặn việc container rơi vào trạng thái ngủ đông (Sleep Mode) sau 15 phút không có traffic, đảm bảo bot luôn trong trạng thái sẵn sàng phản hồi.

---

## 3. CÁC LUỒNG HOẠT ĐỘNG CHÍNH (FEATURE FLOWS)

Hệ thống vận hành song song 2 luồng xử lý tùy thuộc vào ngữ cảnh và nhu cầu của nhân viên sản xuất:

### Luồng 1: Nhập liệu thủ công (Manual Input Flow)
Sử dụng hoàn toàn bằng logic nghiệp vụ thông thường (Deterministic Code), không sử dụng AI để đảm bảo tốc độ phản hồi nhanh, chính xác 100% đối với các danh mục cố định.

* **Lệnh kích hoạt:** `/cost` (Quản lý chi phí) hoặc `/task` (Cập nhật tiến độ dự án).
* **Kịch bản vận hành:**
  1. Người dùng gõ lệnh `/cost`.
  2. Bot lập tức hiển thị bảng menu nút bấm tương tác (`Inline Keyboard`) phân loại danh mục (Ví dụ: `[🍕 Ăn uống]`, `[🚗 Di chuyển]`, `[🎬 Thiết bị]`,...).
  3. Người dùng bấm chọn nút `[🍕 Ăn uống]`.
  4. Bot nhận tín hiệu `callback_query` và chuyển trạng thái hội thoại sang hàng đợi nhập liệu, đồng thời phản hồi: *"Vui lòng nhập số tiền chi cho mục Ăn uống:"*.
  5. Người dùng nhập số tiền (Ví dụ: `500000`).
  6. Hệ thống thực hiện lưu trữ vào database và phản hồi thông báo thành công, cập nhật lũy kế tổng chi phí dự án.

Code output
File created successfully.

[User: /cost] ──> [Bot: Hiện Inline Keyboard] ──> [User: Chọn 🍕 Ăn uống]
──> [Bot: Yêu cầu nhập tiền] ──> [User: Gõ 500000] ──> [Lưu Database]


### Luồng 2: Nhập liệu thông minh bằng AI (AI-Powered Flow)
Áp dụng cho các tình huống nhân viên đang bận rộn tại set quay, cần báo cáo nhanh bằng ngôn ngữ tự nhiên, hình ảnh hóa đơn hoặc tin nhắn thoại (Voice). Luồng này tích hợp **Gemini API** để bóc tách cấu trúc dữ liệu.

#### Kịch bản A: Nhập liệu bằng văn bản tự do (Free-text parsing)
1. Người dùng gõ lệnh `/ai` kèm nội dung văn bản tự do hoặc bot tự cấu hình để hiểu.
2. *Ví dụ thực tế:* `/ai Hôm qua anh em quay ngoài trời nắng quá nên mua nước hết 120 cành nhé.`
3. Hệ thống chuyển nội dung văn bản sang **Gemini API** xử lý với prompt định hình cấu trúc dữ liệu.
4. Gemini bóc tách ngữ nghĩa, trả về kết quả chuẩn: Hạng mục: `Mua nước/Ăn uống`, Số tiền: `120000`.
5. Bot phản hồi tin nhắn xác nhận kèm nút bấm duyệt: 
   > *"Xác nhận ghi nhận: Mua nước - 120.000 VNĐ. [✅ OK] [❌ Hủy]"*

#### Kịch bản B: Bóc tách hóa đơn/biên lai từ hình ảnh (OCR Image Parsing)
1. Nhân viên hiện trường chụp ảnh tờ biên lai/hóa đơn bán lẻ (tiền ăn trưa, xăng xe, thuê đồ) gửi trực tiếp vào Telegram Chatbot.
2. Bot tải tệp ảnh tạm thời, chuyển đổi dữ liệu và gọi **Gemini API (Multimodal)** kèm cấu trúc yêu cầu dữ liệu đầu ra dạng JSON:
   ```json
   {
     "hang_muc": "Ăn uống",
     "so_tien": 450000
   }
Sau khi nhận kết quả từ Gemini, Bot không lưu tự động mà gửi một tin nhắn xác nhận kiểm tra chéo vào nhóm quản trị dự án:

🤖 HỆ THỐNG NHẬN DIỆN HÓA ĐƠN

Mục: Ăn uống

Số tiền: 450,000 VNĐ

Vui lòng xác nhận để lưu trữ:
[✅ Chuẩn xác. Lưu ngay] [❌ AI nhận diện sai, để nhập tay]

Xử lý tương tác nút bấm:

Nếu người dùng bấm [✅ Chuẩn xác. Lưu ngay]: Kích hoạt tín hiệu callback_query, hệ thống ghi dữ liệu tức thời vào Cloud Database và thông báo cộng dồn chi phí thành công.

Nếu người dùng bấm [❌ AI nhận diện sai, để nhập tay]: Bot hủy phiên làm việc bằng AI và tự động kích hoạt lại Luồng 1 (Manual Input) để người dùng chọn danh mục và nhập tiền bằng tay.

4. CƠ SỞ DỮ LIỆU & ĐẦU RA (DATABASE & OUTPUT)
Cloud Database: Lưu trữ thông tin chi tiết từng giao dịch bao gồm: Thời gian, Người chi, Hạng mục, Số tiền, Hình thức nhập (Manual/AI), Ảnh hóa đơn gốc (nếu có).

Hàm tổng hợp (Aggregation): Hệ thống liên tục cập nhật trường total_cost của dự án để bất kỳ khi nào nhà quản trị yêu cầu, bot có thể xuất ra báo cáo tổng số tiền đã chi tiêu ngay lập tức.

5. LỢI ÍCH CỦA GIẢI PHÁP ĐỐI VỚI 204PROD.
Tiết kiệm thời gian: Nhân viên hiện trường không cần mở file Excel hay ghi chép thủ công, chỉ cần nhắn tin hoặc chụp ảnh hóa đơn trong 3 giây.

Độ chính xác cao: Kết hợp kiểm duyệt con người (Human-in-the-loop) qua nút bấm xác nhận giúp loại bỏ hoàn toàn tỷ lệ sai sót (hallucination) của AI.

Tối ưu chi phí vận hành bot: Chạy hoàn toàn trên kiến trúc Webhook và tận dụng gói miễn phí của các dịch vụ Cloud mà vẫn đảm bảo bot hoạt động 24/7 nhờ cơ chế Keep-alive.
