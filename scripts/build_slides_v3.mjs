// Rebuild with the bundled Node runtime and RUNTIME_NODE_MODULES set.
// All slide text, alignment tables and charts remain editable in PowerPoint.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const skill=process.env.MSA_PRESENTATION_SKILL_DIR ?? 'C:/Users/manhk/.codex/plugins/cache/openai-primary-runtime/presentations/26.1022.11436/skills/presentations';
const python=process.env.RUNTIME_PYTHON ?? 'C:/Users/manhk/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const {importRuntimeModule}=await import(pathToFileURL(path.join(skill,'container_tools/runtime_helpers.mjs')).href);
const {Presentation,PresentationFile}=await importRuntimeModule('@oai/artifact-tool');
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const tmp=path.join(root,'.local/slides-v3');
const out=path.join(root,'outputs/slides-v3');
await fs.mkdir(tmp,{recursive:true});await fs.mkdir(out,{recursive:true});
const finalPath=path.join(out,process.env.MSA_V3_OUTPUT ?? 'Slide_Thuyet_Trinh_PTTKTT_Nhom_5_MSA_v3.pptx');
const C={bg:'#F7F5EF',ink:'#142D3B',teal:'#147D78',muted:'#61716F',pale:'#DDECE6',line:'#D7DED6',white:'#FFFFFF',warm:'#A76C4D'};
const REF={mm:'https://doi.org/10.1093/bioinformatics/4.1.11',gotoh:'https://pubmed.ncbi.nlm.nih.gov/7166760/',blosum:'https://pmc.ncbi.nlm.nih.gov/articles/PMC50453/',balibase:'https://pubmed.ncbi.nlm.nih.gov/16044462/'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
const records=[],tableOwners=new Set(),chartOwners=[];
const durations=[20,35,40,40,45,30,35,50,40,35,50,45,45,45,45,50,40,40,45,50,50,35,140,50,0,0,0,0];
function tx(s,text,x,y,w,h,size=26,color=C.ink,bold=false,font='Segoe UI',align='left'){
 const a=s.shapes.add({name:text.slice(0,70),geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 a.text=text;a.text.style={typeface:font,fontSize:size,color,bold,insets:0,wrap:'none',autoFit:'none',alignment:align};return a;
}
function lines(s,arr,x,y,w,size=27,color=C.ink,step=41){arr.forEach((v,i)=>tx(s,v,x,y+i*step,w,step,size,color));}
function page(title,sub=''){
 const s=p.slides.add(),n=p.slides.items.length;
 s.background.fill=C.bg;
 tx(s,String(n).padStart(2,'0'),1170,650,44,27,17,C.muted);
 if(title)tx(s,title,80,70,1120,78,51,C.ink,true);
 if(sub)tx(s,sub,80,158,1120,46,26,C.muted);
 records.push({n,title,seconds:durations[n-1],person:n<=6?1:n<=13?2:n<=18?3:n<=24?4:null,notes:'',sources:[]});
 return s;
}
function notes(s,text,sources=[]){const r=records.at(-1);r.notes=text;r.sources=sources;s.speakerNotes.text=`${r.person?'Người '+r.person+' — '+r.seconds+' giây':'Phụ lục, chỉ mở khi cần'}\n\n${text}\n\nNguồn:\n${sources.join('\n')}`;}
function takeaway(s,text){tx(s,text,80,604,1120,44,28,C.teal,true);}
function tab(s,values,x,y,w,h,{size=27,widths,mono=false,header=false,grid=false}={}){
 tableOwners.add(p.slides.items.indexOf(s)+1);
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,...(widths?{columnWidths:widths}:{})});
 t.styleOptions={headerRow:false,bandedRows:false,firstColumn:false};
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({fill:C.bg,textStyle:{typeface:mono?'Consolas':'Segoe UI',fontSize:size,color:C.ink,alignment:'center',verticalAlignment:'middle'},margins:{left:8,right:8,top:6,bottom:6},anchor:'center'});
 t.borders.assign({fill:grid?C.line:C.bg,width:grid?1:0});
 if(header)for(let c=0;c<values[0].length;c++){t.getCell(0,c).fill=C.pale;t.getCell(0,c).text.style={typeface:mono?'Consolas':'Segoe UI',fontSize:size,color:C.teal,bold:true,alignment:'center'};}
 return t;
}
function highlight(t,r,c,solid=false,size=28){t.getCell(r,c).fill=solid?C.teal:C.pale;t.getCell(r,c).text.style={typeface:'Consolas',fontSize:size,color:solid?C.white:C.teal,bold:true,alignment:'center'};}
function step(s,no,title,body,y){tx(s,no,80,y,75,55,41,C.teal,true);tx(s,title,180,y,1010,50,32,C.ink,true);if(body)tx(s,body,180,y+52,1010,40,25,C.muted);}
function sourceFoot(s,text){tx(s,text,80,660,1050,25,16,C.muted);}

// Source data are parsed once and used in both chart series and speaker notes.
const csv=(await fs.readFile(path.join(root,'results/benchmark_summary.csv'),'utf8')).trim().split(/\r?\n/);
const fields=csv.shift().split(',');
const data=csv.map(row=>Object.fromEntries(row.split(',').map((v,i)=>[fields[i],v])));
const scale=id=>data.filter(d=>d.Category==='Scalability'&&d.Dataset.startsWith(id)).map(d=>({...d,threads:Number(d.Threads),time:Number(d.Time_ms),speed:Number(d.Speedup)}));
const accuracy=data.filter(d=>d.Category==='BAliBASE_Accuracy');
const proteinSource=await fs.readFile(path.join(root,'src/core/blosum62.cpp'),'utf8');
const alphabet='ARNDCQEGHILKMFPSTWYVBZX*';
const blosum=[...proteinSource.matchAll(/\/\* [A-Z*] \*\/\s*\{([^}]+)\}/g)].map(m=>m[1].split(',').map(x=>Number(x.trim())));
if(blosum.length!==24)throw Error('BLOSUM62 source parse failed');
const score=(a,b)=>blosum[alphabet.indexOf(a)][alphabet.indexOf(b)];
function dp(a,b){
 const m=a.length,n=b.length,N=-1e9;
 const M=Array.from({length:m+1},()=>Array(n+1).fill(N)),X=M.map(r=>[...r]),Y=M.map(r=>[...r]);M[0][0]=0;
 for(let i=1;i<=m;i++)X[i][0]=-10-(i-1);for(let j=1;j<=n;j++)Y[0][j]=-10-(j-1);
 for(let i=1;i<=m;i++)for(let j=1;j<=n;j++){
  M[i][j]=Math.max(M[i-1][j-1],X[i-1][j-1],Y[i-1][j-1])+score(a[i-1],b[j-1]);
  X[i][j]=Math.max(M[i-1][j]-10,X[i-1][j]-1,Y[i-1][j]-10);
  Y[i][j]=Math.max(M[i][j-1]-10,Y[i][j-1]-1,X[i][j-1]-10);
 }
 const H=M.map((r,i)=>r.map((_,j)=>Math.max(M[i][j],X[i][j],Y[i][j])));
 return {M,X,Y,H,score:H[m][n]};
}
const demo=dp('ACDE','ACDF');if(demo.score!==16||demo.H[2][2]!==13)throw Error('Unexpected DP example');
const fmt=v=>String(v).replaceAll('-','−');
function matrix(s,mode){
 const vals=[['','∅',...'ACDF'],...demo.H.map((r,i)=>[i?'ACDE'[i-1]:'∅',...r.map(fmt)])];
 const t=tab(s,vals,80,237,590,330,{size:27,widths:[85,101,101,101,101,101],mono:true,grid:true});
 for(let r=0;r<6;r++)for(let c=0;c<6;c++)t.getCell(r,c).fill=r===0||c===0?C.bg:C.white;
 if(mode==='cut'){for(let c=1;c<6;c++)t.getCell(3,c).fill=C.pale;highlight(t,3,3,true,27);}
 else if(mode==='path'){for(let i=1;i<6;i++)highlight(t,i,i,i===5,27);}
 else highlight(t,5,5,true,27);
 return t;
}
function chart(s,type,config){const z=s.charts.add(type,{chartFill:C.bg,plotAreaFill:C.bg,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},...config});applyPresentationChartFont(z,{fontFamily:'Segoe UI'});chartOwners.push(p.slides.items.indexOf(s)+1);return z;}

