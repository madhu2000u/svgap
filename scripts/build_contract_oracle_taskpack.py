#!/usr/bin/env python3
"""Build the frozen temporal/protocol/equivalence generation taskpack."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from svgap.provenance import canonical_tree_digest


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "taskpacks/contract-oracles-v0.1"


@dataclass(frozen=True)
class Task:
    task_id: str
    top: str
    oracle_class: str
    rule_id: str
    depth: int
    message: str
    prompt: str
    testbench: str
    reference_safe: str
    reference_unsafe: str
    support_name: str
    support: str
    support_top: str | None = None


TASKS = (
    Task(
        task_id="stream_hold",
        top="stream_hold",
        oracle_class="protocol",
        rule_id="REF-PROT-001",
        depth=10,
        message="output valid or payload changes while the stream is backpressured",
        prompt="""Create a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module stream_hold(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       s_valid,
    input  logic [7:0] s_data,
    output logic       s_ready,
    output logic       m_valid,
    output logic [7:0] m_data,
    input  logic       m_ready
);
```

Implement a one-entry ready/valid elastic buffer. A transfer occurs only when
`valid && ready`. Once `m_valid` is asserted, both `m_valid` and `m_data` must
remain stable for every cycle of downstream backpressure (`m_ready == 0`) and
may change only after acceptance. Reset is synchronous active-low and empties
the buffer. Use portable synthesizable RTL and no vendor primitives.

Return only the module, without markdown or explanation.
""",
        testbench="""`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, s_valid = 0, m_ready = 1;
  logic [7:0] s_data = 0;
  logic s_ready, m_valid;
  logic [7:0] m_data;
  stream_hold dut (.*);
  always #5 clk = ~clk;
  task send(input logic [7:0] value);
    begin
      @(negedge clk); s_valid = 1; s_data = value;
      @(posedge clk); #1;
      if (!m_valid || m_data !== value) $fatal(1, "stream mismatch");
      @(negedge clk); s_valid = 0;
    end
  endtask
  initial begin
    repeat (2) @(posedge clk); @(negedge clk); rst_n = 1;
    send(8'h25); send(8'hA6);
    $display("PASS"); $finish;
  end
endmodule
""",
        reference_safe="""module stream_hold(
  input logic clk, input logic rst_n, input logic s_valid,
  input logic [7:0] s_data, output logic s_ready, output logic m_valid,
  output logic [7:0] m_data, input logic m_ready
);
  assign s_ready = !m_valid || m_ready;
  always_ff @(posedge clk) begin
    if (!rst_n) begin m_valid <= 0; m_data <= 0; end
    else if (s_ready) begin
      m_valid <= s_valid;
      if (s_valid) m_data <= s_data;
    end
  end
endmodule
""",
        reference_unsafe="""module stream_hold(
  input logic clk, input logic rst_n, input logic s_valid,
  input logic [7:0] s_data, output logic s_ready, output logic m_valid,
  output logic [7:0] m_data, input logic m_ready
);
  assign s_ready = m_ready;
  always_ff @(posedge clk) begin
    if (!rst_n) begin m_valid <= 0; m_data <= 0; end
    else begin m_valid <= s_valid; if (s_valid) m_data <= s_data; end
  end
endmodule
""",
        support_name="properties.sv",
        support_top="stream_hold_properties",
        support="""module stream_hold_properties;
  (* anyseq *) logic clk, rst_n, s_valid, m_ready;
  (* anyseq *) logic [7:0] s_data;
  logic s_ready, m_valid;
  logic [7:0] m_data;
  logic f_past_valid;
  stream_hold dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (f_past_valid && $past(rst_n && m_valid && !m_ready)) begin
      assert (m_valid);
      assert (m_data == $past(m_data));
    end
  end
