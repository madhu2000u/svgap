module irq_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic trigger,
    output logic irq
);

    // State variable to hold the state of the IRQ signal
    enum logic {IDLE, ASSERT} state, next_state;

    // Sequential block to update the state on each clock cycle
    always_ff @(posedge clk or negedge rst_n) begin : state_transition
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // Combinational block to determine the next state based on current state and inputs
    always_comb begin : next_state_logic
        case (state)
            IDLE: 
                if (trigger)
                    next_state = ASSERT;
                else
                    next_state = IDLE;
            ASSERT:
                next_state = IDLE;
            default:
                next_state = IDLE;
        endcase
    end

    // Combinational block to assign the output based on the current state
    always_comb begin : output_logic
        case (state)
            IDLE: irq = 1'b0;
            ASSERT: irq = 1'b1;
            default: irq = 1'b0;
        endcase
    end

endmodule