// 1 — Cover. Same composition as the approved sample.
{
 const s=page('');records.at(-1).title='Căn chỉnh đa chuỗi Protein / ADN';
 tx(s,'NHÓM 5',80,65,200,30,19,C.teal,true);tx(s,'PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN',80,105,1050,30,19,C.muted);
 tx(s,'Căn chỉnh đa chuỗi',75,215,1115,100,76,C.ink,true);tx(s,'Protein / ADN',75,310,1050,100,76,C.ink,true);
 tx(s,'Chia để trị song song',80,461,1080,48,34,C.teal);tx(s,'kết hợp quy hoạch động',80,510,1080,48,34,C.teal);tx(s,'Multiple Sequence Alignment',80,650,900,29,20,C.muted);
 notes(s,'Chào thầy cô và các bạn. Nhóm 5 trình bày cách căn chỉnh nhiều chuỗi sinh học bằng quy hoạch động, chia để trị và tính toán song song. Trước khi vào thuật toán, chúng ta nhìn chuỗi sinh học như một bài toán xử lý chuỗi ký tự. Mục tiêu là hiểu cách sắp các ký tự tương ứng vào cùng cột, rồi xem làm thế nào để tính kết quả với chi phí hợp lý.',['README.md']);
}
// 2 — Biological context for an algorithms class.
{
 const s=page('Chuỗi sinh học dưới góc nhìn tin học','Mỗi ký tự biểu diễn một đơn vị cấu tạo của chuỗi');
 tx(s,'ADN',80,253,430,70,51,C.teal,true);tx(s,'Protein',690,253,460,70,51,C.teal,true);
 tx(s,'A  C  G  T',80,348,490,65,43,C.ink,true,'Consolas');tx(s,'M  A  L  W  K  V',690,348,500,65,43,C.ink,true,'Consolas');
 lines(s,['4 loại nucleotide','Lưu trữ thông tin di truyền'],80,444,500,27,C.muted,44);
 lines(s,['20 loại amino acid tiêu chuẩn','Có thể so sánh bằng BLOSUM62'],690,444,510,27,C.muted,44);
 takeaway(s,'Căn chỉnh giúp nhận ra các vị trí tương ứng giữa các chuỗi');
 notes(s,'ADN có thể được biểu diễn bằng bốn ký tự A, C, G, T. Protein là một chuỗi amino acid, thường biểu diễn bằng bảng chữ cái gồm 20 ký tự tiêu chuẩn. Các chuỗi liên quan có thể khác ký tự hoặc khác độ dài, nên so sánh cùng chỉ số trong chuỗi gốc chưa đủ. Căn chỉnh giúp đề xuất các vị trí tương ứng để khảo sát mức độ bảo tồn. Phần nhập môn dùng ADN cho dễ nhìn. Phần thuật toán và dữ liệu thực nghiệm của dự án dùng protein với BLOSUM62; không áp dụng BLOSUM62 như một mô hình điểm dành riêng cho ADN.',['README.md',REF.blosum]);
}
// 3 — Approved DNA alignment sample.
{
 const s=page('Căn chỉnh chuỗi ADN','Thêm khoảng trống để so sánh các vị trí tương ứng');
 tx(s,'Đầu vào',80,248,420,40,26,C.teal,true);tx(s,'Một phương án căn chỉnh',650,248,550,40,26,C.teal,true);
 tab(s,[['S₁','A','C','G','T'],['S₂','A','G','T',''],['S₃','A','C','T','']],74,303,440,176,{size:35,widths:[112,82,82,82,82],mono:true});
 const t=tab(s,[['S₁','A','C','G','T'],['S₂','A','–','G','T'],['S₃','A','C','–','T']],644,303,540,176,{size:35,widths:[132,102,102,102,102],mono:true});highlight(t,1,2,false,35);highlight(t,2,3,false,35);
 tx(s,'Gap “–” biểu diễn một vị trí trống trong căn chỉnh',80,552,1100,44,29,C.ink,true);tx(s,'Giữ nguyên thứ tự ký tự. Các hàng kết quả có cùng số cột.',80,606,1100,38,24,C.muted);
 notes(s,'Đọc ba chuỗi đầu vào: ACGT, AGT và ACT. Nếu đặt sát lề trái, G của chuỗi thứ hai sẽ nằm dưới C của chuỗi thứ nhất. Chèn một gap trước G giúp đặt các G vào cùng cột; làm tương tự với chuỗi thứ ba. Gap là vị trí trống do cách biểu diễn căn chỉnh, không phải một ký tự sinh học mới. Xóa toàn bộ gap phải khôi phục đúng chuỗi gốc. Đây là một phương án hợp lệ, chưa tuyên bố tối ưu vì chúng ta chưa định nghĩa mô hình điểm.',['Ví dụ giảng dạy tự xây dựng; docs/Kich_Ban_Thuyet_Trinh_Va_Demo_Nhom_5.md']);
}
// 4 — Formal problem.
{
 const s=page('Bài toán căn chỉnh đa chuỗi','Đầu vào là k chuỗi có thể khác nhau về độ dài');
 tx(s,'S₁, S₂, …, Sₖ',80,248,1100,80,56,C.teal,true,'Consolas');
 lines(s,['Đầu ra: k hàng căn chỉnh có cùng số cột','Chỉ chèn gap, giữ nguyên ký tự và thứ tự của từng chuỗi','Chọn phương án có điểm tốt theo mô hình đã định'],80,365,1120,29,C.ink,65);
 takeaway(s,'Mục tiêu thường dùng: tổng điểm các cặp chuỗi trong căn chỉnh');
 notes(s,'Phát biểu bài toán gồm ba thành phần: dữ liệu đầu vào, điều kiện hợp lệ và hàm mục tiêu. Chúng ta nhận k chuỗi; kết quả có k hàng cùng độ dài. Thuật toán chỉ được thêm gap, không được đổi thứ tự hay làm mất amino acid. Một mô hình thường dùng là Sum-of-Pairs: lấy các căn chỉnh cặp suy ra từ kết quả nhiều hàng rồi cộng điểm. Tìm tối ưu trực tiếp cho nhiều chuỗi rất tốn kém, nên dự án dùng một chiến lược căn chỉnh tiến bộ. Không đồng nhất hàm mục tiêu SP với thước đo SP đối chiếu dữ liệu chuẩn ở phần thực nghiệm.',['include/msa/core/profile.hpp','src/core/profile.cpp','README.md']);
}
// 5 — Protein scoring.
{
 const s=page('Điểm thay thế và phạt gap','Từ đây, ví dụ thuật toán dùng chuỗi protein');
 tx(s,'BLOSUM62',80,242,500,48,33,C.teal,true);
 tab(s,[['Cặp amino acid','Điểm'],['A / A','+4'],['C / C','+9'],['E / F','−3']],80,308,490,235,{size:29,widths:[320,170],header:true});
 tx(s,'Affine gap',690,242,500,48,33,C.teal,true);
 tx(s,'g(ℓ) = −10 − (ℓ − 1)',690,322,510,55,34,C.ink,true,'Consolas');
 lines(s,['Mở một gap: −10','Kéo dài thêm một vị trí: −1','Một đoạn 3 gap: −12'],690,405,500,27,C.muted,45);
 takeaway(s,'Mô hình điểm quyết định phương án căn chỉnh được ưu tiên');
 notes(s,'BLOSUM62 cho điểm khác nhau tùy cặp amino acid. Ví dụ A với A được 4 điểm, C với C được 9, E với F bị trừ 3. Một đoạn gap liên tiếp dùng phạt affine: mở gap tốn nhiều hơn kéo dài gap. Theo recurrence Gotoh và Myers–Miller của dự án, g(l)=-10-(l-1), nên một gap tốn -10 và ba gap liên tiếp tốn -12. Việc dùng hai tham số giúp phân biệt một đoạn thiếu liên tiếp với nhiều đoạn thiếu rời rạc. Lưu ý kỹ thuật: helper ScoreModel::gapCost có quy ước khác; ở đây theo recurrence thực thi trong các bộ căn chỉnh, không dùng helper để tính ví dụ.',['src/core/blosum62.cpp','src/align/needleman_wunsch.cpp','src/align/hirschberg.cpp',REF.blosum]);
}
// 6 — Why progressive alignment.
{
 const s=page('Vì sao cần một chiến lược gần đúng?','Số chiều của bảng DP tăng theo số chuỗi');
 tx(s,'2 chuỗi',80,261,500,52,37,C.teal,true);tx(s,'k chuỗi',690,261,500,52,37,C.teal,true);
 tx(s,'O(L²)',80,346,500,90,68,C.ink,true,'Consolas');tx(s,'O(Lᵏ)',690,346,500,90,68,C.ink,true,'Consolas');
 lines(s,['Số ô của bảng hai chiều','L là độ dài điển hình'],80,459,500,27,C.muted,43);lines(s,['Số ô của bảng k chiều','Nhanh chóng vượt khả năng lưu trữ'],690,459,520,27,C.muted,43);
 takeaway(s,'Dự án ghép dần theo cây hướng dẫn để tạo căn chỉnh đa chuỗi');
 notes(s,'Với hai chuỗi độ dài gần L, bảng DP có khoảng L bình phương ô. Nếu mở rộng trực tiếp để đồng thời xét k chuỗi, bảng có k chiều với khoảng L mũ k ô. Đây mới chỉ là số trạng thái, chưa tính số chuyển trạng thái. Vì vậy dự án dùng progressive alignment: căn chỉnh các chuỗi hoặc nhóm chuỗi theo một cây hướng dẫn. Mỗi bước ghép có thể giải tốt bài toán con theo mô hình của nó, nhưng toàn bộ chiến lược không bảo đảm tìm nghiệm MSA tối ưu toàn cục. Chuyển lời cho người thứ hai để đi vào bộ giải bài toán cặp.',['README.md','src/tree/guide_tree.cpp']);
}
// 7 — Pipeline.
{
 const s=page('Luồng xử lý của dự án','Bộ giải cặp và bộ giải đa chuỗi có vai trò khác nhau');
 step(s,'01','Tính khoảng cách từng cặp','Điểm căn chỉnh cặp được chuẩn hóa thành khoảng cách',235);
 step(s,'02','Dựng cây hướng dẫn UPGMA','Chọn thứ tự ghép các chuỗi và các nhóm',340);
 step(s,'03','Căn chỉnh profile theo cây','Myers–Miller giải các bước ghép profile',445);
 takeaway(s,'Kết quả: ma trận đa chuỗi cùng độ dài, xuất ra FASTA');
 notes(s,'Đầu tiên hệ thống căn chỉnh các cặp để tạo ma trận khoảng cách. Sau đó UPGMA dựng cây hướng dẫn. Cuối cùng, duyệt cây từ lá lên: mỗi lá là một chuỗi, mỗi nút trong ghép hai profile. Bộ giải Myers–Miller nằm ở các bước ghép profile. Một chi tiết quan trọng của bản triển khai hiện tại: khâu tính khoảng cách vẫn gọi Gotoh lưu bảng đầy đủ, nên không thể lấy bộ nhớ tuyến tính của một bộ giải con để kết luận toàn bộ pipeline dùng bộ nhớ tuyến tính.',['src/tree/distance_matrix.cpp','src/tree/upgma.cpp','src/align/profile_aligner.cpp']);
}
// 8 — DP recurrence core.
{
 const s=page('Quy hoạch động với affine gap','Một ô cần phân biệt cách căn chỉnh kết thúc');
 tab(s,[['Trạng thái','Ý nghĩa'],['M(i, j)','Kết thúc bằng cặp ký tự'],['Iₓ(i, j)','Kết thúc bằng gap ở chuỗi thứ hai'],['Iᵧ(i, j)','Kết thúc bằng gap ở chuỗi thứ nhất']],80,240,1120,258,{size:28,widths:[300,820],header:true});
 tx(s,'H(i, j) = max{M(i, j), Iₓ(i, j), Iᵧ(i, j)}',80,535,1120,55,34,C.teal,true,'Consolas');
 sourceFoot(s,'Chi tiết recurrence và điều kiện biên: phụ lục 25');
 notes(s,'Mỗi ô đại diện cho căn chỉnh hai tiền tố. Nếu chỉ lưu một giá trị, chúng ta không biết gap đang được mở hay được kéo dài, nên không tính đúng phạt affine. Gotoh lưu ba trạng thái: M kết thúc bằng hai ký tự, Ix kết thúc bằng một ký tự của chuỗi thứ nhất đối diện gap, Iy là chiều ngược lại. M chuyển từ đường chéo; Ix từ phía trên; Iy từ bên trái. Giá trị tốt nhất của ô là max ba trạng thái. Phần phụ lục chứa công thức đầy đủ, kể cả chuyển từ loại gap này sang loại gap kia theo code hiện có.',['src/align/needleman_wunsch.cpp',REF.gotoh]);
}
// 9 — Computed matrix.
{
 const s=page('Ví dụ DP trên hai chuỗi protein','ACDE và ACDF, BLOSUM62, mở gap −10, kéo dài −1');matrix(s,'score');
 tx(s,'Điểm kết thúc: 16',732,247,460,48,33,C.teal,true);lines(s,['A / A:     +4','C / C:     +9','D / D:     +6','E / F:     −3'],732,326,470,30,C.ink,50);
 takeaway(s,'Một căn chỉnh đạt điểm 16: ACDE / ACDF');
 notes(s,'Bảng hiển thị H, tức giá trị tốt nhất trong ba trạng thái của mỗi ô. Cột và hàng rỗng tương ứng tiền tố có độ dài 0. Với ACDE và ACDF, phương án không có gap cho điểm 4+9+6-3=16. DP cũng cho giá trị kết thúc 16 nên phương án này đạt tối ưu theo mô hình điểm của bài toán cặp. Chúng ta đang giải global alignment, sử dụng toàn bộ hai chuỗi. Ví dụ này nhỏ có chủ đích để người nghe theo được các số.',['src/core/blosum62.cpp','src/align/needleman_wunsch.cpp','Ví dụ được tính lại khi tạo slide bằng recurrence của dự án']);
}
// 10 — Traceback memory.
{
 const s=page('Truy vết và chi phí lưu bảng','Biết điểm tối ưu chưa đủ để khôi phục căn chỉnh');matrix(s,'path');
 tx(s,'Gotoh lưu bảng đầy đủ',732,246,480,44,30,C.teal,true);lines(s,['Truy vết từ cuối về đầu','Theo trạng thái đã chọn','Khôi phục ký tự và gap'],732,317,470,26,C.ink,48);
 tx(s,'3(m + 1)(n + 1)',732,492,470,48,33,C.ink,true,'Consolas');tx(s,'giá trị DP, chưa tính chuỗi kết quả',732,546,470,38,24,C.muted);
 takeaway(s,'Myers–Miller tìm cách truy vết với ít bộ nhớ làm việc hơn');
 notes(s,'Từ ô cuối, traceback đi ngược về ô đầu theo các quyết định tối ưu. Trong hình, đường đi của ví dụ nằm trên đường chéo. Với affine gap, traceback phải theo cả loại trạng thái, không chỉ theo giá trị H đã rút gọn trên slide. Cách cài Gotoh cơ bản lưu ba bảng có kích thước m+1 nhân n+1 nên bộ nhớ là bậc hai. Nếu chỉ cần điểm số, có thể cuộn hàng. Nhưng khi cần cả chuỗi căn chỉnh, chúng ta phải có cách khôi phục đường đi mà không giữ mọi ô. Đây là lý do đưa chia để trị vào.',['src/align/needleman_wunsch.cpp',REF.mm]);
}
// 11 — Approved cut example.
{
 const s=page('Điểm cắt Myers–Miller','Ví dụ protein: ACDE và ACDF');matrix(s,'cut');
 tx(s,'Cắt sau AC',732,234,460,44,31,C.teal,true);lines(s,['Quét điểm từ hai phía để tìm','vị trí đi qua hàng giữa.'],732,296,470,26,C.ink,38);
 tx(s,'AC / AC     DE / DF',732,414,470,45,31,C.ink,true,'Consolas');lines(s,['Giải tiếp hai bài toán con,','rồi ghép kết quả căn chỉnh.'],732,488,470,26,C.ink,38);
 takeaway(s,'Mục tiêu: truy vết mà không lưu toàn bộ bảng DP');
 notes(s,'Chọn một hàng giữa của chuỗi thứ nhất, ở đây là sau AC. Câu hỏi then chốt: đường căn chỉnh tối ưu đi qua vị trí nào trên hàng này? Thuật toán tính điểm đi từ đầu đến hàng giữa và điểm đi ngược từ cuối về hàng giữa. Kết hợp thông tin hai phía để tìm cột và trạng thái cắt phù hợp. Sau đó giải hai nửa rồi ghép kết quả. Bảng đầy đủ trên slide chỉ dùng minh họa vị trí cắt. Thuật toán thật dùng các vector điểm. Với affine gap, phải xét trạng thái gap tại ranh giới, không chỉ lấy tổng hai điểm vô điều kiện.',['src/align/hirschberg.cpp',REF.mm]);
}
// 12 — Make the cut selection visible before discussing the recursion cost.
{
 const s=page('Chọn cột cắt từ hai lượt quét','Trong ví dụ này, nghiệm chọn không có gap chạy xuyên điểm cắt');
 const f=Array.from({length:5},(_,j)=>dp('AC','ACDF'.slice(0,j)).score);
 const r=Array.from({length:5},(_,j)=>dp('DE','ACDF'.slice(j)).score);
 const sum=f.map((v,j)=>v+r[j]);if(sum[2]!==16||sum.some((v,j)=>j!==2&&v>=16))throw Error('Ambiguous cut example');
 const t=tab(s,[['Cột cắt j','0','1','2','3','4'],['Điểm tiến F',...f.map(fmt)],['Điểm lùi R',...r.map(fmt)],['F + R',...sum.map(fmt)]],80,241,1120,255,{size:29,widths:[310,162,162,162,162,162],mono:true,grid:true,header:true});
 for(let i=1;i<4;i++)highlight(t,i,3,i===3,29);
 tx(s,'Nửa trái: AC / AC',80,532,535,50,31,C.ink,true,'Consolas');tx(s,'Nửa phải: DE / DF',690,532,520,50,31,C.ink,true,'Consolas');
 takeaway(s,'Chọn j = 2, giải hai nửa rồi ghép: 13 + 3 = 16');
 notes(s,'F(j) là điểm tốt nhất khi căn chỉnh AC với tiền tố độ dài j của ACDF. R(j) là điểm tốt nhất khi căn chỉnh DE với hậu tố bắt đầu sau j ký tự của ACDF. Hai lượt DP tiến và lùi cho hai vector trên. Với ví dụ này, tổng lớn nhất là 16 ở j=2 và phép nối không có gap xuyên ranh giới, nên hình minh họa đúng điểm cắt đã chọn. Bài toán trái là AC với AC, đạt 13; bài toán phải là DE với DF, đạt 3. Không dùng bảng F+R này như toàn bộ thuật toán affine gap tổng quát: cần kiểm tra trạng thái biên và hiệu chỉnh khi một gap kéo xuyên qua ranh giới. Tiếp tục chia đến khi một chiều đủ nhỏ thì giải trực tiếp bằng DP, sau đó ghép các phần căn chỉnh.',['src/align/hirschberg.cpp','Ví dụ vector được tính từ recurrence và BLOSUM62 của dự án',REF.mm]);
}
// 13 — Theory, clearly scoped.
{
 const s=page('Chi phí của chia để trị','Phân tích lý thuyết cho một bài toán căn chỉnh cặp');
 tx(s,'Thời gian',80,253,500,44,31,C.teal,true);tx(s,'Bộ nhớ DP làm việc',690,253,510,44,31,C.teal,true);
 tx(s,'O(mn)',80,334,500,92,66,C.ink,true,'Consolas');tx(s,'O(min(m, n))',690,334,510,92,58,C.ink,true,'Consolas');
 lines(s,['Tổng diện tích các mức giảm dần','mn + mn/2 + mn/4 + …'],80,460,530,26,C.muted,44);lines(s,['Giữ vector theo chiều ngắn hơn','Giải phóng vùng tạm trước khi đệ quy'],690,460,520,26,C.muted,44);
 takeaway(s,'Đổi việc lưu toàn bộ bảng lấy việc tính lại điểm ở các mức');
 notes(s,'Ở mỗi mức, các lượt quét tiến và lùi có chi phí tỷ lệ diện tích bài toán. Khi chia chiều thứ nhất làm đôi, tổng diện tích các bài toán con giảm theo cấp số nhân, nên tổng vẫn là O(mn). Thuật toán Myers–Miller chuẩn chỉ cần bộ nhớ DP làm việc tuyến tính theo chiều ngắn hơn khi bố trí đúng chiều và tái sử dụng hoặc giải phóng các vector. Chưa tính vùng lưu đầu ra và ngăn xếp đệ quy. Đây là kết quả lý thuyết của bộ giải cặp, không phải phép đo RAM toàn chương trình và không phải kết luận về toàn pipeline hiện có. Phụ lục 26 nêu khác biệt của code thực tế. Chuyển lời cho người thứ ba.',['src/align/hirschberg.cpp',REF.mm]);
}
// 14 — UPGMA merge table, rather than a decorative illustration.
{
 const s=page('UPGMA chọn thứ tự ghép','Gom hai cụm gần nhau nhất rồi cập nhật khoảng cách trung bình');
 const d=[['','S₁','S₂','S₃','S₄'],['S₁','0','0,1','0,8','0,9'],['S₂','0,1','0','0,7','0,8'],['S₃','0,8','0,7','0','0,2'],['S₄','0,9','0,8','0,2','0']];
 const t=tab(s,d,80,248,560,290,{size:29,widths:[112,112,112,112,112],mono:true,grid:true});highlight(t,1,2,true,29);highlight(t,2,1,true,29);
 lines(s,['Lượt 1: ghép S₁ và S₂','Lượt 2: ghép S₃ và S₄','Lượt 3: ghép hai nhóm'],710,271,490,29,C.ink,80);
 takeaway(s,'Cây hướng dẫn xác định thứ tự giải các bước ghép profile');
 notes(s,'Ma trận này là ví dụ giảng dạy tự xây dựng, không phải số đo khoảng cách của các chuỗi ở slide trước. Cặp S1,S2 gần nhất với 0,1 nên được ghép đầu tiên. Khoảng cách từ cụm mới đến cụm khác được tính bằng trung bình có trọng số theo số chuỗi. S3,S4 tạo nhóm tiếp theo, rồi hai nhóm hợp lại. UPGMA ở đây là cây hướng dẫn thuật toán, không được xem như bằng chứng độc lập về cây tiến hóa thật. Khoảng cách thực trong dự án lấy một trừ điểm cặp chia điểm tự so lớn hơn, chặn trong khoảng 0 đến 2.',['src/tree/upgma.cpp','src/tree/distance_matrix.cpp','Ví dụ khoảng cách tự xây dựng']);
}
// 15 — Profile propagation.
{
 const s=page('Profile giữ lại căn chỉnh của một nhóm','Khi thêm một gap vào profile, mọi hàng trong nhóm cùng nhận gap');
 tx(s,'Hai nhóm trước khi ghép',80,248,700,45,30,C.teal,true);
 tab(s,[['S₁','A','C','D'],['S₂','A','C','E']],80,314,450,130,{size:35,widths:[120,110,110,110],mono:true});tab(s,[['S₃','A','D'],['S₄','A','E']],700,314,430,130,{size:35,widths:[130,150,150],mono:true});
 tx(s,'Sau khi ghép',80,494,340,50,30,C.teal,true);
 const t=tab(s,[['S₃','A','–','D'],['S₄','A','–','E']],500,480,630,114,{size:33,widths:[180,150,150,150],mono:true});highlight(t,0,2,false,33);highlight(t,1,2,false,33);
 takeaway(s,'Myers–Miller căn chỉnh các cột của hai profile');
 notes(s,'Một profile lưu nhiều hàng đã căn chỉnh và phân bố amino acid ở mỗi cột. Khi ghép profile với profile, đơn vị DP là cột thay vì một amino acid đơn lẻ. Code tính điểm hai cột bằng tần suất amino acid và BLOSUM62, rồi làm tròn trước khi đưa vào kernel. Hình minh họa nhóm bên phải cần một cột trống, nên cả S3 và S4 đều nhận gap tại cùng vị trí. Nhóm trái giữ các hàng ACD và ACE. Toàn bộ kết quả cuối là ACD, ACE, A-D, A-E. Đây là minh họa phép lan truyền gap, không tuyên bố là kết quả tối ưu của bộ giải cho các nhóm này.',['src/core/profile.cpp','src/align/profile_aligner.cpp','src/align/hirschberg.cpp']);
}
// 16 — Parallel schedules in a native evidence table.
{
 const s=page('Các công việc có thể chạy song song','Công việc độc lập chạy cùng lúc, bước ghép cha chờ các con');
 tab(s,[['Tầng tính toán','Các công việc độc lập','Điểm chờ'],['Khoảng cách','(S₁,S₂), (S₁,S₃), …','Đủ ma trận khoảng cách'],['Profile theo cây','Ghép (S₁,S₂) và (S₃,S₄)','Hai profile con hoàn tất'],['Nút gốc','Ghép hai profile cuối','Trả về MSA']],80,249,1120,300,{size:25,widths:[270,500,350],header:true,grid:true});
 takeaway(s,'OpenMP chia tải theo cặp và theo các nhánh độc lập');
 notes(s,'Khâu khoảng cách có k nhân k trừ một chia hai cặp. Mỗi cặp có thể được tính độc lập nên thuận lợi chia cho các luồng. Ở cây hướng dẫn, hai nhánh con độc lập có thể được xử lý đồng thời. Nhưng một nút cha chỉ ghép được sau khi cả hai profile con đã xong. Gần gốc, số việc độc lập giảm xuống. Bản cài hiện tại dùng OpenMP parallel for với lịch động cho các cặp và parallel sections đệ quy cho hai nhánh, không phải một bộ lập lịch task toàn cục. Việc chia nhỏ quá nhiều cũng có chi phí tạo luồng và đồng bộ.',['src/tree/distance_matrix.cpp','src/parallel/tree_scheduler.cpp']);
}
// 17 — Editable wavefront schedule table.
{
 const s=page('Wavefront trên các đường chéo phụ','Các ô cùng i + j có thể tính sau khi dữ liệu phụ thuộc đã sẵn sàng');
 const v=[['i / j','1','2','3','4'],...Array.from({length:4},(_,i)=>[String(i+1),...Array.from({length:4},(_,j)=>String(i+j+2))])];
 const t=tab(s,v,80,244,540,300,{size:29,mono:true,grid:true});for(let i=1;i<=4;i++)for(let j=1;j<=4;j++)if(i+j===5)highlight(t,i,j,true,29);
 lines(s,['Mỗi số là chỉ số đường chéo','Cùng màu: các ô cùng đợt tính','Đồng bộ trước khi sang đợt sau'],690,264,520,27,C.ink,65);
 takeaway(s,'Module wavefront có trong dự án, tách khỏi pipeline benchmark chính');
 notes(s,'Mỗi ô phụ thuộc các ô phía trên, bên trái và đường chéo trước đó. Những ô có cùng tổng chỉ số i+j không phụ thuộc trực tiếp nhau nên có thể tính đồng thời. Các ô tô xanh là một đợt wavefront; xong đợt này mới tiến sang đợt sau. Cần phân biệt sự tồn tại của module với đường thực thi: benchmark pipeline đang gọi DistanceMatrix dùng NeedlemanWunsch và bộ ghép profile dùng HirschbergAligner, không gọi wavefront. Vì vậy số liệu tăng tốc của pipeline ở phần sau không phải phép đo riêng lợi ích wavefront. Hàm wavefront_gotoh_score và hàm trả căn chỉnh cũng có cấu trúc lưu trữ khác nhau.',['src/parallel/wavefront.cpp','src/tree/distance_matrix.cpp','src/eval/benchmark.cpp']);
}
// 18 — MPI extension, accurately bounded.
{
 const s=page('Mở rộng MPI kết hợp OpenMP','Phân tán các cặp ở bước tính khoảng cách');
 step(s,'01','Chia cặp cho các MPI rank','Chỉ số cặp mod số rank xác định rank nhận việc',235);
 step(s,'02','Tính cặp bằng OpenMP trong từng rank','MPI_Allreduce tổng hợp ma trận khoảng cách',340);
 step(s,'03','Rank 0 dựng cây và ghép profile','Phần progressive tiếp tục trên rank 0',445);
 takeaway(s,'Kết quả OpenMP ở phần sau chưa chứng minh tốc độ trên cụm MPI');
 notes(s,'Khi có nhiều máy hoặc nhiều tiến trình, target MPI phân các cặp cho các rank. Bên trong một rank, OpenMP tiếp tục chia các cặp được giao cho nhiều luồng. Các rank tổng hợp ma trận bằng MPI_Allreduce. Theo code hiện tại, rank 0 là nơi dựng cây và thực hiện progressive alignment; không có phân tán toàn cây qua MPI. Đây là hướng mở rộng kiến trúc đã có trong source. Bộ kết quả CSV hiện tại đo OpenMP trên một tiến trình, nên chúng ta không dùng nó để kết luận về mức tăng tốc của cụm MPI. Chuyển lời cho người thứ tư để xem thực nghiệm.',['src/parallel/mpi_distance_matrix.cpp','src/msa_mpi_main.cpp','results/benchmark_summary.csv']);
}
// 19 — Experimental questions and boundaries.
{
 const s=page('Ba câu hỏi thực nghiệm','Kết quả lưu trong dự án, không phải một lượt đo mới');
 step(s,'01','Điểm số cặp có trùng Gotoh?','Đối chiếu bộ giải cặp và chỉ số bộ nhớ do code báo',235);
 step(s,'02','Thêm luồng có giảm thời gian?','So sánh 1, 2, 4 và 8 luồng OpenMP',340);
 step(s,'03','Căn chỉnh có gần dữ liệu chuẩn?','Đối chiếu SP và TC trên các bộ BAliBASE được chọn',445);
 takeaway(s,'Mỗi phép đo trả lời một câu hỏi, với một phạm vi riêng');
 notes(s,'Thực nghiệm chia làm ba nhóm. Nhóm đầu so điểm căn chỉnh cặp giữa Gotoh và Myers–Miller. Nhóm thứ hai xem thời gian pipeline khi đổi số luồng. Nhóm thứ ba so căn chỉnh thu được với reference BAliBASE. Bản v3 dùng lại log và CSV trong dự án, không tuyên bố đã chạy benchmark mới. Với phần scaling, runner lấy trung bình các lần lặp, cấu hình từ CLI là hai lần; kết quả chưa kèm khoảng tin cậy hoặc đầy đủ cấu hình máy để khái quát sang máy khác. Các ca accuracy dùng dữ liệu đầu vào khác cách trích xuất ở nhóm scaling nên cần đọc đúng Category trong CSV.',['results/benchmark_summary.csv','scripts/run_benchmarks.py','src/eval/benchmark.cpp','src/main.cpp',REF.balibase]);
}
// 20 — A comparison table with an explicit measurement boundary.
{
 const s=page('Đối chiếu điểm số và bộ nhớ','Cặp protein dài 901 và 897 amino acid trong log hiện có');
 tab(s,[['Chỉ số','Gotoh','Myers–Miller'],['Điểm căn chỉnh cặp','4.159','4.159'],['Chỉ số bộ nhớ code báo','9.723.566 B','7.184 B'],['Thời gian trong log','11,11 ms','14,47 ms']],80,246,1120,282,{size:29,widths:[480,320,320],header:true,grid:true});
 tx(s,'≈ 1.353,5 lần',80,554,570,61,44,C.teal,true);tx(s,'tỷ số của hai chỉ số bộ nhớ',650,567,540,42,26,C.muted);
 sourceFoot(s,'Chỉ số ước tính từ công thức trong code, chưa phải phép đo RAM đỉnh thực tế');
 notes(s,'Ở cặp chuỗi dài trong log, hai bộ giải cùng cho điểm 4159. Đây là đối chiếu điểm bài toán cặp trong ca đo, không có nghĩa toàn bộ MSA đúng sinh học 100%. Cột bộ nhớ cần đọc thận trọng. Trường peak_memory_bytes của Myers–Miller hiện gán bằng 2 nhân min(m,n)+1 nhân sizeof(int); Gotoh báo từ kích thước bảng và dung lượng chuỗi kết quả. Tỷ số 9723566 chia 7184 xấp xỉ 1353,5, nhưng đây là so sánh chỉ số công thức, chưa chứng minh RAM đỉnh thực. Log cũng cho thấy thời gian Myers–Miller ở ca này cao hơn. Chúng ta trình bày đánh đổi bộ nhớ và thời gian, không gán giảm RAM toàn pipeline.',['results/logs/memory_gotoh_vs_hirschberg.log','src/align/hirschberg.cpp','src/align/needleman_wunsch.cpp']);
}
// 21 — Editable speedup chart using source CSV values, including a regression.
{
 const s=page('Thêm luồng không luôn nhanh hơn','Speedup S(p) = T(1) / T(p), đo toàn pipeline OpenMP');
 const sets=[['BB20001',C.teal],['Benchmark 40',C.ink],['BB12001',C.warm]];
 chart(s,'line',{position:{left:72,top:230,width:805,height:330},categories:['1','2','4','8'],lineOptions:{smooth:false},series:sets.map(([id,color])=>({name:id==='Benchmark 40'?'40 chuỗi':id,values:scale(id).map(d=>d.speed),smooth:false,line:{fill:color,width:3},marker:{symbol:'circle',size:7,fill:color}})),hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontSize:19,fill:C.ink}},xAxis:{title:{text:'Số luồng',textStyle:{fontSize:18,fill:C.muted}},textStyle:{fontSize:19,fill:C.muted},majorGridlines:null},yAxis:{title:{text:'Speedup',textStyle:{fontSize:18,fill:C.muted}},min:0,max:2,majorUnit:0.5,numberFormatCode:'0.0"×"',textStyle:{fontSize:18,fill:C.muted},majorGridlines:{fill:C.line,width:1}}});
 tx(s,'1,73×',931,260,275,75,57,C.teal,true);tx(s,'BB20001, 8 luồng',931,347,280,38,23,C.muted);
 tx(s,'0,70×',931,423,275,75,57,C.warm,true);tx(s,'BB12001, 8 luồng',931,510,280,38,23,C.muted);
 takeaway(s,'Tải công việc và chi phí đồng bộ ảnh hưởng hiệu quả song song');
 sourceFoot(s,'Nguồn: benchmark_summary.csv, nhóm Scalability');
 notes(s,'Trục ngang là số luồng, trục dọc là speedup so với một luồng. BB20001 đạt khoảng 1,73 lần ở tám luồng, trong khi bộ 40 chuỗi đạt khoảng 1,61 lần. Nhưng BB12001 chỉ còn 0,70 lần, nghĩa là chạy chậm hơn mốc một luồng. Vì vậy kết luận đúng là lợi ích song song phụ thuộc dữ liệu và cách chia tải. Các phụ thuộc ở cây, overhead tạo luồng và đồng bộ là những yếu tố hợp lý để khảo sát tiếp. Chưa có profiling để kết luận chính xác bao nhiêu phần trăm thời gian do từng nguyên nhân, nên không khẳng định bão hòa cache hay băng thông từ biểu đồ này.',['results/benchmark_summary.csv (Category=Scalability)','results/logs/benchmark_scaling_threads.log','src/parallel/tree_scheduler.cpp']);
}
// 22 — Accuracy is a different metric from optimization score.
{
 const s=page('Chất lượng căn chỉnh theo dữ liệu chuẩn','SP: đúng các cặp residue. TC: đúng toàn cột theo phép chấm của dự án');
 const ids=['BB11001','BB12003','BB20003'];
 const rows=ids.map(id=>{const r=accuracy.find(d=>d.Dataset.includes(id));return[id,`${(100*Number(r.SP_Score)).toFixed(1).replace('.',',')}%`,`${(100*Number(r.TC_Score)).toFixed(1).replace('.',',')}%`];});
 tab(s,[['Bộ dữ liệu','SP','TC'],...rows],80,251,1120,278,{size:33,widths:[520,300,300],header:true,grid:true});
 takeaway(s,'SP cao vẫn có thể đi cùng TC thấp');sourceFoot(s,'Nguồn: nhóm BAliBASE_Accuracy, không trộn với nhóm Scalability');
 notes(s,'Đây là ba ví dụ được chọn từ 13 ca BAliBASE_Accuracy, không phải trung bình của cả BAliBASE. BB11001 có SP khoảng 98,2% và TC khoảng 96,5%; BB12003 có SP khoảng 93,0%, TC khoảng 83,8%; BB20003 có SP khoảng 92,0% nhưng TC bằng 0. SP đếm tỷ lệ các cặp residue tham chiếu còn căn đúng. TC của code yêu cầu tất cả residue trong một cột tham chiếu đủ điều kiện cùng nằm một cột ở kết quả. Do đó nhiều quan hệ cặp vẫn đúng trong khi không cột nào đúng trọn vẹn. Số liệu chưa tự chỉ ra chính xác chuỗi nào gây lệch. Không nói 92% chuỗi đúng hay 100% độ chính xác sinh học.',['results/benchmark_summary.csv (Category=BAliBASE_Accuracy)','src/eval/sp_score.cpp','src/eval/tc_score.cpp',REF.balibase]);
}
// 23 — Existing project screenshot, not generated artwork.
{
 const s=page('Demo: từ chuỗi đầu vào đến căn chỉnh','2 phút trên Web GUI, dùng Hemoglobin để theo dõi các hàng kết quả');
 const bytes=await fs.readFile(path.join(root,'docs/images/fig_5_1_web_alignment_matrix.png'));
 s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:'Ảnh giao diện MSA Pipeline Studio có trong dự án, minh họa bảng căn chỉnh',fit:'contain',position:{left:80,top:246,width:800,height:410}});
 lines(s,['1. Chọn Hemoglobin','2. Chạy căn chỉnh','3. Xem gap và cây','4. Xuất FASTA'],920,258,300,24,C.ink,68);
 sourceFoot(s,'Ảnh dự phòng: kết quả đã lưu của bộ 40 chuỗi; demo trực tiếp dùng Hemoglobin');
 notes(s,'Chuẩn bị trước buổi: chạy .\\run_gui.bat ở thư mục dự án, mở localhost:8000, xác nhận engine sẵn sàng. Đây là hướng dẫn thao tác cho buổi báo cáo; bản slide không tuyên bố đã chạy demo mới. 0–20 giây: chuyển sang trình duyệt, chọn Hemoglobin và chế độ Standard. 20–50 giây: chọn 4 luồng, chạy căn chỉnh. 50–90 giây: chỉ các hàng cùng độ dài, các gap và vùng bảo tồn, chuyển Guide Tree để liên hệ thứ tự ghép. 90–120 giây: xuất FASTA, nói rằng bỏ gap phải khôi phục chuỗi đầu vào. Ảnh trong slide là ảnh đã có của bộ 40 chuỗi, dùng dự phòng, không phải kết quả Hemoglobin. Nếu không khởi động được GUI, dùng CLI đã ghi trong kịch bản v3 hoặc mở ảnh dự phòng và nói rõ đó là kết quả đã lưu.',['docs/images/fig_5_1_web_alignment_matrix.png','run_gui.bat','web/static/js/app.js','data/presets/hemoglobin.fa']);
}
// 24 — Conclusion with appropriate limits.
{
 const s=page('Kết luận','Ba kỹ thuật phối hợp ở các cấp khác nhau');
 step(s,'01','Quy hoạch động','Giải các bài toán căn chỉnh cặp và cột profile',235);
 step(s,'02','Chia để trị','Khôi phục căn chỉnh bằng các lượt quét tiến và lùi',340);
 step(s,'03','Song song','Khai thác các cặp và nhánh độc lập trong pipeline',445);
 takeaway(s,'Ưu tiên tiếp theo: đo RAM thực, profiling và cải thiện chất lượng MSA');
 notes(s,'Tổng kết: quy hoạch động xác định điểm và chuyển trạng thái; Myers–Miller dùng chia để trị để giảm nhu cầu lưu bảng của bộ giải cặp; OpenMP khai thác các công việc độc lập. Căn chỉnh đa chuỗi trong dự án dùng chiến lược progressive nên không bảo đảm tối ưu MSA toàn cục. Thực nghiệm đã lưu có ca được lợi khi tăng luồng và có ca chậm hơn. Chỉ số bộ nhớ công thức cần được kiểm chứng bằng đo allocation và RAM thực. Hướng phát triển là profiling trước khi tối ưu thêm, kiểm tra bộ nhớ theo triển khai, và cân nhắc iterative refinement cho chất lượng căn chỉnh. Cảm ơn thầy cô và các bạn, xin nhận câu hỏi.',['src/align/hirschberg.cpp','src/parallel/tree_scheduler.cpp','results/benchmark_summary.csv']);
}
// 25 — Recurrence appendix: includes actual transitions used in source.
{
 const s=page('Phụ lục: công thức truy hồi','Theo các chuyển trạng thái trong Gotoh của dự án');
 lines(s,['M(i,j) = max{M, Iₓ, Iᵧ}(i−1,j−1) + s(aᵢ,bⱼ)','Iₓ(i,j) = max{M(i−1,j)−10, Iₓ(i−1,j)−1, Iᵧ(i−1,j)−10}','Iᵧ(i,j) = max{M(i,j−1)−10, Iᵧ(i,j−1)−1, Iₓ(i,j−1)−10}'],80,248,1120,26,C.ink,82);
 lines(s,['M(0,0)=0; trạng thái không hợp lệ nhận −∞','Iₓ(i,0)=−10−(i−1); Iᵧ(0,j)=−10−(j−1)'],80,512,1120,25,C.muted,45);
 sourceFoot(s,'Điểm cắt Myers–Miller phải xét trạng thái biên và hiệu chỉnh gap chạy qua ranh giới');
 notes(s,'Công thức phản ánh code thực tế, bao gồm mở loại gap mới từ một trạng thái gap khác. M tại hai biên khác gốc là âm vô cùng. Mỗi bước traceback đi theo trạng thái chứ không chỉ theo H=max(M,Ix,Iy). Khi kết hợp forward và backward trong Myers–Miller, kiểm tra cả trường hợp điểm cắt thông thường và trường hợp gap kéo qua ranh giới. Không dùng F(j)+R(j) như một công thức hoàn chỉnh cho affine gap mà bỏ trạng thái và hiệu chỉnh.',['src/align/needleman_wunsch.cpp','src/align/hirschberg.cpp',REF.gotoh,REF.mm]);
}
// 26 — Code-aware complexity, not the optimistic README table.
{
 const s=page('Phụ lục: lý thuyết và triển khai','k là số chuỗi, L là độ dài điển hình, m và n là hai độ dài cặp');
 tab(s,[['Thành phần','Chi phí tuần tự','Lưu ý của bản hiện tại'],['Khoảng cách từng cặp','O(k²L²)','Gọi Gotoh lưu bảng đầy đủ'],['UPGMA quét cặp gần nhất','O(k³)','Mỗi lượt quét bảng các cụm'],['Myers–Miller chuẩn','O(mn), DP O(min(m,n))','Cần tái sử dụng vùng nhớ đúng'],['Ghép progressive','Σ O(mᵥnᵥ)','Độ dài profile thay đổi theo nút']],80,239,1120,305,{size:23,widths:[380,290,450],header:true,grid:true});
 lines(s,['Code hiện chưa hoán đổi chiều và giữ vector cha trong lúc đệ quy.','Chưa thể dùng công thức 2(min(m,n)+1) để chứng minh peak RAM.'],80,573,1120,24,C.muted,39);
 notes(s,'UPGMA đang lặp k-1 lần; ở mỗi lần, quét tất cả cặp cụm còn lại và xóa các phần tử bảng, nên thời gian tổng bậc ba với triển khai này. Không ghi O(k²) chỉ vì ma trận khoảng cách có bậc hai. Bộ giải Myers–Miller chuẩn có kết quả bộ nhớ tuyến tính theo chiều ngắn hơn khi quản lý vector và hướng đúng. Code hiện khởi tạo vector theo chiều thứ hai, chưa hoán đổi m,n, và các vector local forward/backward còn sống khi gọi đệ quy; thêm các chuỗi kết quả. Vì vậy số peak_memory_bytes gán theo hai hàng min không phải phép đo hoặc chứng minh peak thực. Cần một lượt kiểm tra riêng nếu muốn xác nhận bound của bản cài. Thời gian ghép progressive nên biểu diễn theo tổng chi phí từng nút vì profile có thể dài ra do gap.',['src/tree/upgma.cpp','src/tree/distance_matrix.cpp','src/align/hirschberg.cpp']);
}
// 27 — All accuracy results, preserving zero values and category boundaries.
{
 const s=page('Phụ lục: 13 ca đánh giá BAliBASE','Chỉ nhóm BAliBASE_Accuracy trong CSV');
 const rows=accuracy.map(d=>[d.Dataset.match(/BB\d+/)[0],Number(d.SP_Score).toFixed(4),Number(d.TC_Score).toFixed(4)]);
 const left=[['Bộ dữ liệu','SP','TC'],...rows.slice(0,7)],right=[['Bộ dữ liệu','SP','TC'],...rows.slice(7)];
 tab(s,left,80,236,535,335,{size:23,widths:[235,150,150],header:true,grid:true});tab(s,right,665,236,535,335,{size:23,widths:[235,150,150],header:true,grid:true});
 lines(s,['TC của code bỏ cột tham chiếu có gap; tùy cờ, chỉ xét core block.','Không diễn giải TC=0 thành “không có cặp residue nào căn đúng”.'],80,594,1120,23,C.muted,37);
 notes(s,'Bảng giữ đủ 13 ca trong nhóm accuracy, không chọn riêng các ca thuận lợi. Dữ liệu bảng trái gồm RV11 và hai ca đầu RV12; bảng phải gồm phần còn lại của RV12 và RV20. SP và TC in bốn chữ số thập phân. Code TC bỏ qua cột tham chiếu thiếu residue ở bất kỳ chuỗi nào, và cờ core_blocks_only còn lọc theo core block khi có. Định nghĩa hiển thị ở đây là phép chấm của dự án, chưa tuyên bố đã đối chiếu đồng nhất với một evaluator BAliBASE độc lập. Đầu vào nhóm scaling dùng đường MSF/reference, trong khi accuracy dùng FASTA unaligned, nên tên BB giống nhau không bảo đảm hai dòng thuộc cùng một phép thử.',['results/benchmark_summary.csv','scripts/run_benchmarks.py','src/eval/sp_score.cpp','src/eval/tc_score.cpp']);
}
// 28 — Source list; additional URLs are in the relevant speaker notes.
{
 const s=page('Tài liệu tham khảo','Nguồn học thuật và bằng chứng thực nghiệm');
 lines(s,['Gotoh (1982) — An improved algorithm for matching biological sequences','Myers & Miller (1988) — Optimal alignments in linear space','Henikoff & Henikoff (1992) — Amino acid substitution matrices','Thompson và cộng sự (2005) — BAliBASE 3.0'],80,247,1120,25,C.ink,65);
 lines(s,['Source code C++17 của dự án MSA Nhóm 5','benchmark_summary.csv và các log thực nghiệm trong results/logs'],80,549,1120,25,C.muted,43);
 notes(s,'Các đường dẫn đầy đủ bên dưới có thể mở từ ghi chú. Nguồn bài báo dùng cho thuật toán nền tảng và mô hình điểm; kết quả định lượng lấy từ file cục bộ và không gán cho bài báo. Không có phép benchmark mới khi xây dựng bản v3. Hình ảnh giao diện lấy từ docs/images của dự án. Các bảng chuỗi, DP và ví dụ UPGMA được xây dựng cho giảng dạy, với bảng DP tính lại từ BLOSUM62 thực trong source.',[REF.gotoh,REF.mm,REF.blosum,REF.balibase,'results/benchmark_summary.csv','results/logs/memory_gotoh_vs_hirschberg.log','results/logs/benchmark_scaling_threads.log','results/logs/balibase_accuracy_eval.log']);
}

