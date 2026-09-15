#!/usr/bin/env python3
"""Build real-fix-derived prompt-depth tasks for contract-closure studies.

The source records come from a pinned HWE-Bench JSONL snapshot.  The generated
tasks are transparent, standalone reductions of an upstream bug mechanism; they
are not substitutes for HWE-Bench's full-repository fail-to-pass regressions.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from svgap.provenance import canonical_tree_digest


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "taskpacks/real-fix-prompt-depth-v0.1"
EXPECTED_DATASET_SHA256 = (
    "518c7781fea12e9c658f8b1b46e7736a68828da1269c983bb016722b14c5737a"
)
DATASET_URL = (
    "https://huggingface.co/datasets/henryen/hwe-bench/resolve/main/"
    "hwe_bench_full.jsonl"
)


@dataclass(frozen=True)
class Source:
    org: str
    repo: str
    number: int


@dataclass(frozen=True)
class Task:
    task_id: str
    top: str
    source: Source
    category: str
    oracle_class: str
    rule_id: str
    context: str
    requirement: str
    cycle_contract: str
    verification_contract: tuple[str, ...]
    interface: str
    testbench: str
    reference_safe: str
    reference_unsafe: str
    support_name: str
    support: str
    support_top: str | None
    depth: int
    message: str


def _protocol_tasks() -> tuple[Task, ...]:
    return (
        Task(
            task_id="ibex_882_icache_response",
            top="icache_response",
            source=Source("lowRISC", "ibex", 882),
            category="protocol",
            oracle_class="protocol",
            rule_id="REF-PROT-001",
            context=(
                "A completed instruction response could be withheld while the consumer "
                "was not ready, coupling response availability to acceptance."
            ),
            requirement=(
                "Buffer each available response. Assert valid as soon as it is buffered, "
                "independent of ready, and retain the response until accepted."
            ),
            cycle_contract=(
                "At a rising edge with available_i=1, capture data_i. From the following "
                "cycle through the first cycle with valid_o&&ready_i, valid_o is 1 and "
                "data_o is unchanged. ready_i controls consumption only."
            ),
            verification_contract=(
                "A response arriving while ready_i=0 is still advertised on valid_o.",
                "valid_o and data_o are stable throughout backpressure.",
                "Synchronous active-low reset clears valid_o.",
            ),
            interface="""module icache_response(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        available_i,
    input  logic [31:0] data_i,
    input  logic        ready_i,
    output logic        valid_o,
    output logic [31:0] data_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0, rst_n=0, available_i=0, ready_i=1, valid_o;
  logic [31:0] data_i=0, data_o;
  icache_response dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    @(negedge clk); available_i=1; data_i=32'h12345678;
    @(posedge clk); #1; if(!valid_o || data_o!==data_i) $fatal(1,"response");
    $display("PASS"); $finish;
  end
endmodule
""",
            reference_safe="""module icache_response(input logic clk, rst_n,
  input logic available_i, input logic [31:0] data_i, input logic ready_i,
  output logic valid_o, output logic [31:0] data_o);
  always_ff @(posedge clk) begin
    if (!rst_n) begin valid_o<=0; data_o<=0; end
    else if (!valid_o || ready_i) begin
      valid_o<=available_i; if (available_i) data_o<=data_i;
    end
  end
endmodule
""",
            reference_unsafe="""module icache_response(input logic clk, rst_n,
  input logic available_i, input logic [31:0] data_i, input logic ready_i,
  output logic valid_o, output logic [31:0] data_o);
  logic stored; logic [31:0] stored_data;
  always_ff @(posedge clk) begin
    if (!rst_n) begin stored<=0; stored_data<=0; end
    else if (available_i) begin stored<=1; stored_data<=data_i; end
    else if (ready_i) stored<=0;
  end
  assign valid_o=stored && ready_i; assign data_o=stored_data;
endmodule
""",
            support_name="properties.sv",
            support_top="icache_response_properties",
            support="""module icache_response_properties;
  (* anyseq *) logic clk, rst_n, available_i, ready_i;
  (* anyseq *) logic [31:0] data_i;
  logic valid_o, f_past_valid; logic [31:0] data_o;
  icache_response dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if (!f_past_valid) assume(!rst_n); else assume(rst_n);
    if (f_past_valid && $past(rst_n && available_i && !ready_i)) assert(valid_o);
    if (f_past_valid && $past(rst_n && valid_o && !ready_i)) begin
      assert(valid_o); assert(data_o==$past(data_o));
    end
  end
endmodule
""",
            depth=8,
            message="buffered instruction response is not persistent under backpressure",
        ),
        Task(
            task_id="ibex_332_fetch_request",
            top="fetch_request",
            source=Source("lowRISC", "ibex", 332),
            category="protocol",
            oracle_class="protocol",
            rule_id="REF-PROT-001",
            context=(
                "A branch redirect could replace the address of an instruction request "
                "that had not yet received a grant."
            ),
            requirement=(
                "Once a fetch request is issued, preserve its request and address until "
                "the request/grant handshake completes; queue no redirect into that beat."
            ),
            cycle_contract=(
                "If req_o&& !gnt_i is sampled on a rising edge, req_o must be 1 and "
                "addr_o must equal its previous value on every following stalled cycle."
            ),
            verification_contract=(
                "A redirect during a stall cannot modify the pending address.",
                "The request remains asserted until grant.",
                "Reset removes any pending request.",
            ),
            interface="""module fetch_request(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        start_i,
    input  logic [31:0] start_addr_i,
    input  logic        redirect_i,
    input  logic [31:0] redirect_addr_i,
    input  logic        gnt_i,
    output logic        req_o,
    output logic [31:0] addr_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,start_i=0,redirect_i=0,gnt_i=0,req_o;
  logic [31:0] start_addr_i=0,redirect_addr_i=0,addr_o;
  fetch_request dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    @(negedge clk); start_i=1; start_addr_i=32'h1000;
    @(posedge clk); #1; if(!req_o || addr_o!==32'h1000) $fatal(1,"request");
    @(negedge clk); start_i=0; gnt_i=1;
    @(posedge clk); $display("PASS"); $finish;
  end
endmodule
""",
            reference_safe="""module fetch_request(input logic clk,rst_n,start_i,
  input logic [31:0] start_addr_i,input logic redirect_i,
  input logic [31:0] redirect_addr_i,input logic gnt_i,
  output logic req_o,output logic [31:0] addr_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin req_o<=0; addr_o<=0; end
    else if(!req_o && start_i) begin req_o<=1; addr_o<=start_addr_i; end
    else if(req_o && gnt_i) req_o<=0;
  end
endmodule
""",
            reference_unsafe="""module fetch_request(input logic clk,rst_n,start_i,
  input logic [31:0] start_addr_i,input logic redirect_i,
  input logic [31:0] redirect_addr_i,input logic gnt_i,
  output logic req_o,output logic [31:0] addr_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin req_o<=0; addr_o<=0; end
    else begin
      if(!req_o && start_i) begin req_o<=1; addr_o<=start_addr_i; end
      else if(req_o && gnt_i) req_o<=0;
      if(req_o && redirect_i) addr_o<=redirect_addr_i;
    end
  end
endmodule
""",
            support_name="properties.sv",
            support_top="fetch_request_properties",
            support="""module fetch_request_properties;
  (* anyseq *) logic clk,rst_n,start_i,redirect_i,gnt_i;
  (* anyseq *) logic [31:0] start_addr_i,redirect_addr_i;
  logic req_o,f_past_valid; logic [31:0] addr_o;
  fetch_request dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n && req_o && !gnt_i)) begin
      assert(req_o); assert(addr_o==$past(addr_o));
    end
  end
endmodule
""",
            depth=8,
            message="pending fetch request or address changes before grant",
        ),
        Task(
            task_id="caliptra_747_ahb_error_completion",
            top="ahb_error_completion",
            source=Source("chipsalliance", "caliptra-rtl", 747),
            category="protocol",
            oracle_class="protocol",
            rule_id="REF-PROT-001",
            context=(
                "An internal AHB request-valid signal remained asserted for an extra "
                "cycle after an outstanding request completed with an error."
            ),
            requirement=(
                "Assert dv_o for an accepted transfer and clear it as soon as either a "
                "normal or error completion is sampled."
            ),
            cycle_contract=(
                "After a rising edge that samples dv_o&&(done_i||error_i), dv_o is low "
                "in the following cycle and remains low until a new transfer_i."
            ),
            verification_contract=(
                "Error completion and normal completion retire the request identically.",
                "No one-cycle tail is allowed after completion.",
                "Reset clears dv_o.",
            ),
            interface="""module ahb_error_completion(
    input  logic clk,
    input  logic rst_n,
    input  logic transfer_i,
    input  logic done_i,
    input  logic error_i,
    output logic dv_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,transfer_i=0,done_i=0,error_i=0,dv_o;
  ahb_error_completion dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1; transfer_i=1;
    @(posedge clk); #1; if(!dv_o) $fatal(1,"dv");
    @(negedge clk); transfer_i=0; done_i=1;
    @(posedge clk); $display("PASS"); $finish;
  end
endmodule
""",
            reference_safe="""module ahb_error_completion(input logic clk,rst_n,
  input logic transfer_i,done_i,error_i,output logic dv_o);
  always_ff @(posedge clk) begin
    if(!rst_n) dv_o<=0;
    else if(dv_o && (done_i||error_i)) dv_o<=0;
    else if(transfer_i) dv_o<=1;
  end
endmodule
""",
            reference_unsafe="""module ahb_error_completion(input logic clk,rst_n,
  input logic transfer_i,done_i,error_i,output logic dv_o);
  logic retire_q;
  always_ff @(posedge clk) begin
    if(!rst_n) begin dv_o<=0; retire_q<=0; end
    else begin
      retire_q<=dv_o&&(done_i||error_i);
      if(retire_q) dv_o<=0; else if(transfer_i) dv_o<=1;
    end
  end
endmodule
""",
            support_name="properties.sv",
            support_top="ahb_error_completion_properties",
            support="""module ahb_error_completion_properties;
  (* anyseq *) logic clk,rst_n,transfer_i,done_i,error_i;
  logic dv_o,f_past_valid; ahb_error_completion dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n && dv_o && (done_i||error_i))) assert(!dv_o);
  end
endmodule
""",
            depth=8,
            message="AHB downstream valid persists after error or normal completion",
        ),
        Task(
            task_id="caliptra_757_axi_sub_arbiter",
            top="axi_sub_arbiter",
            source=Source("chipsalliance", "caliptra-rtl", 757),
            category="protocol",
            oracle_class="protocol",
            rule_id="REF-PROT-001",
            context=(
                "A newly arriving write could replace a previously selected read while "
                "the shared downstream request was stalled."
            ),
            requirement=(
                "Apply write-over-read priority only when choosing a new beat. Latch the "
                "winner and its address until the downstream transfer is accepted."
            ),
            cycle_contract=(
                "For every cycle after out_valid_o&&!out_ready_i, out_valid_o, "
                "out_is_write_o, and out_addr_o remain unchanged until acceptance."
            ),
            verification_contract=(
                "Later arrivals cannot preempt a stalled winner.",
                "Priority is reevaluated only after handshake.",
                "Reset leaves no selected beat.",
            ),
            interface="""module axi_sub_arbiter(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        read_valid_i,
    input  logic [15:0] read_addr_i,
    input  logic        write_valid_i,
    input  logic [15:0] write_addr_i,
    input  logic        out_ready_i,
    output logic        out_valid_o,
    output logic        out_is_write_o,
    output logic [15:0] out_addr_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,read_valid_i=0,write_valid_i=0,out_ready_i=1;
  logic [15:0] read_addr_i=0,write_addr_i=0,out_addr_o;
  logic out_valid_o,out_is_write_o;
  axi_sub_arbiter dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    read_valid_i=1; read_addr_i=16'h1234;
    @(posedge clk); #1; if(!out_valid_o || out_is_write_o || out_addr_o!==16'h1234) $fatal(1,"arb");
    $display("PASS"); $finish;
  end
endmodule
""",
            reference_safe="""module axi_sub_arbiter(input logic clk,rst_n,
  input logic read_valid_i,input logic [15:0] read_addr_i,
  input logic write_valid_i,input logic [15:0] write_addr_i,input logic out_ready_i,
  output logic out_valid_o,out_is_write_o,output logic [15:0] out_addr_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin out_valid_o<=0; out_is_write_o<=0; out_addr_o<=0; end
    else if(out_valid_o && out_ready_i) out_valid_o<=0;
    else if(!out_valid_o) begin
      if(write_valid_i) begin out_valid_o<=1; out_is_write_o<=1; out_addr_o<=write_addr_i; end
      else if(read_valid_i) begin out_valid_o<=1; out_is_write_o<=0; out_addr_o<=read_addr_i; end
    end
  end
endmodule
""",
            reference_unsafe="""module axi_sub_arbiter(input logic clk,rst_n,
  input logic read_valid_i,input logic [15:0] read_addr_i,
  input logic write_valid_i,input logic [15:0] write_addr_i,input logic out_ready_i,
  output logic out_valid_o,out_is_write_o,output logic [15:0] out_addr_o);
  always_comb begin
    out_valid_o=write_valid_i||read_valid_i;
    out_is_write_o=write_valid_i;
    out_addr_o=write_valid_i?write_addr_i:read_addr_i;
  end
endmodule
""",
            support_name="properties.sv",
            support_top="axi_sub_arbiter_properties",
            support="""module axi_sub_arbiter_properties;
  (* anyseq *) logic clk,rst_n,read_valid_i,write_valid_i,out_ready_i;
  (* anyseq *) logic [15:0] read_addr_i,write_addr_i;
  logic out_valid_o,out_is_write_o,f_past_valid; logic [15:0] out_addr_o;
  axi_sub_arbiter dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n && out_valid_o && !out_ready_i)) begin
      assert(out_valid_o); assert(out_is_write_o==$past(out_is_write_o));
      assert(out_addr_o==$past(out_addr_o));
    end
  end
endmodule
""",
            depth=8,
            message="AXI arbiter winner changes while the selected beat is stalled",
        ),
        Task(
            task_id="opentitan_6473_rom_kmac_counter",
            top="rom_kmac_counter",
            source=Source("lowRISC", "opentitan", 6473),
            category="protocol",
            oracle_class="protocol",
            rule_id="REF-PROT-001",
            context=(
                "After KMAC released backpressure, the ROM stream address remained on "
                "the accepted word for one extra cycle and fetched it twice."
            ),
            requirement=(
                "Advance the ROM address once for each valid/ready word handshake, "
                "including the first handshake after a stall."
            ),
            cycle_contract=(
                "If word_valid_i&&kmac_ready_i is sampled, addr_o in the following cycle "
                "equals its previous value plus one; otherwise a pending word does not advance."
            ),
            verification_contract=(
                "Exactly one address increment occurs per accepted word.",
                "Backpressure alone never increments the address.",
                "The first post-reset address is zero.",
            ),
            interface="""module rom_kmac_counter(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       word_valid_i,
    input  logic       kmac_ready_i,
    output logic [7:0] addr_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,word_valid_i=0,kmac_ready_i=0; logic [7:0] addr_o;
  rom_kmac_counter dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    word_valid_i=1; kmac_ready_i=1;
    @(posedge clk); $display("PASS"); $finish;
  end
endmodule
""",
            reference_safe="""module rom_kmac_counter(input logic clk,rst_n,word_valid_i,
  input logic kmac_ready_i,output logic [7:0] addr_o);
  always_ff @(posedge clk) begin
    if(!rst_n) addr_o<=0; else if(word_valid_i&&kmac_ready_i) addr_o<=addr_o+1'b1;
  end
endmodule
""",
            reference_unsafe="""module rom_kmac_counter(input logic clk,rst_n,word_valid_i,
  input logic kmac_ready_i,output logic [7:0] addr_o);
  logic advance_q;
  always_ff @(posedge clk) begin
    if(!rst_n) begin addr_o<=0; advance_q<=0; end
    else begin advance_q<=word_valid_i&&kmac_ready_i; if(advance_q) addr_o<=addr_o+1'b1; end
  end
endmodule
""",
            support_name="properties.sv",
            support_top="rom_kmac_counter_properties",
            support="""module rom_kmac_counter_properties;
  (* anyseq *) logic clk,rst_n,word_valid_i,kmac_ready_i;
  logic f_past_valid; logic [7:0] addr_o; rom_kmac_counter dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n)) begin
      if($past(word_valid_i&&kmac_ready_i)) assert(addr_o==$past(addr_o)+1'b1);
      else assert(addr_o==$past(addr_o));
    end
  end
endmodule
""",
            depth=8,
            message="ROM stream address does not advance exactly on KMAC handshake",
        ),
        Task(
            task_id="opentitan_634_masked_packer",
            top="masked_packer",
            source=Source("lowRISC", "opentitan", 634),
            category="protocol",
            oracle_class="protocol",
            rule_id="REF-PROT-001",
            context=(
                "A full packed word could stop appearing valid and upstream ready could "
                "remain asserted when the downstream interface was stalled."
            ),
            requirement=(
                "Treat an all-masked input as one complete buffered word. Hold the word and "
                "apply upstream backpressure until it is accepted."
            ),
            cycle_contract=(
                "After accepting valid_i with mask_i=4'b1111, valid_o stays high and "
                "data_o stays stable while ready_i=0; ready_o is low during that stall."
            ),
            verification_contract=(
                "A complete buffered word cannot disappear under backpressure.",
                "No new input is accepted while a word is stalled.",
                "Same-cycle consume-and-replace is permitted.",
            ),
            interface="""module masked_packer(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       valid_i,
    input  logic [7:0] data_i,
    input  logic [3:0] mask_i,
    output logic       ready_o,
    output logic       valid_o,
    output logic [7:0] data_o,
    input  logic       ready_i
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,valid_i=0,ready_i=1,ready_o,valid_o;
  logic [7:0] data_i=0,data_o; logic [3:0] mask_i=0;
  masked_packer dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    valid_i=1; data_i=8'hA5; mask_i=4'hF;
    @(posedge clk); #1; if(!valid_o || data_o!==8'hA5) $fatal(1,"packer");
    $display("PASS"); $finish;
  end
endmodule
""",
            reference_safe="""module masked_packer(input logic clk,rst_n,valid_i,
  input logic [7:0] data_i,input logic [3:0] mask_i,output logic ready_o,
  output logic valid_o,output logic [7:0] data_o,input logic ready_i);
  assign ready_o=!valid_o||ready_i;
  always_ff @(posedge clk) begin
    if(!rst_n) begin valid_o<=0; data_o<=0; end
    else if(ready_o) begin valid_o<=valid_i&&(mask_i==4'hF); if(valid_i) data_o<=data_i; end
  end
endmodule
""",
            reference_unsafe="""module masked_packer(input logic clk,rst_n,valid_i,
  input logic [7:0] data_i,input logic [3:0] mask_i,output logic ready_o,
  output logic valid_o,output logic [7:0] data_o,input logic ready_i);
  assign ready_o=1'b1;
  always_ff @(posedge clk) begin
    if(!rst_n) begin valid_o<=0; data_o<=0; end
    else begin valid_o<=valid_i&&(mask_i==4'hF); if(valid_i) data_o<=data_i; end
  end
endmodule
""",
            support_name="properties.sv",
            support_top="masked_packer_properties",
            support="""module masked_packer_properties;
  (* anyseq *) logic clk,rst_n,valid_i,ready_i; (* anyseq *) logic [7:0] data_i;
  (* anyseq *) logic [3:0] mask_i; logic ready_o,valid_o,f_past_valid;
  logic [7:0] data_o; masked_packer dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n&&valid_o&&!ready_i)) begin
      assert(valid_o); assert(data_o==$past(data_o));
    end
    if(valid_o&&!ready_i) assert(!ready_o);
  end
endmodule
""",
            depth=8,
            message="packed output or upstream backpressure is not persistent during stall",
        ),
        Task(
            task_id="opentitan_172_sticky_arbiter",
            top="sticky_arbiter",
            source=Source("lowRISC", "opentitan", 172),
            category="protocol",
            oracle_class="protocol",
            rule_id="REF-PROT-001",
            context=(
                "A later higher-priority request could replace the requester and data of "
                "an already-selected transfer before acknowledgement."
            ),
            requirement=(
                "Select the highest active requester when idle, then hold the one-hot grant "
                "and selected data until ack_i."
            ),
            cycle_contract=(
                "Whenever valid_o&&!ack_i is sampled, valid_o, grant_o, and data_o remain "
                "bit-for-bit stable in the next cycle."
            ),
            verification_contract=(
                "A stalled selection is sticky.",
                "New priority decisions occur only when no transfer is pending.",
                "grant_o is one-hot whenever valid_o is asserted.",
            ),
            interface="""module sticky_arbiter(
    input  logic        clk,
    input  logic        rst_n,
    input  logic [2:0]  req_i,
    input  logic [23:0] data_i,
    input  logic        ack_i,
    output logic        valid_o,
    output logic [2:0]  grant_o,
    output logic [7:0]  data_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,ack_i=1,valid_o; logic [2:0] req_i=0,grant_o;
  logic [23:0] data_i=24'h332211; logic [7:0] data_o;
  sticky_arbiter dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1; req_i=3'b010;
    @(posedge clk); #1; if(!valid_o || grant_o!==3'b010 || data_o!==8'h22) $fatal(1,"arb");
    $display("PASS"); $finish;
  end
endmodule
""",
            reference_safe="""module sticky_arbiter(input logic clk,rst_n,input logic [2:0] req_i,
  input logic [23:0] data_i,input logic ack_i,output logic valid_o,
  output logic [2:0] grant_o,output logic [7:0] data_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin valid_o<=0; grant_o<=0; data_o<=0; end
    else if(valid_o&&ack_i) valid_o<=0;
    else if(!valid_o) begin
      if(req_i[2]) begin valid_o<=1;grant_o<=3'b100;data_o<=data_i[23:16];end
      else if(req_i[1]) begin valid_o<=1;grant_o<=3'b010;data_o<=data_i[15:8];end
      else if(req_i[0]) begin valid_o<=1;grant_o<=3'b001;data_o<=data_i[7:0];end
    end
  end
endmodule
""",
            reference_unsafe="""module sticky_arbiter(input logic clk,rst_n,input logic [2:0] req_i,
  input logic [23:0] data_i,input logic ack_i,output logic valid_o,
  output logic [2:0] grant_o,output logic [7:0] data_o);
  always_comb begin
    valid_o=|req_i; grant_o=0; data_o=0;
    if(req_i[2]) begin grant_o=3'b100;data_o=data_i[23:16];end
    else if(req_i[1]) begin grant_o=3'b010;data_o=data_i[15:8];end
    else if(req_i[0]) begin grant_o=3'b001;data_o=data_i[7:0];end
  end
endmodule
""",
            support_name="properties.sv",
            support_top="sticky_arbiter_properties",
            support="""module sticky_arbiter_properties;
  (* anyseq *) logic clk,rst_n,ack_i; (* anyseq *) logic [2:0] req_i;
  (* anyseq *) logic [23:0] data_i; logic valid_o,f_past_valid;
  logic [2:0] grant_o; logic [7:0] data_o; sticky_arbiter dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n&&valid_o&&!ack_i)) begin
      assert(valid_o); assert(grant_o==$past(grant_o)); assert(data_o==$past(data_o));
    end
    if(valid_o) assert(grant_o==3'b001||grant_o==3'b010||grant_o==3'b100);
  end
endmodule
""",
            depth=8,
            message="arbiter grant or payload changes before acknowledgement",
        ),
        Task(
            task_id="opentitan_23607_csrng_command",
            top="csrng_command",
            source=Source("lowRISC", "opentitan", 23607),
            category="protocol",
            oracle_class="protocol",
            rule_id="REF-PROT-001",
            context=(
                "An acknowledge-status error could cancel a pending CSRNG command while "
                "the receiver was still applying backpressure."
            ),
            requirement=(
                "Hold command valid and payload until ready completes the handshake. An "
                "error may be recorded but cannot cancel the in-flight command."
            ),
            cycle_contract=(
                "After cmd_valid_o&&!cmd_ready_i, cmd_valid_o and cmd_o remain stable on "
                "all following stalled cycles regardless of status_error_i."
            ),
            verification_contract=(
                "status_error_i never drops an unaccepted command.",
                "Payload is immutable while valid is stalled.",
                "Valid clears only after handshake or reset.",
            ),
            interface="""module csrng_command(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       submit_i,
    input  logic [7:0] submit_cmd_i,
    input  logic       cmd_ready_i,
    input  logic       status_error_i,
    output logic       cmd_valid_o,
    output logic [7:0] cmd_o,
    output logic       error_seen_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,submit_i=0,cmd_ready_i=1,status_error_i=0;
  logic cmd_valid_o,error_seen_o; logic [7:0] submit_cmd_i=0,cmd_o;
  csrng_command dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1; submit_i=1; submit_cmd_i=8'hA7;
    @(posedge clk); #1; if(!cmd_valid_o || cmd_o!==8'hA7) $fatal(1,"cmd");
    $display("PASS"); $finish;
  end
endmodule
""",
            reference_safe="""module csrng_command(input logic clk,rst_n,submit_i,
  input logic [7:0] submit_cmd_i,input logic cmd_ready_i,status_error_i,
  output logic cmd_valid_o,output logic [7:0] cmd_o,output logic error_seen_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin cmd_valid_o<=0;cmd_o<=0;error_seen_o<=0;end
    else begin
      if(status_error_i) error_seen_o<=1;
      if(cmd_valid_o&&cmd_ready_i) cmd_valid_o<=0;
      if(!cmd_valid_o&&submit_i) begin cmd_valid_o<=1;cmd_o<=submit_cmd_i;end
    end
  end
endmodule
""",
            reference_unsafe="""module csrng_command(input logic clk,rst_n,submit_i,
  input logic [7:0] submit_cmd_i,input logic cmd_ready_i,status_error_i,
  output logic cmd_valid_o,output logic [7:0] cmd_o,output logic error_seen_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin cmd_valid_o<=0;cmd_o<=0;error_seen_o<=0;end
    else begin
      if(status_error_i) begin error_seen_o<=1;cmd_valid_o<=0;end
      else if(cmd_valid_o&&cmd_ready_i) cmd_valid_o<=0;
      else if(!cmd_valid_o&&submit_i) begin cmd_valid_o<=1;cmd_o<=submit_cmd_i;end
    end
  end
endmodule
""",
            support_name="properties.sv",
            support_top="csrng_command_properties",
            support="""module csrng_command_properties;
  (* anyseq *) logic clk,rst_n,submit_i,cmd_ready_i,status_error_i;
  (* anyseq *) logic [7:0] submit_cmd_i; logic cmd_valid_o,error_seen_o,f_past_valid;
  logic [7:0] cmd_o; csrng_command dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n&&cmd_valid_o&&!cmd_ready_i)) begin
      assert(cmd_valid_o); assert(cmd_o==$past(cmd_o));
    end
  end
endmodule
""",
            depth=8,
            message="CSRNG command is canceled or modified before valid/ready acceptance",
        ),
    )


def _temporal_tasks() -> tuple[Task, ...]:
    return (
        Task(
            task_id="ibex_1816_debug_cause",
            top="debug_cause",
            source=Source("lowRISC", "ibex", 1816),
            category="temporal",
            oracle_class="temporal",
            rule_id="REF-TEMP-001",
            context=(
                "A debug halt request could disappear before a later CSR-save cycle, "
                "causing the saved entry cause to describe the wrong event."
            ),
            requirement=(
                "Capture the halt-request cause when debug entry is decided and use that "
                "captured cause when save_cause_i arrives later."
            ),
            cycle_contract=(
                "On enter_debug_i, latch debug_req_i. On a later save_cause_i, update "
                "cause_haltreq_o from that latched value, never from live debug_req_i."
            ),
            verification_contract=(
                "debug_req_i may change arbitrarily after entry.",
                "The saved cause is associated with the same entry transaction.",
                "Reset clears pending and saved cause state.",
            ),
            interface="""module debug_cause(
    input  logic clk,
    input  logic rst_n,
    input  logic enter_debug_i,
    input  logic debug_req_i,
    input  logic save_cause_i,
    output logic cause_haltreq_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,enter_debug_i=0,debug_req_i=0,save_cause_i=0,cause_haltreq_o;
  debug_cause dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;enter_debug_i=1;debug_req_i=1;
    @(negedge clk); enter_debug_i=0;save_cause_i=1;
    @(posedge clk); #1; if(!cause_haltreq_o) $fatal(1,"cause");
    $display("PASS");$finish;
  end
endmodule
""",
            reference_safe="""module debug_cause(input logic clk,rst_n,enter_debug_i,
  input logic debug_req_i,save_cause_i,output logic cause_haltreq_o);
  logic entry_haltreq;
  always_ff @(posedge clk) begin
    if(!rst_n) begin entry_haltreq<=0;cause_haltreq_o<=0;end
    else begin
      if(enter_debug_i) entry_haltreq<=debug_req_i;
      if(save_cause_i) cause_haltreq_o<=entry_haltreq;
    end
  end
endmodule
""",
            reference_unsafe="""module debug_cause(input logic clk,rst_n,enter_debug_i,
  input logic debug_req_i,save_cause_i,output logic cause_haltreq_o);
  always_ff @(posedge clk) begin
    if(!rst_n) cause_haltreq_o<=0;
    else if(save_cause_i) cause_haltreq_o<=debug_req_i;
  end
endmodule
""",
            support_name="properties.sv",
            support_top="debug_cause_properties",
            support="""module debug_cause_properties;
  (* anyseq *) logic clk,rst_n,enter_debug_i,debug_req_i,save_cause_i;
  logic cause_haltreq_o,f_past_valid,pending,expected;
  debug_cause dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(!rst_n) begin pending<=0;expected<=0;end
    else begin
      if(enter_debug_i) begin pending<=1;expected<=debug_req_i;end
      if(save_cause_i&&pending) pending<=0;
    end
    if(f_past_valid && $past(rst_n&&save_cause_i&&pending))
      assert(cause_haltreq_o==$past(expected));
  end
endmodule
""",
            depth=10,
            message="saved debug cause samples a later signal instead of the entry event",
        ),
        Task(
            task_id="ibex_377_split_store",
            top="split_store",
            source=Source("lowRISC", "ibex", 377),
            category="temporal",
            oracle_class="temporal",
            rule_id="REF-TEMP-001",
            context=(
                "A misaligned store split into two requests could report the first-half "
                "error before the second half had completed."
            ),
            requirement=(
                "Always issue and finish the second half after the first response. Latch "
                "any first-half error and report completion/fault only with second_done_i."
            ),
            cycle_contract=(
                "After first_done_i, assert second_req_o. Until second_done_i, complete_o "
                "and fault_o remain low. At second_done_i, complete_o pulses and fault_o "
                "equals the accumulated error."
            ),
            verification_contract=(
                "A first-half error never short-circuits the second transfer.",
                "Fault and completion are aligned.",
                "Only one transaction is active at a time.",
            ),
            interface="""module split_store(
    input  logic clk,
    input  logic rst_n,
    input  logic start_i,
    input  logic first_done_i,
    input  logic first_error_i,
    input  logic second_done_i,
    output logic second_req_o,
    output logic complete_o,
    output logic fault_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,start_i=0,first_done_i=0,first_error_i=0,second_done_i=0;
  logic second_req_o,complete_o,fault_o; split_store dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk);rst_n=1;start_i=1;
    @(negedge clk);start_i=0;first_done_i=1;
    @(posedge clk);#1;if(!second_req_o)$fatal(1,"second");
    @(negedge clk);first_done_i=0;second_done_i=1;
    @(posedge clk);#1;if(!complete_o||fault_o)$fatal(1,"complete");
    $display("PASS");$finish;
  end
endmodule
""",
            reference_safe="""module split_store(input logic clk,rst_n,start_i,first_done_i,
  input logic first_error_i,second_done_i,output logic second_req_o,complete_o,fault_o);
  logic active,error_q;
  always_ff @(posedge clk) begin
    if(!rst_n) begin active<=0;error_q<=0;second_req_o<=0;complete_o<=0;fault_o<=0;end
    else begin
      complete_o<=0;fault_o<=0;
      if(start_i&&!active) begin active<=1;error_q<=0;end
      if(active&&first_done_i) begin second_req_o<=1;error_q<=first_error_i;end
      if(active&&second_req_o&&second_done_i) begin
        active<=0;second_req_o<=0;complete_o<=1;fault_o<=error_q;
      end
    end
  end
endmodule
""",
            reference_unsafe="""module split_store(input logic clk,rst_n,start_i,first_done_i,
  input logic first_error_i,second_done_i,output logic second_req_o,complete_o,fault_o);
  logic active;
  always_ff @(posedge clk) begin
    if(!rst_n) begin active<=0;second_req_o<=0;complete_o<=0;fault_o<=0;end
    else begin
      complete_o<=0;fault_o<=0;
      if(start_i&&!active) active<=1;
      if(active&&first_done_i&&first_error_i) begin active<=0;complete_o<=1;fault_o<=1;end
      else if(active&&first_done_i) second_req_o<=1;
      if(active&&second_req_o&&second_done_i) begin active<=0;second_req_o<=0;complete_o<=1;end
    end
  end
endmodule
""",
            support_name="properties.sv",
            support_top="split_store_properties",
            support="""module split_store_properties;
  (* anyseq *) logic clk,rst_n,start_i,first_done_i,first_error_i,second_done_i;
  logic second_req_o,complete_o,fault_o,f_past_valid;
  split_store dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid&&rst_n&&fault_o) assert($past(second_done_i));
  end
endmodule
""",
            depth=10,
            message="split-store error is reported before the second half completes",
        ),
        Task(
            task_id="cva6_2802_delayed_misaligned",
            top="delayed_misaligned",
            source=Source("openhwgroup", "cva6", 2802),
            category="temporal",
            oracle_class="temporal",
            rule_id="REF-TEMP-001",
            context=(
                "A one-cycle-delayed MMU response could use the misalignment state from "
                "the wrong request cycle or leak it into an idle cycle."
            ),
            requirement=(
                "Pipeline request validity and its misaligned flag together so the response "
                "exception belongs to the originating access."
            ),
            cycle_contract=(
                "response_o in cycle N+1 equals request_i from cycle N. When response_o is "
                "high, misaligned_o equals misaligned_i captured with that request; when "
                "response_o is low, misaligned_o is low."
            ),
            verification_contract=(
                "Changing live misaligned_i cannot alter an in-flight response.",
                "No pending response means no exception.",
                "Reset clears both pipeline fields.",
            ),
            interface="""module delayed_misaligned(
    input  logic clk,
    input  logic rst_n,
    input  logic request_i,
    input  logic misaligned_i,
    output logic response_o,
    output logic misaligned_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,request_i=0,misaligned_i=0,response_o,misaligned_o;
  delayed_misaligned dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;request_i=1;misaligned_i=1;
    @(posedge clk);#1;if(!response_o||!misaligned_o)$fatal(1,"response");
    $display("PASS");$finish;
  end
endmodule
""",
            reference_safe="""module delayed_misaligned(input logic clk,rst_n,request_i,
  input logic misaligned_i,output logic response_o,misaligned_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin response_o<=0;misaligned_o<=0;end
    else begin response_o<=request_i;misaligned_o<=request_i&&misaligned_i;end
  end
endmodule
""",
            reference_unsafe="""module delayed_misaligned(input logic clk,rst_n,request_i,
  input logic misaligned_i,output logic response_o,misaligned_o);
  always_ff @(posedge clk) begin if(!rst_n) response_o<=0;else response_o<=request_i;end
  assign misaligned_o=response_o&&misaligned_i;
endmodule
""",
            support_name="properties.sv",
            support_top="delayed_misaligned_properties",
            support="""module delayed_misaligned_properties;
  (* anyseq *) logic clk,rst_n,request_i,misaligned_i;
  logic response_o,misaligned_o,f_past_valid; delayed_misaligned dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid&&$past(rst_n)) begin
      assert(response_o==$past(request_i));
      assert(misaligned_o==($past(request_i)&&$past(misaligned_i)));
    end
  end
endmodule
""",
            depth=8,
            message="misaligned exception is not aligned with its delayed request",
        ),
        Task(
            task_id="xiangshan_2781_fma_round_mode",
            top="fma_round_mode",
            source=Source("OpenXiangShan", "XiangShan", 2781),
            category="temporal",
            oracle_class="temporal",
            rule_id="REF-TEMP-001",
            context=(
                "A multi-stage FMA could use a newer live rounding mode in its add stage "
                "instead of the mode present when the instruction issued."
            ),
            requirement=(
                "Capture rm_i at issue_i and report that captured mode when complete_i "
                "finishes the same in-flight operation."
            ),
            cycle_contract=(
                "At issue_i, latch rm_i. A later complete_i updates rm_used_o with that "
                "latched value; changes to rm_i while pending have no effect."
            ),
            verification_contract=(
                "One pending instruction owns one rounding-mode snapshot.",
                "Live rm_i is irrelevant after issue.",
                "Reset clears pending state and output.",
            ),
            interface="""module fma_round_mode(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       issue_i,
    input  logic [2:0] rm_i,
    input  logic       complete_i,
    output logic [2:0] rm_used_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,issue_i=0,complete_i=0;logic[2:0]rm_i=0,rm_used_o;
  fma_round_mode dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;issue_i=1;rm_i=3'd3;
    @(negedge clk);issue_i=0;complete_i=1;
    @(posedge clk);#1;if(rm_used_o!==3'd3)$fatal(1,"rm");
    $display("PASS");$finish;
  end
endmodule
""",
            reference_safe="""module fma_round_mode(input logic clk,rst_n,issue_i,
  input logic[2:0]rm_i,input logic complete_i,output logic[2:0]rm_used_o);
  logic[2:0]rm_q;
  always_ff @(posedge clk) begin
    if(!rst_n)begin rm_q<=0;rm_used_o<=0;end
    else begin if(issue_i)rm_q<=rm_i;if(complete_i)rm_used_o<=rm_q;end
  end
endmodule
""",
            reference_unsafe="""module fma_round_mode(input logic clk,rst_n,issue_i,
  input logic[2:0]rm_i,input logic complete_i,output logic[2:0]rm_used_o);
  always_ff @(posedge clk) begin
    if(!rst_n)rm_used_o<=0;else if(complete_i)rm_used_o<=rm_i;
  end
endmodule
""",
            support_name="properties.sv",
            support_top="fma_round_mode_properties",
            support="""module fma_round_mode_properties;
  (* anyseq *)logic clk,rst_n,issue_i,complete_i;(* anyseq *)logic[2:0]rm_i;
  logic[2:0]rm_used_o,expected;logic pending,f_past_valid;fma_round_mode dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(!rst_n)begin pending<=0;expected<=0;end
    else begin if(issue_i)begin pending<=1;expected<=rm_i;end if(complete_i&&pending)pending<=0;end
    if(f_past_valid&&$past(rst_n&&complete_i&&pending))assert(rm_used_o==$past(expected));
  end
endmodule
""",
            depth=10,
            message="FMA completion uses a live rounding mode rather than its issue-time mode",
        ),
        Task(
            task_id="xiangshan_3329_itlb_wait",
            top="itlb_wait",
            source=Source("OpenXiangShan", "XiangShan", 3329),
            category="temporal",
            oracle_class="temporal",
            rule_id="REF-TEMP-001",
            context=(
                "An MMIO fetch state machine could leave its translation step before the "
                "current iTLB response was valid."
            ),
            requirement=(
                "After request_i, remain pending until tlb_valid_i. Pulse done_o only when "
                "the corresponding translation is valid."
            ),
            cycle_contract=(
                "A request starts one pending operation. While pending and tlb_valid_i=0, "
                "done_o is 0. Sampling tlb_valid_i completes it with a one-cycle done_o."
            ),
            verification_contract=(
                "Arbitrary translation latency is supported.",
                "Stale response bits are never consumed without valid.",
                "New requests while pending are ignored.",
            ),
            interface="""module itlb_wait(
    input  logic clk,
    input  logic rst_n,
    input  logic request_i,
    input  logic tlb_valid_i,
    output logic pending_o,
    output logic done_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,request_i=0,tlb_valid_i=0,pending_o,done_o;
  itlb_wait dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;request_i=1;tlb_valid_i=1;
    @(posedge clk);#1;if(!pending_o)$fatal(1,"pending");
    @(negedge clk);request_i=0;
    @(posedge clk);#1;if(!done_o)$fatal(1,"done");
    $display("PASS");$finish;
  end
endmodule
""",
            reference_safe="""module itlb_wait(input logic clk,rst_n,request_i,tlb_valid_i,
  output logic pending_o,done_o);
  always_ff @(posedge clk)begin
    if(!rst_n)begin pending_o<=0;done_o<=0;end
    else begin done_o<=0;if(!pending_o&&request_i)pending_o<=1;
      else if(pending_o&&tlb_valid_i)begin pending_o<=0;done_o<=1;end end
  end
endmodule
""",
            reference_unsafe="""module itlb_wait(input logic clk,rst_n,request_i,tlb_valid_i,
  output logic pending_o,done_o);
  always_ff @(posedge clk)begin
    if(!rst_n)begin pending_o<=0;done_o<=0;end
    else begin done_o<=pending_o;if(request_i)pending_o<=1;else if(pending_o)pending_o<=0;end
  end
endmodule
""",
            support_name="properties.sv",
            support_top="itlb_wait_properties",
            support="""module itlb_wait_properties;
  (* anyseq *)logic clk,rst_n,request_i,tlb_valid_i;logic pending_o,done_o,f_past_valid;
  itlb_wait dut(.*);
  always_ff @(posedge clk)begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(pending_o&&!tlb_valid_i)assert(!done_o);
    if(f_past_valid&&$past(rst_n&&pending_o&&!tlb_valid_i))assert(pending_o&&!done_o);
  end
endmodule
""",
            depth=10,
            message="MMIO translation completes before the iTLB response is valid",
        ),
        Task(
            task_id="opentitan_7701_wakeup_latch",
            top="wakeup_latch",
            source=Source("lowRISC", "opentitan", 7701),
            category="temporal",
            oracle_class="temporal",
            rule_id="REF-TEMP-001",
            context=(
                "A timer wakeup request could drop when sleep ended even though software "
                "had not cleared the recorded wakeup cause."
            ),
            requirement=(
                "Latch each wakeup_event_i and keep wakeup_o asserted until clear_cause_i, "
                "independent of the current sleeping_i value."
            ),
            cycle_contract=(
                "A sampled wakeup_event_i sets wakeup_o. Once set, wakeup_o stays high on "
                "every cycle until clear_cause_i is sampled."
            ),
            verification_contract=(
                "Leaving sleep cannot acknowledge a wakeup.",
                "Only clear_cause_i or reset clears the latched request.",
                "Events are not lost if sleep state changes immediately.",
            ),
            interface="""module wakeup_latch(
    input  logic clk,
    input  logic rst_n,
    input  logic sleeping_i,
    input  logic wakeup_event_i,
    input  logic clear_cause_i,
    output logic wakeup_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,sleeping_i=0,wakeup_event_i=0,clear_cause_i=0,wakeup_o;
  wakeup_latch dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;sleeping_i=1;wakeup_event_i=1;
    @(posedge clk);#1;if(!wakeup_o)$fatal(1,"wakeup");
    $display("PASS");$finish;
  end
endmodule
""",
            reference_safe="""module wakeup_latch(input logic clk,rst_n,sleeping_i,
  input logic wakeup_event_i,clear_cause_i,output logic wakeup_o);
  always_ff @(posedge clk)begin
    if(!rst_n)wakeup_o<=0;else if(clear_cause_i)wakeup_o<=0;else if(wakeup_event_i)wakeup_o<=1;
  end
endmodule
""",
            reference_unsafe="""module wakeup_latch(input logic clk,rst_n,sleeping_i,
  input logic wakeup_event_i,clear_cause_i,output logic wakeup_o);
  always_ff @(posedge clk)begin
    if(!rst_n)wakeup_o<=0;else wakeup_o<=sleeping_i&&wakeup_event_i;
  end
endmodule
""",
            support_name="properties.sv",
            support_top="wakeup_latch_properties",
            support="""module wakeup_latch_properties;
  (* anyseq *)logic clk,rst_n,sleeping_i,wakeup_event_i,clear_cause_i;
  logic wakeup_o,f_past_valid;wakeup_latch dut(.*);
  always_ff @(posedge clk)begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(f_past_valid&&$past(rst_n&&wakeup_o&&!clear_cause_i))assert(wakeup_o);
  end
endmodule
""",
            depth=8,
            message="wakeup request drops before software clears its recorded cause",
        ),
        Task(
            task_id="opentitan_13760_alert_pulse",
            top="alert_pulse",
            source=Source("lowRISC", "opentitan", 13760),
            category="temporal",
            oracle_class="temporal",
            rule_id="REF-TEMP-002",
            context=(
                "A recoverable alert was driven as a level from a latched invalid-field "
                "condition, repeatedly alerting for one software error."
            ),
            requirement=(
                "Emit one alert_o pulse on the rising edge of bad_field_i. Do not retrigger "
                "while the same bad condition remains high."
            ),
            cycle_contract=(
                "alert_o is high for exactly one cycle when bad_field_i transitions 0->1. "
                "It is low on the next cycle even if bad_field_i remains 1."
            ),
            verification_contract=(
                "A sustained invalid encoding produces one pulse.",
                "A later new 0->1 event may produce another pulse.",
                "Reset clears the edge history and output.",
            ),
            interface="""module alert_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic bad_field_i,
    output logic alert_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,bad_field_i=0,alert_o;alert_pulse dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;bad_field_i=1;
    @(posedge clk);#1;if(!alert_o)$fatal(1,"alert");
    $display("PASS");$finish;
  end
endmodule
""",
            reference_safe="""module alert_pulse(input logic clk,rst_n,bad_field_i,output logic alert_o);
  logic bad_q;always_ff @(posedge clk)begin
    if(!rst_n)begin bad_q<=0;alert_o<=0;end
    else begin alert_o<=bad_field_i&&!bad_q;bad_q<=bad_field_i;end
  end
endmodule
""",
            reference_unsafe="""module alert_pulse(input logic clk,rst_n,bad_field_i,output logic alert_o);
  always_ff @(posedge clk)begin if(!rst_n)alert_o<=0;else alert_o<=bad_field_i;end
endmodule
""",
            support_name="properties.sv",
            support_top="alert_pulse_properties",
            support="""module alert_pulse_properties;
  (* anyseq *)logic clk,rst_n,bad_field_i;logic alert_o,f_past_valid;alert_pulse dut(.*);
  always_ff @(posedge clk)begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(f_past_valid&&$past(rst_n&&alert_o&&bad_field_i))begin assume(bad_field_i);assert(!alert_o);end
  end
endmodule
""",
            depth=8,
            message="recoverable alert repeats instead of pulsing once per bad-field event",
        ),
        Task(
            task_id="opentitan_23775_conditioner_done",
            top="conditioner_done",
            source=Source("lowRISC", "opentitan", 23775),
            category="temporal",
            oracle_class="temporal",
            rule_id="REF-TEMP-001",
            context=(
                "A health-test window completion could start conditioning before its final "
                "FIFO word had actually been accepted."
            ),
            requirement=(
                "Pulse process_o only when the word marked window_last_i completes a "
                "word_valid_i/word_ready_i handshake."
            ),
            cycle_contract=(
                "process_o in cycle N+1 equals word_valid_i&&word_ready_i&&window_last_i "
                "sampled in cycle N. Merely presenting an unaccepted final word is insufficient."
            ),
            verification_contract=(
                "Backpressure on the final word delays processing.",
                "Every accepted final word produces one pulse.",
                "Non-final words never produce process_o.",
            ),
            interface="""module conditioner_done(
    input  logic clk,
    input  logic rst_n,
    input  logic word_valid_i,
    input  logic word_ready_i,
    input  logic window_last_i,
    output logic process_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,word_valid_i=0,word_ready_i=1,window_last_i=0,process_o;
  conditioner_done dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;word_valid_i=1;window_last_i=1;
    @(posedge clk);#1;if(!process_o)$fatal(1,"process");
    $display("PASS");$finish;
  end
endmodule
""",
            reference_safe="""module conditioner_done(input logic clk,rst_n,word_valid_i,
  input logic word_ready_i,window_last_i,output logic process_o);
  always_ff @(posedge clk)begin
    if(!rst_n)process_o<=0;else process_o<=word_valid_i&&word_ready_i&&window_last_i;
  end
endmodule
""",
            reference_unsafe="""module conditioner_done(input logic clk,rst_n,word_valid_i,
  input logic word_ready_i,window_last_i,output logic process_o);
  always_ff @(posedge clk)begin
    if(!rst_n)process_o<=0;else process_o<=word_valid_i&&window_last_i;
  end
endmodule
""",
            support_name="properties.sv",
            support_top="conditioner_done_properties",
            support="""module conditioner_done_properties;
  (* anyseq *)logic clk,rst_n,word_valid_i,word_ready_i,window_last_i;
  logic process_o,f_past_valid;conditioner_done dut(.*);
  always_ff @(posedge clk)begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(f_past_valid&&$past(rst_n))
      assert(process_o==$past(word_valid_i&&word_ready_i&&window_last_i));
  end
endmodule
""",
            depth=8,
            message="conditioner starts before the final window word is accepted",
        ),
    )


def _equivalence_tasks() -> tuple[Task, ...]:
    return (
        Task(
            task_id="cva6_3107_iti_valid",
            top="iti_valid",
            source=Source("openhwgroup", "cva6", 3107),
            category="synthesis_equivalence",
            oracle_class="equivalence",
            rule_id="REF-EQUIV-001",
            context=(
                "Incomplete combinational assignment inferred a latch, allowing an "
                "instruction-trace valid bit to retain a previous cycle's value."
            ),
            requirement=(
                "Produce valid_o solely from the current enable_i and slot_valid_i inputs, "
                "with no state retention on inactive paths."
            ),
            cycle_contract=(
                "For every input valuation, valid_o = enable_i && (slot_valid_i[0] || "
                "slot_valid_i[1]). The output is zero for every other valuation."
            ),
            verification_contract=(
                "The synthesized logic is purely combinational.",
                "No inferred latch or prior-cycle dependence is permitted.",
                "All four slot_valid_i values are covered.",
            ),
            interface="""module iti_valid(
    input  logic       enable_i,
    input  logic [1:0] slot_valid_i,
    output logic       valid_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic enable_i=1;logic[1:0]slot_valid_i=2'b01;logic valid_o;iti_valid dut(.*);
  initial begin #1;if(!valid_o)$fatal(1,"valid");$display("PASS");$finish;end
endmodule
""",
            reference_safe="""module iti_valid(input logic enable_i,input logic[1:0]slot_valid_i,
  output logic valid_o);always_comb valid_o=enable_i&&(|slot_valid_i);endmodule
""",
            reference_unsafe="""module iti_valid(input logic enable_i,input logic[1:0]slot_valid_i,
  output logic valid_o);assign valid_o=|slot_valid_i;endmodule
""",
            support_name="reference.sv",
            support_top=None,
            support="""module iti_valid(input logic enable_i,input logic[1:0]slot_valid_i,
  output logic valid_o);always_comb valid_o=enable_i&&(|slot_valid_i);endmodule
""",
            depth=2,
            message="synthesized ITI valid logic differs from the total combinational reference",
        ),
        Task(
            task_id="cva6_2844_exception_record",
            top="exception_record",
            source=Source("openhwgroup", "cva6", 2844),
            category="synthesis_equivalence",
            oracle_class="equivalence",
            rule_id="REF-EQUIV-001",
            context=(
                "An illegal custom-instruction path left hypervisor exception fields "
                "undefined, allowing arbitrary transformed-instruction metadata."
            ),
            requirement=(
                "Build a completely defined exception record. On illegal_i, report cause 2, "
                "copy instr_i to tval_o, zero htval_o/mtinst_o, and copy virt_i to gva_o."
            ),
            cycle_contract=(
                "Combinational truth table: illegal_i=0 makes every output zero. illegal_i=1 "
                "sets valid_o=1,cause_o=2,tval_o=instr_i,htval_o=0,mtinst_o=0,gva_o=virt_i."
            ),
            verification_contract=(
                "Every output has a value on every path.",
                "No X-, latch-, or previous-value semantics remain after synthesis.",
                "Virtualization changes only gva_o on this path.",
            ),
            interface="""module exception_record(
    input  logic        illegal_i,
    input  logic        virt_i,
    input  logic [31:0] instr_i,
    output logic        valid_o,
    output logic [5:0]  cause_o,
    output logic [31:0] tval_o,
    output logic [31:0] htval_o,
    output logic [31:0] mtinst_o,
    output logic        gva_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic illegal_i=1,virt_i=1,valid_o,gva_o;logic[31:0]instr_i=32'hDEADBEEF;
  logic[5:0]cause_o;logic[31:0]tval_o,htval_o,mtinst_o;exception_record dut(.*);
  initial begin #1;if(!valid_o||cause_o!==6'd2||tval_o!==instr_i)$fatal(1,"exception");
    $display("PASS");$finish;end
endmodule
""",
            reference_safe="""module exception_record(input logic illegal_i,virt_i,
  input logic[31:0]instr_i,output logic valid_o,output logic[5:0]cause_o,
  output logic[31:0]tval_o,htval_o,mtinst_o,output logic gva_o);
  always_comb begin
    valid_o=0;cause_o=0;tval_o=0;htval_o=0;mtinst_o=0;gva_o=0;
    if(illegal_i)begin valid_o=1;cause_o=6'd2;tval_o=instr_i;gva_o=virt_i;end
  end
endmodule
""",
            reference_unsafe="""module exception_record(input logic illegal_i,virt_i,
  input logic[31:0]instr_i,output logic valid_o,output logic[5:0]cause_o,
  output logic[31:0]tval_o,htval_o,mtinst_o,output logic gva_o);
  always_comb begin
    valid_o=illegal_i;cause_o=illegal_i?6'd2:0;tval_o=illegal_i?instr_i:0;gva_o=virt_i;
    htval_o=illegal_i?instr_i:0;mtinst_o=illegal_i?instr_i:0;
  end
endmodule
""",
            support_name="reference.sv",
            support_top=None,
            support="""module exception_record(input logic illegal_i,virt_i,
  input logic[31:0]instr_i,output logic valid_o,output logic[5:0]cause_o,
  output logic[31:0]tval_o,htval_o,mtinst_o,output logic gva_o);
  always_comb begin
    valid_o=0;cause_o=0;tval_o=0;htval_o=0;mtinst_o=0;gva_o=0;
    if(illegal_i)begin valid_o=1;cause_o=6'd2;tval_o=instr_i;gva_o=virt_i;end
  end
endmodule
""",
            depth=2,
            message="synthesized exception record is not fully defined like the reference",
        ),
        Task(
            task_id="xiangshan_1323_csr_mask",
            top="csr_mask",
            source=Source("OpenXiangShan", "XiangShan", 1323),
            category="synthesis_equivalence",
            oracle_class="equivalence",
            rule_id="REF-EQUIV-001",
            context=(
                "CSR writes could modify a read-only status field and preserve page-number "
                "bits above the implementation's physical-address width."
            ),
            requirement=(
                "Preserve old_mstatus_i[5:4] across writes and accept all other mstatus bits. "
                "Keep only satp_ppn_i[11:0], forcing its upper four output bits to zero."
            ),
            cycle_contract=(
                "new_mstatus_o=(write_mstatus_i & ~16'h0030) | (old_mstatus_i & 16'h0030). "
                "new_satp_ppn_o={4'b0,write_satp_ppn_i[11:0]}."
            ),
            verification_contract=(
                "Read-only XS bits never follow write data.",
                "Unsupported PPN bits cannot survive synthesis by truncation or sign extension.",
                "Every input combination matches the equations exactly.",
            ),
            interface="""module csr_mask(
    input  logic [15:0] old_mstatus_i,
    input  logic [15:0] write_mstatus_i,
    input  logic [15:0] write_satp_ppn_i,
    output logic [15:0] new_mstatus_o,
    output logic [15:0] new_satp_ppn_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic[15:0]old_mstatus_i=16'h0010,write_mstatus_i=16'hA51A,write_satp_ppn_i=16'h0123;
  logic[15:0]new_mstatus_o,new_satp_ppn_o;csr_mask dut(.*);
  initial begin #1;if(new_mstatus_o!==16'hA51A||new_satp_ppn_o!==16'h0123)$fatal(1,"mask");
    $display("PASS");$finish;end
endmodule
""",
            reference_safe="""module csr_mask(input logic[15:0]old_mstatus_i,write_mstatus_i,
  input logic[15:0]write_satp_ppn_i,output logic[15:0]new_mstatus_o,new_satp_ppn_o);
  always_comb begin
    new_mstatus_o=(write_mstatus_i&16'hFFCF)|(old_mstatus_i&16'h0030);
    new_satp_ppn_o={4'b0,write_satp_ppn_i[11:0]};
  end
endmodule
""",
            reference_unsafe="""module csr_mask(input logic[15:0]old_mstatus_i,write_mstatus_i,
  input logic[15:0]write_satp_ppn_i,output logic[15:0]new_mstatus_o,new_satp_ppn_o);
  assign new_mstatus_o=write_mstatus_i;assign new_satp_ppn_o=write_satp_ppn_i;
endmodule
""",
            support_name="reference.sv",
            support_top=None,
            support="""module csr_mask(input logic[15:0]old_mstatus_i,write_mstatus_i,
  input logic[15:0]write_satp_ppn_i,output logic[15:0]new_mstatus_o,new_satp_ppn_o);
  always_comb begin
    new_mstatus_o=(write_mstatus_i&16'hFFCF)|(old_mstatus_i&16'h0030);
    new_satp_ppn_o={4'b0,write_satp_ppn_i[11:0]};
  end
endmodule
""",
            depth=1,
            message="CSR write-mask behavior differs after synthesis",
        ),
        Task(
            task_id="rocket_2543_tile_widths",
            top="tile_widths",
            source=Source("chipsalliance", "rocket-chip", 2543),
            category="synthesis_equivalence",
            oracle_class="equivalence",
            rule_id="REF-EQUIV-001",
            context=(
                "Tile HartID and reset-vector ports could be narrower than the configured "
                "values in heterogeneous elaborations."
            ),
            requirement=(
                "Preserve the full 16-bit HartID and full 48-bit reset vector on the "
                "corresponding Tile-facing outputs."
            ),
            cycle_contract=(
                "Combinationally, tile_hart_id_o===hart_id_i and "
                "tile_reset_vector_o===reset_vector_i for all bits and all values."
            ),
            verification_contract=(
                "No high bit may be silently truncated.",
                "No signed extension or narrowing conversion is allowed.",
                "The post-synthesis mapping is an identity function.",
            ),
            interface="""module tile_widths(
    input  logic [15:0] hart_id_i,
    input  logic [47:0] reset_vector_i,
    output logic [15:0] tile_hart_id_o,
    output logic [47:0] tile_reset_vector_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic[15:0]hart_id_i=16'h0034,tile_hart_id_o;
  logic[47:0]reset_vector_i=48'h0000_8000_0000,tile_reset_vector_o;tile_widths dut(.*);
  initial begin #1;if(tile_hart_id_o!==hart_id_i||tile_reset_vector_o!==reset_vector_i)$fatal(1,"width");
    $display("PASS");$finish;end
endmodule
""",
            reference_safe="""module tile_widths(input logic[15:0]hart_id_i,input logic[47:0]reset_vector_i,
  output logic[15:0]tile_hart_id_o,output logic[47:0]tile_reset_vector_o);
  assign tile_hart_id_o=hart_id_i;assign tile_reset_vector_o=reset_vector_i;
endmodule
""",
            reference_unsafe="""module tile_widths(input logic[15:0]hart_id_i,input logic[47:0]reset_vector_i,
  output logic[15:0]tile_hart_id_o,output logic[47:0]tile_reset_vector_o);
  assign tile_hart_id_o={8'b0,hart_id_i[7:0]};
  assign tile_reset_vector_o={16'b0,reset_vector_i[31:0]};
endmodule
""",
            support_name="reference.sv",
            support_top=None,
            support="""module tile_widths(input logic[15:0]hart_id_i,input logic[47:0]reset_vector_i,
  output logic[15:0]tile_hart_id_o,output logic[47:0]tile_reset_vector_o);
  assign tile_hart_id_o=hart_id_i;assign tile_reset_vector_o=reset_vector_i;
endmodule
""",
            depth=1,
            message="synthesized Tile input adapter truncates configured signal widths",
        ),
        Task(
            task_id="rocket_3065_ptw_address",
            top="ptw_address",
            source=Source("chipsalliance", "rocket-chip", 3065),
            category="synthesis_equivalence",
            oracle_class="equivalence",
            rule_id="REF-EQUIV-001",
            context=(
                "Sv57 plus hypervisor configuration built a page-table address from a "
                "fragment narrower than the slice assumed by the implementation."
            ),
            requirement=(
                "Form the 56-bit address by zero-extending the complete 35-bit VPN "
                "fragment with nine high zeros and twelve low page-offset zeros."
            ),
            cycle_contract=(
                "pte_addr_o={9'b0,vpn_fragment_i[34:0],12'b0} for every VPN fragment."
            ),
            verification_contract=(
                "All 35 source bits contribute in their declared positions.",
                "Padding is explicit and unsigned.",
                "No out-of-range slice or implicit-width behavior is relied upon.",
            ),
            interface="""module ptw_address(
    input  logic [34:0] vpn_fragment_i,
    output logic [55:0] pte_addr_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;logic[34:0]vpn_fragment_i=35'h0012345;logic[55:0]pte_addr_o;ptw_address dut(.*);
  initial begin #1;if(pte_addr_o!=={9'b0,vpn_fragment_i,12'b0})$fatal(1,"addr");
  $display("PASS");$finish;end endmodule
""",
            reference_safe="""module ptw_address(input logic[34:0]vpn_fragment_i,
  output logic[55:0]pte_addr_o);assign pte_addr_o={9'b0,vpn_fragment_i,12'b0};endmodule
""",
            reference_unsafe="""module ptw_address(input logic[34:0]vpn_fragment_i,
  output logic[55:0]pte_addr_o);assign pte_addr_o={vpn_fragment_i[26:0],12'b0};endmodule
""",
            support_name="reference.sv",
            support_top=None,
            support="""module ptw_address(input logic[34:0]vpn_fragment_i,
  output logic[55:0]pte_addr_o);assign pte_addr_o={9'b0,vpn_fragment_i,12'b0};endmodule
""",
            depth=1,
            message="post-synthesis PTW address construction loses Sv57 VPN bits",
        ),
        Task(
            task_id="ibex_176_load_decoder",
            top="load_decoder",
            source=Source("lowRISC", "ibex", 176),
            category="synthesis_equivalence",
            oracle_class="equivalence",
            rule_id="REF-EQUIV-001",
            context=(
                "The unsupported LWU funct3 encoding was accepted as a normal load "
                "instead of being marked illegal."
            ),
            requirement=(
                "For load opcode 7'b0000011, accept funct3 000,001,010,100,101 only. "
                "All other funct3 encodings, including 110, are illegal."
            ),
            cycle_contract=(
                "valid_load_o is one exactly for the five supported load encodings. "
                "illegal_o is one for unsupported funct3 under the load opcode and zero otherwise."
            ),
            verification_contract=(
                "funct3=110 is exhaustively distinguished from LW.",
                "Non-load opcodes assert neither output.",
                "The synthesized truth table matches all 1024 opcode/funct3 combinations.",
            ),
            interface="""module load_decoder(
    input  logic [6:0] opcode_i,
    input  logic [2:0] funct3_i,
    output logic       valid_load_o,
    output logic       illegal_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;logic[6:0]opcode_i=7'b0000011;logic[2:0]funct3_i=3'b010;
  logic valid_load_o,illegal_o;load_decoder dut(.*);
  initial begin #1;if(!valid_load_o||illegal_o)$fatal(1,"lw");$display("PASS");$finish;end
endmodule
""",
            reference_safe="""module load_decoder(input logic[6:0]opcode_i,input logic[2:0]funct3_i,
  output logic valid_load_o,illegal_o);logic supported;
  always_comb begin
    supported=(funct3_i==0)||(funct3_i==1)||(funct3_i==2)||(funct3_i==4)||(funct3_i==5);
    valid_load_o=(opcode_i==7'b0000011)&&supported;
    illegal_o=(opcode_i==7'b0000011)&&!supported;
  end
endmodule
""",
            reference_unsafe="""module load_decoder(input logic[6:0]opcode_i,input logic[2:0]funct3_i,
  output logic valid_load_o,illegal_o);logic supported;
  always_comb begin
    supported=(funct3_i!=3'b111);valid_load_o=(opcode_i==7'b0000011)&&supported;
    illegal_o=(opcode_i==7'b0000011)&&!supported;
  end
endmodule
""",
            support_name="reference.sv",
            support_top=None,
            support="""module load_decoder(input logic[6:0]opcode_i,input logic[2:0]funct3_i,
  output logic valid_load_o,illegal_o);logic supported;
  always_comb begin
    supported=(funct3_i==0)||(funct3_i==1)||(funct3_i==2)||(funct3_i==4)||(funct3_i==5);
    valid_load_o=(opcode_i==7'b0000011)&&supported;
    illegal_o=(opcode_i==7'b0000011)&&!supported;
  end
endmodule
""",
            depth=1,
            message="synthesized decoder accepts unsupported load encodings",
        ),
        Task(
            task_id="opentitan_26589_range_priority",
            top="range_priority",
            source=Source("lowRISC", "opentitan", 26589),
            category="synthesis_equivalence",
            oracle_class="equivalence",
            rule_id="REF-EQUIV-001",
            context=(
                "An overlapping lower-priority access-control range could override the "
                "per-access permission of the lower-index winning range."
            ),
            requirement=(
                "Choose the first enabled matching range, index 0 before index 1. Use only "
                "that range's read or write permission for the requested access type."
            ),
            cycle_contract=(
                "match0=en0_i&&addr_i in [lo0_i,hi0_i]; match1 similarly. If match0, "
                "index_o=0 and allow_o=read_i?allow_r0_i:allow_w0_i. Else use range1."
            ),
            verification_contract=(
                "Overlapping ranges never combine permissions.",
                "Lowest index has priority independently for reads and writes.",
                "No match yields matched_o=0 and allow_o=0.",
            ),
            interface="""module range_priority(
    input  logic [7:0] addr_i,
    input  logic       read_i,
    input  logic       en0_i,
    input  logic [7:0] lo0_i,
    input  logic [7:0] hi0_i,
    input  logic       allow_r0_i,
    input  logic       allow_w0_i,
    input  logic       en1_i,
    input  logic [7:0] lo1_i,
    input  logic [7:0] hi1_i,
    input  logic       allow_r1_i,
    input  logic       allow_w1_i,
    output logic       matched_o,
    output logic       allow_o,
    output logic       index_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic[7:0]addr_i=8'h10,lo0_i=8'h00,hi0_i=8'h1F,lo1_i=8'h80,hi1_i=8'h8F;
  logic read_i=1,en0_i=1,allow_r0_i=1,allow_w0_i=0,en1_i=1,allow_r1_i=0,allow_w1_i=1;
  logic matched_o,allow_o,index_o;range_priority dut(.*);
  initial begin #1;if(!matched_o||!allow_o||index_o)$fatal(1,"range");$display("PASS");$finish;end
endmodule
""",
            reference_safe="""module range_priority(input logic[7:0]addr_i,input logic read_i,en0_i,
  input logic[7:0]lo0_i,hi0_i,input logic allow_r0_i,allow_w0_i,en1_i,
  input logic[7:0]lo1_i,hi1_i,input logic allow_r1_i,allow_w1_i,
  output logic matched_o,allow_o,index_o);
  logic m0,m1;always_comb begin
    m0=en0_i&&(addr_i>=lo0_i)&&(addr_i<=hi0_i);m1=en1_i&&(addr_i>=lo1_i)&&(addr_i<=hi1_i);
    matched_o=0;allow_o=0;index_o=0;
    if(m0)begin matched_o=1;allow_o=read_i?allow_r0_i:allow_w0_i;index_o=0;end
    else if(m1)begin matched_o=1;allow_o=read_i?allow_r1_i:allow_w1_i;index_o=1;end
  end
endmodule
""",
            reference_unsafe="""module range_priority(input logic[7:0]addr_i,input logic read_i,en0_i,
  input logic[7:0]lo0_i,hi0_i,input logic allow_r0_i,allow_w0_i,en1_i,
  input logic[7:0]lo1_i,hi1_i,input logic allow_r1_i,allow_w1_i,
  output logic matched_o,allow_o,index_o);
  logic m0,m1;always_comb begin
    m0=en0_i&&(addr_i>=lo0_i)&&(addr_i<=hi0_i);m1=en1_i&&(addr_i>=lo1_i)&&(addr_i<=hi1_i);
    matched_o=m0||m1;allow_o=(m0&&(read_i?allow_r0_i:allow_w0_i))||(m1&&(read_i?allow_r1_i:allow_w1_i));
    index_o=!m0&&m1;
  end
endmodule
""",
            support_name="reference.sv",
            support_top=None,
            support="""module range_priority(input logic[7:0]addr_i,input logic read_i,en0_i,
  input logic[7:0]lo0_i,hi0_i,input logic allow_r0_i,allow_w0_i,en1_i,
  input logic[7:0]lo1_i,hi1_i,input logic allow_r1_i,allow_w1_i,
  output logic matched_o,allow_o,index_o);
  logic m0,m1;always_comb begin
    m0=en0_i&&(addr_i>=lo0_i)&&(addr_i<=hi0_i);m1=en1_i&&(addr_i>=lo1_i)&&(addr_i<=hi1_i);
    matched_o=0;allow_o=0;index_o=0;
    if(m0)begin matched_o=1;allow_o=read_i?allow_r0_i:allow_w0_i;index_o=0;end
    else if(m1)begin matched_o=1;allow_o=read_i?allow_r1_i:allow_w1_i;index_o=1;end
  end
endmodule
""",
            depth=1,
            message="post-synthesis access-control priority differs for overlapping ranges",
        ),
        Task(
            task_id="opentitan_2420_fifo_empty_data",
            top="fifo_empty_data",
            source=Source("lowRISC", "opentitan", 2420),
            category="synthesis_equivalence",
            oracle_class="equivalence",
            rule_id="REF-EQUIV-001",
            context=(
                "A one-entry FIFO correctly dropped valid after its last read but continued "
                "to expose the stale dequeued byte on its data output."
            ),
            requirement=(
                "Implement a one-entry FIFO. When empty, valid_o is zero and data_o is zero; "
                "when full, data_o is the stored byte until it is read."
            ),
            cycle_contract=(
                "write_i while empty stores data_i and sets valid. read_i while valid clears "
                "valid. data_o is stored_data only when valid, otherwise exactly 8'h00."
            ),
            verification_contract=(
                "The cycle after the last dequeue exposes zero data.",
                "A stale storage flop may exist internally but cannot reach data_o while empty.",
                "Reset produces the same empty/zero observable state.",
            ),
            interface="""module fifo_empty_data(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       write_i,
    input  logic [7:0] data_i,
    input  logic       read_i,
    output logic       valid_o,
    output logic [7:0] data_o
);""",
            testbench="""`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,write_i=0,read_i=0,valid_o;logic[7:0]data_i=0,data_o;
  fifo_empty_data dut(.*);always #5 clk=~clk;
  initial begin repeat(2)@(posedge clk);@(negedge clk);rst_n=1;write_i=1;data_i=8'h5A;
    @(posedge clk);#1;if(!valid_o||data_o!==8'h5A)$fatal(1,"fifo");
    $display("PASS");$finish;end
endmodule
""",
            reference_safe="""module fifo_empty_data(input logic clk,rst_n,write_i,
  input logic[7:0]data_i,input logic read_i,output logic valid_o,output logic[7:0]data_o);
  logic[7:0]storage;always_ff @(posedge clk)begin
    if(!rst_n)begin valid_o<=0;storage<=0;end
    else begin if(read_i&&valid_o)valid_o<=0;if(write_i&&!valid_o)begin storage<=data_i;valid_o<=1;end end
  end
  assign data_o=valid_o?storage:8'h00;
endmodule
""",
            reference_unsafe="""module fifo_empty_data(input logic clk,rst_n,write_i,
  input logic[7:0]data_i,input logic read_i,output logic valid_o,output logic[7:0]data_o);
  always_ff @(posedge clk)begin
    if(!rst_n)begin valid_o<=0;data_o<=0;end
    else begin if(read_i&&valid_o)valid_o<=0;if(write_i&&!valid_o)begin data_o<=data_i;valid_o<=1;end end
  end
endmodule
""",
            support_name="reference.sv",
            support_top=None,
            support="""module fifo_empty_data(input logic clk,rst_n,write_i,
  input logic[7:0]data_i,input logic read_i,output logic valid_o,output logic[7:0]data_o);
  logic[7:0]storage;always_ff @(posedge clk)begin
    if(!rst_n)begin valid_o<=0;storage<=0;end
    else begin if(read_i&&valid_o)valid_o<=0;if(write_i&&!valid_o)begin storage<=data_i;valid_o<=1;end end
  end
  assign data_o=valid_o?storage:8'h00;
endmodule
""",
            depth=6,
            message="post-synthesis FIFO exposes stale data while empty",
        ),
    )


TASKS = _protocol_tasks() + _temporal_tasks() + _equivalence_tasks()


def render_prompt(task: Task, level: int) -> str:
    sections = [
        "You are implementing a standalone SystemVerilog reduction derived from a real "
        "historical RTL fix. Implement exactly this interface:\n\n"
        f"```systemverilog\n{task.interface}\n```\n\n"
        f"Issue-style context: {task.context}\n\n"
        "Use portable synthesizable SystemVerilog and no vendor primitives. Return only "
        "the complete module, without markdown or explanation.\n"
    ]
    if level >= 1:
        sections.append(f"\nRequired externally observable behavior: {task.requirement}\n")
    if level >= 2:
        sections.append(f"\nCycle-exact contract: {task.cycle_contract}\n")
    if level >= 3:
        checks = "\n".join(f"- {item}" for item in task.verification_contract)
        sections.append(
            "\nVerification checklist (the implementation is checked beyond examples):\n"
            f"{checks}\n"
        )
    return "".join(sections)


def render_manifest(task: Task) -> str:
    if task.oracle_class == "equivalence":
        backend = "equivalence-yosys"
        oracle_id = "synthesized-reference"
        options = f'''reference_sources = ["{task.support_name}"]
reference_top = "{task.top}"
depth = {task.depth}'''
    else:
        backend = "formal-yosys"
        oracle_id = "contract-property"
        options = f'''property_sources = ["{task.support_name}"]
property_top = "{task.support_top}"
depth = {task.depth}'''
    return f'''schema_version = "2.0"
candidate_id = "{task.task_id}"

[design]
top = "{task.top}"
sources = ["design.sv"]

[functional]
commands = [
  ["iverilog", "-g2012", "-o", "${{SVGAP_BUILD}}/sim.vvp", "design.sv", "task-testbench.sv"],
  ["vvp", "${{SVGAP_BUILD}}/sim.vvp"],
]

[[oracles]]
id = "{oracle_id}"
class = "{task.oracle_class}"
backend = "{backend}"
contributes_to_gap = true
required = true

[oracles.options]
{options}
rule_id = "{task.rule_id}"
message = {json.dumps(task.message)}

[[oracles]]
id = "ordinary-lint"
class = "lint"
backend = "lint-verilator"
contributes_to_gap = false
required = false

[oracles.options]
extra_args = ["-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL"]

[intent]

[output]
report = "report.json"
'''


def load_sources(path: Path) -> dict[tuple[str, str, int], dict[str, Any]]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED_DATASET_SHA256:
        raise SystemExit(
            f"HWE-Bench snapshot checksum mismatch: expected {EXPECTED_DATASET_SHA256}, "
            f"got {digest}"
        )
    records: dict[tuple[str, str, int], dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            key = (str(record["org"]), str(record["repo"]), int(record["number"]))
            records[key] = record
    return records


def source_payload(task: Task, record: dict[str, Any]) -> dict[str, Any]:
    base = record.get("base", {})
    base_sha = base.get("sha") if isinstance(base, dict) else str(base)
    return {
        "schema_version": "1.0",
        "task_id": task.task_id,
        "derivation": "standalone real-fix-derived reduction; not a full upstream regression",
        "upstream": {
            "org": task.source.org,
            "repo": task.source.repo,
            "pull_request": task.source.number,
            "url": record["html_url"],
            "title": record["title"],
            "base_sha": base_sha,
            "merge_commit_sha": record.get("merge_commit_sha"),
            "fix_patch_sha256": hashlib.sha256(record["fix_patch"].encode()).hexdigest(),
            "level1": record.get("level1"),
            "level2": record.get("level2"),
            "modified_files": record.get("modified_files", []),
        },
        "hwe_bench": {
            "dataset_url": DATASET_URL,
            "dataset_sha256": EXPECTED_DATASET_SHA256,
            "problem_statement": record["problem_statement"],
            "license": "Apache-2.0 for HWE-Bench dataset metadata; upstream RTL retains its own license",
        },
        "reduction": {
            "category": task.category,
            "oracle_class": task.oracle_class,
            "preserved_mechanism": task.context,
            "preserved_contract": task.requirement,
            "limitations": (
                "Reauthored interface and minimal environment isolate one contract; this "
                "does not reproduce upstream integration, performance, or full regression behavior."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hwe-dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite {output}")
    sources = load_sources(args.hwe_dataset.resolve())
    if len(TASKS) != 24 or len({task.task_id for task in TASKS}) != len(TASKS):
        raise SystemExit("task definition must contain 24 unique task IDs")

    source_index = []
    for task in TASKS:
        key = (task.source.org, task.source.repo, task.source.number)
        if key not in sources:
            raise SystemExit(f"missing selected HWE-Bench source record: {key}")
        target = output / "tasks" / task.task_id
        (target / "prompts").mkdir(parents=True)
        prompts = {f"level_{level}": render_prompt(task, level) for level in range(4)}
        for name, payload in prompts.items():
            (target / "prompts" / f"{name}.md").write_text(payload, encoding="utf-8")
        (target / "prompt.md").write_text(prompts["level_2"], encoding="utf-8")
        (target / "tb.sv").write_text(task.testbench, encoding="utf-8")
        (target / "reference-safe.sv").write_text(task.reference_safe, encoding="utf-8")
        (target / "reference-unsafe.sv").write_text(task.reference_unsafe, encoding="utf-8")
        (target / task.support_name).write_text(task.support, encoding="utf-8")
        (target / "manifest.toml").write_text(render_manifest(task), encoding="utf-8")
        provenance = source_payload(task, sources[key])
        (target / "source.json").write_text(
            json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (target / "prompt-contract.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "levels": [
                        {
                            "id": f"level_{level}",
                            "ordinal": level,
                            "label": (
                                "issue symptom",
                                "explicit behavior",
                                "cycle-exact contract",
                                "verification checklist",
                            )[level],
                            "sha256": hashlib.sha256(prompts[f"level_{level}"].encode()).hexdigest(),
                            "words": len(prompts[f"level_{level}"].split()),
                        }
                        for level in range(4)
                    ],
                    "cumulative": True,
                    "held_constant": ["module interface", "smoke test", "hidden oracle", "reference"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (target / "task.toml").write_text(
            f'''id = "{task.task_id}"
top = "{task.top}"
testbench = "tb.sv"
manifest = "manifest.toml"
support_files = ["{task.support_name}"]
oracle_class = "{task.oracle_class}"
category = "{task.category}"
rule_id = "{task.rule_id}"
default_prompt_level = "level_2"

[prompt_levels]
level_0 = "prompts/level_0.md"
level_1 = "prompts/level_1.md"
level_2 = "prompts/level_2.md"
level_3 = "prompts/level_3.md"
''',
            encoding="utf-8",
        )
        source_index.append(provenance)

    (output / "source-index.json").write_text(
        json.dumps(source_index, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "README.md").write_text(_readme(), encoding="utf-8")
    (output / "protocol.md").write_text(_protocol(), encoding="utf-8")
    digest = canonical_tree_digest(output, exclude_names={"freeze.json"})
    (output / "freeze.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "canonical_digest": digest,
                "digest_excludes": ["freeze.json"],
                "tasks": len(TASKS),
                "categories": {
                    category: sum(task.category == category for task in TASKS)
                    for category in sorted({task.category for task in TASKS})
                },
                "prompt_levels": 4,
                "hwe_bench_dataset_sha256": EXPECTED_DATASET_SHA256,
                "status": "prospective local freeze; not externally timestamped preregistration",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"tasks       {len(TASKS)}")
    print(f"digest      {digest}")
    print(f"output      {output}")
    return 0


def _readme() -> str:
    return """# Real-fix prompt-depth taskpack v0.1

This pack contains 24 standalone SystemVerilog reductions derived from 24
historical fail-to-pass records in HWE-Bench: eight protocol, eight temporal,
and eight synthesis/equivalence-semantic tasks. The reductions preserve a bug
mechanism and external contract, not the complete upstream repository or test.
Every task records its PR URL, base SHA, fix-patch digest, original HWE-Bench
problem statement, and an explicit reduction limitation in `source.json`.

Each task has four cumulative model-visible prompt levels. The interface,
functional smoke test, hidden contributing oracle, and reference are identical
at every level. The intended outcome is the minimum observed prompt depth that
closes the contract, not a scalar model leaderboard.

The finite Icarus smoke test is deliberately incomplete. A separate bounded
Yosys property or post-Yosys reference-equivalence miter is the contributing
oracle. Verilator lint is noncontributing context. Both safe and unsafe reference
implementations must pass the smoke test; only the hidden oracle separates them.
"""


def _protocol() -> str:
    return """# Prompt-depth contract-closure protocol

## Treatments

- `level_0`: issue-style symptom and interface only.
- `level_1`: adds an explicit externally observable behavior.
- `level_2`: adds cycle-exact semantics.
- `level_3`: adds a verification-oriented checklist without oracle source code.

Levels are cumulative. Calls are fresh and independent: a model does not see
its output or result at another level. All non-prompt task inputs are matched.

## Outcomes

For each model-configuration/task cell report functional pass, specialized
oracle pass, first observed contract-closing depth, non-monotone level outcomes,
and whether concise oracle feedback repairs a functional-pass/oracle-fail
candidate. Treat no observed closure through level 3 as right-censored. Do not
rank models by a single aggregate pass rate.

## Repair and final verification

The repair call receives the original visible prompt, candidate RTL, and only
the public finding ID/message (never the hidden property or reference). The
returned module is materialized in a fresh directory and re-run through the
same functional, contributing-oracle, and noncontributing-lint profile. Report
repair transitions rather than silently replacing the initial outcome.

## Unit of analysis and limits

The task cluster, not a prompt level or generated candidate, is the resampling
unit. One generation per cell measures these recorded configurations, not a
stochastic population of model behavior. These reauthored reductions support
mechanism-level analysis; HWE-Bench remains the source for full-repository agent
repair claims.
"""


if __name__ == "__main__":
    raise SystemExit(main())
