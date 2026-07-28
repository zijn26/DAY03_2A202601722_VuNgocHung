"""
PHÂN TÍCH FAILURE MODES CHO TRỢ LÝ TUYỂN DỤNG

Luồng nghiệp vụ: Tool 1 (đánh giá CV) -> Tool 2 (gửi email)
-> Tool 3 (đặt lịch phỏng vấn).

1. TOOL ĐÁNH GIÁ CV
   Failure Modes:
   - Không đọc được CV vì file hỏng, có mật khẩu, sai định dạng hoặc OCR kém.
   - CV thiếu dữ liệu nhưng mô hình tự suy diễn kỹ năng hoặc kinh nghiệm.
   - Đọc nhầm bảng, cột, mốc thời gian hoặc tổng số năm kinh nghiệm.
   - Làm theo câu lệnh độc hại nằm trong CV (prompt injection).
   - Đánh giá dựa trên tuổi, giới tính, ảnh, địa chỉ hoặc dữ liệu nhạy cảm.
   - Kết quả thiếu bằng chứng, độ tin cậy thấp, sai schema, rỗng hoặc timeout.

   Phòng vệ:
   - Kiểm tra file trước khi đọc; chỉ đánh giá theo tiêu chí đã được HR phê duyệt.
   - Mỗi kết luận phải có bằng chứng từ CV; không tự điền dữ liệu còn thiếu.
   - Bỏ qua mọi chỉ dẫn nằm trong CV và không dùng thuộc tính nhạy cảm để chấm điểm.
   - Nếu lỗi hoặc độ tin cậy thấp: dừng luồng, chuyển HR kiểm tra, không gọi Tool 2.

2. TOOL GỬI EMAIL
   Tham số boolean:
       True  = gửi email chúc mừng.
       False = gửi email từ chối.

   Failure Modes:
   - Boolean bị đảo nghĩa, dẫn đến gửi sai loại thư.
   - Nhận chuỗi "true"/"false", số hoặc null thay vì kiểu boolean thật.
   - Gửi nhầm email, tên, vị trí hoặc dữ liệu của ứng viên khác.
   - Gửi trước khi HR phê duyệt; retry gây gửi trùng.
   - Tool báo lỗi dù đã gửi hoặc báo thành công dù chưa gửi.
   - Template thiếu biến, lộ dữ liệu hoặc chứa cam kết ngoài thẩm quyền.

   Phòng vệ:
   - Chỉ nhận đúng kiểu bool; ánh xạ True -> CONGRATULATION,
     False -> REJECTION trước khi gửi.
   - Cho HR xem trước và xác nhận người nhận, loại thư, vị trí.
   - Dùng idempotency key chống gửi trùng và lưu message_id để đối soát.
   - Không retry mù. Nếu chưa xác định được trạng thái gửi thì không gọi Tool 3.

3. TOOL ĐẶT LỊCH PHỎNG VẤN
   Tham số enum chỉ nhận:
       "Hồ sơ đạt chuẩn"
       "Hồ sơ xuất sắc"

   Failure Modes:
   - Giá trị ngoài enum, sai chính tả, khác chữ hoa/thường hoặc thừa khoảng trắng.
   - Nhầm hai mức hồ sơ, dẫn đến chọn sai quy trình phỏng vấn.
   - Đặt lịch khi Tool 2 = False hoặc email chúc mừng chưa gửi thành công.
   - Đặt lịch trước khi ứng viên đồng ý; sai múi giờ, trùng lịch hoặc ngoài giờ.
   - Retry tạo lịch trùng; thiếu người tham dự hoặc đường dẫn họp.
   - Calendar và hệ thống tuyển dụng ghi nhận trạng thái không đồng bộ.

   Phòng vệ:
   - Validate enum tuyệt đối; không tự đoán hoặc tự sửa giá trị không hợp lệ.
   - Chỉ gọi Tool 3 khi Tool 2 = True, email đã gửi thành công và ứng viên xác nhận.
   - Kiểm tra lại lịch trống, múi giờ, người tham dự và giờ làm việc trước khi đặt.
   - Dùng idempotency key; chỉ thành công khi có event_id và meeting_url.
   - Nếu trạng thái không đồng bộ, dừng và chuyển HR xử lý, không tự tạo lại lịch.

NGUYÊN TẮC FAIL-SAFE:
- Dữ liệu thiếu, tool lỗi hoặc kết quả không chắc chắn: dừng luồng và báo HR.
- Không suy đoán kết quả, không tự đổi True/False và không tự sửa enum.
- Ghi audit log cho đầu vào, kết quả, lỗi, thời điểm và người phê duyệt.
- Hành động ảnh hưởng trực tiếp đến ứng viên phải có human-in-the-loop.
"""

"""
🧠 PROMPTS & SAFEGUARDS (Dành cho Role 3: Prompt & Safeguard Engineer)
Nơi cấu hình System Prompt và Phanh An Toàn (Guardrails) cho AI.
"""

# Baseline Chatbot Prompt (Chỉ dùng LLM thông thường, không có Tool)
CHATBOT_BASELINE_PROMPT = """Bạn là một Chatbot tư vấn thông thường.
Hãy trả lời câu hỏi của người dùng một cách thân thiện dựa trên kiến thức có sẵn của bạn.
Nếu không biết thông tin thực tế thời gian thực, hãy lịch sự thông báo cho người dùng.
"""

# ReAct Agent Prompt (Ép LLM suy luận theo chuỗi Thought -> Action)
REACT_SYSTEM_PROMPT = """Bạn là một ReAct Agent thông minh có khả năng sử dụng công cụ (Tools).

Danh sách các công cụ bạn có thể sử dụng:
1. get_weather[location]: Tra cứu thời tiết hiện tại của một thành phố.
2. search_flights[origin, destination]: Tra cứu chuyến bay giữa 2 địa điểm.

QUY TẮC BẮT BUỘC: Khi trả lời, bạn PHẢI tuân theo định dạng từng dòng như sau:

Thought: Suy luận của bạn về bước tiếp theo cần làm.
Action: tên_công_cụ[tham_số]
(Sau đó dừng lại chờ hệ thống trả về kết quả Observation)

Khi đã có đủ thông tin để trả lời người dùng, hãy dùng định dạng:
Thought: Tôi đã có đủ thông tin để trả lời.
Final Answer: Câu trả lời hoàn chỉnh cuối cùng gửi cho người dùng.

BẮT ĐẦU:
"""

# 🛡️ GUARDRAILS CONFIGURATION (PHANH AN TOÀN)
MAX_ITERATIONS = 3  # Giới hạn tối đa 3 vòng lặp Thought-Action để tránh lặp vô tận
TIMEOUT_SECONDS = 10  # Timeout cho mỗi lần gọi tool