endmodule
""",
    ),
    Task(
        task_id="result_hold",
        top="result_hold",
        oracle_class="protocol",
        rule_id="REF-PROT-001",
        depth=10,
        message="result valid or payload changes before a stalled result is accepted",
        prompt="""Write a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module result_hold(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        produce,
    input  logic [15:0] result_in,
    output logic        produce_ready,
    output logic        result_valid,
    output logic [15:0] result_out,
    input  logic        result_ready
);
```

Implement one-entry decoupling storage. Accept `produce/result_in` only when
`produce && produce_ready`. Present it with `result_valid/result_out`. While
`result_valid && !result_ready`, keep `result_valid` asserted and keep
`result_out` bit-for-bit stable until acceptance. Permit replacement on the
same cycle an old result is accepted. Reset is synchronous active-low and
clears valid. Use portable synthesizable RTL.

Return only the module.
""",
        testbench="""`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, produce = 0, result_ready = 1;
  logic [15:0] result_in = 0;
  logic produce_ready, result_valid;
  logic [15:0] result_out;
  result_hold dut (.*);
  always #5 clk = ~clk;
  task send(input logic [15:0] value);
    begin
      @(negedge clk); produce = 1; result_in = value;
      @(posedge clk); #1;
      if (!result_valid || result_out !== value) $fatal(1, "result mismatch");
      @(negedge clk); produce = 0;
    end
  endtask
  initial begin
    repeat (2) @(posedge clk); @(negedge clk); rst_n = 1;
    send(16'h1234); send(16'hBEEF);
    $display("PASS"); $finish;
  end
endmodule
""",
        reference_safe="""module result_hold(
  input logic clk, input logic rst_n, input logic produce,
  input logic [15:0] result_in, output logic produce_ready,
  output logic result_valid, output logic [15:0] result_out,
  input logic result_ready
);
  assign produce_ready = !result_valid || result_ready;
  always_ff @(posedge clk) begin
    if (!rst_n) begin result_valid <= 0; result_out <= 0; end
    else if (produce_ready) begin
      result_valid <= produce;
      if (produce) result_out <= result_in;
    end
  end
endmodule
""",
        reference_unsafe="""module result_hold(
  input logic clk, input logic rst_n, input logic produce,
  input logic [15:0] result_in, output logic produce_ready,
  output logic result_valid, output logic [15:0] result_out,
  input logic result_ready
);
  assign produce_ready = result_ready;
  always_ff @(posedge clk) begin
    if (!rst_n) begin result_valid <= 0; result_out <= 0; end
    else begin result_valid <= produce; if (produce) result_out <= result_in; end
  end
endmodule
""",
        support_name="properties.sv",
        support_top="result_hold_properties",
        support="""module result_hold_properties;
  (* anyseq *) logic clk, rst_n, produce, result_ready;
  (* anyseq *) logic [15:0] result_in;
  logic produce_ready, result_valid;
  logic [15:0] result_out;
  logic f_past_valid;
  result_hold dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (f_past_valid && $past(rst_n && result_valid && !result_ready)) begin
      assert (result_valid);
      assert (result_out == $past(result_out));
    end
  end
endmodule
""",
    ),
    Task(
        task_id="command_deadline",
        top="command_deadline",
        oracle_class="temporal",
        rule_id="REF-TEMP-001",
        depth=12,
        message="an accepted command does not complete within three cycles",
        prompt="""Create a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module command_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    output logic done
);
```

On a rising edge that samples `start` while idle, accept one command. Ignore
new starts while it is pending. Assert `done` for exactly one clock cycle no
later than the third rising edge after acceptance, then return idle. Reset is
synchronous active-low and clears all state. Use portable synthesizable RTL.

Return only the module.
""",
        testbench="""`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, start = 0, done;
  command_deadline dut (.*);
  always #5 clk = ~clk;
  initial begin
    repeat (2) @(posedge clk); rst_n = 1;
    @(negedge clk); start = 1; @(negedge clk); start = 0;
    repeat (8) begin @(posedge clk); #1; if (done) begin $display("PASS"); $finish; end end
    $fatal(1, "no completion");
  end
endmodule
""",
        reference_safe="""module command_deadline(input logic clk, input logic rst_n,
  input logic start, output logic done);
  logic busy; logic [1:0] age;
  always_ff @(posedge clk) begin
    if (!rst_n) begin busy <= 0; age <= 0; done <= 0; end
    else begin
      done <= 0;
      if (start && !busy) begin busy <= 1; age <= 0; end
      else if (busy && age == 2) begin busy <= 0; done <= 1; end
      else if (busy) age <= age + 1'b1;
    end
  end
