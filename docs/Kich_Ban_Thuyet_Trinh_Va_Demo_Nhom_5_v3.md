# Kịch bản thuyết trình và demo MSA — v3

Bản PowerPoint: `outputs/slides-v3/Slide_Thuyet_Trinh_PTTKTT_Nhom_5_MSA_v3.pptx`.

28 slide tổng cộng: 24 slide trình bày chính và 4 slide phụ lục. Các bước minh họa nằm trên slide liên tiếp; không phụ thuộc animation.

## Phân công và thời lượng

| Người | Slide | Thời lượng dự kiến |
|---|---|---|
| 1 | 1–6 | 3 phút 30 giây |
| 2 | 7–13 | 5 phút 0 giây |
| 3 | 14–18 | 3 phút 40 giây |
| 4 | 19–24 | 6 phút 10 giây (gồm 2 phút demo) |

Tổng 18 phút 20 giây, gồm 16 phút 20 giây trình bày và 2 phút demo. Thời lượng là gợi ý, cần tập thử theo tốc độ nói của nhóm.

## Chuẩn bị và phương án dự phòng

- Chạy `.\run_gui.bat` từ thư mục gốc, mở `http://localhost:8000` và xác nhận engine sẵn sàng trước buổi báo cáo.
- Chọn preset Hemoglobin, chế độ Standard, dùng 4 luồng cho demo.
- Nếu GUI không sẵn sàng, có thể chạy CLI: `.\build\Release\msa_align.exe -i data/presets/hemoglobin.fa -o outputs/slides-v3/demo_hemoglobin.aln.fa -t 4`. Đây là lệnh dự phòng, chưa được chạy trong quá trình làm slide.
- Nếu không thể chạy ứng dụng, dùng ảnh giao diện có sẵn ở slide 23 và nói rõ là kết quả đã lưu của bộ 40 chuỗi.
- Kết quả benchmark dùng từ log/CSV hiện có; chưa chạy lại benchmark và chưa kiểm tra ứng dụng PowerPoint trực tiếp.

## Lưu ý học thuật

- Tối ưu bài toán cặp không đồng nghĩa tối ưu MSA toàn cục hoặc đúng sinh học 100%.
- Trường bộ nhớ từ bộ giải là ước lượng công thức, chưa phải RAM đỉnh đo thực.
- UPGMA hiện thực hiện quét cặp mỗi vòng, thời gian O(k³).
- Wavefront là module riêng, không phải đường gọi của benchmark pipeline đang báo.
- MPI hiện phân tán khoảng cách; rank 0 làm cây/progressive, chưa có benchmark cụm trong bộ dữ liệu này.
- Phép chấm TC của code có lọc cột có gap/core block. Không trộn các nhóm Scalability và BAliBASE_Accuracy.

## Slide 1: Căn chỉnh đa chuỗi Protein / ADN

Người 1, khoảng 20 giây.

Chào thầy cô và các bạn. Nhóm 5 trình bày cách căn chỉnh nhiều chuỗi sinh học bằng quy hoạch động, chia để trị và tính toán song song. Trước khi vào thuật toán, chúng ta nhìn chuỗi sinh học như một bài toán xử lý chuỗi ký tự. Mục tiêu là hiểu cách sắp các ký tự tương ứng vào cùng cột, rồi xem làm thế nào để tính kết quả với chi phí hợp lý.

Nguồn: `README.md`

## Slide 2: Chuỗi sinh học dưới góc nhìn tin học

Người 1, khoảng 35 giây.

ADN có thể được biểu diễn bằng bốn ký tự A, C, G, T. Protein là một chuỗi amino acid, thường biểu diễn bằng bảng chữ cái gồm 20 ký tự tiêu chuẩn. Các chuỗi liên quan có thể khác ký tự hoặc khác độ dài, nên so sánh cùng chỉ số trong chuỗi gốc chưa đủ. Căn chỉnh giúp đề xuất các vị trí tương ứng để khảo sát mức độ bảo tồn. Phần nhập môn dùng ADN cho dễ nhìn. Phần thuật toán và dữ liệu thực nghiệm của dự án dùng protein với BLOSUM62; không áp dụng BLOSUM62 như một mô hình điểm dành riêng cho ADN.

