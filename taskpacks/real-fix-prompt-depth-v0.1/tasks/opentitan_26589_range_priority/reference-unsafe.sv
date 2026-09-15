module range_priority(input logic[7:0]addr_i,input logic read_i,en0_i,
  input logic[7:0]lo0_i,hi0_i,input logic allow_r0_i,allow_w0_i,en1_i,
  input logic[7:0]lo1_i,hi1_i,input logic allow_r1_i,allow_w1_i,
  output logic matched_o,allow_o,index_o);
  logic m0,m1;always_comb begin
    m0=en0_i&&(addr_i>=lo0_i)&&(addr_i<=hi0_i);m1=en1_i&&(addr_i>=lo1_i)&&(addr_i<=hi1_i);
    matched_o=m0||m1;allow_o=(m0&&(read_i?allow_r0_i:allow_w0_i))||(m1&&(read_i?allow_r1_i:allow_w1_i));
    index_o=!m0&&m1;
  end
endmodule