endmodule
""",
        reference_unsafe="""module command_deadline(input logic clk, input logic rst_n,
  input logic start, output logic done);
  logic busy; logic [2:0] age;
  always_ff @(posedge clk) begin
    if (!rst_n) begin busy <= 0; age <= 0; done <= 0; end
    else begin
      done <= 0;
      if (start && !busy) begin busy <= 1; age <= 0; end
      else if (busy && age == 4) begin busy <= 0; done <= 1; end
      else if (busy) age <= age + 1'b1;
    end
  end
endmodule
""",
        support_name="properties.sv",
        support_top="command_deadline_properties",
        support="""module command_deadline_properties;
  (* anyseq *) logic clk, rst_n, start;
  logic done, f_past_valid, pending;
  logic [2:0] age;
  command_deadline dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (pending) assume (!start);
    if (!rst_n) begin pending <= 0; age <= 0; end
    else if (start && !pending) begin pending <= 1; age <= 0; end
    else if (pending && done) pending <= 0;
    else if (pending) begin assert (age < 3); age <= age + 1'b1; end
  end
endmodule
""",
    ),
    Task(
        task_id="grant_deadline",
        top="grant_deadline",
        oracle_class="temporal",
        rule_id="REF-TEMP-001",
        depth=10,
        message="an accepted request does not receive a grant within two cycles",
        prompt="""Write a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module grant_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic request,
    output logic grant
);
```

When idle, accept a request on a rising edge. Ignore additional requests while
one is pending. Produce a one-cycle `grant` pulse no later than the second
rising edge after acceptance, then return idle. Reset is synchronous active-low
and clears all state. Use portable synthesizable RTL.

Return only the module.
""",
        testbench="""`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, request = 0, grant;
  grant_deadline dut (.*);
  always #5 clk = ~clk;
  initial begin
    repeat (2) @(posedge clk); rst_n = 1;
    @(negedge clk); request = 1; @(negedge clk); request = 0;
    repeat (6) begin @(posedge clk); #1; if (grant) begin $display("PASS"); $finish; end end
    $fatal(1, "no grant");
  end
endmodule
""",
        reference_safe="""module grant_deadline(input logic clk, input logic rst_n,
  input logic request, output logic grant);
  logic pending;
  always_ff @(posedge clk) begin
    if (!rst_n) begin pending <= 0; grant <= 0; end
    else begin
      grant <= 0;
      if (request && !pending) pending <= 1;
      else if (pending) begin pending <= 0; grant <= 1; end
    end
  end
endmodule
""",
        reference_unsafe="""module grant_deadline(input logic clk, input logic rst_n,
  input logic request, output logic grant);
  logic pending; logic [1:0] age;
  always_ff @(posedge clk) begin
    if (!rst_n) begin pending <= 0; age <= 0; grant <= 0; end
    else begin
      grant <= 0;
      if (request && !pending) begin pending <= 1; age <= 0; end
      else if (pending && age == 2) begin pending <= 0; grant <= 1; end
      else if (pending) age <= age + 1'b1;
    end
  end
endmodule
""",
        support_name="properties.sv",
        support_top="grant_deadline_properties",
        support="""module grant_deadline_properties;
  (* anyseq *) logic clk, rst_n, request;
  logic grant, f_past_valid, pending;
  logic [1:0] age;
  grant_deadline dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (pending) assume (!request);
    if (!rst_n) begin pending <= 0; age <= 0; end
    else if (request && !pending) begin pending <= 1; age <= 0; end
    else if (pending && grant) pending <= 0;
    else if (pending) begin assert (age < 2); age <= age + 1'b1; end
  end
endmodule
""",
    ),
    Task(
        task_id="irq_pulse",
        top="irq_pulse",
        oracle_class="temporal",
        rule_id="REF-TEMP-002",
        depth=8,
        message="the interrupt pulse remains asserted for more than one cycle",
        prompt="""Create a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module irq_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic trigger,
    output logic irq
);
```

For each isolated one-cycle `trigger`, assert `irq` for exactly one clock cycle.
Never stretch the interrupt into a second cycle. Reset is synchronous
active-low and clears `irq`. Use portable synthesizable RTL.

Return only the module.
""",
        testbench="""`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, trigger = 0, irq;
  irq_pulse dut (.*);
  always #5 clk = ~clk;
  initial begin
    repeat (2) @(posedge clk); @(negedge clk); rst_n = 1;
    @(negedge clk); trigger = 1;
    @(posedge clk); #1; if (!irq) $fatal(1, "no interrupt");
    @(negedge clk); trigger = 0;
    $display("PASS"); $finish;
  end
