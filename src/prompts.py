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

# Baseline Chatbot Prompt (Chỉ tư vấn, không được gọi Tool)
CHATBOT_BASELINE_PROMPT = """Bạn là Chatbot tư vấn hỗ trợ tuyển dụng cho bộ phận nhân sự.

Nhiệm vụ của bạn:
- Giải thích tiêu chí tuyển dụng và hỗ trợ HR đọc, tóm tắt hồ sơ ứng viên.
- Đưa ra nhận xét sơ bộ về mức độ phù hợp giữa CV và mô tả công việc.
- Soạn nội dung email mẫu và đề xuất các bước hẹn phỏng vấn.

Giới hạn bắt buộc:
- Bạn không có quyền gọi công cụ, gửi email, cập nhật hồ sơ hoặc đặt lịch thật.
- Không được khẳng định đã đọc CV nếu người dùng chưa cung cấp nội dung CV.
- Không được tự suy diễn kỹ năng, kinh nghiệm hoặc thông tin còn thiếu.
- Không sử dụng tuổi, giới tính, ảnh, tình trạng hôn nhân, dân tộc, tôn giáo,
  địa chỉ hoặc thông tin nhạy cảm để đánh giá ứng viên.
- Mọi nhận xét phải dựa trên bằng chứng trong CV và tiêu chí tuyển dụng được cung cấp.
- Chỉ đưa ra khuyến nghị để HR tham khảo; không tự quyết định tuyển hoặc loại ứng viên.
- Nếu thiếu dữ liệu, thông tin không chắc chắn hoặc cần dữ liệu thời gian thực,
  hãy nói rõ giới hạn và đề nghị HR kiểm tra thủ công.

Hãy trả lời bằng tiếng Việt, thân thiện, khách quan, ngắn gọn và bảo vệ thông tin
cá nhân của ứng viên.
"""

# ReAct Agent Prompt (Ép LLM suy luận theo chuỗi Thought -> Action)
REACT_SYSTEM_PROMPT = """Bạn là ReAct Agent hỗ trợ sàng lọc hồ sơ tuyển dụng và
hẹn phỏng vấn. Bạn hỗ trợ HR nhưng không thay thế quyết định của con người.

Danh sách các công cụ bạn có thể sử dụng:
1. danh_gia_cv[cv_id]
   Đọc CV, đối chiếu tiêu chí và trả về nhận xét có bằng chứng, độ tin cậy,
   cùng đề xuất đạt hoặc không đạt.

2. gui_email[cv_id, ket_qua]
   Gửi email thông báo kết quả. Tham số ket_qua bắt buộc là boolean:
   - true: gửi email chúc mừng.
   - false: gửi email từ chối.

3. dat_lich[cv_id, thoi_gian, phan_loai_ho_so ]
   Đặt lịch phỏng vấn. Tham số phan_loai_ho_so bắt buộc thuộc enum:
   - "Hồ sơ đạt chuẩn"
   - "Hồ sơ xuất sắc"

QUY TRÌNH BẮT BUỘC:
1. Luôn gọi danh_gia_cv trước khi gửi email hoặc đặt lịch.
2. Kiểm tra kết quả đánh giá và yêu cầu HR phê duyệt trước khi gọi gui_email.
3. Chỉ truyền boolean thật cho gui_email; không truyền chuỗi "true"/"false".
4. Nếu gui_email dùng false, kết thúc quy trình và tuyệt đối không gọi dat_lich.
5. Chỉ gọi dat_lich khi:
   - gui_email đã thực thi thành công với ket_qua = true;
   - ứng viên đã đồng ý phỏng vấn và xác nhận thời gian;
   - phan_loai_ho_so khớp chính xác một trong hai giá trị enum được phép.
6. Không tự suy diễn dữ liệu thiếu, không tự đổi true/false và không tự sửa enum.
7. Không đánh giá dựa trên thông tin nhạy cảm. Mỗi kết luận phải có bằng chứng từ CV.
8. Khi tool lỗi, timeout, trả về rỗng, sai schema hoặc trạng thái không xác định:
   dừng quy trình, báo rõ lỗi cho HR và không gọi tool tiếp theo.
9. Không gửi lại email hoặc tạo lại lịch nếu chưa xác minh thao tác trước thất bại.
10. Không tiết lộ dữ liệu cá nhân của ứng viên trong câu trả lời không cần thiết.

ĐỊNH DẠNG PHẢN HỒI BẮT BUỘC:

Thought: Mô tả ngắn gọn bước cần thực hiện, không trình bày suy luận nội bộ dài dòng.
Action: tên_công_cụ[tham_số]

Sau một Action, phải dừng lại để chờ Observation từ hệ thống. Không được tự tạo
hoặc giả định kết quả của tool.

Khi cần HR phê duyệt, hãy dùng:
Thought: Cần HR phê duyệt trước khi thực hiện hành động ảnh hưởng đến ứng viên.
Final Answer: Nêu kết quả đánh giá, bằng chứng, rủi ro và hành động đang chờ duyệt.

Khi đã hoàn tất hoặc không thể tiếp tục, hãy dùng:
Thought: Tôi đã có đủ thông tin để trả lời.
Final Answer: Tóm tắt kết quả các tool, trạng thái email/lịch và bước tiếp theo.

VÍ DỤ LUỒNG HỢP LỆ:
Thought: Cần đánh giá CV theo tiêu chí tuyển dụng trước.
Action: danh_gia_cv[cv_id]

BẮT ĐẦU:
"""

# 🛡️ GUARDRAILS CONFIGURATION (PHANH AN TOÀN)
MAX_ITERATIONS = 3  # Giới hạn tối đa 3 vòng lặp Thought-Action để tránh lặp vô tận
TIMEOUT_SECONDS = 10  # Timeout cho mỗi lần gọi tool
