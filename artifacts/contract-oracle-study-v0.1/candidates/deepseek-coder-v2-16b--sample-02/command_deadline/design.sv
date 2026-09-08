module command_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    output logic done
);

    // Define states for the FSM
    typedef enum {IDLE, PENDING} state_t;
    state_t state, next_state;

    // State transition logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // Next state logic based on current state and input start signal
    always_comb begin
        case (state)
            IDLE:   next_state = start ? PENDING : IDLE;
            PENDING:next_state = (start || $past(start, 3)) ? PENDING : DONE;
            default:next_state = IDLE;
        endcase
    end

    // Output logic for done signal
    always_comb begin
        case (state)
            IDLE:   done = 0;
            PENDING:done = ($past(start, 3)) ? 1 : 0;
            DONE:   done = 0;
            default:done = 0;
        endcase
    end
endmodule