endmodule
""",
        reference_safe="""module irq_pulse(input logic clk, input logic rst_n,
  input logic trigger, output logic irq);
  always_ff @(posedge clk) begin if (!rst_n) irq <= 0; else irq <= trigger; end
endmodule
""",
        reference_unsafe="""module irq_pulse(input logic clk, input logic rst_n,
  input logic trigger, output logic irq);
  logic hold;
  always_ff @(posedge clk) begin
    if (!rst_n) begin irq <= 0; hold <= 0; end
    else begin hold <= trigger; irq <= trigger || hold; end
  end
endmodule
""",
        support_name="properties.sv",
        support_top="irq_pulse_properties",
        support="""module irq_pulse_properties;
  (* anyseq *) logic clk, rst_n, trigger;
  logic irq, f_past_valid;
  irq_pulse dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (f_past_valid && $past(trigger)) assume (!trigger);
    if (f_past_valid && $past(rst_n && irq)) assert (!irq);
  end
endmodule
""",
    ),
    Task(
        task_id="completion_pulse",
        top="completion_pulse",
        oracle_class="temporal",
        rule_id="REF-TEMP-002",
        depth=8,
        message="the completion pulse remains asserted for more than one cycle",
        prompt="""Write a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module completion_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic event_done,
    output logic completed
);
```

Convert each isolated one-cycle `event_done` into an exactly one-cycle
`completed` pulse. `completed` must be low on the following cycle even if no
other event occurs. Reset is synchronous active-low and clears the output. Use
portable synthesizable RTL.

Return only the module.
""",
        testbench="""`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, event_done = 0, completed;
  completion_pulse dut (.*);
  always #5 clk = ~clk;
  initial begin
    repeat (2) @(posedge clk); @(negedge clk); rst_n = 1;
    @(negedge clk); event_done = 1;
    @(posedge clk); #1; if (!completed) $fatal(1, "no completion pulse");
    @(negedge clk); event_done = 0;
    $display("PASS"); $finish;
  end
endmodule
""",
        reference_safe="""module completion_pulse(input logic clk, input logic rst_n,
  input logic event_done, output logic completed);
  always_ff @(posedge clk) begin if (!rst_n) completed <= 0; else completed <= event_done; end
endmodule
""",
        reference_unsafe="""module completion_pulse(input logic clk, input logic rst_n,
  input logic event_done, output logic completed);
  logic delayed;
  always_ff @(posedge clk) begin
    if (!rst_n) begin completed <= 0; delayed <= 0; end
    else begin delayed <= event_done; completed <= event_done || delayed; end
  end
endmodule
""",
        support_name="properties.sv",
        support_top="completion_pulse_properties",
        support="""module completion_pulse_properties;
  (* anyseq *) logic clk, rst_n, event_done;
  logic completed, f_past_valid;
  completion_pulse dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (f_past_valid && $past(event_done)) assume (!event_done);
    if (f_past_valid && $past(rst_n && completed)) assert (!completed);
  end
endmodule
""",
    ),
    Task(
        task_id="opcode_unit",
        top="opcode_unit",
        oracle_class="equivalence",
        rule_id="REF-EQUIV-001",
        depth=1,
        message="the synthesized candidate differs from the complete opcode reference",
        prompt="""Rewrite the following reference as portable synthesizable SystemVerilog.
Preserve its behavior for every input and every opcode after synthesis, not only
for examples or simulation. Use exactly the same module name and interface.

```systemverilog
module opcode_unit(
    input  logic [7:0] a,
    input  logic [7:0] b,
    input  logic [2:0] op,
    output logic [7:0] y
);
    always_comb begin
        case (op)
            3'd0: y = a + b;
            3'd1: y = a - b;
            3'd2: y = a & b;
            3'd3: y = a | b;
            3'd4: y = a ^ b;
            3'd5: y = a << b[2:0];
            3'd6: y = a >> b[2:0];
            default: y = (a < b) ? 8'h01 : 8'h00;
        endcase
    end
endmodule
```

