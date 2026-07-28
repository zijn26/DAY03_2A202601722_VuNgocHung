"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import ast
import json
import os
import re
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")

    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def build_tools_description() -> str:
    """Sinh mô tả tool trực tiếp từ AVAILABLE_TOOLS (nguồn thật của Role 2),
    để prompt luôn khớp tool hiện có dù Role 3 quên cập nhật REACT_SYSTEM_PROMPT."""
    lines = []
    for name, func in AVAILABLE_TOOLS.items():
        first_doc_line = (func.__doc__ or "Không có mô tả.").strip().splitlines()[0]
        lines.append(f"- {name}: {first_doc_line}")
    return "\n".join(lines)


def parse_action(step_text: str):
    """Bóc tách 'Action: tool_name(args)' hoặc 'Action: tool_name[args]' từ output LLM."""
    match = re.search(r"Action:\s*(\w+)[\[\(](.*)[\]\)]", step_text)
    if not match:
        return None, None
    return match.group(1).strip(), match.group(2).strip()


def parse_final_answer(step_text: str):
    match = re.search(r"Final Answer:\s*(.+)", step_text, re.DOTALL)
    return match.group(1).strip() if match else None


def _split_top_level_args(raw_args: str):
    """Tách tham số theo dấu phẩy ở cấp ngoài cùng, bỏ qua dấu phẩy nằm trong
    dấu nháy hoặc ngoặc lồng nhau (VD tránh tách nhầm bên trong chuỗi ngày giờ)."""
    parts, depth, quote, current = [], 0, None, ""
    for ch in raw_args:
        if quote:
            current += ch
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
            current += ch
        elif ch in "([{":
            depth += 1
            current += ch
        elif ch in ")]}":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current)
    return [p.strip() for p in parts if p.strip()]


_JSON_STYLE_BOOLEANS = {"true": True, "false": False}


def _coerce_value(raw: str):
    """Thử hiểu raw như literal Python an toàn (số, bool, chuỗi có nháy...).
    LLM hay viết true/false chữ thường kiểu JSON thay vì True/False của Python -
    nếu không bắt riêng, chuỗi "false" sẽ bị coi là chuỗi khác rỗng (luôn truthy!),
    khiến is_passed=False bị hiểu nhầm thành True. Cũng xử lý luôn trường hợp
    LLM quên dấu nháy quanh chuỗi (VD ngày 02/08/2026 bị hiểu nhầm là phép chia)."""
    stripped = raw.strip()
    if stripped.lower() in _JSON_STYLE_BOOLEANS:
        return _JSON_STYLE_BOOLEANS[stripped.lower()]
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return raw


def parse_tool_args(raw_args: str):
    """Bóc tách 'cv_id=\"CV_001\", is_passed=False' thành (args, kwargs).
    Mỗi tham số được xử lý độc lập nên 1 tham số thiếu dấu nháy không làm hỏng cả câu."""
    args, kwargs = [], {}
    for part in _split_top_level_args(raw_args):
        if "=" in part:
            key, _, value = part.partition("=")
            key = key.strip()
            if key.isidentifier():
                kwargs[key] = _coerce_value(value.strip())
                continue
        args.append(_coerce_value(part))
    return args, kwargs


# Sau khi các tool trong danh sách này chạy xong, bắt buộc dừng lại chờ HR (người thật)
# xác nhận trước khi Agent được đi tiếp sang bước ảnh hưởng ứng viên (gửi mail, xếp lịch...).
HUMAN_APPROVAL_REQUIRED_AFTER = {"screen_and_score_cv"}


def ask_human_approval(observation: str) -> bool:
    """Human-in-the-loop: dừng chương trình thật, chờ HR gõ y/n ngoài terminal."""
    print("\n🙋 [HUMAN-IN-THE-LOOP] Yêu cầu phê duyệt từ HR cho kết quả sàng lọc CV trên:")
    answer = input("HR có đồng ý cho Agent tiếp tục xử lý (gửi email / xếp lịch)? (y/n): ").strip().lower()
    return answer in ("y", "yes", "co", "có")


def call_tool(tool_name: str, raw_args: str) -> str:
    if tool_name not in AVAILABLE_TOOLS:
        return f"LỖI: Tool '{tool_name}' không tồn tại. Tool khả dụng: {list(AVAILABLE_TOOLS.keys())}"
    try:
        args, kwargs = parse_tool_args(raw_args)
        return AVAILABLE_TOOLS[tool_name](*args, **kwargs)
    except Exception as e:
        return f"LỖI khi gọi tool '{tool_name}' với tham số '{raw_args}': {e}"


def run_react_agent(user_query: str, provider):
    """
    Vòng lặp ReAct Agent thật: LLM tự sinh Thought -> Action dựa trên REACT_SYSTEM_PROMPT,
    hệ thống thực thi tool tương ứng và trả Observation, lặp tới khi có Final Answer
    hoặc chạm Guardrail MAX_ITERATIONS.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")

    system_prompt = (
        REACT_SYSTEM_PROMPT
        + "\n\nDANH SÁCH TOOL THỰC TẾ ĐANG KHẢ DỤNG (chỉ được dùng đúng tên trong danh sách này):\n"
        + build_tools_description()
    )
    transcript = f"Câu hỏi của người dùng: {user_query}\n"

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        raw_response = provider.generate(transcript, system_prompt=system_prompt)
        # Cắt bỏ phần Observation nếu LLM tự "bịa" thêm (chỉ hệ thống mới được sinh Observation)
        cut_idx = raw_response.find("Observation:")
        step_text = raw_response[:cut_idx].rstrip() if cut_idx != -1 else raw_response.rstrip()

        final_answer = parse_final_answer(step_text)
        if final_answer:
            fa_idx = step_text.find("Final Answer:")
            if fa_idx > 0:
                thought_part = step_text[:fa_idx].strip()
                if thought_part:
                    print(thought_part)
            elif fa_idx == -1:
                print(step_text)
            print(f"🏁 Final Answer: {final_answer}")
            return

        print(step_text)

        tool_name, raw_args = parse_action(step_text)
        if not tool_name:
            print("⚠️ Không phân tích được Action hợp lệ trong phản hồi của LLM. Dừng vòng lặp an toàn.")
            return

        observation = call_tool(tool_name, raw_args)
        print(f"👁️ Observation: {observation}")

        if tool_name in HUMAN_APPROVAL_REQUIRED_AFTER and not observation.startswith("LỖI"):
            if not ask_human_approval(observation):
                print("🛑 HR TỪ CHỐI PHÊ DUYỆT: Dừng quy trình, không gửi email/xếp lịch cho ứng viên này.")
                return
            transcript += f"{step_text}\nObservation: {observation}\nHR đã PHÊ DUYỆT, được phép tiếp tục xử lý ứng viên này.\n"
        else:
            transcript += f"{step_text}\nObservation: {observation}\n"

    print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Chạy thử câu test số 3
    sample_query = tests[2]["question"]
    
    # print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    # run_baseline_chatbot(sample_query, provider)
    
    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)
