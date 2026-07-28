"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Cung cấp 3 Tool tuyển dụng:
1. screen_and_score_cv: Đánh giá & chấm điểm CV
2. send_recruitment_email: Gửi email (tham số boolean is_passed: True/False)
3. schedule_interview: Đặt lịch phỏng vấn (tham số Enum: 'Hồ sơ đạt chuẩn' | 'Hồ sơ xuất sắc')
"""

import random
from typing import Dict, Any

# Cơ sở dữ liệu mẫu hồ sơ CV (Giàu thông tin thực tế)
MOCK_CV_DATABASE: Dict[str, Dict[str, Any]] = {
    "CV_001": {
        "name": "Nguyễn Văn A",
        "email": "nguyenvana@gmail.com",
        "phone": "0901234567",
        "position": "Java Developer",
        "experience": "6 tháng (Fresher/Junior)",
        "skills": ["Java Core", "HTML/CSS", "MySQL basic"],
        "education": "Cử nhân CNTT - ĐH Bách Khoa Hà Nội",
        "certifications": ["Toeic 600"],
        "summary": "Mới tốt nghiệp, từng thực hiện bài tập lớn bằng Java Swing và Servlet. Chưa có kinh nghiệm thực tế với Spring Boot hay Microservices.",
    },
    "CV_002": {
        "name": "Lê Văn C",
        "email": "levanc@gmail.com",
        "phone": "0912345678",
        "position": "Senior Technical Lead",
        "experience": "7 năm (Senior/Lead)",
        "skills": ["Java", "Spring Boot", "Microservices", "Docker", "Kubernetes", "Kafka", "PostgreSQL"],
        "education": "Thạc sĩ Khoa học Máy tính - ĐH Quốc Gia TP.HCM",
        "certifications": ["AWS Certified Solutions Architect - Professional", "Oracle Certified Master"],
        "summary": "Từng làm Technical Lead quản lý đội nhóm 12 kỹ sư, kiến trúc hệ thống thanh toán chịu tải 100k TPS.",
    },
    "CV_003": {
        "name": "Trần Thị B",
        "email": "tranthib@gmail.com",
        "phone": "0987654321",
        "position": "Frontend Developer",
        "experience": "3.5 năm (Mid-level)",
        "skills": ["ReactJS", "VueJS", "TypeScript", "TailwindCSS", "Redux Toolkit", "RESTful API"],
        "education": "Cử nhân Công nghệ Phần mềm - ĐH FPT",
        "certifications": ["Meta Frontend Developer Professional Certificate"],
        "summary": "Có 3.5 năm kinh nghiệm phát triển SPA Dashboard & Web App e-Commerce responsive, tối ưu Performance & SEO tốt.",
    },
    "CV_004": {
        "name": "Phạm Minh D",
        "email": "phamminhd@gmail.com",
        "phone": "0934567890",
        "position": "DevOps Engineer",
        "experience": "4 năm (Mid/Senior)",
        "skills": ["CI/CD (Jenkins, GitHub Actions)", "Terraform", "Ansible", "AWS", "Kubernetes", "Prometheus"],
        "education": "Cử nhân Điện tử Viễn thông - ĐH Bách Khoa Đà Nẵng",
        "certifications": ["Certified Kubernetes Administrator (CKA)", "AWS SysOps Administrator"],
        "summary": "Chuyên xây dựng hạ tầng Cloud và tự động hóa luồng CI/CD cho các ứng dụng ngân hàng, tài chính.",
    },
    "CV_005": {
        "name": "Hoàng Anh E",
        "email": "hoanganhe@gmail.com",
        "phone": "0945678901",
        "position": "Data Engineer",
        "experience": "2 năm (Junior/Mid)",
        "skills": ["Python", "PySpark", "BigQuery", "SQL", "Apache Airflow", "Data Modeling"],
        "education": "Cử nhân Khoa học Dữ liệu - ĐH Khoa Học Tự Nhiên",
        "certifications": ["Google Cloud Professional Data Engineer"],
        "summary": "Có kinh nghiệm thiết kế pipeline xử lý dữ liệu Batch & Streaming trên Google Cloud Platform.",
    },
}


def screen_and_score_cv(cv_id: str, random_score: bool = True) -> str:
    """
    Tool 1: Sàng lọc và đánh giá hồ sơ CV dựa trên mã ứng viên.
    
    Args:
        cv_id (str): Mã hồ sơ CV (Ví dụ: 'CV_001', 'CV_002', 'CV_003', 'CV_004', 'CV_005')
        random_score (bool, optional): Mặc định True (sinh điểm ngẫu nhiên 30-95 và minh chứng tương ứng).
        
    Returns:
        str: Thông tin chi tiết hồ sơ, điểm số, kết quả đánh giá và minh chứng của ứng viên
    """
    cv_id_clean = str(cv_id).strip().upper()
    if cv_id_clean not in MOCK_CV_DATABASE:
        return f"LỖI: Mã hồ sơ '{cv_id}' không tồn tại trong hệ thống."
    
    candidate = MOCK_CV_DATABASE[cv_id_clean]
    
    if random_score or "score" not in candidate:
        score = random.randint(30, 95)
    else:
        score = candidate["score"]
    
    if score > 85:
        classification = "Hồ sơ xuất sắc"
        status = "Đạt (Fast-track)"
        reason = f"Ứng viên có kinh nghiệm ấn tượng ({candidate.get('experience', 'N/A')}), bộ kỹ năng mạnh ({', '.join(candidate.get('skills', []))}) và học vấn/chứng chỉ xuất sắc ({', '.join(candidate.get('certifications', []))}). Đáp ứng 100% tiêu chí JD."
    elif 60 <= score <= 85:
        classification = "Hồ sơ đạt chuẩn"
        status = "Đạt"
        reason = f"Ứng viên có kinh nghiệm ({candidate.get('experience', 'N/A')}), sở hữu kỹ năng chuyên môn phù hợp ({', '.join(candidate.get('skills', []))}). Đáp ứng đầy đủ tiêu chí yêu cầu trong mô tả công việc (JD)."
    else:
        classification = "Không đạt"
        status = "Loại"
        reason = f"Ứng viên có kinh nghiệm còn hạn chế ({candidate.get('experience', 'N/A')}), chưa đáp ứng một số kỹ năng chuyên môn bắt buộc theo yêu cầu JD vị trí {candidate.get('position', 'N/A')}."
        
    skills_str = ", ".join(candidate.get("skills", []))
    certs_str = ", ".join(candidate.get("certifications", [])) or "Không có"
    
    return (
        f"📋 [HỒ SƠ ỨNG VIÊN {cv_id_clean}]\n"
        f"- Họ tên: {candidate['name']} | Email: {candidate['email']} | SĐT: {candidate.get('phone', 'N/A')}\n"
        f"- Vị trí ứng tuyển: {candidate['position']}\n"
        f"- Kinh nghiệm: {candidate.get('experience', 'N/A')} | Học vấn: {candidate.get('education', 'N/A')}\n"
        f"- Kỹ năng: {skills_str}\n"
        f"- Chứng chỉ: {certs_str}\n"
        f"- Tóm tắt CV: {candidate.get('summary', 'N/A')}\n"
        f"--------------------------------------------------\n"
        f"📊 [KẾT QUẢ ĐÁNH GIÁ & SÀNG LỌC]\n"
        f"- Điểm số: {score}/100 | Xếp loại: {classification} | Trạng thái: {status}\n"
        f"- 📌 Minh chứng/Lý do: {reason}"
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