Return only the module, without markdown or explanation.
""",
        testbench="""`timescale 1ns/1ps
module tb;
  logic [7:0] a, b, y; logic [2:0] op;
  opcode_unit dut (.*);
  task check(input logic [2:0] code, input logic [7:0] av, bv, expected);
    begin op = code; a = av; b = bv; #1; if (y !== expected) $fatal(1, "opcode mismatch"); end
  endtask
  initial begin
    check(0, 8'h12, 8'h05, 8'h17);
    check(1, 8'h12, 8'h05, 8'h0d);
    check(2, 8'hac, 8'h66, 8'h24);
    $display("PASS"); $finish;
  end
endmodule
""",
        reference_safe="""module opcode_unit(input logic [7:0] a, input logic [7:0] b,
  input logic [2:0] op, output logic [7:0] y);
  always_comb case (op)
    0: y=a+b; 1: y=a-b; 2: y=a&b; 3: y=a|b; 4: y=a^b;
    5: y=a<<b[2:0]; 6: y=a>>b[2:0]; default: y=(a<b)?1:0;
  endcase
endmodule
""",
        reference_unsafe="""module opcode_unit(input logic [7:0] a, input logic [7:0] b,
  input logic [2:0] op, output logic [7:0] y);
  always_comb case (op)
    0: y=a+b; 1: y=a-b; 2: y=a&b; 3: y=a|b; 4: y=a^b;
    5: y=a<<b[2:0]; 6: y=a>>b[2:0]; default: y=(a>b)?1:0;
  endcase
endmodule
""",
        support_name="reference.sv",
        support="""module opcode_unit(input logic [7:0] a, input logic [7:0] b,
  input logic [2:0] op, output logic [7:0] y);
  always_comb case (op)
    0: y=a+b; 1: y=a-b; 2: y=a&b; 3: y=a|b; 4: y=a^b;
    5: y=a<<b[2:0]; 6: y=a>>b[2:0]; default: y=(a<b)?1:0;
  endcase
endmodule
""",
    ),
    Task(
        task_id="signed_clamp",
        top="signed_clamp",
        oracle_class="equivalence",
        rule_id="REF-EQUIV-001",
        depth=1,
        message="the synthesized candidate differs from the signed-priority reference",
        prompt="""Rewrite the following reference as portable synthesizable SystemVerilog.
Preserve its exact signed and priority semantics after synthesis for every input,
including the reference behavior when `lo > hi`. Use the identical interface.

```systemverilog
module signed_clamp(
    input  logic signed [7:0] x,
    input  logic signed [7:0] lo,
    input  logic signed [7:0] hi,
    output logic signed [7:0] y
);
    always_comb begin
        if (x < lo)
            y = lo;
        else if (x > hi)
            y = hi;
        else
            y = x;
    end
endmodule
```

Return only the module, without markdown or explanation.
""",
        testbench="""`timescale 1ns/1ps
module tb;
  logic signed [7:0] x, lo, hi, y;
  signed_clamp dut (.*);
  task check(input integer xv, lv, hv, expected);
    begin x=xv; lo=lv; hi=hv; #1; if (y !== expected[7:0]) $fatal(1, "clamp mismatch"); end
  endtask
  initial begin
    check(-20, -10, 30, -10); check(40, -10, 30, 30); check(5, -10, 30, 5);
    $display("PASS"); $finish;
  end
endmodule
""",
        reference_safe="""module signed_clamp(input logic signed [7:0] x,
  input logic signed [7:0] lo, input logic signed [7:0] hi,
  output logic signed [7:0] y);
  always_comb if (x < lo) y=lo; else if (x > hi) y=hi; else y=x;
endmodule
""",
        reference_unsafe="""module signed_clamp(input logic signed [7:0] x,
  input logic signed [7:0] lo, input logic signed [7:0] hi,
  output logic signed [7:0] y);
  always_comb if (lo > hi) y=x; else if (x < lo) y=lo; else if (x > hi) y=hi; else y=x;
