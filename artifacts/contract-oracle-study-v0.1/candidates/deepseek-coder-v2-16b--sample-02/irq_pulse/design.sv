module irq_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic trigger,
    output logic irq
);

    // State variable to hold the state of the IRQ signal
    enum logic {IDLE, ASSERT} state, next_state;

    // Sequential part of the FSM
    always_ff @(posedge clk or negedge rst_n) begin : state_transition
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // Combinational logic for the FSM
    always_comb begin : fsm_logic
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

    // Output logic for the FSM
    always_comb begin : output_logic
        irq = 0;
        case (state)
            ASSERT:
                irq = 1;
            default:
                ;
        endcase
    end

endmodule