Nguồn: `README.md`; [Bài gốc](https://pmc.ncbi.nlm.nih.gov/articles/PMC50453/)

## Slide 3: Căn chỉnh chuỗi ADN

Người 1, khoảng 40 giây.

Đọc ba chuỗi đầu vào: ACGT, AGT và ACT. Nếu đặt sát lề trái, G của chuỗi thứ hai sẽ nằm dưới C của chuỗi thứ nhất. Chèn một gap trước G giúp đặt các G vào cùng cột; làm tương tự với chuỗi thứ ba. Gap là vị trí trống do cách biểu diễn căn chỉnh, không phải một ký tự sinh học mới. Xóa toàn bộ gap phải khôi phục đúng chuỗi gốc. Đây là một phương án hợp lệ, chưa tuyên bố tối ưu vì chúng ta chưa định nghĩa mô hình điểm.

Nguồn: `Ví dụ giảng dạy tự xây dựng; docs/Kich_Ban_Thuyet_Trinh_Va_Demo_Nhom_5.md`

## Slide 4: Bài toán căn chỉnh đa chuỗi

Người 1, khoảng 40 giây.

Phát biểu bài toán gồm ba thành phần: dữ liệu đầu vào, điều kiện hợp lệ và hàm mục tiêu. Chúng ta nhận k chuỗi; kết quả có k hàng cùng độ dài. Thuật toán chỉ được thêm gap, không được đổi thứ tự hay làm mất amino acid. Một mô hình thường dùng là Sum-of-Pairs: lấy các căn chỉnh cặp suy ra từ kết quả nhiều hàng rồi cộng điểm. Tìm tối ưu trực tiếp cho nhiều chuỗi rất tốn kém, nên dự án dùng một chiến lược căn chỉnh tiến bộ. Không đồng nhất hàm mục tiêu SP với thước đo SP đối chiếu dữ liệu chuẩn ở phần thực nghiệm.

Nguồn: `include/msa/core/profile.hpp`; `src/core/profile.cpp`; `README.md`

## Slide 5: Điểm thay thế và phạt gap

Người 1, khoảng 45 giây.

BLOSUM62 cho điểm khác nhau tùy cặp amino acid. Ví dụ A với A được 4 điểm, C với C được 9, E với F bị trừ 3. Một đoạn gap liên tiếp dùng phạt affine: mở gap tốn nhiều hơn kéo dài gap. Theo recurrence Gotoh và Myers–Miller của dự án, g(l)=-10-(l-1), nên một gap tốn -10 và ba gap liên tiếp tốn -12. Việc dùng hai tham số giúp phân biệt một đoạn thiếu liên tiếp với nhiều đoạn thiếu rời rạc. Lưu ý kỹ thuật: helper ScoreModel::gapCost có quy ước khác; ở đây theo recurrence thực thi trong các bộ căn chỉnh, không dùng helper để tính ví dụ.

Nguồn: `src/core/blosum62.cpp`; `src/align/needleman_wunsch.cpp`; `src/align/hirschberg.cpp`; [Bài gốc](https://pmc.ncbi.nlm.nih.gov/articles/PMC50453/)

## Slide 6: Vì sao cần một chiến lược gần đúng?

Người 1, khoảng 30 giây.

Với hai chuỗi độ dài gần L, bảng DP có khoảng L bình phương ô. Nếu mở rộng trực tiếp để đồng thời xét k chuỗi, bảng có k chiều với khoảng L mũ k ô. Đây mới chỉ là số trạng thái, chưa tính số chuyển trạng thái. Vì vậy dự án dùng progressive alignment: căn chỉnh các chuỗi hoặc nhóm chuỗi theo một cây hướng dẫn. Mỗi bước ghép có thể giải tốt bài toán con theo mô hình của nó, nhưng toàn bộ chiến lược không bảo đảm tìm nghiệm MSA tối ưu toàn cục. Chuyển lời cho người thứ hai để đi vào bộ giải bài toán cặp.

Nguồn: `README.md`; `src/tree/guide_tree.cpp`

## Slide 7: Luồng xử lý của dự án

Người 2, khoảng 35 giây.

Đầu tiên hệ thống căn chỉnh các cặp để tạo ma trận khoảng cách. Sau đó UPGMA dựng cây hướng dẫn. Cuối cùng, duyệt cây từ lá lên: mỗi lá là một chuỗi, mỗi nút trong ghép hai profile. Bộ giải Myers–Miller nằm ở các bước ghép profile. Một chi tiết quan trọng của bản triển khai hiện tại: khâu tính khoảng cách vẫn gọi Gotoh lưu bảng đầy đủ, nên không thể lấy bộ nhớ tuyến tính của một bộ giải con để kết luận toàn bộ pipeline dùng bộ nhớ tuyến tính.

Nguồn: `src/tree/distance_matrix.cpp`; `src/tree/upgma.cpp`; `src/align/profile_aligner.cpp`

## Slide 8: Quy hoạch động với affine gap

Người 2, khoảng 50 giây.

Mỗi ô đại diện cho căn chỉnh hai tiền tố. Nếu chỉ lưu một giá trị, chúng ta không biết gap đang được mở hay được kéo dài, nên không tính đúng phạt affine. Gotoh lưu ba trạng thái: M kết thúc bằng hai ký tự, Ix kết thúc bằng một ký tự của chuỗi thứ nhất đối diện gap, Iy là chiều ngược lại. M chuyển từ đường chéo; Ix từ phía trên; Iy từ bên trái. Giá trị tốt nhất của ô là max ba trạng thái. Phần phụ lục chứa công thức đầy đủ, kể cả chuyển từ loại gap này sang loại gap kia theo code hiện có.

Nguồn: `src/align/needleman_wunsch.cpp`; [Bài gốc](https://pubmed.ncbi.nlm.nih.gov/7166760/)

## Slide 9: Ví dụ DP trên hai chuỗi protein

Người 2, khoảng 40 giây.

Bảng hiển thị H, tức giá trị tốt nhất trong ba trạng thái của mỗi ô. Cột và hàng rỗng tương ứng tiền tố có độ dài 0. Với ACDE và ACDF, phương án không có gap cho điểm 4+9+6-3=16. DP cũng cho giá trị kết thúc 16 nên phương án này đạt tối ưu theo mô hình điểm của bài toán cặp. Chúng ta đang giải global alignment, sử dụng toàn bộ hai chuỗi. Ví dụ này nhỏ có chủ đích để người nghe theo được các số.

Nguồn: `src/core/blosum62.cpp`; `src/align/needleman_wunsch.cpp`; `Ví dụ được tính lại khi tạo slide bằng recurrence của dự án`

## Slide 10: Truy vết và chi phí lưu bảng

Người 2, khoảng 35 giây.

Từ ô cuối, traceback đi ngược về ô đầu theo các quyết định tối ưu. Trong hình, đường đi của ví dụ nằm trên đường chéo. Với affine gap, traceback phải theo cả loại trạng thái, không chỉ theo giá trị H đã rút gọn trên slide. Cách cài Gotoh cơ bản lưu ba bảng có kích thước m+1 nhân n+1 nên bộ nhớ là bậc hai. Nếu chỉ cần điểm số, có thể cuộn hàng. Nhưng khi cần cả chuỗi căn chỉnh, chúng ta phải có cách khôi phục đường đi mà không giữ mọi ô. Đây là lý do đưa chia để trị vào.

Nguồn: `src/align/needleman_wunsch.cpp`; [Bài gốc](https://doi.org/10.1093/bioinformatics/4.1.11)

## Slide 11: Điểm cắt Myers–Miller

Người 2, khoảng 50 giây.

Chọn một hàng giữa của chuỗi thứ nhất, ở đây là sau AC. Câu hỏi then chốt: đường căn chỉnh tối ưu đi qua vị trí nào trên hàng này? Thuật toán tính điểm đi từ đầu đến hàng giữa và điểm đi ngược từ cuối về hàng giữa. Kết hợp thông tin hai phía để tìm cột và trạng thái cắt phù hợp. Sau đó giải hai nửa rồi ghép kết quả. Bảng đầy đủ trên slide chỉ dùng minh họa vị trí cắt. Thuật toán thật dùng các vector điểm. Với affine gap, phải xét trạng thái gap tại ranh giới, không chỉ lấy tổng hai điểm vô điều kiện.

Nguồn: `src/align/hirschberg.cpp`; [Bài gốc](https://doi.org/10.1093/bioinformatics/4.1.11)

## Slide 12: Chọn cột cắt từ hai lượt quét

Người 2, khoảng 45 giây.

F(j) là điểm tốt nhất khi căn chỉnh AC với tiền tố độ dài j của ACDF. R(j) là điểm tốt nhất khi căn chỉnh DE với hậu tố bắt đầu sau j ký tự của ACDF. Hai lượt DP tiến và lùi cho hai vector trên. Với ví dụ này, tổng lớn nhất là 16 ở j=2 và phép nối không có gap xuyên ranh giới, nên hình minh họa đúng điểm cắt đã chọn. Bài toán trái là AC với AC, đạt 13; bài toán phải là DE với DF, đạt 3. Không dùng bảng F+R này như toàn bộ thuật toán affine gap tổng quát: cần kiểm tra trạng thái biên và hiệu chỉnh khi một gap kéo xuyên qua ranh giới. Tiếp tục chia đến khi một chiều đủ nhỏ thì giải trực tiếp bằng DP, sau đó ghép các phần căn chỉnh.

Nguồn: `src/align/hirschberg.cpp`; `Ví dụ vector được tính từ recurrence và BLOSUM62 của dự án`; [Bài gốc](https://doi.org/10.1093/bioinformatics/4.1.11)

## Slide 13: Chi phí của chia để trị

Người 2, khoảng 45 giây.

Ở mỗi mức, các lượt quét tiến và lùi có chi phí tỷ lệ diện tích bài toán. Khi chia chiều thứ nhất làm đôi, tổng diện tích các bài toán con giảm theo cấp số nhân, nên tổng vẫn là O(mn). Thuật toán Myers–Miller chuẩn chỉ cần bộ nhớ DP làm việc tuyến tính theo chiều ngắn hơn khi bố trí đúng chiều và tái sử dụng hoặc giải phóng các vector. Chưa tính vùng lưu đầu ra và ngăn xếp đệ quy. Đây là kết quả lý thuyết của bộ giải cặp, không phải phép đo RAM toàn chương trình và không phải kết luận về toàn pipeline hiện có. Phụ lục 26 nêu khác biệt của code thực tế. Chuyển lời cho người thứ ba.

Nguồn: `src/align/hirschberg.cpp`; [Bài gốc](https://doi.org/10.1093/bioinformatics/4.1.11)

## Slide 14: UPGMA chọn thứ tự ghép

Người 3, khoảng 45 giây.

Ma trận này là ví dụ giảng dạy tự xây dựng, không phải số đo khoảng cách của các chuỗi ở slide trước. Cặp S1,S2 gần nhất với 0,1 nên được ghép đầu tiên. Khoảng cách từ cụm mới đến cụm khác được tính bằng trung bình có trọng số theo số chuỗi. S3,S4 tạo nhóm tiếp theo, rồi hai nhóm hợp lại. UPGMA ở đây là cây hướng dẫn thuật toán, không được xem như bằng chứng độc lập về cây tiến hóa thật. Khoảng cách thực trong dự án lấy một trừ điểm cặp chia điểm tự so lớn hơn, chặn trong khoảng 0 đến 2.

Nguồn: `src/tree/upgma.cpp`; `src/tree/distance_matrix.cpp`; `Ví dụ khoảng cách tự xây dựng`

## Slide 15: Profile giữ lại căn chỉnh của một nhóm

Người 3, khoảng 45 giây.

Một profile lưu nhiều hàng đã căn chỉnh và phân bố amino acid ở mỗi cột. Khi ghép profile với profile, đơn vị DP là cột thay vì một amino acid đơn lẻ. Code tính điểm hai cột bằng tần suất amino acid và BLOSUM62, rồi làm tròn trước khi đưa vào kernel. Hình minh họa nhóm bên phải cần một cột trống, nên cả S3 và S4 đều nhận gap tại cùng vị trí. Nhóm trái giữ các hàng ACD và ACE. Toàn bộ kết quả cuối là ACD, ACE, A-D, A-E. Đây là minh họa phép lan truyền gap, không tuyên bố là kết quả tối ưu của bộ giải cho các nhóm này.

Nguồn: `src/core/profile.cpp`; `src/align/profile_aligner.cpp`; `src/align/hirschberg.cpp`

## Slide 16: Các công việc có thể chạy song song

Người 3, khoảng 50 giây.

Khâu khoảng cách có k nhân k trừ một chia hai cặp. Mỗi cặp có thể được tính độc lập nên thuận lợi chia cho các luồng. Ở cây hướng dẫn, hai nhánh con độc lập có thể được xử lý đồng thời. Nhưng một nút cha chỉ ghép được sau khi cả hai profile con đã xong. Gần gốc, số việc độc lập giảm xuống. Bản cài hiện tại dùng OpenMP parallel for với lịch động cho các cặp và parallel sections đệ quy cho hai nhánh, không phải một bộ lập lịch task toàn cục. Việc chia nhỏ quá nhiều cũng có chi phí tạo luồng và đồng bộ.

Nguồn: `src/tree/distance_matrix.cpp`; `src/parallel/tree_scheduler.cpp`

## Slide 17: Wavefront trên các đường chéo phụ

Người 3, khoảng 40 giây.

Mỗi ô phụ thuộc các ô phía trên, bên trái và đường chéo trước đó. Những ô có cùng tổng chỉ số i+j không phụ thuộc trực tiếp nhau nên có thể tính đồng thời. Các ô tô xanh là một đợt wavefront; xong đợt này mới tiến sang đợt sau. Cần phân biệt sự tồn tại của module với đường thực thi: benchmark pipeline đang gọi DistanceMatrix dùng NeedlemanWunsch và bộ ghép profile dùng HirschbergAligner, không gọi wavefront. Vì vậy số liệu tăng tốc của pipeline ở phần sau không phải phép đo riêng lợi ích wavefront. Hàm wavefront_gotoh_score và hàm trả căn chỉnh cũng có cấu trúc lưu trữ khác nhau.

Nguồn: `src/parallel/wavefront.cpp`; `src/tree/distance_matrix.cpp`; `src/eval/benchmark.cpp`

## Slide 18: Mở rộng MPI kết hợp OpenMP

Người 3, khoảng 40 giây.

Khi có nhiều máy hoặc nhiều tiến trình, target MPI phân các cặp cho các rank. Bên trong một rank, OpenMP tiếp tục chia các cặp được giao cho nhiều luồng. Các rank tổng hợp ma trận bằng MPI_Allreduce. Theo code hiện tại, rank 0 là nơi dựng cây và thực hiện progressive alignment; không có phân tán toàn cây qua MPI. Đây là hướng mở rộng kiến trúc đã có trong source. Bộ kết quả CSV hiện tại đo OpenMP trên một tiến trình, nên chúng ta không dùng nó để kết luận về mức tăng tốc của cụm MPI. Chuyển lời cho người thứ tư để xem thực nghiệm.

Nguồn: `src/parallel/mpi_distance_matrix.cpp`; `src/msa_mpi_main.cpp`; `results/benchmark_summary.csv`

## Slide 19: Ba câu hỏi thực nghiệm

Người 4, khoảng 45 giây.

Thực nghiệm chia làm ba nhóm. Nhóm đầu so điểm căn chỉnh cặp giữa Gotoh và Myers–Miller. Nhóm thứ hai xem thời gian pipeline khi đổi số luồng. Nhóm thứ ba so căn chỉnh thu được với reference BAliBASE. Bản v3 dùng lại log và CSV trong dự án, không tuyên bố đã chạy benchmark mới. Với phần scaling, runner lấy trung bình các lần lặp, cấu hình từ CLI là hai lần; kết quả chưa kèm khoảng tin cậy hoặc đầy đủ cấu hình máy để khái quát sang máy khác. Các ca accuracy dùng dữ liệu đầu vào khác cách trích xuất ở nhóm scaling nên cần đọc đúng Category trong CSV.

Nguồn: `results/benchmark_summary.csv`; `scripts/run_benchmarks.py`; `src/eval/benchmark.cpp`; `src/main.cpp`; [Bài gốc](https://pubmed.ncbi.nlm.nih.gov/16044462/)

## Slide 20: Đối chiếu điểm số và bộ nhớ

Người 4, khoảng 50 giây.

Ở cặp chuỗi dài trong log, hai bộ giải cùng cho điểm 4159. Đây là đối chiếu điểm bài toán cặp trong ca đo, không có nghĩa toàn bộ MSA đúng sinh học 100%. Cột bộ nhớ cần đọc thận trọng. Trường peak_memory_bytes của Myers–Miller hiện gán bằng 2 nhân min(m,n)+1 nhân sizeof(int); Gotoh báo từ kích thước bảng và dung lượng chuỗi kết quả. Tỷ số 9723566 chia 7184 xấp xỉ 1353,5, nhưng đây là so sánh chỉ số công thức, chưa chứng minh RAM đỉnh thực. Log cũng cho thấy thời gian Myers–Miller ở ca này cao hơn. Chúng ta trình bày đánh đổi bộ nhớ và thời gian, không gán giảm RAM toàn pipeline.

Nguồn: `results/logs/memory_gotoh_vs_hirschberg.log`; `src/align/hirschberg.cpp`; `src/align/needleman_wunsch.cpp`

## Slide 21: Thêm luồng không luôn nhanh hơn

Người 4, khoảng 50 giây.

Trục ngang là số luồng, trục dọc là speedup so với một luồng. BB20001 đạt khoảng 1,73 lần ở tám luồng, trong khi bộ 40 chuỗi đạt khoảng 1,61 lần. Nhưng BB12001 chỉ còn 0,70 lần, nghĩa là chạy chậm hơn mốc một luồng. Vì vậy kết luận đúng là lợi ích song song phụ thuộc dữ liệu và cách chia tải. Các phụ thuộc ở cây, overhead tạo luồng và đồng bộ là những yếu tố hợp lý để khảo sát tiếp. Chưa có profiling để kết luận chính xác bao nhiêu phần trăm thời gian do từng nguyên nhân, nên không khẳng định bão hòa cache hay băng thông từ biểu đồ này.

Nguồn: `results/benchmark_summary.csv (Category=Scalability)`; `results/logs/benchmark_scaling_threads.log`; `src/parallel/tree_scheduler.cpp`

## Slide 22: Chất lượng căn chỉnh theo dữ liệu chuẩn

Người 4, khoảng 35 giây.

Đây là ba ví dụ được chọn từ 13 ca BAliBASE_Accuracy, không phải trung bình của cả BAliBASE. BB11001 có SP khoảng 98,2% và TC khoảng 96,5%; BB12003 có SP khoảng 93,0%, TC khoảng 83,8%; BB20003 có SP khoảng 92,0% nhưng TC bằng 0. SP đếm tỷ lệ các cặp residue tham chiếu còn căn đúng. TC của code yêu cầu tất cả residue trong một cột tham chiếu đủ điều kiện cùng nằm một cột ở kết quả. Do đó nhiều quan hệ cặp vẫn đúng trong khi không cột nào đúng trọn vẹn. Số liệu chưa tự chỉ ra chính xác chuỗi nào gây lệch. Không nói 92% chuỗi đúng hay 100% độ chính xác sinh học.

Nguồn: `results/benchmark_summary.csv (Category=BAliBASE_Accuracy)`; `src/eval/sp_score.cpp`; `src/eval/tc_score.cpp`; [Bài gốc](https://pubmed.ncbi.nlm.nih.gov/16044462/)

## Slide 23: Demo: từ chuỗi đầu vào đến căn chỉnh

Người 4, khoảng 140 giây.

Chuẩn bị trước buổi: chạy .\run_gui.bat ở thư mục dự án, mở localhost:8000, xác nhận engine sẵn sàng. Đây là hướng dẫn thao tác cho buổi báo cáo; bản slide không tuyên bố đã chạy demo mới. 0–20 giây: chuyển sang trình duyệt, chọn Hemoglobin và chế độ Standard. 20–50 giây: chọn 4 luồng, chạy căn chỉnh. 50–90 giây: chỉ các hàng cùng độ dài, các gap và vùng bảo tồn, chuyển Guide Tree để liên hệ thứ tự ghép. 90–120 giây: xuất FASTA, nói rằng bỏ gap phải khôi phục chuỗi đầu vào. Ảnh trong slide là ảnh đã có của bộ 40 chuỗi, dùng dự phòng, không phải kết quả Hemoglobin. Nếu không khởi động được GUI, dùng CLI đã ghi trong kịch bản v3 hoặc mở ảnh dự phòng và nói rõ đó là kết quả đã lưu.

Nguồn: `docs/images/fig_5_1_web_alignment_matrix.png`; `run_gui.bat`; `web/static/js/app.js`; `data/presets/hemoglobin.fa`

## Slide 24: Kết luận

Người 4, khoảng 50 giây.

Tổng kết: quy hoạch động xác định điểm và chuyển trạng thái; Myers–Miller dùng chia để trị để giảm nhu cầu lưu bảng của bộ giải cặp; OpenMP khai thác các công việc độc lập. Căn chỉnh đa chuỗi trong dự án dùng chiến lược progressive nên không bảo đảm tối ưu MSA toàn cục. Thực nghiệm đã lưu có ca được lợi khi tăng luồng và có ca chậm hơn. Chỉ số bộ nhớ công thức cần được kiểm chứng bằng đo allocation và RAM thực. Hướng phát triển là profiling trước khi tối ưu thêm, kiểm tra bộ nhớ theo triển khai, và cân nhắc iterative refinement cho chất lượng căn chỉnh. Cảm ơn thầy cô và các bạn, xin nhận câu hỏi.

Nguồn: `src/align/hirschberg.cpp`; `src/parallel/tree_scheduler.cpp`; `results/benchmark_summary.csv`

## Slide 25: Phụ lục: công thức truy hồi

Phụ lục, mở khi cần.

Công thức phản ánh code thực tế, bao gồm mở loại gap mới từ một trạng thái gap khác. M tại hai biên khác gốc là âm vô cùng. Mỗi bước traceback đi theo trạng thái chứ không chỉ theo H=max(M,Ix,Iy). Khi kết hợp forward và backward trong Myers–Miller, kiểm tra cả trường hợp điểm cắt thông thường và trường hợp gap kéo qua ranh giới. Không dùng F(j)+R(j) như một công thức hoàn chỉnh cho affine gap mà bỏ trạng thái và hiệu chỉnh.

Nguồn: `src/align/needleman_wunsch.cpp`; `src/align/hirschberg.cpp`; [Bài gốc](https://pubmed.ncbi.nlm.nih.gov/7166760/); [Bài gốc](https://doi.org/10.1093/bioinformatics/4.1.11)

## Slide 26: Phụ lục: lý thuyết và triển khai

Phụ lục, mở khi cần.

UPGMA đang lặp k-1 lần; ở mỗi lần, quét tất cả cặp cụm còn lại và xóa các phần tử bảng, nên thời gian tổng bậc ba với triển khai này. Không ghi O(k²) chỉ vì ma trận khoảng cách có bậc hai. Bộ giải Myers–Miller chuẩn có kết quả bộ nhớ tuyến tính theo chiều ngắn hơn khi quản lý vector và hướng đúng. Code hiện khởi tạo vector theo chiều thứ hai, chưa hoán đổi m,n, và các vector local forward/backward còn sống khi gọi đệ quy; thêm các chuỗi kết quả. Vì vậy số peak_memory_bytes gán theo hai hàng min không phải phép đo hoặc chứng minh peak thực. Cần một lượt kiểm tra riêng nếu muốn xác nhận bound của bản cài. Thời gian ghép progressive nên biểu diễn theo tổng chi phí từng nút vì profile có thể dài ra do gap.

Nguồn: `src/tree/upgma.cpp`; `src/tree/distance_matrix.cpp`; `src/align/hirschberg.cpp`

## Slide 27: Phụ lục: 13 ca đánh giá BAliBASE

Phụ lục, mở khi cần.

Bảng giữ đủ 13 ca trong nhóm accuracy, không chọn riêng các ca thuận lợi. Dữ liệu bảng trái gồm RV11 và hai ca đầu RV12; bảng phải gồm phần còn lại của RV12 và RV20. SP và TC in bốn chữ số thập phân. Code TC bỏ qua cột tham chiếu thiếu residue ở bất kỳ chuỗi nào, và cờ core_blocks_only còn lọc theo core block khi có. Định nghĩa hiển thị ở đây là phép chấm của dự án, chưa tuyên bố đã đối chiếu đồng nhất với một evaluator BAliBASE độc lập. Đầu vào nhóm scaling dùng đường MSF/reference, trong khi accuracy dùng FASTA unaligned, nên tên BB giống nhau không bảo đảm hai dòng thuộc cùng một phép thử.

Nguồn: `results/benchmark_summary.csv`; `scripts/run_benchmarks.py`; `src/eval/sp_score.cpp`; `src/eval/tc_score.cpp`

## Slide 28: Tài liệu tham khảo

Phụ lục, mở khi cần.

Các đường dẫn đầy đủ bên dưới có thể mở từ ghi chú. Nguồn bài báo dùng cho thuật toán nền tảng và mô hình điểm; kết quả định lượng lấy từ file cục bộ và không gán cho bài báo. Không có phép benchmark mới khi xây dựng bản v3. Hình ảnh giao diện lấy từ docs/images của dự án. Các bảng chuỗi, DP và ví dụ UPGMA được xây dựng cho giảng dạy, với bảng DP tính lại từ BLOSUM62 thực trong source.

Nguồn: [Bài gốc](https://pubmed.ncbi.nlm.nih.gov/7166760/); [Bài gốc](https://doi.org/10.1093/bioinformatics/4.1.11); [Bài gốc](https://pmc.ncbi.nlm.nih.gov/articles/PMC50453/); [Bài gốc](https://pubmed.ncbi.nlm.nih.gov/16044462/); `results/benchmark_summary.csv`; `results/logs/memory_gotoh_vs_hirschberg.log`; `results/logs/benchmark_scaling_threads.log`; `results/logs/balibase_accuracy_eval.log`

