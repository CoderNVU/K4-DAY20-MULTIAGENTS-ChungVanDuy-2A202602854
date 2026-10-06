# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Chung Văn Duy | 2A202602854 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: VyceAI (`deepseek-v4-flash`), `LAB_TEMPERATURE=0`, `recursion_limit=60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows 11 / Python 3.12.0, chạy trực tiếp
- Số lần chạy tác vụ đã dùng / ngân sách: 0 / 25
- Commit của tag `freeze`: (chưa chốt freeze)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Dự đoán subagents đạt điểm tương đương hoặc cao hơn nhẹ baseline (chênh lệch <= 15%), nhưng chi phí token cao hơn 20-50%. Căn cứ: Từ phân tích ở Mục 4 và Mục 5, tác tử không kích hoạt subagent trong không gian tác vụ cục bộ (subagent_calls = 0), nhưng system prompt bổ sung vai trò giúp định hướng suy luận kỹ thuật tốt hơn (như thấy ở code-learn: 0.4 so với 0.2), phù hợp với nghiên cứu của Wang et al. (2023) về vai trò chuyên biệt trong hệ đa tác tử.
- H2 (skills-auto so với baseline): Dự đoán skills-auto đạt điểm cao nhất trên các tác vụ đánh giá (vượt trội baseline từ 20-40%), đặc biệt ở các check kỹ thuật và tuân thủ đặc tả. Căn cứ: 3 skill do Curator sinh ra giải quyết trực tiếp các nguyên nhân gốc ở baseline (Nhóm A: tuân thủ docstring, Nhóm E: không sửa test gốc, Nhóm F: kiểm tra tệp đầu ra). Thực nghiệm ở Phần 3.4 trên code-learn đã chứng minh điểm số tăng vọt từ 0.2 lên 0.6 nhờ vượt qua toàn bộ 6 check kỹ thuật, nhất quán với cơ chế bộ nhớ thủ tục của Voyager (Wang et al., 2023).
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm số của điều kiện skills-auto trên tác vụ học sẽ cao hơn tác vụ đánh giá từ 10-25%. Căn cứ: Các tác vụ đánh giá đưa vào các quy ước tổ chức mới (rule_*) mà Curator chưa từng quan sát trong phản hồi lỗi của tác vụ học. Skill chỉ tổng quát hóa được các quy tắc kỹ thuật chung (nhóm A, B, D, F) mà không dự đoán trước được quy ước tổ chức mới, phản ánh hiện tượng suy giảm hiệu năng do phân phối dữ liệu mới (out-of-distribution).

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ:
   - Nhóm thao tác tệp: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`.
   - Nhóm shell: `execute`.
   - Nhóm uỷ quyền subagent: `task`.
   Công cụ cho phép chạy lệnh shell là `execute`.

2. Mô tả của công cụ `task` về subagent `general-purpose`:
   - Đây là subagent đa năng dùng để nghiên cứu các câu hỏi phức tạp, tìm kiếm file và nội dung, cũng như thực thi các tác vụ nhiều bước khi tác tử chính không chắc chắn tìm ra ngay. Subagent này có quyền truy cập toàn bộ công cụ như tác tử chính (*"This agent has access to all tools as the main agent"*).
   - Về ngữ cảnh: Subagent mặc định là phi trạng thái/cô lập (*"Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report"*). Nó chỉ nhìn thấy duy nhất nội dung prompt mà tác tử chính gửi trực tiếp sang, hoàn toàn không thấy lịch sử hội thoại trước đó hay yêu cầu gốc của tác tử chính trừ khi được truyền đầy đủ trong prompt.

3. System prompt mặc định của Deep Agents rỗng.
   - Một câu hướng dẫn hành vi từ mô tả của công cụ `task`: *"Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead."*
   - Một câu hướng dẫn hành vi từ mô tả của công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `visible_suite_passes` | B | `1 failed, 5 passed in 0.12s`: Tác tử kết thúc mà không chạy lại test để kiểm chứng |
| `code-learn` | `tests_not_modified` | E | `the original files in tests/ must not be modified`: Sửa trực tiếp file test có sẵn thay vì thêm file mới |
| `code-learn` | `parse_price_all_formats` | D | `wrong for: ['(12.00)']`: Bỏ sót định dạng số âm kế toán trong ngoặc đơn |
| `code-learn` | `discount_rounds_half_up` | D | `wrong for: [('10.05', 10, '9.05'), ...]`: Bỏ sót quy tắc làm tròn nửa lên (ROUND_HALF_UP) |
| `code-learn` | `csv_quoting_follows_docstring` | A | `to_csv_row returned 'Desk, large "oak",10.00,2'`: Bỏ qua đặc tả docstring về escaping dấu ngoặc kép |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function ... has type annotations`: Vi phạm quy ước ẩn của tổ chức |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py ...`: Vi phạm quy ước ẩn của tổ chức |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md ...`: Vi phạm quy ước ẩn của tổ chức |
| `data-learn` | `answer.json` (7 checks) | G | `FileNotFoundError: answer.json`: Tác tử gặp GraphRecursionError (vượt giới hạn 60 bước lặp) nên chưa kịp lưu tệp |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv ...`: Vi phạm quy ước ẩn của tổ chức |
| `logs-learn` | `errors.json` (6 checks) | F | `FileNotFoundError: errors.json`: Tác tử dừng sớm sau 2 tool calls mà không tạo tệp kết quả |
| `logs-learn` | `rule_service_names` | E | `RULE: service names in the output are lower-case ...`: Vi phạm quy ước ẩn của tổ chức |

Nhận xét:
- Nhóm lỗi chiếm đa số là **Nhóm E (Vi phạm quy ước tổ chức)** với các check `rule_*` ẩn trong đề bài, và **Nhóm D/A (Bỏ sót định dạng dữ liệu bẩn / Bỏ qua đặc tả docstring)**. Ngoài ra với `data-learn` và `logs-learn`, lỗi do chạm trần đệ quy (Nhóm G) hoặc dừng sớm không tạo file kết quả (Nhóm F).
- Bằng chứng phủ định cho các nhóm A-D: Trên tác vụ `code-learn`, tác tử baseline vẫn đạt 2 check kỹ thuật cốt lõi là `other_caller_fixed` và `low_stock_follows_docstring`, chứng minh mô hình hiểu được logic nghiệp vụ cơ bản.
- Khả năng phòng ngừa: Skill tự sinh (curator) hoàn toàn có thể phòng ngừa hiệu quả Nhóm E (nhắc nhở tuân thủ quy ước không sửa test gốc), Nhóm A (tuân thủ nghiêm ngặt docstring), và Nhóm F/G (yêu cầu kiểm tra sự tồn tại của tệp kết quả trước khi kết thúc).

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  - `code-reviewer`: Chuyên trách rà soát mã nguồn, kiểm tra docstring, type hints và đảm bảo không sửa các file kiểm thử gốc. Thiết kế nhằm phòng ngừa lỗi vi phạm quy ước (nhóm E) và bỏ qua đặc tả (nhóm A).
  - `researcher`: Chuyên trách đọc và phân tích dữ liệu mẫu, cấu trúc log lớn và trích xuất schema mà không làm quá tải context của tác tử chính.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  - `code-learn`: 0 cuộc gọi (`subagent_calls=0`)
  - `data-learn`: 0 cuộc gọi (`subagent_calls=0`)
  - `logs-learn`: 0 cuộc gọi (`subagent_calls=0`)
  - Nhận xét: Tác tử chính chọn tự giải quyết trực tiếp qua các công cụ tệp (`read_file`, `write_file`) và shell (`execute`) thay vì ủy quyền qua công cụ `task`. Điều này xảy ra do mô hình đánh giá không gian bài toán cục bộ đủ nhỏ để tự giải quyết trong 1 luồng mà không cần phân rã cho subagent.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): Không có cuộc gọi giao việc phát sinh trên 3 tác vụ học.
- Ảnh hưởng đến token và thời gian:
  - Trên `code-learn`: Điểm số cải thiện từ 0.2 lên 0.4 (đạt thêm `visible_suite_passes` và `discount_rounds_half_up`), token tăng lên 51,559 (so với baseline 21,049) do mô hình suy luận sâu hơn từ gợi ý vai trò trong system prompt.
  - Trên `data-learn`: Tốn 221,399 tokens (giảm đáng kể so với baseline 377,851 tokens).
  - Trên `logs-learn`: Điểm số đạt 0.11 (đạt check `valid_structure`), tốn 20,341 tokens (thấp hơn baseline 29,140 tokens).

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Curator chạy 1 lần; 0 skill bị xóa vì cả 3 skill sinh ra đều đạt chuẩn định dạng (frontmatter hợp lệ, dưới 100 dòng, không rò rỉ dữ liệu đánh giá).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `adhere-to-docstring-specifications` | Tổng quát cho mọi bài toán lập trình Python cần tuân thủ docstring | Đúng, nhắc nhở đối chiếu kỹ kiểu dữ liệu, tham số và giá trị trả về | 11 dòng, `description: Use when implementing functions to ensure compliance with their docstring specifications.` |
| `enforce-test-immutability` | Tổng quát cho các quy trình kiểm thử phần mềm / benchmark | Đúng, nhấn mạnh không được sửa file test gốc mà chỉ tạo test mới | 11 dòng, `description: Use when modifying test files to ensure original test files remain unchanged.` |
| `validate-file-existence` | Tổng quát cho các tác vụ xử lý dữ liệu và tạo tệp đầu ra | Đúng, yêu cầu kiểm tra tệp bắt buộc phải tồn tại trước khi kết thúc task | 11 dòng, `description: Use when ensuring that required files exist before executing tasks that depend on them.` |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