if(p.slides.items.length!==28)throw Error('Expected 28 slides');
for(const id of ['BB20001','Benchmark 40','BB12001'])if(scale(id).length!==4)throw Error('Incomplete scaling data '+id);
if(accuracy.length!==13)throw Error('Accuracy source row count changed');
await fs.writeFile(path.join(tmp,'content-and-sources.json'),JSON.stringify(records,null,2));
const groups=[1,2,3,4].map(person=>{const rows=records.filter(r=>r.person===person);const seconds=rows.reduce((a,r)=>a+r.seconds,0);return {person,from:rows[0].n,to:rows.at(-1).n,seconds};});
let guide='# Kịch bản thuyết trình và demo MSA — v3\n\n';
guide+='Bản PowerPoint: `outputs/slides-v3/Slide_Thuyet_Trinh_PTTKTT_Nhom_5_MSA_v3.pptx`.\n\n28 slide tổng cộng: 24 slide trình bày chính và 4 slide phụ lục. Các bước minh họa nằm trên slide liên tiếp; không phụ thuộc animation.\n\n';
guide+='## Phân công và thời lượng\n\n| Người | Slide | Thời lượng dự kiến |\n|---|---|---|\n'+groups.map(g=>`| ${g.person} | ${g.from}–${g.to} | ${Math.floor(g.seconds/60)} phút ${g.seconds%60} giây${g.person===4?' (gồm 2 phút demo)':''} |`).join('\n')+'\n\nTổng 18 phút 20 giây, gồm 16 phút 20 giây trình bày và 2 phút demo. Thời lượng là gợi ý, cần tập thử theo tốc độ nói của nhóm.\n\n';
guide+='## Chuẩn bị và phương án dự phòng\n\n- Chạy `.\\run_gui.bat` từ thư mục gốc, mở `http://localhost:8000` và xác nhận engine sẵn sàng trước buổi báo cáo.\n- Chọn preset Hemoglobin, chế độ Standard, dùng 4 luồng cho demo.\n- Nếu GUI không sẵn sàng, có thể chạy CLI: `.\\build\\Release\\msa_align.exe -i data/presets/hemoglobin.fa -o outputs/slides-v3/demo_hemoglobin.aln.fa -t 4`. Đây là lệnh dự phòng, chưa được chạy trong quá trình làm slide.\n- Nếu không thể chạy ứng dụng, dùng ảnh giao diện có sẵn ở slide 23 và nói rõ là kết quả đã lưu của bộ 40 chuỗi.\n- Kết quả benchmark dùng từ log/CSV hiện có; chưa chạy lại benchmark và chưa kiểm tra ứng dụng PowerPoint trực tiếp.\n\n';
guide+='## Lưu ý học thuật\n\n- Tối ưu bài toán cặp không đồng nghĩa tối ưu MSA toàn cục hoặc đúng sinh học 100%.\n- Trường bộ nhớ từ bộ giải là ước lượng công thức, chưa phải RAM đỉnh đo thực.\n- UPGMA hiện thực hiện quét cặp mỗi vòng, thời gian O(k³).\n- Wavefront là module riêng, không phải đường gọi của benchmark pipeline đang báo.\n- MPI hiện phân tán khoảng cách; rank 0 làm cây/progressive, chưa có benchmark cụm trong bộ dữ liệu này.\n- Phép chấm TC của code có lọc cột có gap/core block. Không trộn các nhóm Scalability và BAliBASE_Accuracy.\n\n';
for(const r of records)guide+=`## Slide ${r.n}: ${r.title}\n\n${r.person?`Người ${r.person}, khoảng ${r.seconds} giây.`:'Phụ lục, mở khi cần.'}\n\n${r.notes}\n\nNguồn: ${r.sources.map(x=>/^https:/.test(x)?`[Bài gốc](${x})`:'`'+x+'`').join('; ')}\n\n`;
await fs.writeFile(path.join(root,'docs/Kich_Ban_Thuyet_Trinh_Va_Demo_Nhom_5_v3.md'),guide);

// Draft export precedes finalization. PNGs are for private visual QA.
const candidate=path.join(tmp,'candidate.pptx');
await(await PresentationFile.exportPptx(p)).save(candidate);
console.log('Draft exported: '+candidate);
for(let i=0;i<p.slides.items.length;i++){
 const slide=p.slides.items[i],blob=await p.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(tmp,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
 if((i+1)%5===0)console.log('Rendered '+(i+1)+' / 28');
}
const requirements={explicitTotalSlideCount:28,requiredNativeTableOwnerSlides:[...tableOwners].sort((a,b)=>a-b),requiredNativeChartOwnerSlides:chartOwners,nativeChartTargetApplication:'powerpoint',materializeLiteralChartWorkbooks:true};
const result=await finalizePresentation({...requirements,workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...requirements.requiredNativeTableOwnerSlides.flatMap(n=>['--require-native-table-slide',String(n)])],fontPolicy:{basis:'design',families:['Segoe UI','Consolas']},verifyArtifactToolImport:true,receiptPath:path.join(tmp,`validation-${Date.now()}.json`)});
console.log(JSON.stringify({finalPath:result.finalPath,sha256:result.finalSha256,slides:28,notes:records.length}));
