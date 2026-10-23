# Kịch bản Thuyết trình Chi tiết Từng Slide & Quy trình Live Demo (Bản v2 — 27 Slides)

**Đề tài Nhóm 5**: *Thuật toán Chia để trị Song song kết hợp Quy hoạch động cho Căn chỉnh Đa chuỗi Protein/ADN (MSA)*  
**Bộ Slide đối chiếu**:
- 🌐 **Google Slides Online**: [Nhóm 5 - PTTKTT - Chia để trị Song song Myers-Miller cho MSA (v2)](https://docs.google.com/presentation/d/1hyApzYpnj-BbdNEk98pTbxLC8Vy3yRR0_qr9GLVxx5E/edit)
- 📊 **File PowerPoint trên máy**: `Slide_Thuyet_Trinh_PTTKTT_Nhom_5_MSA_v2.pptx`

---

## Gợi ý Phân công Thuyết trình (Tổng thời lượng: ~16 – 18 phút + 2 phút Demo)
- **Thành viên 1 (Phần 1 — Slides 1 đến 5 | ~3,5 phút)**: Mở đầu, giải thích bản chất Sinh học, phát biểu bài toán (*Cho cái gì / Yêu cầu làm cái gì*), mô hình điểm BLOSUM62 & Affine Gap, thách thức NP-Hard.
- **Thành viên 2 (Phần 2 — Slides 6 đến 13 | ~5,5 phút)**: Kiến trúc 4 giai đoạn, thuật toán Gotoh Baseline, đột phá Chia để trị Myers-Miller, cây hướng dẫn UPGMA và căn chỉnh Profile-to-Profile.
- **Thành viên 3 (Phần 3 & 4 — Slides 14 đến 21 | ~5,0 phút)**: Kiến trúc song song đa tầng (MPI + OpenMP + Wavefront), chứng minh độ phức tạp chuỗi hình học $2NM$ và 4 thực nghiệm chuẩn quốc tế BAliBASE 3.0.
- **Thành viên 4 (Phần 5 — Slides 22 đến 24 + Live Demo | ~3,5 phút)**: Trực tiếp điều khiển Live Demo trên Web GUI Studio / CLI và trình bày Kết luận, Hướng phát triển.

---

## PHẦN I: KỊCH BẢN LỜI THOẠI CHI TIẾT TỪNG SLIDE (SLIDES 1 – 24)

### 1. Cụm Mở đầu, Giải thích Sinh học & Phát biểu Bài toán (Slides 1 – 5)

#### Slide 1: Trang Bìa (Title Slide) — *(~30 giây)*
* **[Hành động trên bục]**: Đứng hướng về phía Hội đồng, mở sẵn Slide 1 toàn màn hình, chỉ nhẹ vào 4 ô số liệu nổi bật ở giữa slide khi điểm qua kết quả.
* **[Lời thoại]**:
  > "Em xin kính chào Thầy/Cô và các bạn. Hôm nay, Nhóm 5 xin phép trình bày báo cáo đồ án môn Phân tích và Thiết kế Thuật toán với đề tài: **Thuật toán Chia để trị Song song kết hợp Quy hoạch động cho Căn chỉnh Đa chuỗi Protein/ADN (Multiple Sequence Alignment — MSA)**.  
  > Đóng góp cốt lõi của nhóm là giải quyết nút thắt bộ nhớ bậc hai $O(mn)$ của quy hoạch động truyền thống xuống không gian tuyến tính $O(\min(m, n))$ bằng thuật toán Chia để trị Myers-Miller, giúp giảm tới **1.353,5 lần dung lượng RAM** mà vẫn giữ nguyên **100% điểm số tối ưu**, kết hợp song song hóa đa tầng OpenMP/MPI và kiểm chứng trên bộ dữ liệu chuẩn quốc tế BAliBASE 3.0."

#### Slide 2: Bản chất Sinh học — Chuỗi ADN/Protein & Hai Cơ chế Đột biến — *(~60 giây)*
* **[Hành động]**: Chỉ vào **Hộp 1 & 2 (bên trái)** khi nói về chuỗi Protein; sau đó chuyển tay sang **Hộp 3 (màu cam)** và **Hộp 4 (màu xanh lá)** bên phải để giải thích tại sao phải chèn dấu `-`.
* **[Lời thoại]**:
  > "Trước khi đi vào công thức toán học, nhóm xin giải thích ngắn gọn bối cảnh sinh học của bài toán dưới góc nhìn Khoa học máy tính:  
  > - **Thứ nhất (Hộp 1 & 2)**: Mỗi phân tử ADN hay Protein trong cơ thể sống thực chất là một chuỗi văn bản. Với ADN là 4 chữ cái `{A, T, G, C}`, còn với Protein là chuỗi gồm **20 chữ cái đại diện cho 20 loại Amino Acid** có độ dài từ vài trăm đến vài nghìn ký tự. Khi so sánh cùng một loại Protein (ví dụ Hemoglobin vận chuyển Oxy trong máu) giữa Người, Tinh tinh và Cá voi, những vị trí cột ký tự **không hề thay đổi qua hàng triệu năm** chính là vùng lõi quyết định sự sống.  
  > - **Thứ hai (Hộp 3 — Màu cam)**: Tại sao các chuỗi có cùng nguồn gốc tiến hóa lại lệch nhau? Vì trong tự nhiên xảy ra **2 cơ chế đột biến**: Một là *Đột biến Thay thế* (đổi chữ cái này thành chữ cái khác, như `L` thành `I`, không làm đổi độ dài chuỗi); Hai là *Đột biến Thêm hoặc Mất đoạn (Indel)* — tức một vài Amino Acid bị đứt gãy mất đi hoặc chèn thêm vào, làm cho các chuỗi hậu duệ **bị hụt độ dài và trượt lệch vị trí** so với nhau!  
  > - **Thứ ba (Hộp 4 — Màu xanh lá)**: Nhìn vào ví dụ 4 chuỗi ở góc dưới phải: ở Tinh tinh bị mất chữ `P`, ở Cá voi bị mất `P, T, N`. Khi đưa vào máy tính, **việc thuật toán chèn ký tự dấu gạch ngang `-` (gọi là Gap)** chính là khôi phục lại đúng vị trí đã bị mất đoạn trong quá khứ, nhằm kéo các Amino Acid có cùng nguồn gốc tiến hóa thẳng hàng về chung một cột!"

#### Slide 3: Phát biểu Bài toán MSA: Cho Cái Gì (Input) & Yêu Cầu Làm Cái Gì (Output)? — *(~60 giây)*
* **[Hành động]**: Chỉ rõ vào khung **INPUT (Xanh dương bên trái)**, sang khung **OUTPUT (Xanh lá bên phải)**, rồi quét xuống **Khung 3 Ràng buộc ở đáy**.
* **[Lời thoại]**:
  > "Từ bản chất sinh học đó, bài toán Căn chỉnh Đa chuỗi (MSA) được phát biểu tường minh như sau:  
  > - **Bài toán CHO CÁI GÌ (Input — Khung trái)?** Cho một tập gồm $k$ chuỗi sinh học $S_1, S_2, \dots, S_k$ ($k \ge 3$) có **độ dài ban đầu khác nhau** $n_1, n_2, \dots, n_k$. Ví dụ trên slide: chuỗi $S_1$ dài 10 ký tự, $S_2$ dài 9 ký tự và $S_3$ chỉ dài 8 ký tự. Cùng với đó là bảng điểm thay thế BLOSUM62 và tham số phạt khoảng trống.  
  > - **Bài toán YÊU CẦU LÀM CÁI GÌ (Output — Khung phải)?** Thuật toán phải tìm vị trí tối ưu để chèn các dấu gạch ngang `-` vào các chuỗi sao cho tạo thành một **Ma trận chữ nhật $A$ gồm $k$ hàng và $L$ cột** (trong ví dụ là cùng đưa về độ dài $L = 10$), thỏa mãn **3 ràng buộc bắt buộc ở khung dưới**:  
  >   1. *Đồng nhất độ dài*: Mọi hàng sau khi chèn `-` phải dài bằng nhau và bằng $L$.  
  >   2. *Bảo toàn thứ tự gốc*: Tuyệt đối không được đảo vị trí hay làm mất chữ cái nào — tức nếu xóa hết dấu `-` đi thì phải thu lại đúng 100% chuỗi gốc ban đầu.  
  >   3. *Không dư thừa*: Không được có cột nào chứa toàn dấu `-`.  
  > - **Mục tiêu tối ưu**: Trong hàng tỷ cách chèn dấu `-` hợp lệ, ta phải tìm ra ma trận $A^*$ có **Tổng điểm tương đồng cặp đôi trên tất cả các cột (Sum-of-Pairs Score) trừ đi điểm phạt khoảng trống là LỚN NHẤT**!"

#### Slide 4: Tại sao dùng Ma trận BLOSUM62 & Phạt Khoảng trống Affine (-10, -1)? — *(~50 giây)*
* **[Hành động]**: Chỉ vào các con số ví dụ ở cột trái (`+11`, `+3`, `-4`) và phép so sánh ❌ Cách 1 (`-30 điểm`) vs. ✅ Cách 2 (`-12 điểm`) ở cột phải.
* **[Lời thoại]**:
  > "Một câu hỏi đặt ra là: Tại sao ta không chấm điểm đơn giản kiểu *'2 chữ giống nhau được +1, khác nhau bị -1'* như bài toán Xâu con chung dài nhất (LCS)? Có 2 lý do sinh học cốt lõi:  
  > - **Bên trái — Ma trận BLOSUM62**: 20 loại Amino Acid có tính chất hóa lý khác nhau. Hai Amino Acid khác tên nhưng **cùng tính chất kỵ nước** như `I` và `V` thay thế cho nhau trong tự nhiên rất dễ xảy ra, nên bảng BLOSUM62 vẫn thưởng **+3 điểm**. Ngược lại, thay thế hai chất trái ngược nhau như `L` với `D` sẽ làm hỏng cấu trúc Protein nên bị phạt nặng **-4 điểm**.  
  > - **Bên phải — Phạt Khoảng trống Affine ($\gamma(g) = -10 - (g-1)\times 1$)**: Trong tự nhiên, **1 lần đứt gãy ADN làm mất liền 3 ký tự** dễ xảy ra hơn rất nhiều so với **3 lần đứt gãy rời rạc ở 3 nơi**. Do đó, hệ thống phạt rất nặng khi **mở mới** một khoảng trống ($G_{\text{open}} = -10$), nhưng chỉ phạt rất nhẹ khi **kéo dài** khoảng trống đó ($G_{\text{ext}} = -1$). Nhìn vào ví dụ ở góc dưới phải: cùng chèn 3 dấu `-`, nếu xé lẻ 3 nơi (Cách 1) sẽ bị phạt tới **-30 điểm**, còn gom thành 1 khối liền mạch (Cách 2) chỉ bị phạt **-12 điểm**!"

#### Slide 5: Thách thức Tính toán: NP-Hard $O(2^k N^k)$ & Nút thắt Bộ nhớ Gotoh $O(mn)$ — *(~45 giây)*
* **[Hành động]**: Điểm qua 3 thẻ rào cản (Đỏ, Cam, Tím) ở trên và nhấn mạnh vào **Khung Giải pháp 3 Trụ cột màu xanh lá** ở dưới.
* **[Lời thoại]**:
  > "Tuy nhiên, khi giải bài toán này trên máy tính, chúng ta đối mặt với 3 rào cản lớn:  
  > 1. **Thẻ Đỏ**: Nếu dùng Quy hoạch động chính xác đồng thời trên $k$ chuỗi, ta cần một bảng $k$ chiều tốn $O(N^k)$ bộ nhớ và $O(2^k N^k)$ thời gian — bài toán đã được chứng minh là **NP-Complete**, hoàn toàn bất khả thi ngay khi $k \ge 5$.  
  > 2. **Thẻ Cam**: Ngay cả khi tách thành từng cặp 2 chuỗi bằng thuật toán Gotoh (1982), việc lưu 3 ma trận 2 chiều tốn $O(mn)$ bộ nhớ. Với 2 chuỗi dài $10.000$ ký tự, chỉ riêng 1 cặp đã ngốn **1,2 GB RAM** — nếu chạy đa luồng sẽ lập tức tràn bộ nhớ!  
  > 3. **Khung Xanh lá ở dưới**: Để giải quyết triệt để, Nhóm 5 kết hợp 3 trụ cột: **(1) Chia để trị Myers-Miller** ép bộ nhớ từ $O(mn)$ xuống tuyến tính $O(\min(m,n))$; **(2) Căn chỉnh Tiến bộ theo Cây UPGMA + Profile** đưa bài toán NP-Hard về đa thức; và **(3) Song song hóa Đa tầng Hybrid MPI + OpenMP**. Phần tiếp theo bạn [Tên Thành viên 2] sẽ trình bày chi tiết thiết kế thuật toán."

---

### 2. Cụm Thiết kế Thuật toán Chia để trị Myers-Miller & Progressive MSA (Slides 6 – 13)

#### Slide 6: [FULL-BLEED DIAGRAM] Tổng quan Kiến trúc Pipeline 4 Giai đoạn — *(~45 giây)*
* **[Hành động]**: Chỉ tay dọc theo 4 khối lớn từ trên xuống dưới trên sơ đồ toàn màn hình.
* **[Lời thoại]**:
  > "Em xin tiếp tục phần 2 về Thiết kế Thuật toán Lõi. Trên màn hình là sơ đồ kiến trúc 4 giai đoạn của phương pháp Căn chỉnh Đa chuỗi Tiến bộ (Progressive MSA):  
  > - **Giai đoạn 1**: Từ $k$ chuỗi đầu vào, hệ thống tính điểm tương đồng cho tất cả $\frac{k(k-1)}{2}$ cặp chuỗi bằng quy hoạch động 1 chiều để lập **Ma trận khoảng cách tiến hóa**.  
  > - **Giai đoạn 2**: Từ ma trận khoảng cách, thuật toán gom cụm **UPGMA** xây dựng **Cây hướng dẫn nhị phân (Guide Tree)**.  
  > - **Giai đoạn 3**: Bộ lập lịch **Tree Scheduler** phân tích các nhánh cây con độc lập để giao việc cho các luồng CPU.  
  > - **Giai đoạn 4**: Đi từ các nút lá lên nút gốc, hợp nhất từng cặp nhóm chuỗi (**Profile-to-Profile**) bằng thuật toán **Chia để trị không gian tuyến tính Myers-Miller**."

#### Slide 7: Quy hoạch Động Gotoh (1982) Baseline & Nút thắt Truy vết — *(~50 giây)*
* **[Hành động]**: Chỉ vào 3 phương trình $M, I_x, I_y$ bên trái, sau đó nhấn mạnh vào hộp màu xanh và màu đỏ bên phải.
* **[Lời thoại]**:
  > "Trước hết, hãy nhìn vào thuật toán quy hoạch động chuẩn của Gotoh (1982) cho 2 chuỗi dài $m$ và $n$. Vì có phạt mở khoảng trống (-10) khác với kéo dài khoảng trống (-1), tại mỗi ô $(i, j)$ ta phải lưu **3 trạng thái**: $M(i,j)$ là khớp ký tự đi chéo, $I_x(i,j)$ là mở/kéo dài khoảng trống dọc, và $I_y(i,j)$ là mở/kéo dài khoảng trống ngang.  
  > **Nhận xét đột phá ở cột bên phải là**: Trong cả 3 phương trình trên, dòng thứ $i$ chỉ phụ thuộc duy nhất vào dòng $i-1$ liền trước. Nghĩa là nếu **chỉ cần tính điểm số cuối cùng** (như ở Bước 1 tính khoảng cách), ta chỉ cần lưu đúng **2 hàng trong RAM**, tốn bộ nhớ tuyến tính $O(n)$.  
  > Lý do duy nhất khiến Gotoh tốn $O(mn)$ bộ nhớ là để giữ lại toàn bộ bảng $m \times n$ nhằm **lần ngược mũi tên truy vết (Backtracking)** từ ô cuối $(m,n)$ về $(0,0)$. Vậy làm sao tìm được đường đi mà chỉ dùng bộ nhớ 1 chiều $O(n)$?"

#### Slide 8: Thuật toán Chia để trị Tuyến tính Myers-Miller / Hirschberg (1988) — *(~60 giây)*
* **[Hành động]**: Chỉ vào 4 bước bên trái, sau đó giải thích kỹ công thức tìm $j^*$ và số hạng `-G_open + G_ext` ở khung bên phải.
* **[Lời thoại]**:
  > "Câu trả lời chính là thuật toán Chia để trị của Myers và Miller (1988) — mở rộng ý tưởng của Hirschberg cho hàm phạt Affine Gap:  
  > - **Bước 1 (Chia)**: Ta cắt đôi ma trận theo chiều ngang tại dòng chính giữa $i^* = \lfloor m / 2 \rfloor$.  
  > - **Bước 2 (Quét Xuôi — Forward Pass)**: Ta chạy quy hoạch động 2 dòng (chỉ tốn $O(n)$ RAM) từ góc trên-trái $(0,0)$ xuống tới dòng giữa $i^*$, thu được mảng điểm 1 chiều `Fwd[j]`.  
  > - **Bước 3 (Quét Ngược — Backward Pass)**: Ta chạy quy hoạch động 2 dòng theo chiều ngược lại từ góc dưới-phải $(m,n)$ lên tới dòng giữa $i^*$, thu được mảng điểm hậu tố `Bwd[j]`.  
  > - **Bước 4 (Tổ hợp tìm điểm cắt $j^*$ — Khung phải)**: Đường căn chỉnh tối ưu toàn cục từ $(0,0)$ đến $(m,n)$ bắt buộc phải đi qua dòng giữa $i^*$ tại cột $j^*$ nào có **tổng điểm tiền tố cộng hậu tố lớn nhất**!  
  > Đặc biệt, ở nhánh thứ hai của công thức `max`, nhóm xử lý bài toán **Hợp nhất khoảng trống (Gap Coalescing)**: nếu một khoảng trống mở từ nửa trên kéo dài xuyên qua đường cắt $i^*$ xuống nửa dưới, cả lượt xuôi và lượt ngược đều đã phạt $G_{\text{open}}$ (-10) một lần. Do đó ta phải **trừ đi $G_{\text{open}}$ và cộng bù $G_{\text{ext}}$** để nối 2 nửa thành 1 khoảng trống liên tục duy nhất!"

#### Slide 9: [FULL-BLEED DIAGRAM] Minh họa Hình học Nhát cắt Giữa $i^* = \lfloor m/2 \rfloor$ — *(~40 giây)*
* **[Hành động]**: Chỉ trực tiếp lên sơ đồ lớn: đường màu đỏ ở giữa ($i = m/2$), mũi tên xanh dương (Forward), mũi tên xanh lá (Backward), ngôi sao vàng $(i^*, j^*)$ và 2 hộp con.
* **[Lời thoại]**:
  > "Nhìn vào sơ đồ hình học toàn màn hình này, chúng ta thấy ngay vẻ đẹp của thuật toán Chia để trị:  
  > Lượt quét tiến (màu xanh dương) và lượt quét lùi (màu xanh lá) gặp nhau tại đường chia giữa màu đỏ và xác định được giao điểm tối ưu **ngôi sao màu vàng $(i^*, j^*)$**.  
  > Ngay khi tìm được ngôi sao này, đường đi tối ưu chỉ có thể nằm trong **Bài toán con 1 (góc trên-trái)** và **Bài toán con 2 (góc dưới-phải)**. Toàn bộ 2 góc phần tư màu trắng còn lại bị loại bỏ hoàn toàn! Tổng diện tích của 2 bài toán con giảm đi **đúng một nửa** sau mỗi bước chia đôi."

#### Slide 10: Xây dựng Cây Hướng dẫn UPGMA (Lý thuyết) — *(~40 giây)*
* **[Hành động]**: Chỉ vào công thức chuẩn hóa khoảng cách $d(A,B) \in [0, 1]$ bên trái và công thức cập nhật cụm trung bình trọng số bên phải.
* **[Lời thoại]**:
  > "Sau khi đã có công cụ căn chỉnh cặp đôi tối ưu bộ nhớ, làm sao mở rộng ra cho $k$ chuỗi?  
  > Nếu ta ghép các chuỗi theo thứ tự ngẫu nhiên, việc ghép nhầm 2 chuỗi rất khác biệt nhau trước sẽ sinh ra các khoảng trống sai lệch. Vì vậy, hệ thống chuyển điểm tương đồng cặp đôi thành **khoảng cách tiến hóa chuẩn hóa $d(A,B)$ thuộc đoạn $[0, 1]$** (hai chuỗi giống hệt nhau có khoảng cách bằng $0$).  
  > Sau đó, thuật toán gom cụm phân cấp **UPGMA** liên tục tìm 2 cụm có khoảng cách nhỏ nhất (họ hàng gần nhất) để ghép trước, và cập nhật khoảng cách tới các cụm còn lại bằng trung bình cộng có trọng số."

#### Slide 11: [FULL-BLEED DIAGRAM] Minh họa Gom cụm Ma trận Khoảng cách thành Cây UPGMA — *(~30 giây)*
* **[Hành động]**: Chỉ từ bảng ma trận khoảng cách bên trái sang các bước gom cụm tạo thành cây nhị phân bên phải trên hình lớn.
* **[Lời thoại]**:
  > "Sơ đồ toàn màn hình này minh họa trực quan quá trình UPGMA: từ bảng ma trận khoảng cách tam giác đối xứng bên trái, cặp chuỗi có khoảng cách nhỏ nhất được nối lại thành nút nhánh đầu tiên ở đáy cây, tiếp tục hợp nhất dần lên cho tới khi hội tụ tại **Nút gốc (Root)**. Cây nhị phân này chính là bản đồ chỉ đường cho Giai đoạn 4."

#### Slide 12: Căn chỉnh Profile-to-Profile & Nguyên lý *"Once a gap, always a gap"* — *(~50 giây)*
* **[Hành động]**: Chỉ vào công thức hàm điểm cột `PSP(x, y)` bên trái và ví dụ chèn cột `[ - ]` đồng bộ ở khung bên phải.
* **[Lời thoại]**:
  > "Ở các nút nhánh bên trong cây UPGMA, ta cần hợp nhất một nhóm chuỗi đã căn chỉnh (**Profile $P_1$**) với một nhóm chuỗi khác (**Profile $P_2$**).  
  > Điểm tinh tế trong thiết kế của nhóm là **tái sử dụng nguyên vẹn bộ khung Chia để trị Myers-Miller**: ta coi mỗi **cột** của Profile $P_1$ như một phần tử $x$, mỗi **cột** của Profile $P_2$ như một phần tử $y$, và thay phép tra bảng BLOSUM62 đơn lẻ bằng **Hàm điểm trung bình cặp cột $\text{PSP}(x, y)$** ở khung bên trái.  
  > Đồng thời, ở khung bên phải, hệ thống tuân thủ nghiêm ngặt quy tắc **'Once a gap, always a gap'**: khi thuật toán quyết định chèn một khoảng trống vào Profile $P_1$, cả một cột gồm toàn dấu `-` được chèn đồng loạt vào tất cả các chuỗi con trong $P_1$, giúp bảo toàn 100% các cột đã gióng hàng đúng ở các bước trước!"

#### Slide 13: [FULL-BLEED DIAGRAM] Sơ đồ Căn chỉnh Profile-to-Profile — *(~30 giây)*
* **[Hành động]**: Chỉ vào 2 khối Profile đầu vào, vector tần suất cột và khối Profile hợp nhất ở đầu ra trên hình lớn.
* **[Lời thoại]**:
  > "Hình minh họa trên slide cho thấy cách hệ thống tối ưu tốc độ tính hàm $\text{PSP}(x, y)$: thay vì duyệt từng cặp chuỗi con mỗi lần tính, hệ thống lưu sẵn **vector tần suất xuất hiện của 20 loại Amino Acid trên từng cột**, giúp phép tính điểm khớp giữa 2 cột Profile diễn ra siêu nhanh. Tiếp theo, bạn [Tên Thành viên 3] sẽ trình bày phần Kiến trúc Song song và Thực nghiệm."

---

### 3. Cụm Kiến trúc Song song Đa tầng & Chứng minh Độ phức tạp (Slides 14 – 17)

#### Slide 14: [FULL-BLEED DIAGRAM] Kiến trúc Song song Đa tầng Hybrid (MPI + OpenMP) — *(~45 giây)*
* **[Hành động]**: Chỉ vào khối Stage 1 (MPI + OpenMP) và Stage 3 (Wavefront Tree Scheduler) trên sơ đồ kiến trúc song song.
* **[Lời thoại]**:
  > "Em xin tiếp tục Phần 3 về Kiến trúc Tính toán Song song và Phân tích Độ phức tạp.  
  > Trên sơ đồ toàn màn hình là kiến trúc song song đa tầng kết hợp **MPI** (cho cụm nhiều máy tính) và **OpenMP** (cho CPU đa nhân):  
  > - **Ở Stage 1 (Tính ma trận khoảng cách)**: Toàn bộ $\frac{k(k-1)}{2}$ cặp chuỗi hoàn toàn độc lập dữ liệu. Trên cụm MPI, nhóm chia tải theo vòng tròn **Block-Cyclic (`idx % P == rank`)** và gom kết quả bằng `MPI_Allgatherv`. Bên trong mỗi Node, OpenMP phân phối các cặp qua các luồng bằng cơ chế lập lịch động `schedule(dynamic, 1)` để chống lệch tải khi độ dài các chuỗi không đều nhau.  
  > - **Ở Stage 3 (Duyệt cây UPGMA)**: Nhóm thiết kế bộ lập lịch **Level-Set Tree Scheduler** gom tất cả các nút nhánh độc lập ở cùng một tầng độ cao của cây để chạy song song."

#### Slide 15: [FULL-BLEED DIAGRAM] Song song hóa Đường chéo phụ Wavefront Anti-Diagonal DP — *(~40 giây)*
* **[Hành động]**: Chỉ vào các đường chéo màu trên ma trận quy hoạch động của hình lớn.
* **[Lời thoại]**:
  > "Thậm chí, ngay bên trong một phép quy hoạch động của 2 chuỗi rất dài, làm sao để nhiều luồng cùng tính chung 1 ma trận khi ô $(i, j)$ phụ thuộc vào ô bên trái, ô phía trên và ô chéo trên?  
  > Như sơ đồ Wavefront trên màn hình minh họa: tất cả các ô nằm trên **cùng một đường chéo phụ $i + j = d$** hoàn toàn không phụ thuộc dữ liệu vào nhau, mà chỉ phụ thuộc vào 2 đường chéo $d-1$ và $d-2$ trước đó. Nhờ vậy, hệ thống có thể đẩy mặt sóng tính toán song song dọc theo từng đường chéo phụ!"

#### Slide 16: Chứng minh Toán học Độ phức tạp Bộ nhớ $O(\min(m,n))$ & Thời gian $2 \cdot O(mn)$ — *(~60 giây)*
* **[Hành động]**: Chỉ rõ vào **Định lý 1 (Cột trái)** rồi nhấn mạnh vào phép khai triển tổng chuỗi hình học `1 + 1/2 + 1/4 + ... = 2` ở **Định lý 2 (Cột phải)**.
* **[Lời thoại]**:
  > "Slide thứ 16 trình bày 2 định lý chứng minh độ phức tạp cốt lõi của báo cáo:  
  > - **Định lý 1 (Bên trái — Độ phức tạp Không gian)**: Tại mỗi bước chia để trị, lượt quét xuôi và ngược chỉ cấp phát 6 mảng 1 chiều kích thước $n+1$ và **giải phóng/tái sử dụng ngay trước khi gọi đệ quy** xuống 2 nửa con. Cộng với chiều cao cây đệ quy tối đa $\log_2 m$ trên ngăn xếp, bộ nhớ đỉnh cho 1 cặp chuỗi chỉ là $O(\min(m, n))$, và cho toàn hệ thống $k$ chuỗi chỉ là **$O(k \cdot L)$ — tức tuyến tính hoàn toàn**!  
  > - **Định lý 2 (Bên phải — Độ phức tạp Thời gian)**: Một câu hỏi rất hay được đặt ra là: *'Chia để trị gọi đệ quy $\log_2 m$ tầng, vậy thời gian có bị nhân thêm $\log_2 m$ thành $O(mn \log m)$ không?'*  
  > Phép chứng minh ở khung màu xanh lá chỉ ra rằng: Ở mức 0, quét nửa trên và nửa dưới tốn $c \cdot mn$. Sang mức 1, dù cột cắt tối ưu $j^*$ rơi vào vị trí nào đi nữa, tổng diện tích của 2 bài toán con luôn là $\frac{m}{2} j^* + \frac{m}{2}(n - j^*) = \mathbf{\frac{1}{2} mn}$ (vì $j^*$ tự triệt tiêu!).  
  > Cứ mỗi tầng đệ quy, tổng diện tích giảm đi một nửa, tạo thành tổng chuỗi hình học hội tụ: $1 + \frac{1}{2} + \frac{1}{4} + \frac{1}{8} + \dots \le \mathbf{2}$. Như vậy, thời gian tính toán chỉ gấp đôi hằng số ($2\times$) so với Gotoh và giữ nguyên bậc **$O(mn)$**!"

#### Slide 17: Bảng Tổng hợp Độ phức tạp & Định luật Amdahl / Gustafson — *(~40 giây)*
* **[Hành động]**: Chỉ vào dòng tô sáng màu xanh lá trên bảng, rồi chỉ xuống 2 hộp Định luật Amdahl và Gustafson bên dưới.
* **[Lời thoại]**:
  > "Bảng tổng hợp trên slide đối chiếu toàn bộ các giai đoạn. Ở nửa dưới, nhóm phân tích giới hạn tăng tốc song song bằng **Định luật Amdahl** và **Định luật Gustafson**: với một bộ dữ liệu nhỏ cố định, nút gốc của cây UPGMA phải đợi 2 nhánh con hoàn tất nên tạo ra tỷ lệ tuần tự $(1-f)$ khoảng $15\% - 25\%$. Tuy nhiên, theo Định luật Gustafson, khi số lượng chuỗi $k$ tăng lớn, Giai đoạn 1 tính ma trận khoảng cách bậc hai $O(k^2 N^2)$ chiếm tỷ trọng áp đảo, giúp hiệu suất song song hóa tăng mạnh theo quy mô bài toán."

---

### 4. Cụm Kết quả Thực nghiệm trên Chuẩn Quốc tế BAliBASE 3.0 (Slides 18 – 21)

#### Slide 18: [FULL-BLEED CHART] Thực nghiệm 1 — Kiểm chứng Nén Bộ nhớ Gotoh $O(N^2)$ vs. Myers-Miller $O(N)$ — *(~45 giây)*
* **[Hành động]**: Chỉ vào cột đỏ cao vọt vs. cột xanh thấp ở nhóm cuối cùng (`Long Seq 897 aa`) và con số `1353.5x` trên đường màu cam.
* **[Lời thoại]**:
  > "Bước sang Phần 4 — Thực nghiệm kiểm chứng trên bộ dữ liệu chuẩn quốc tế **BAliBASE 3.0**.  
  > Biểu đồ toàn màn hình đầu tiên so sánh lượng RAM đỉnh giữa Gotoh truyền thống (cột đỏ) và Myers-Miller của nhóm (cột xanh dương) trên **thang đo Logarit**, cùng đường màu cam biểu diễn hệ số giảm bộ nhớ:  
  > - Ở chuỗi ngắn 85 ký tự (`RV11`), bộ nhớ đã giảm **129,5 lần**.  
  > - Khi độ dài chuỗi tăng lên 421 ký tự (`RV12`), mức tiết kiệm vọt lên **726,5 lần**.  
  > - Và ở chuỗi dài 897 ký tự (`Long Seq`), trong khi Gotoh ngốn tới **9.495 KB (~9,5 MB)** thì Myers-Miller chỉ tốn đúng **7,02 KB** — tức **giảm 1.353,5 lần bộ nhớ RAM**, đồng thời điểm số căn chỉnh trùng khớp tuyệt đối **100%** trên mọi bộ thử nghiệm!"

#### Slide 19: [FULL-BLEED CHART] Thực nghiệm 2 — Tốc độ Tăng tốc Đa luồng OpenMP (Speedup) — *(~45 giây)*
* **[Hành động]**: Chỉ vào đường màu xanh dương (`BB20001`), đường màu xanh lá (`Benchmark 40 seqs`) và đường chấm gạch màu đỏ (`Amdahl's Upper Bound`).
* **[Lời thoại]**:
  > "Thực nghiệm thứ hai đánh giá tốc độ tăng tốc đa luồng OpenMP từ 1 đến 8 luồng:  
  > - Trên các họ gen lớn như `BB20001` (16 chuỗi, phân vùng RV20 — đường xanh dương) và `Benchmark 40 chuỗi` (gồm 780 cặp quy hoạch động — đường xanh lá), thời gian thực thi giảm mạnh từ **5,42 giây xuống 3,36 giây**, đạt hệ số tăng tốc **Speedup cực đại từ $1,61\times$ đến $1,73\times$**.  
  > - Đường thực nghiệm bám sát quy luật tiệm cận của đường cận trên Amdahl (màu đỏ), phản ánh đúng chi phí hợp nhất tuần tự tại nút gốc của cây UPGMA."

#### Slide 20: [FULL-BLEED CHART] Thực nghiệm 3 — Đánh giá Độ chính xác Sinh học (SP & TC Score) trên BAliBASE 3.0 — *(~45 giây)*
* **[Hành động]**: Chỉ vào cụm cột ở giữa (`RV12: SP = 0.868, TC = 0.681`) và giải thích ngắn gọn 2 thước đo SP/TC.
* **[Lời thoại]**:
  > "Không chỉ chạy nhanh và tốn ít RAM, kết quả căn chỉnh có chính xác về mặt sinh học không? Nhóm đã cài đặt module chấm điểm tự động đối chiếu trực tiếp với các file căn chỉnh cấu trúc 3D chuẩn của BAliBASE 3.0 theo 2 thước đo quốc tế: **SP Score** (tỷ lệ cặp ký tự căn chỉnh đúng) và **TC Score** (tỷ lệ cột đúng hoàn toàn trên tất cả các chuỗi):  
  > - Trên phân vùng **RV12 (độ tương đồng trung bình 20–40%)**, hệ thống đạt độ chính xác rất cao với **SP trung bình đạt 86,8%** và **TC đạt 68,1%** (riêng mẫu `BB12003` đạt tới 93% SP).  
  > - Ngay cả trên phân vùng khó nhất là **RV11 (Vùng hoàng hôn dưới 20% tương đồng)**, mẫu `BB11001` vẫn đạt **98,2% SP Score** và **96,5% TC Score**."

#### Slide 21: [FULL-BLEED CHART] Thực nghiệm 4 — Đối sánh với ClustalW 2.1 & MUSCLE v3.8 — *(~45 giây)*
* **[Hành động]**: Chỉ vào cột màu xanh lá thấp nhất ở Hình (A) bên trái (`26.8 MB`) và cột màu xanh lá ở Hình (B) bên phải (`0.488`).
* **[Lời thoại]**:
  > "Thực nghiệm thứ tư đặt hệ thống của Nhóm 5 cạnh hai phần mềm tiêu chuẩn quốc tế là **ClustalW 2.1** và **MUSCLE v3.8** trên bộ dữ liệu lớn `BB20001`:  
  > - **Ở biểu đồ (A) bên trái (Dung lượng RAM đỉnh)**: Hệ thống của Nhóm 5 tiêu thụ RAM thấp nhất — chỉ **26,8 MB**, giảm gần **50%** so với ClustalW (`48,5 MB`) và MUSCLE (`52,0 MB`), và thấp hơn 12 lần so với Gotoh truyền thống (`320 MB`).  
  > - **Ở biểu đồ (B) bên phải (Độ chính xác SP Score)**: Nhóm 5 đạt **0,488**, vượt qua ClustalW 2.1 (`0,472`) và bám rất sát MUSCLE v3.8 (`0,495` — vốn có thêm nhiều vòng lặp tinh chỉnh hậu xử lý). Tiếp theo, bạn [Tên Thành viên 4] sẽ trình bày hệ thống Web GUI Studio và thực hiện Live Demo."

---

### 5. Cụm Giao diện Web GUI Studio, Live Demo & Kết luận (Slides 22 – 24)

#### Slide 22: [FULL-BLEED UI 1] Giao diện Web GUI Studio — Ma trận Căn chỉnh Màu Hóa học — *(~30 giây)*
* **[Hành động]**: Chỉ vào các dải cột màu đồng nhất trên ảnh chụp giao diện lớn và biểu đồ cột ở đáy.
* **[Lời thoại]**:
  > "Em xin tiếp tục Phần 5. Để hỗ trợ trực quan hóa sinh học và kiểm chứng hiệu năng tức thì, nhóm đã xây dựng hệ thống **Web GUI Studio** kết nối trực tiếp tới nhân thực thi C++17 (`msa_align.exe`).  
  > Trên màn hình là giao diện **Ma trận căn chỉnh đa chuỗi** được tô màu tự động theo chuẩn hóa lý ClustalX/Jalview cùng thanh biểu đồ cột **Conservation Histogram** đo mức độ bảo tồn tiến hóa tại từng vị trí cột."

#### Slide 23: [FULL-BLEED UI 2] Cây Phát sinh UPGMA SVG & Bảng Điều khiển Benchmark (Chuyển sang Live Demo) — *(~20 giây lời dẫn trước khi bấm `Alt + Tab` sang trình duyệt)*
* **[Hành động]**: Chỉ nhanh vào ảnh Cây UPGMA bên trái và Dashboard bên phải, sau đó bấm `Alt + Tab` chuyển sang cửa sổ trình duyệt đang mở sẵn `http://localhost:8000`.
* **[Lời thoại]**:
  > "Bên cạnh ma trận màu, Web Studio còn cung cấp trình xem **Cây phát sinh loài UPGMA dạng đồ họa vector SVG tương tác** (bên trái) và **Bảng điều khiển Benchmark thời gian thực** (bên phải). Ngay sau đây, em xin phép chuyển sang màn hình ứng dụng trong khoảng 90 giây để trình diễn trực tiếp (Live Demo) quá trình chạy thuật toán!"

#### Slide 24: Tổng kết Đóng góp Khoa học, Kiểm thử Tự động & Hướng Phát triển — *(~45 giây)*
* **[Hành động]**: Quay lại Slide 24 sau khi kết thúc Demo, điểm qua 4 kết quả bên trái và 3 hướng mở rộng bên phải.
* **[Lời thoại]**:
  > "Để kết luận phần trình bày, đồ án của Nhóm 5 đã hoàn thành trọn vẹn 4 mục tiêu đề ra:  
  > 1. Thiết kế và cài đặt thành công thuật toán **Chia để trị Myers-Miller kết hợp Profile-to-Profile**, nén bộ nhớ tới **1.353,5 lần** về mức tuyến tính $O(\min(m,n))$ với điểm số khớp **100%** so với Gotoh.  
  > 2. Xây dựng kiến trúc song song đa tầng **Hybrid OpenMP + MPI** đạt Speedup **1,73 lần** trên CPU đa nhân.  
  > 3. Kiểm chứng thực nghiệm trên chuẩn quốc tế **BAliBASE 3.0**, đạt **86,8% SP Score** trên RV12 và tiết kiệm gần một nửa bộ nhớ so với ClustalW và MUSCLE.  
  > 4. Toàn bộ mã nguồn C++17 vượt qua **342 bộ kiểm thử tự động (với 139.463 assertions đạt 100% Pass)**.  
  > Trong tương lai, trên nền tảng bộ nhớ tuyến tính rất nhẹ này, nhóm định hướng tích hợp thêm pha **Tinh chỉnh lặp (Iterative Refinement)** kiểu MUSCLE để nâng cao hơn nữa điểm số TC trên các họ gen lớn, đồng thời mở rộng tăng tốc bằng tập lệnh **SIMD AVX-512 và GPU CUDA**.  
  > Bài trình bày của Nhóm 5 đến đây là kết thúc. Nhóm xin cảm ơn Thầy/Cô và các bạn đã lắng nghe và rất mong nhận được các câu hỏi phản biện từ Hội đồng ạ!"

---

## PHẦN II: QUY TRÌNH THAO TÁC TRÌNH DIỄN DEMO THỰC TẾ (LIVE DEMO RUNBOOK)

### Bước 0 — Chuẩn bị Kỹ thuật 5 Phút Trước Khi Lên Bục (Pre-Flight Checklist):
1. Mở sẵn 1 cửa sổ PowerShell tại `D:\workspace\MSA`, chạy lệnh khởi động máy chủ Web GUI:
   ```powershell
   .\run_gui.bat
   ```
   *(Máy chủ FastAPI sẽ chạy tại `http://localhost:8000` và kết nối sẵn với file thực thi C++17 `build\Release\msa_align.exe`)*.
2. Trên trình duyệt Chrome/Edge:
   - **Tab 1**: Mở bộ slide Google Slides v2 ở chế độ Thuyết trình.
   - **Tab 2**: Mở sẵn `http://localhost:8000` (zoom trình duyệt ở mức `100%` hoặc `110%` để chữ hiển thị to, rõ trên máy chiếu).
3. Mở sẵn thêm **1 cửa sổ PowerShell thứ hai** (chỉnh font chữ `Consolas 18pt`) đặt ở thư mục `D:\workspace\MSA` để sẵn sàng chạy 3 lệnh CLI nếu Giảng viên yêu cầu kiểm tra dưới dòng lệnh.

### Kịch bản Live Demo trên Web GUI Studio (4 Pha — Đúng 90 đến 120 Giây)

#### Pha 1 (20 giây): Nạp Dữ liệu Chuẩn & Cấu hình Tham số Thuật toán
* **Thao tác chuột**:
  1. Tại cột điều khiển bên trái (*Input & Control Panel*), bấm vào danh sách **Preset Dataset** và chọn **`BAliBASE RV12 (BB12001.msf)`**.
  2. Kéo thanh trượt **OpenMP Threads** lên **`4`** (hoặc `8`). Giữ nguyên `Gap Open = -10`, `Gap Extend = -1`.
  3. Tích chọn bật cả 2 chế độ: **Baseline Comparison (Gotoh vs. Myers-Miller)** và **Multi-threaded Benchmark**.
  4. Bấm nút màu xanh **Run Alignment**.
* **Lời nói khi thao tác**:
  > *"Trên giao diện Web Studio, em chọn bộ dữ liệu chuẩn quốc tế BAliBASE RV12 (`BB12001`), thiết lập phạt khoảng trống Affine (-10, -1), bật 4 luồng OpenMP cùng chế độ đối chứng trực tiếp với Gotoh Baseline và nhấn Run Alignment."*

#### Pha 2 (35 giây): Giải thích Ma trận Căn chỉnh Màu Hóa học & Mức độ Bảo tồn
* **Thao tác chuột**:
  1. Di chuột dọc theo thanh cuộn ngang của **Interactive Color-Coded MSA Matrix**.
  2. Chỉ con trỏ chuột vào một cụm cột có màu đồng nhất từ trên xuống dưới (ví dụ các cột màu Xanh dương hoặc Đỏ) và chỉ xuống các cột cao trên biểu đồ **Conservation Histogram** ngay bên dưới.
* **Lời nói khi thao tác**:
  > *"Chỉ sau chưa đầy nửa giây, nhân C++17 trả về ma trận căn chỉnh hoàn chỉnh. Thầy/Cô có thể thấy các cột có màu sắc đồng nhất thẳng hàng từ trên xuống dưới: màu xanh lam là các Amino Acid kỵ nước, màu đỏ là điện tích dương, màu xám là các khoảng trống '-' mà thuật toán Myers-Miller đã chèn vào để khôi phục các vị trí đột biến mất đoạn. Thanh biểu đồ cột phía dưới càng cao chứng tỏ cột đó càng được bảo tồn chặt chẽ qua tiến hóa."*

#### Pha 3 (20 giây): Trực quan hóa Cây Hướng dẫn UPGMA SVG
* **Thao tác chuột**:
  1. Bấm chuyển sang tab/khung **UPGMA Guide Tree Visualizer**.
  2. Lăn chuột phóng to nhẹ vào các nhánh lá và di chuột qua các nút để xem khoảng cách tiến hóa.
* **Lời nói khi thao tác**:
  > *"Chuyển sang khung Cây hướng dẫn UPGMA: cây nhị phân được dựng tự động dưới dạng đồ họa vector SVG. Các cặp chuỗi có khoảng cách tiến hóa nhỏ nhất ở bên phải được ghép cặp trước thành các Profile con, sau đó hợp nhất dần về phía nút gốc bên trái."*

#### Pha 4 (30 giây): Kiểm chứng Nén Bộ nhớ & Tăng tốc Đa luồng trên Dashboard
* **Thao tác chuột**:
  1. Cuộn xuống / bấm vào khu vực **Benchmark & Analytics Dashboard**.
  2. Chỉ chuột vào **Thẻ Memory Reduction** (hiển thị bộ nhớ Gotoh vs. Myers-Miller và nhãn `100% IDENTICAL SCORE`).
  3. Chỉ chuột vào **Thẻ BAliBASE Biological Accuracy** (hiển thị `SP Score` và `TC Score`) và **Đồ thị Speedup Chart.js** bên cạnh.
  4. *(Tùy chọn 10s)*: Chọn nhanh thêm preset **Long Sequence Memory Test (~900 aa)** và bấm Run để Hội đồng thấy trực tiếp con số giảm bộ nhớ vọt lên **hơn $1.350\times$** ngay trên màn hình!
* **Lời nói khi thao tác**:
  > *"Cuối cùng, tại bảng điều khiển Benchmark: Thẻ đối chứng bộ nhớ xác nhận điểm số của Myers-Miller trùng khớp 100% với Gotoh nhưng dung lượng RAM giảm hơn 726 lần trên RV12 (và lên tới 1.353 lần khi em bấm chạy mẫu chuỗi dài 900 amino acid). Bên cạnh là điểm chính xác sinh học SP/TC chấm tự động với chuẩn BAliBASE và đồ thị Speedup đa luồng."*

---

### Kịch bản Demo Dòng lệnh CLI Dự phòng (Dùng khi Giảng viên yêu cầu chạy trực tiếp trên Terminal)

1. **Lệnh 1 — Chứng minh Điểm số Khớp 100% & Giảm RAM trực tiếp giữa Gotoh vs. Myers-Miller**:
   ```powershell
   .\build\Release\msa_align.exe -i data/balibase/BB11001.msf --baseline-compare
   ```
2. **Lệnh 2 — Vừa Căn chỉnh Đa luồng vừa Chấm điểm SP/TC trực tiếp với chuẩn BAliBASE 3.0**:
   ```powershell
   .\build\Release\msa_align.exe -i data/balibase/BB12001.msf --ref data/balibase/BB12001.msf -o results/demo_out.fa -t 4
   ```
3. **Lệnh 3 — Chạy Bộ Kiểm thử Tự động (108 Unit Tests / 139.463 Assertions)**:
   ```powershell
   .\build\Release\msa_unit_tests.exe
   ```
