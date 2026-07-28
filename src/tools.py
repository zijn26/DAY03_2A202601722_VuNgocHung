"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Cung cấp 3 Tool tuyển dụng:
1. screen_and_score_cv: Đánh giá & chấm điểm CV (Tự động sinh/tính điểm ngẫu nhiên)
2. send_recruitment_email: Gửi email (tham số boolean is_passed: True/False)
3. schedule_interview: Đặt lịch phỏng vấn (tham số Enum: 'Hồ sơ đạt chuẩn' | 'Hồ sơ xuất sắc')
"""

import random
from typing import Dict, Any, List

# Cơ sở dữ liệu mẫu hồ sơ CV (Không cố định điểm score nữa, chỉ lưu thông tin hồ sơ)
MOCK_CV_DATABASE: Dict[str, Dict[str, Any]] = {
    "CV_001": {
        "name": "Nguyễn Văn A",
        "email": "nguyenvana@gmail.com",
        "phone": "0901234567",
        "position": "Java Developer",
        "experience_years": 2,
        "education": "Cử nhân CNTT - Đại học Bách Khoa",
        "skills": ["Java", "Spring Boot", "MySQL", "Git"],
    },
    "CV_002": {
        "name": "Lê Văn C",
        "email": "levanc@gmail.com",
        "phone": "0987654321",
        "position": "Senior Technical Lead",
        "experience_years": 7,
        "education": "Kỹ sư Phần mềm - Đại học Quốc Gia",
        "skills": ["Python", "System Design", "Microservices", "Docker", "Kubernetes", "Leadership"],
    },
    "CV_003": {
        "name": "Trần Thị B",
        "email": "tranthib@gmail.com",
        "phone": "0912345678",
        "position": "Frontend Developer",
        "experience_years": 4,
        "education": "Cử nhân Khoa học Máy tính - Đại học VinUni",
        "skills": ["React", "TypeScript", "HTML5/CSS3", "TailwindCSS", "REST API"],
    },
}


def screen_and_score_cv(cv_id: str) -> str:
    """
    Tool 1: Sàng lọc và đánh giá chi tiết hồ sơ CV dựa trên mã ứng viên (Tự động sinh/tính điểm ngẫu nhiên).
    
    Args:
        cv_id (str): Mã hồ sơ CV (Ví dụ: 'CV_001', 'CV_002', 'CV_003')
        
    Returns:
        str: Thông tin chi tiết hồ sơ, điểm số tự động và kết quả đánh giá
    """
    cv_id_clean = str(cv_id).strip().upper()
    if cv_id_clean not in MOCK_CV_DATABASE:
        return f"LỖI: Mã hồ sơ '{cv_id}' không tồn tại trong hệ thống."
    
    candidate = MOCK_CV_DATABASE[cv_id_clean]
    
    # Tự động sinh điểm số ngẫu nhiên (Random score từ 35 đến 98) khi chấm điểm CV
    score = random.randint(35, 98)
    skills_str = ", ".join(candidate["skills"])
    
    if score > 85:
        classification = "Hồ sơ xuất sắc"
        status = "Đạt (Fast-track)"
    elif 60 <= score <= 85:
        classification = "Hồ sơ đạt chuẩn"
        status = "Đạt"
    else:
        classification = "Không đạt"
        status = "Loại"
        
    return (
        f"📋 HỒ SƠ ỨNG VIÊN [{cv_id_clean}]:\n"
        f"- Họ tên: {candidate['name']} | Email: {candidate['email']} | SĐT: {candidate['phone']}\n"
        f"- Vị trí: {candidate['position']} | Kinh nghiệm: {candidate['experience_years']} năm\n"
        f"- Học vấn: {candidate['education']}\n"
        f"- Kỹ năng: {skills_str}\n"
        f"- Điểm số tự động (Random): {score}/100 | Xếp loại: {classification} | Trạng thái: {status}"
    )


def send_recruitment_email(cv_id: str, is_passed: bool, message: str = "") -> str:
    """
    Tool 2: Gửi email tuyển dụng cho ứng viên.
    
    Args:
        cv_id (str): Mã hồ sơ CV của ứng viên
        is_passed (bool): True = Mail chúc mừng/mời phỏng vấn, False = Mail từ chối lịch sự
        message (str, optional): Lời nhắn bổ sung trong email
        
    Returns:
        str: Thông báo kết quả gửi email
    """
    cv_id_clean = str(cv_id).strip().upper()
    candidate = MOCK_CV_DATABASE.get(cv_id_clean, {})
    candidate_name = candidate.get("name", cv_id_clean)
    candidate_email = candidate.get("email", f"{cv_id_clean.lower()}@example.com")

    if isinstance(is_passed, str):
        is_passed = is_passed.strip().lower() in ["true", "1", "yes"]
    else:
        is_passed = bool(is_passed)

    if is_passed:
        subject = "THƯ MỜI PHỎNG VẤN TRỰC TIẾP"
        email_type = "Email Chúc Mừng & Mời Phỏng Vấn"
    else:
        subject = "THƯ CẢM ƠN VÀ THÔNG BÁO KẾT QUẢ SÀNG LỌC CV"
        email_type = "Email Từ Chối Lịch Sự"
        
    return (
        f"✅ ĐÃ GỬI MAIL THÀNH CÔNG!\n"
        f"- Loại Email: {email_type}\n"
        f"- Người nhận: {candidate_name} ({candidate_email})\n"
        f"- Tiêu đề: [{subject}]\n"
        f"- Ghi chú bổ sung: {message if message else 'N/A'}"
    )


def schedule_interview(cv_id: str, date: str, classification: str) -> str:
    """
    Tool 3: Lên lịch phỏng vấn cho ứng viên đạt yêu cầu.
    
    Args:
        cv_id (str): Mã hồ sơ CV của ứng viên
        date (str): Ngày phỏng vấn (Định dạng DD/MM/YYYY)
        classification (str): Xếp loại hồ sơ. CHỈ NHẬN 1 trong 2 giá trị Enum: 'Hồ sơ đạt chuẩn' hoặc 'Hồ sơ xuất sắc'
        
    Returns:
        str: Thông tin xác nhận lịch phỏng vấn hoặc thông báo lỗi
    """
    cv_id_clean = str(cv_id).strip().upper()
    
    if cv_id_clean not in MOCK_CV_DATABASE:
        return f"LỖI: Mã hồ sơ '{cv_id}' không tồn tại trong hệ thống."
        
    valid_enums = ["Hồ sơ đạt chuẩn", "Hồ sơ xuất sắc"]
    if classification not in valid_enums:
        return f"LỖI: Classification '{classification}' không hợp lệ. Chỉ chấp nhận: {valid_enums}."
        
    # Kiểm tra ngày hợp lệ (Bẫy ngày 32/13/2026...)
    try:
        parts = date.split("/")
        if len(parts) != 3:
            raise ValueError()
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= month <= 12 and 1 <= day <= 31):
            raise ValueError()
        if month in [4, 6, 9, 11] and day > 30:
            raise ValueError()
        if month == 2 and day > 29:
            raise ValueError()
    except ValueError:
        return f"LỖI: Ngày phỏng vấn '{date}' không hợp lệ. Định dạng chuẩn là DD/MM/YYYY."

    candidate = MOCK_CV_DATABASE[cv_id_clean]
    interviewer = "Giám đốc kỹ thuật" if classification == "Hồ sơ xuất sắc" else "Hội đồng Tuyển dụng"
    
    return (
        f"📅 ĐẶT LỊCH PHỎNG VẤN THÀNH CÔNG!\n"
        f"- Mã CV: {cv_id_clean} ({candidate['name']})\n"
        f"- Phân loại: {classification}\n"
        f"- Người phỏng vấn: {interviewer}\n"
        f"- Thời gian: {date}"
    )


# Register Available Tools
AVAILABLE_TOOLS = {
    "screen_and_score_cv": screen_and_score_cv,
    "send_recruitment_email": send_recruitment_email,
    "schedule_interview": schedule_interview,
}