endmodule
""",
        support_name="reference.sv",
        support="""module signed_clamp(input logic signed [7:0] x,
  input logic signed [7:0] lo, input logic signed [7:0] hi,
  output logic signed [7:0] y);
  always_comb if (x < lo) y=lo; else if (x > hi) y=hi; else y=x;
endmodule
""",
    ),
)


def render_manifest(task: Task) -> str:
    if task.oracle_class == "equivalence":
        options = f'''reference_sources = ["{task.support_name}"]
reference_top = "{task.top}"
depth = {task.depth}'''
        backend = "equivalence-yosys"
        oracle_id = "synthesized-reference"
    else:
        options = f'''property_sources = ["{task.support_name}"]
property_top = "{task.support_top}"
depth = {task.depth}'''
        backend = "formal-yosys"
        oracle_id = "contract-property"
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
extra_args = ["-Wno-DECLFILENAME"]

[intent]

[output]
report = "report.json"
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite {output}")
    for task in TASKS:
        target = output / "tasks" / task.task_id
        target.mkdir(parents=True)
        (target / "prompt.md").write_text(task.prompt, encoding="utf-8")
        (target / "tb.sv").write_text(task.testbench, encoding="utf-8")
        (target / "reference-safe.sv").write_text(task.reference_safe, encoding="utf-8")
        (target / "reference-unsafe.sv").write_text(task.reference_unsafe, encoding="utf-8")
        (target / task.support_name).write_text(task.support, encoding="utf-8")
        (target / "manifest.toml").write_text(render_manifest(task), encoding="utf-8")
        (target / "task.toml").write_text(
            f'''id = "{task.task_id}"
top = "{task.top}"
testbench = "tb.sv"
manifest = "manifest.toml"
support_files = ["{task.support_name}"]
oracle_class = "{task.oracle_class}"
rule_id = "{task.rule_id}"
''',
            encoding="utf-8",
        )
    (output / "README.md").write_text(
        """# Contract-oracle generation study v0.1

Eight frozen generation tasks exercise four SV-Gap rules beyond CDC/RDC and
power-on structure: ready/valid persistence (`REF-PROT-001`), bounded response
(`REF-TEMP-001`), one-cycle pulse width (`REF-TEMP-002`), and synthesized
reference equivalence (`REF-EQUIV-001`). Each rule has two task clusters.

Every task has a finite Icarus smoke test plus a distinct contributing formal
property or synthesized-reference oracle. The safe and unsafe references both
pass the same smoke test; the specialized oracle separates them. Verilator lint
is retained as noncontributing context. The design is a prospective local
freeze, not an externally timestamped preregistration or a population sample.
""",
        encoding="utf-8",
    )
    (output / "protocol.md").write_text(
        """# Contract-oracle study protocol

## Question

Among fresh model generations that pass each task's finite smoke test, does a
property-appropriate protocol, temporal, or synthesized-equivalence oracle find
violations of an explicit requirement that the smoke test does not identify?

## Frozen design

- Eight task clusters: two per contributing rule.
- Fresh single-turn calls with tools disabled and no repair.
- Two calls per model-task cell in the initial multi-model run.
- Candidate-level functional and oracle outcomes, grouped by task.
- Task-resampling intervals reported only as finite-task sensitivity analyses.

The primary count is functional pass plus contributing-oracle fail. Compile
errors, functional failures, unknowns, and tool errors remain separate. Model
results are descriptive; the study is not powered for a leaderboard. Ordinary
lint is contextual and cannot contribute to gap membership.

## Calibration

Before generation, both references for every task must pass the same functional
test. The safe reference must pass its contributing oracle and the unsafe
reference must fail with the task's declared rule. Any failing calibration
blocks model-outcome interpretation.
""",
        encoding="utf-8",
    )
    digest = canonical_tree_digest(output, exclude_names={"freeze.json"})
    (output / "freeze.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "canonical_digest": digest,
                "digest_excludes": ["freeze.json"],
                "tasks": len(TASKS),
                "task_clusters_per_rule": 2,
                "rules": sorted({task.rule_id for task in TASKS}),
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


if __name__ == "__main__":
    raise SystemExit(main())
